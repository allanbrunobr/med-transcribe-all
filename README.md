# Med Transcribe All

Uma aplicação para transcrição médica que captura áudio, transcreve e estrutura os dados médicos em tempo real.

## Estrutura do Projeto

O projeto está organizado em duas partes principais:

### Frontend

A interface do usuário que captura áudio, exibe transcrições e interage com o usuário.

- Tecnologia: JavaScript/React
- Localização: `/frontend`
- Funciona independentemente ou em conjunto com o backend
- Utiliza a Web Speech API para captura e transcrição em tempo real

### Backend

Servidor que recebe as transcrições, estrutura os dados médicos e fornece análises.

- Tecnologia: Python com FastAPI
- Localização: `/backend`
- Opcional - o frontend funciona mesmo sem o backend
- Implementa um fluxo de processamento com PocketFlow

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
- Navegador moderno com suporte à Web Speech API (Chrome recomendado)

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
4. Se o backend estiver ativo, as transcrições são enviadas para processamento via WebSocket
5. O backend analisa e estrutura os dados médicos (opcional)
6. Os resultados da análise são exibidos ao usuário (se o backend estiver ativo)

## Funcionalidades

- Captura de áudio e transcrição em tempo real
- Exibição imediata das transcrições no navegador
- Estruturação de dados médicos a partir de transcrições (requer backend)
- Análise preliminar dos dados médicos (requer backend)
- Detecção automática de termos médicos relevantes
- Interface amigável com feedback visual do status da conexão

## Guia de Uso

1. Inicie a aplicação usando um dos métodos descritos acima
2. Abra http://localhost:4000 em seu navegador
3. Clique em "Iniciar Escuta" para começar a capturar áudio
4. Fale normalmente - você verá a transcrição aparecendo em tempo real
5. A transcrição final aparecerá no campo "Transcrição"
6. Se o backend estiver conectado, você verá uma análise estruturada dos dados médicos
7. Clique em "Parar Escuta" para interromper a captura de áudio

## Arquitetura Técnica

### Comunicação Frontend-Backend

- **WebSockets**: Comunicação em tempo real bidirecional
- **REST API**: Endpoints para operações não-tempo-real

### Backend

- **FastAPI**: Framework web assíncrono e de alto desempenho
- **PocketFlow**: Framework para construção de fluxos de processamento LLM
- **Nodes**: Nós de processamento para estruturação e análise dos dados médicos

### Frontend

- **Web Speech API**: API nativa do navegador para reconhecimento de fala
- **WebSockets**: Comunicação em tempo real com o backend
- **Interface Reativa**: Atualiza em tempo real com o progresso da transcrição

## Resolução de Problemas Comuns

### Permissão de Microfone

Se o navegador não solicitar permissão para o microfone ou se a transcrição não funcionar:

- Verifique se seu navegador tem permissão para acessar o microfone
- Certifique-se de estar usando um navegador compatível (Chrome recomendado)
- Verifique se o site está sendo acessado via HTTP(S) e não via arquivo local

### Conexão com o Backend

Se o frontend não conseguir se conectar ao backend:

- Certifique-se de que o servidor backend está rodando (verifique `http://localhost:3000`)
- Verifique se não há firewall ou outras restrições de rede bloqueando a conexão
- Confira os logs na seção "Log de Conexão" na interface para mensagens de erro

### Transcrição Não Funciona

Se a transcrição não estiver funcionando corretamente:

- Verifique se seu navegador suporta a Web Speech API
- Certifique-se de que seu microfone está funcionando e configurado corretamente
- Tente recarregar a página e reiniciar a aplicação

## Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Faça commit das suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Faça push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Licença

Este projeto é licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.
