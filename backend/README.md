# Medical Transcription Backend

Este é o backend do aplicativo de transcrição médica, desenvolvido em Python com FastAPI.

## Funcionalidades

- Recebe transcrições em tempo real via WebSocket
- Estrutura dados médicos a partir das transcrições
- Fornece análises preliminares dos dados médicos
- API REST para status e controle

## Instalação

1. Instale as dependências:

```
pip install -r requirements.txt
```

2. Execute o servidor:

```
python run.py
```

O servidor será iniciado em `http://localhost:3000` com recarga automática durante o desenvolvimento.

## Endpoints

- `GET /` - Verifica se a API está funcionando
- `GET /api/status` - Retorna o status do servidor
- `WebSocket /ws` - Conecta via WebSocket para receber e enviar transcrições

## Modelos de Dados

### Transcript

```
{
  "preview": string,
  "note": string,
  "listening": boolean,
  "noMatch": boolean,
  "command": string (opcional)
}
```

### StructuredResponse

```
{
  "transcript": string,
  "structured_data": {
    "symptoms": string[],
    "diagnoses": string[],
    "medications": string[],
    "procedures": string[],
    "vital_signs": object,
    "notes": string
  },
  "analysis": string
}
```

## Próximos Passos

- Integração com modelos de linguagem para análise mais avançada
- Implementação de autenticação e autorização
- Armazenamento persistente de transcrições e análises
- Geração de relatórios médicos estruturados
