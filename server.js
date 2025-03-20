const express = require("express");
const http = require("http");
const WebSocket = require("ws");
const path = require("path");
const cors = require("cors");
const app = express();
const port = 3000;

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

// WebSocket connection handler
wss.on("connection", (ws) => {
  console.log("Client connected");
  clients.add(ws);

  // Handle messages from clients
  ws.on("message", (message) => {
    try {
      // Parse the message once
      const data = JSON.parse(message);
      console.log("Received:", data);

      // Create a simple transcript object
      const transcript = {};
      transcript.preview = String(data.preview || "");
      transcript.note = String(data.note || "");
      transcript.listening = Boolean(data.listening);
      transcript.noMatch = Boolean(data.noMatch);

      // Convert to JSON with proper formatting
      const jsonString = JSON.stringify(transcript);
      console.log("Sending:", jsonString);

      // Broadcast to all connected clients (including Rust app)
      clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
          client.send(jsonString);
        }
      });
    } catch (error) {
      console.error("Error parsing message:", error);
    }
  });

  // Handle client disconnection
  ws.on("close", () => {
    console.log("Client disconnected");
    clients.delete(ws);
  });
});

// API routes
app.get("/api/status", (req, res) => {
  res.json({ status: "running", clients: clients.size });
});

app.post("/api/start", (req, res) => {
  // Create a transcript object that includes command and is compatible with Rust struct
  const message = {
    preview: "",
    note: "",
    listening: true,
    noMatch: false,
    command: "start",
  };

  // Broadcast to all clients
  clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify(message));
    }
  });

  res.json({ success: true, message: "Start command sent" });
});

app.post("/api/stop", (req, res) => {
  // Create a transcript object that includes command and is compatible with Rust struct
  const message = {
    preview: "",
    note: "",
    listening: false,
    noMatch: false,
    command: "stop",
  };

  // Broadcast to all clients
  clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify(message));
    }
  });

  res.json({ success: true, message: "Stop command sent" });
});

// Start server
server.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
  console.log(`WebSocket server running at ws://localhost:${port}`);
});
