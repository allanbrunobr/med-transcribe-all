from pocketflow import Flow
from nodes import WebSocketHandlerNode, StructureMedicalDataNode, AnalyzeMedicalDataNode, ResponderNode

def create_medical_transcription_flow():
    """Cria e retorna um fluxo para transcrição médica."""
    # Criar nós
    websocket_handler = WebSocketHandlerNode()
    structure_data = StructureMedicalDataNode()
    analyze_data = AnalyzeMedicalDataNode()
    responder = ResponderNode()
    
    # Conectar nós com transições específicas
    websocket_handler - "structure" >> structure_data
    websocket_handler - "respond" >> responder
    websocket_handler - "error" >> responder
    
    structure_data - "analyze" >> analyze_data
    
    analyze_data - "respond" >> responder
    
    # Retornar o fluxo começando pelo manipulador de WebSocket
    return Flow(start=websocket_handler)

# Criar o fluxo de transcrição médica
medical_transcription_flow = create_medical_transcription_flow()