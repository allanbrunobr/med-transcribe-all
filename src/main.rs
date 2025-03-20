use dioxus::prelude::*;
use dioxus_desktop::{Config, WindowBuilder};
use futures_util::StreamExt;
use reqwest::Client;
use serde::{Deserialize, Serialize};
use tokio_tungstenite::{connect_async, tungstenite::protocol::Message};
use url::Url;

// Server configuration
const SERVER_URL: &str = "http://localhost:3000";
const WS_URL: &str = "ws://localhost:3000";

// Transcript data structure
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
struct Transcript {
    #[serde(default)]
    preview: String,
    #[serde(default)]
    note: String,
    listening: bool,
    #[serde(rename = "noMatch")]
    no_match: bool,
    #[serde(default)]
    command: Option<String>,
}

// State for the application
#[derive(Default)]
struct AppState {
    transcript: Transcript,
    speech_err_message: String,
    is_listening: bool,
    connection_status: String,
}

// Main component
fn app(cx: Scope) -> Element {
    let state = use_ref(cx, || AppState {
        transcript: Transcript {
            preview: String::new(),
            note: String::new(),
            listening: false,
            no_match: false,
            command: None,
        },
        speech_err_message: String::new(),
        is_listening: false,
        connection_status: "Connecting to speech service...".to_string(),
    });
    
    // Setup WebSocket connection
    use_effect(cx, (), |_| {
        let state_clone = state.clone();
        
        async move {
            // Check if server is running
            match check_server_status().await {
                Ok(status) => {
                    state_clone.write().connection_status = format!("Connected to speech service: {}", status);
                    
                    // Connect to WebSocket
                    match connect_to_websocket().await {
                        Ok(mut read) => {
                            state_clone.write().connection_status = "WebSocket connected".to_string();
                            
                            // Process WebSocket messages in this task
                            while let Some(msg) = read.next().await {
                                match msg {
                                    Ok(Message::Text(text)) => {
                                        match serde_json::from_str::<Transcript>(&text) {
                                            Ok(new_transcript) => {
                                                let mut app_state = state_clone.write();
                                                
                                                // Handle command if present
                                                if let Some(cmd) = &new_transcript.command {
                                                    match cmd.as_str() {
                                                        "start" => {
                                                            app_state.is_listening = true;
                                                            println!("Started listening");
                                                        },
                                                        "stop" => {
                                                            app_state.is_listening = false;
                                                            println!("Stopped listening");
                                                        },
                                                        _ => {}
                                                    }
                                                }
                                                
                                                app_state.transcript = new_transcript.clone();
                                                app_state.is_listening = new_transcript.listening;
                                            },
                                            Err(e) => {
                                                println!("Error parsing transcript: {}", e);
                                            }
                                        }
                                    },
                                    Ok(Message::Close(_)) => {
                                        println!("WebSocket closed");
                                        break;
                                    },
                                    Err(e) => {
                                        println!("Error receiving message: {}", e);
                                        break;
                                    },
                                    _ => {}
                                }
                            }
                        },
                        Err(e) => {
                            state_clone.write().connection_status = format!("WebSocket error: {}", e);
                        }
                    }
                },
                Err(e) => {
                    state_clone.write().connection_status = format!("Error connecting to server: {}. Make sure the Node.js server is running with 'npm start'", e);
                }
            }
        }
    });
    
    // Start listening function
    let start_listening = {
        let state = state.clone();
        move |_| {
            state.write().is_listening = true;
            
            // Call the server to start listening
            cx.spawn({
                let state = state.clone();
                async move {
                    match start_recognition().await {
                        Ok(_) => {
                            println!("Started listening");
                        },
                        Err(e) => {
                            state.write().speech_err_message = format!("Error starting recognition: {}", e);
                        }
                    }
                }
            });
        }
    };
    
    // Stop listening function
    let stop_listening = {
        let state = state.clone();
        move |_| {
            state.write().is_listening = false;
            
            // Call the server to stop listening
            cx.spawn({
                let state = state.clone();
                async move {
                    match stop_recognition().await {
                        Ok(_) => {
                            println!("Stopped listening");
                        },
                        Err(e) => {
                            state.write().speech_err_message = format!("Error stopping recognition: {}", e);
                        }
                    }
                }
            });
        }
    };
    
    // Render the UI
    cx.render(rsx! {
        div {
            style: "width: 100%; height: 100vh; display: flex; flex-direction: column; background-color: #f8f9fa;",
            div {
                style: "background-color: #ffffff; color: #333; padding: 10px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e0e0e0; box-shadow: 0 2px 4px rgba(0,0,0,0.05);",
                h1 { 
                    style: "color: #4a86e8; font-weight: 500; margin: 0;",
                    "Speak Notes" 
                }
                div {
                    style: "display: flex; gap: 10px;",
                    select {
                        style: "padding: 8px; border-radius: 4px; border: 1px solid #ddd; background-color: #fff;",
                        option { value: "en-US", "English (US)" }
                        option { value: "pt-BR", "Português (Brasil)" }
                        option { value: "es-ES", "Español" }
                        option { value: "fr-FR", "Français" }
                        option { value: "de-DE", "Deutsch" }
                    }
                    button {
                        style: "background-color: #4a86e8; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-weight: 500;",
                        onclick: start_listening,
                        disabled: state.read().is_listening,
                        "Start Listening"
                    }
                    button {
                        style: "background-color: #f44336; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-weight: 500;",
                        onclick: stop_listening,
                        disabled: !state.read().is_listening,
                        "Stop Listening"
                    }
                }
            }
            
            div {
                style: "padding: 10px; margin: 10px; border-radius: 4px; background-color: #f0f0f0;",
                p {
                    "Connection Status: {state.read().connection_status}"
                }
            }
            
            div {
                style: "flex-grow: 1; padding: 20px; display: flex; flex-direction: column; gap: 20px;",
                
                // Preview section
                div {
                    h3 { "Live Preview:" }
                    div {
                        style: "padding: 15px; background-color: #f8f9fa; border-radius: 4px; min-height: 40px; border: 1px solid #e0e0e0;",
                        "{state.read().transcript.preview}"
                    }
                }
                
                // Transcript section
                div {
                    h3 { "Transcript:" }
                    div {
                        style: "padding: 15px; background-color: #f8f9fa; border-radius: 4px; min-height: 100px; border: 1px solid #e0e0e0; white-space: pre-wrap;",
                        "{state.read().transcript.note}"
                    }
                }
                
                // Error message
                {
                    if !state.read().speech_err_message.is_empty() {
                        rsx! {
                            div {
                                style: "padding: 10px; background-color: rgba(220, 53, 69, 0.1); border: 1px solid rgba(220, 53, 69, 0.2); color: #dc3545; border-radius: 4px;",
                                "{state.read().speech_err_message}"
                            }
                        }
                    } else {
                        rsx! { div {} }
                    }
                }
            }
            
            div {
                style: "padding: 10px; text-align: center; color: #666; font-size: 12px; border-top: 1px solid #e0e0e0;",
                "Speak Notes - Powered by Dioxus and Web Speech API"
            }
        }
    })
}

