import json
from typing import Dict, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Modelo para as transcrições
class Transcript(BaseModel):
    preview: str = ""
    note: str = ""
    listening: bool
    noMatch: bool = False
    command: Optional[str] = None

# Modelo para mensagens estruturadas
class StructuredResponse(BaseModel):
    transcript: str
    structured_data: Dict
    analysis: str

app = FastAPI(title="Medical Transcription API")

# Configurar CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas as origens em desenvolvimento
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gerenciador de conexões WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Estruturar dados médicos a partir da transcrição
def structure_medical_data(transcript: str) -> Dict:
    # Aqui você pode implementar a lógica para estruturar os dados médicos
    # Por enquanto, retornamos uma estrutura básica
    structured_data = {
        "symptoms": [],
        "diagnoses": [],
        "medications": [],
        "procedures": [],
        "vital_signs": {},
        "notes": transcript
    }
    
    # Exemplo simples de extração (a ser expandido com técnicas mais avançadas)
    if "dor" in transcript.lower():
        structured_data["symptoms"].append("dor")
    if "febre" in transcript.lower():
        structured_data["symptoms"].append("febre")
    if "pressão" in transcript.lower() or "pressao" in transcript.lower():
        structured_data["vital_signs"]["pressão arterial"] = "mencionada, valor não especificado"
    
    return structured_data

# Analisar os dados médicos
def analyze_medical_data(structured_data: Dict) -> str:
    # Aqui você pode implementar a lógica para analisar os dados médicos
    # Por enquanto, retornamos uma análise básica
    analysis = "Análise preliminar:\n"
    
    if structured_data["symptoms"]:
        analysis += f"- Sintomas identificados: {', '.join(structured_data['symptoms'])}\n"
    else:
        analysis += "- Nenhum sintoma claramente identificado\n"
        
    if structured_data["vital_signs"]:
        analysis += "- Sinais vitais mencionados: "
        for sign, value in structured_data["vital_signs"].items():
            analysis += f"{sign}: {value}; "
        analysis += "\n"
    
    return analysis

@app.get("/")
async def root():
    return {"message": "Medical Transcription API is running"}

@app.get("/api/status")
async def get_status():
    return {
        "status": "running", 
        "clients": len(manager.active_connections),
        "version": "1.0.0"
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                # Parsear os dados recebidos
                transcript_data = json.loads(data)
                transcript = Transcript(**transcript_data)
                
                # Processar apenas se houver conteúdo na nota
                if transcript.note:
                    # Estruturar os dados médicos
                    structured_data = structure_medical_data(transcript.note)
                    
                    # Analisar os dados médicos
                    analysis = analyze_medical_data(structured_data)
                    
                    # Criar resposta estruturada
                    response = StructuredResponse(
                        transcript=transcript.note,
                        structured_data=structured_data,
                        analysis=analysis
                    )
                    
                    # Enviar resposta estruturada de volta
                    await manager.send_personal_message(json.dumps(response.dict()), websocket)
                    
                # Repassar a mensagem original para todos os clientes
                await manager.broadcast(data)
                
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"error": "Invalid JSON format"}))
            except Exception as e:
                await websocket.send_text(json.dumps({"error": str(e)}))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(json.dumps({"message": "Client disconnected"}))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True) 