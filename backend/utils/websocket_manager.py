from typing import List
from fastapi import WebSocket
import logging

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.logger.info(f"Cliente conectado. Total: {len(self.active_connections)}")
        return len(self.active_connections)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        self.logger.info(f"Cliente desconectado. Restantes: {len(self.active_connections)}")
        return len(self.active_connections)

    def is_connected(self, websocket: WebSocket) -> bool:
        """Verifica se o WebSocket ainda está conectado"""
        # Verificação simplificada - se está na lista de conexões ativas
        return websocket in self.active_connections

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Envia uma mensagem para um cliente específico se estiver conectado"""
        if not self.is_connected(websocket):
            self.logger.warning("Tentativa de enviar mensagem para cliente desconectado")
            return False
            
        try:
            await websocket.send_text(message)
            return True
        except Exception as e:
            self.logger.error(f"Erro ao enviar mensagem: {str(e)}")
            # Se houver erro, provavelmente a conexão foi perdida
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
            return False

    async def broadcast(self, message: str):
        """Envia mensagem para todos os clientes conectados"""
        disconnected_clients = []
        sent_count = 0
        
        for connection in self.active_connections:
            try:
                if self.is_connected(connection):
                    await connection.send_text(message)
                    sent_count += 1
                else:
                    disconnected_clients.append(connection)
            except Exception:
                disconnected_clients.append(connection)
        
        # Remover clientes desconectados
        for client in disconnected_clients:
            if client in self.active_connections:
                self.active_connections.remove(client)
                
        if disconnected_clients:
            self.logger.info(f"Removidos {len(disconnected_clients)} clientes desconectados")
            
        return sent_count

    def get_connection_count(self):
        return len(self.active_connections)

if __name__ == "__main__":
    # Este é um exemplo de como usar o WebSocketManager
    # Em uma aplicação real, seria usado com FastAPI
    print("WebSocketManager criado para gerenciar conexões WebSocket") 