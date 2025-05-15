# Med Transcribe All

Uma aplicação para transcrição médica que captura áudio, transcreve e estrutura os dados médicos.

## Estrutura do Projeto

O projeto está organizado em duas partes principais:

### Frontend

A interface do usuário que captura áudio, exibe transcrições e interage com o usuário.

- Tecnologia: JavaScript/React
- Localização: `/frontend`
- Funciona independentemente ou em conjunto com o backend

### Backend

Servidor que recebe as transcrições, estrutura os dados médicos e fornece análises.

- Tecnologia: Python com FastAPI
- Localização: `/backend`
- Opcional - o frontend funciona mesmo sem o backend

## Modos de Execução

### 1. Modo Completo (Frontend + Backend)

Utiliza todas as funcionalidades, incluindo a análise médica estruturada.

```
./start.sh
```

### 2. Modo Frontend (Sem Backend)

Executa apenas o frontend para captura e exibição de transcrições, sem análise estruturada.

```
./start.sh frontend
```

## Iniciando o Projeto Manualmente

### Pré-requisitos

- Node.js e npm (para o frontend)
- Python 3.8+ (para o backend)

### Backend (Opcional)

1. Navegue até a pasta do backend:

```
cd backend
```

2. Instale as dependências:

```
pip install -r requirements.txt
```

3. Inicie o servidor:

```
python run.py
```

### Frontend

1. Navegue até a pasta do frontend:

```
cd frontend
```

2. Instale as dependências:

```
npm install
```

3. Inicie o servidor de desenvolvimento:

```
node server.js
```

## Endereços de Acesso

- Frontend: http://localhost:4000
- Backend API: http://localhost:3000
- WebSocket Backend: ws://localhost:3000/ws

## Fluxo da Aplicação

1. O usuário fala no microfone
2. O frontend captura o áudio e o transcreve usando a API Web Speech
3. As transcrições são exibidas na interface do usuário
4. Se o backend estiver ativo, as transcrições são enviadas para processamento
5. O backend analisa e estrutura os dados médicos (opcional)
6. Os resultados da análise são exibidos ao usuário (se o backend estiver ativo)

## Funcionalidades

- Captura de áudio e transcrição em tempo real
- Exibição imediata das transcrições no navegador
- Estruturação de dados médicos a partir de transcrições (requer backend)
- Análise preliminar dos dados médicos (requer backend)
