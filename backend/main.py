from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
from utils.websocket_manager import WebSocketManager
from flow import medical_transcription_flow

# Criar aplicação FastAPI
app = FastAPI(title="Medical Transcription API")

# Configurar CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas as origens em desenvolvimento
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Criar gerenciador de WebSockets
manager = WebSocketManager()

@app.get("/")
async def root():
    return {"message": "Medical Transcription API is running"}

@app.get("/api/status")
async def get_status():
    return {
        "status": "running", 
        "clients": manager.get_connection_count(),
        "version": "1.0.0"
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Conectar o cliente
    client_id = await manager.connect(websocket)
    print(f"Cliente WebSocket conectado. Total: {client_id}")
    
    try:
        while True:
            # Receber dados do cliente
            data = await websocket.receive_text()
            print(f"Dados recebidos: {data[:50]}...")
            
            # Criar estrutura compartilhada para o fluxo
            shared = {
                "websocket": websocket
            }
            
            # Executar o fluxo com os dados recebidos
            medical_transcription_flow.set_params({"data": data})
            medical_transcription_flow.run(shared)
            
            # Se houver uma resposta pronta, enviá-la de volta ao cliente
            if shared.get("response_ready", False):
                try:
                    await manager.send_personal_message(shared["response"], websocket)
                    print(f"Resposta enviada: {shared['response'][:50]}...")
                except Exception as e:
                    print(f"Erro ao enviar resposta: {str(e)}")
    
    except WebSocketDisconnect:
        # Gerenciar desconexão do cliente
        client_count = manager.disconnect(websocket)
        print(f"Cliente WebSocket desconectado. Restantes: {client_count}")
        
        # Notificar outros clientes sobre a desconexão
        if client_count > 0:
            await manager.broadcast(json.dumps({"message": "Client disconnected"}))
    
    except Exception as e:
        print(f"Erro no WebSocket: {str(e)}")
        if websocket in manager.active_connections:
            manager.disconnect(websocket)
        await manager.broadcast(json.dumps({"error": str(e)}))

# Função para execução standalone
def main():
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)

if __name__ == "__main__":
    main()
