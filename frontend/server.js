const express = require("express");
const http = require("http");
const WebSocket = require("ws");
const path = require("path");
const cors = require("cors");
const app = express();
const port = 4000;

// Backend Python URL e WebSocket (opcional)
const BACKEND_HOST = "127.0.0.1"; // Use IPv4 explicitamente
const BACKEND_PORT = 3000;
const PYTHON_BACKEND_URL = `http://${BACKEND_HOST}:${BACKEND_PORT}`;
const PYTHON_BACKEND_WS = `ws://${BACKEND_HOST}:${BACKEND_PORT}/ws`;
const USE_BACKEND = true; // Defina como false para usar apenas o frontend

// Enable CORS for all routes
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

// Create HTTP server
const server = http.createServer(app);

// Create WebSocket server
const wss = new WebSocket.Server({ server });

// Store active connections
const clients = new Set();

// Conectar ao backend Python via WebSocket
let backendWs = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 10;
const INITIAL_RECONNECT_DELAY = 1000; // 1 segundo

function connectToBackend() {
  if (!USE_BACKEND) {
    console.log("Modo independente: backend não será utilizado");
    return;
  }

  reconnectAttempts++;
  console.log(`Tentativa de conexão ao backend #${reconnectAttempts}...`);

  try {
    backendWs = new WebSocket(PYTHON_BACKEND_WS);

    backendWs.on("open", () => {
      console.log("Conectado ao backend Python com sucesso!");
      // Resetar contagem de tentativas quando conectar com sucesso
      reconnectAttempts = 0;

      // Enviar uma mensagem de teste para confirmar comunicação bidirecional
      const testMessage = {
        preview: "",
        note: "",
        listening: false,
        noMatch: false,
        command: "connect_test",
      };
      backendWs.send(JSON.stringify(testMessage));
    });

    backendWs.on("message", (message) => {
      try {
        const data = JSON.parse(message);
        console.log("Recebido do backend Python:", data);

        // Garantir que a resposta estruturada do backend seja enviada corretamente
        let clientMessage = message;

        // Verificar se é uma resposta estruturada do backend com análise
        if (data.transcript && data.structured_data && data.analysis) {
          console.log("Enviando análise médica estruturada para o cliente");
        }

        // Broadcast mensagem para todos os clientes web
        clients.forEach((client) => {
          if (client.readyState === WebSocket.OPEN) {
            client.send(clientMessage.toString());
          }
        });
      } catch (error) {
        console.error("Erro ao processar mensagem do backend:", error);
      }
    });

    backendWs.on("close", () => {
      console.log("Conexão com backend Python fechada");
      backendWs = null;

      // Calcular delay exponencial com backoff máximo de 30 segundos
      const delay = Math.min(
        INITIAL_RECONNECT_DELAY * Math.pow(2, reconnectAttempts - 1),
        30000
      );

      if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        console.log(`Tentando reconectar em ${delay / 1000} segundos...`);
        setTimeout(connectToBackend, delay);
      } else {
        console.log(
          "Número máximo de tentativas excedido. Usando modo independente."
        );
      }
    });

    backendWs.on("error", (error) => {
      console.error("Erro na conexão com o backend Python:", error);
      // Não fechar aqui, deixar o evento 'close' lidar com isso
    });
  } catch (error) {
    console.error("Falha ao conectar com o backend Python:", error);

    // Calcular delay exponencial com backoff máximo de 30 segundos
    const delay = Math.min(
      INITIAL_RECONNECT_DELAY * Math.pow(2, reconnectAttempts - 1),
      30000
    );

    if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
      console.log(`Tentando reconectar em ${delay / 1000} segundos...`);
      setTimeout(connectToBackend, delay);
    } else {
      console.log(
        "Número máximo de tentativas excedido. Usando modo independente."
      );
    }
  }
}

// Conectar ao backend Python quando o servidor iniciar (se habilitado)
connectToBackend();

// WebSocket connection handler
wss.on("connection", (ws) => {
  console.log("Cliente web conectado");
  clients.add(ws);

  // Handle messages from web clients
  ws.on("message", (message) => {
    try {
      // Parse the message once
      const data = JSON.parse(message);
      console.log("Recebido do cliente web:", data);

      // Create a transcript object
      const transcript = {};
      transcript.preview = String(data.preview || "");
      transcript.note = String(data.note || "");
      transcript.listening = Boolean(data.listening);
      transcript.noMatch = Boolean(data.noMatch);
      if (data.command) {
        transcript.command = String(data.command);
      }

      // Enviar para o backend Python se estiver conectado
      if (USE_BACKEND && backendWs && backendWs.readyState === WebSocket.OPEN) {
        try {
          backendWs.send(JSON.stringify(transcript));
          console.log("Enviado para o backend Python:", transcript);
        } catch (error) {
          console.error("Erro ao enviar para o backend:", error);
          // Se falhar, tentar reconectar
          if (backendWs) {
            backendWs.close();
            backendWs = null;
          }
          connectToBackend();
        }
      } else if (USE_BACKEND) {
        console.log("Tentando reconectar ao backend antes de enviar...");
        connectToBackend();
      }

      // Broadcast to all web clients
      clients.forEach((client) => {
        if (client !== ws && client.readyState === WebSocket.OPEN) {
          client.send(JSON.stringify(transcript));
        }
      });
    } catch (error) {
      console.error("Erro ao processar mensagem do cliente:", error);
    }
  });

  // Handle client disconnection
  ws.on("close", () => {
    console.log("Cliente web desconectado");
    clients.delete(ws);
  });
});

// API routes
app.get("/api/status", (req, res) => {
  const backendConnected =
    USE_BACKEND && backendWs && backendWs.readyState === WebSocket.OPEN;

  res.json({
    status: "running",
    mode: USE_BACKEND ? "completo" : "independente",
    clients: clients.size,
    backendConnected: backendConnected,
  });
});

app.post("/api/start", (req, res) => {
  const message = {
    preview: "",
    note: "",
    listening: true,
    noMatch: false,
    command: "start",
  };

  // Enviar comando para o backend Python
  if (USE_BACKEND && backendWs && backendWs.readyState === WebSocket.OPEN) {
    backendWs.send(JSON.stringify(message));
  }

  // Broadcast para clientes web
  clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify(message));
    }
  });

  res.json({ success: true, message: "Comando 'start' enviado" });
});

app.post("/api/stop", (req, res) => {
  const message = {
    preview: "",
    note: "",
    listening: false,
    noMatch: false,
    command: "stop",
  };

  // Enviar comando para o backend Python
  if (USE_BACKEND && backendWs && backendWs.readyState === WebSocket.OPEN) {
    backendWs.send(JSON.stringify(message));
  }

  // Broadcast para clientes web
  clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify(message));
    }
  });

  res.json({ success: true, message: "Comando 'stop' enviado" });
});

// Start server
server.listen(port, () => {
  console.log(`Frontend server rodando em http://localhost:${port}`);
  console.log(`WebSocket server rodando em ws://localhost:${port}`);

  if (USE_BACKEND) {
    console.log(`Conectando ao Python backend em ${PYTHON_BACKEND_URL}`);
  } else {
    console.log("Rodando em modo independente (sem backend)");
  }
});
