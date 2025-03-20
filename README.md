# Speak Notes

Uma aplicação de reconhecimento de fala que usa Dioxus (Rust) para a interface e JavaScript para a captura e transcrição de áudio.

## Visão Geral

Este projeto implementa uma solução de reconhecimento de fala que separa a captura de áudio (feita em JavaScript) da interface do usuário (feita em Dioxus/Rust). A arquitetura consiste em:

1. **Servidor Node.js**: Executa o código JavaScript de reconhecimento de fala em um navegador e expõe uma API REST e WebSocket para comunicação.
2. **Aplicação Dioxus**: Fornece uma interface gráfica elegante e se comunica com o servidor para iniciar/parar o reconhecimento de fala e receber os resultados da transcrição.

Esta abordagem resolve problemas de permissão de áudio que podem ocorrer em aplicações desktop com Dioxus, pois a captura de áudio é feita em um navegador, onde as APIs de áudio são bem suportadas.

## Estrutura do Projeto

```
speak-notes/
├── server.js                # Servidor Node.js com WebSocket e API REST
├── package.json             # Dependências do servidor Node.js
├── public/                  # Arquivos estáticos servidos pelo servidor
│   └── index.html           # Página HTML com o código de reconhecimento de fala
├── src/                     # Código Rust/Dioxus
│   └── main.rs              # Aplicação Dioxus que se comunica com o servidor
└── Cargo.toml               # Configuração do projeto Rust/Dioxus
```

## Pré-requisitos

- Node.js (v14 ou superior)
- npm (v6 ou superior)
- Rust (versão estável mais recente)
- Cargo (gerenciador de pacotes Rust)
- Um navegador moderno que suporte a Web Speech API (Chrome, Edge, Safari)

## Instalação

1. Instale as dependências do servidor Node.js:

   ```
   npm install
   ```

2. Compile a aplicação Dioxus:
   ```
   cargo build --release
   ```

## Como Usar

1. Inicie o servidor Node.js:

   ```
   npm start
   ```

2. Execute a aplicação Dioxus:
   ```
   cargo run --release
   ```

## Como Funciona

1. O servidor Node.js serve uma página HTML que contém o código JavaScript para reconhecimento de fala usando a Web Speech API.
2. A página HTML se conecta ao servidor via WebSocket para enviar os resultados da transcrição.
3. A aplicação Dioxus se comunica com o servidor via HTTP para enviar comandos (iniciar/parar) e via WebSocket para receber os resultados da transcrição em tempo real.
4. A interface Dioxus exibe os resultados da transcrição e permite controlar o processo de reconhecimento de fala.

## Vantagens desta Abordagem

1. **Interface Gráfica Elegante**: Usa Dioxus para criar uma interface de usuário moderna e responsiva.
2. **Contorna Problemas de Permissão**: Evita problemas de permissão de áudio que podem ocorrer em aplicações desktop.
3. **Mantém o JavaScript para Reconhecimento**: Todo o código de captura e transcrição de áudio permanece em JavaScript, conforme solicitado.
4. **Arquitetura Flexível**: Permite que você use o melhor de cada linguagem - JavaScript para APIs web e Rust para desempenho e segurança.

## Personalização

Você pode personalizar esta solução de várias maneiras:

1. **Temas e Estilos**: Modifique o CSS na aplicação Dioxus para personalizar a aparência.
2. **Funcionalidades Adicionais**: Adicione recursos como salvamento automático, exportação para diferentes formatos, etc.
3. **Processamento de Linguagem Natural**: Integre com APIs de NLP para análise de sentimento, extração de entidades, etc.
4. **Hospedagem Remota**: Hospede o servidor em um serviço de nuvem para permitir acesso de qualquer lugar.
