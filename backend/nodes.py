import json
from typing import Dict, Any, Optional
from fastapi import WebSocket
from pocketflow import Node
from utils.call_llm import call_llm
from pydantic import BaseModel

# Modelo para as transcrições
class Transcript(BaseModel):
    preview: str = ""
    note: str = ""
    listening: bool
    noMatch: bool = False
    command: Optional[str] = None

class WebSocketHandlerNode(Node):
    def prep(self, shared):
        """Obtém os dados do parâmetro"""
        return self.params.get("data", "")
    
    def exec(self, data):
        """Parseia os dados JSON recebidos do WebSocket"""
        try:
            transcript_data = json.loads(data)
            transcript = Transcript(**transcript_data)
            return transcript
        except Exception as e:
            return {"error": str(e)}
    
    def post(self, shared, prep_res, exec_res):
        """Armazena os dados de transcrição no shared"""
        if isinstance(exec_res, dict) and "error" in exec_res:
            # Retornar erro se ocorrer
            shared["error"] = exec_res["error"]
            return "error"
        
        shared["transcript"] = exec_res
        
        # Se não tiver conteúdo na nota, não prosseguir para estruturação
        if not exec_res.note:
            return "respond"
        
        return "structure"  # Próximo passo é estruturar os dados

class StructureMedicalDataNode(Node):
    def prep(self, shared):
        """Lê a transcrição da memória compartilhada"""
        return shared["transcript"].note
    
    def exec(self, transcript_text):
        """Estrutura os dados médicos da transcrição"""
        # Estrutura básica de dados médicos
        structured_data = {
            "symptoms": [],
            "diagnoses": [],
            "medications": [],
            "procedures": [],
            "vital_signs": {},
            "notes": transcript_text
        }
        
        # Exemplo simples de extração - na versão final, usar LLM para análise completa
        if "dor" in transcript_text.lower():
            structured_data["symptoms"].append("dor")
        if "febre" in transcript_text.lower():
            structured_data["symptoms"].append("febre")
        if "pressão" in transcript_text.lower() or "pressao" in transcript_text.lower():
            structured_data["vital_signs"]["pressão arterial"] = "mencionada, valor não especificado"
        if "diabetes" in transcript_text.lower():
            structured_data["diagnoses"].append("diabetes")
        if "insulina" in transcript_text.lower():
            structured_data["medications"].append("insulina")
            
        return structured_data
    
    def post(self, shared, prep_res, exec_res):
        """Armazena os dados estruturados no shared"""
        shared["structured_data"] = exec_res
        return "analyze"  # Próximo passo é analisar os dados

class AnalyzeMedicalDataNode(Node):
    def prep(self, shared):
        """Lê os dados estruturados da memória compartilhada"""
        return shared["structured_data"]
    
    def exec(self, structured_data):
        """Analisa os dados médicos estruturados"""
        analysis = "Análise preliminar:\n"
        
        if structured_data["symptoms"]:
            analysis += f"- Sintomas identificados: {', '.join(structured_data['symptoms'])}\n"
        else:
            analysis += "- Nenhum sintoma claramente identificado\n"
            
        if structured_data["diagnoses"]:
            analysis += f"- Possíveis diagnósticos: {', '.join(structured_data['diagnoses'])}\n"
            
        if structured_data["medications"]:
            analysis += f"- Medicamentos mencionados: {', '.join(structured_data['medications'])}\n"
            
        if structured_data["vital_signs"]:
            analysis += "- Sinais vitais mencionados: "
            for sign, value in structured_data["vital_signs"].items():
                analysis += f"{sign}: {value}; "
            analysis += "\n"
        
        return analysis
    
    def post(self, shared, prep_res, exec_res):
        """Armazena a análise no shared"""
        shared["analysis"] = exec_res
        return "respond"  # Próximo passo é responder

class ResponderNode(Node):
    def prep(self, shared):
        """Lê todos os dados necessários para construir a resposta"""
        return {
            "transcript": shared.get("transcript"),
            "structured_data": shared.get("structured_data", {}),
            "analysis": shared.get("analysis", ""),
            "websocket": shared.get("websocket"),
            "error": shared.get("error")
        }
    
    def exec(self, data):
        """Formata a resposta para o cliente"""
        if "error" in data and data["error"]:
            return json.dumps({"error": data["error"]})
        
        try:    
            # Se tiver transcrição completa, incluir dados estruturados e análise
            if data["transcript"] and hasattr(data["transcript"], "note") and data["transcript"].note:
                if hasattr(data["transcript"], "dict"):
                    transcript_data = data["transcript"].dict()
                else:
                    transcript_data = {
                        "preview": getattr(data["transcript"], "preview", ""),
                        "note": getattr(data["transcript"], "note", ""),
                        "listening": getattr(data["transcript"], "listening", False),
                        "noMatch": getattr(data["transcript"], "noMatch", False),
                        "command": getattr(data["transcript"], "command", None)
                    }
                
                response = {
                    "transcript": transcript_data,
                    "structured_data": data["structured_data"],
                    "analysis": data["analysis"]
                }
            else:
                # Caso contrário, apenas repassar a transcrição original
                if data["transcript"] and hasattr(data["transcript"], "dict"):
                    transcript_data = data["transcript"].dict()
                elif data["transcript"]:
                    transcript_data = {
                        "preview": getattr(data["transcript"], "preview", ""),
                        "note": getattr(data["transcript"], "note", ""),
                        "listening": getattr(data["transcript"], "listening", False),
                        "noMatch": getattr(data["transcript"], "noMatch", False),
                        "command": getattr(data["transcript"], "command", None)
                    }
                else:
                    transcript_data = {}
                
                response = {
                    "transcript": transcript_data
                }
                
            return json.dumps(response)
        except Exception as e:
            print(f"Erro ao formatar resposta: {str(e)}")
            # Resposta mais simples em caso de erro
            return json.dumps({
                "error": f"Erro ao formatar resposta: {str(e)}",
                "transcript": {"note": "", "listening": False}
            })
    
    def post(self, shared, prep_res, exec_res):
        """Armazena a resposta formatada para ser enviada pelo handler WebSocket"""
        # A mensagem será enviada pelo handler WebSocket
        shared["response"] = exec_res
        shared["response_ready"] = True
        
        # Limpar dados que não são mais necessários
        if "error" in shared:
            del shared["error"]
            
        return "done"  # Fluxo concluído