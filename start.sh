#!/bin/bash

# Verificar parâmetros de linha de comando
MODE="full"
if [ "$1" = "frontend" ]; then
  MODE="frontend"
fi

# Cores para saída
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}Iniciando Med Transcribe All${NC}"
if [ "$MODE" = "frontend" ]; then
  echo -e "${GREEN}Modo: Frontend (sem backend)${NC}"
else
  echo -e "${GREEN}Modo: Completo (frontend + backend)${NC}"
fi
echo -e "${BLUE}===============================================${NC}"

# Iniciar o backend Python em segundo plano (se em modo completo)
if [ "$MODE" = "full" ]; then
  echo -e "${GREEN}Iniciando backend Python...${NC}"
  cd backend
  python run.py &
  BACKEND_PID=$!
  cd ..

  # Dar um tempo para o backend iniciar
  echo -e "${GREEN}Aguardando o backend iniciar (5 segundos)...${NC}"
  sleep 5
  
  # Verificar se o backend está respondendo
  if curl -s http://127.0.0.1:3000 > /dev/null; then
    echo -e "${GREEN}Backend inicializado com sucesso!${NC}"
  else
    echo -e "${GREEN}Aviso: Backend pode não ter iniciado corretamente.${NC}"
    echo -e "${GREEN}Continuando mesmo assim...${NC}"
  fi
fi

# Iniciar o frontend Node.js
echo -e "${GREEN}Iniciando frontend Node.js...${NC}"
cd frontend

# Se estiver em modo frontend, alterar a configuração do servidor
if [ "$MODE" = "frontend" ]; then
  # Criar uma cópia temporária do arquivo
  cp server.js server.js.tmp
  
  # Substituir a configuração USE_BACKEND
  sed -i '' 's/const USE_BACKEND = true;/const USE_BACKEND = false;/' server.js
fi

node server.js &
FRONTEND_PID=$!

# Restaurar o arquivo original se necessário
if [ "$MODE" = "frontend" ]; then
  mv server.js.tmp server.js
fi

cd ..

echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}Serviços iniciados:${NC}"
if [ "$MODE" = "full" ]; then
  echo -e "  Backend Python: http://localhost:3000"
fi
echo -e "  Frontend Node.js: http://localhost:4000"
echo -e "${BLUE}===============================================${NC}"
echo -e "${GREEN}Pressione Ctrl+C para encerrar os serviços${NC}"

# Função para encerrar os processos ao sair
function cleanup {
  echo -e "${BLUE}===============================================${NC}"
  echo -e "${GREEN}Encerrando serviços...${NC}"
  if [ "$MODE" = "full" ]; then
    kill $BACKEND_PID
  fi
  kill $FRONTEND_PID
  echo -e "${GREEN}Serviços encerrados!${NC}"
  echo -e "${BLUE}===============================================${NC}"
  exit 0
}

# Capturar Ctrl+C e chamar a função de limpeza
trap cleanup SIGINT

# Manter o script em execução
while true; do
  sleep 1
done 