// Connect to WebSocket and return the read half of the stream
async fn connect_to_websocket() -> Result<impl StreamExt<Item = Result<Message, tokio_tungstenite::tungstenite::Error>>, Box<dyn std::error::Error>> {
    let url = Url::parse(WS_URL)?;
    let (ws_stream, _) = connect_async(url).await?;
    println!("WebSocket connected");
    
    let (_, read) = ws_stream.split();
    
    Ok(read)
}

// Check if the server is running
async fn check_server_status() -> Result<String, Box<dyn std::error::Error>> {
    let client = Client::new();
    let response = client.get(&format!("{}/api/status", SERVER_URL)).send().await?;
    
    if response.status().is_success() {
        let status: serde_json::Value = response.json().await?;
        Ok(status.to_string())
    } else {
        Err(format!("Server returned error: {}", response.status()).into())
    }
}

// Start speech recognition
async fn start_recognition() -> Result<(), Box<dyn std::error::Error>> {
    let client = Client::new();
    let response = client.post(&format!("{}/api/start", SERVER_URL)).send().await?;
    
    if response.status().is_success() {
        Ok(())
    } else {
        Err(format!("Server returned error: {}", response.status()).into())
    }
}

// Stop speech recognition
async fn stop_recognition() -> Result<(), Box<dyn std::error::Error>> {
    let client = Client::new();
    let response = client.post(&format!("{}/api/stop", SERVER_URL)).send().await?;
    
    if response.status().is_success() {
        Ok(())
    } else {
        Err(format!("Server returned error: {}", response.status()).into())
    }
}

fn main() {
    // Configure the desktop application
    let config = Config::default()
        .with_window(
            WindowBuilder::new()
                .with_title("Speak Notes")
                .with_inner_size(dioxus_desktop::LogicalSize::new(1000, 800))
        );
    
    // Launch the Dioxus application
    dioxus_desktop::launch_with_props(app, (), config);
}

