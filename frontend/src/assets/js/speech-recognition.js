// Adapted from React hooks to vanilla JavaScript
class SpeechRecognitionManager {
  constructor() {
    this.transcript = {
      preview: "",
      note: "",
      listening: false,
      noMatch: false,
    };
    this.speechErrMessage = "";
    this.listeners = {
      onTranscriptChange: () => {},
      onSpeechErrMessage: () => {},
      onListeningChange: () => {},
    };

    // Load audio files
    this.audioStart = new Audio("./assets/sounds/audio-start.mp3");
    this.audioEnd = new Audio("./assets/sounds/audio-end.mp3");

    // Speech recognition setup
    this.Recognition =
      new window.webkitSpeechRecognition() || new window.SpeechRecognition();
    this.Recognition.continuos = true;
    this.Recognition.interimResults = true;

    this.speechRecVars = {
      clicked: false,
      stopped: false,
    };

    // Set up event handlers
    this.setupRecognitionEvents();
  }

  setupRecognitionEvents() {
    this.Recognition.onaudiostart = () => {
      this.updateTranscript({ listening: true });
    };

    this.Recognition.onaudioend = () => {
      this.updateTranscript({ listening: false });
    };

    this.Recognition.onnomatch = () => {
      this.updateTranscript({ noMatch: true });
    };

    this.Recognition.onresult = (evt) => {
      this.updateTranscript({ noMatch: false });
      const speechRecResult = evt.results;
      let idx = evt.resultIndex;
      const currentSpeechResult = speechRecResult[idx];
      const currentSpeechTranscript = speechRecResult[idx][0].transcript;

      this.updateTranscript({ preview: currentSpeechTranscript });

      // if recognised speech sounds like a complete sentence, then add it to the note.
      if (currentSpeechResult.isFinal) {
        this.updateTranscript({
          note: this.transcript.note + " " + currentSpeechTranscript,
        });
      }
    };

    this.Recognition.onend = () => {
      if (this.speechRecVars.stopped) return;
      // to make the Web Speech API listen continuously
      this.Recognition.start();
      this.speechRecVars.clicked = true;
      this.updateTranscript({ listening: true });
    };

    this.Recognition.onerror = (evt) => {
      if (!this.speechRecVars.stopped) {
        this.setSpeechErrMessage(evt.error);
      }
    };
  }

  updateTranscript(stateValue) {
    this.transcript = { ...this.transcript, ...stateValue };
    this.listeners.onTranscriptChange(this.transcript);

    if ("listening" in stateValue) {
      this.listeners.onListeningChange(stateValue.listening);
    }
  }

  setSpeechErrMessage(message) {
    this.speechErrMessage = message;
    this.listeners.onSpeechErrMessage(message);
  }

  startSpeechRec() {
    // calling Recognition.start() more than once throws an error
    if (!this.speechRecVars.clicked) {
      this.Recognition.start();
      this.audioEnd.pause();
      this.audioEnd.currentTime = 0;
      this.audioStart.play();
      this.updateTranscript({ listening: true });
      this.speechRecVars.clicked = true;
      this.speechRecVars.stopped = false;
    }
  }

  stopSpeechRec(_, isBlurredBySameElement) {
    if (this.speechRecVars.clicked) {
      this.audioStart.pause();
      this.audioStart.currentTime = 0;
      if (!isBlurredBySameElement) this.audioEnd.play();
      this.Recognition.stop();
      this.updateTranscript({ listening: false });
      this.setSpeechErrMessage("");
      this.speechRecVars.clicked = false;
      this.speechRecVars.stopped = true;
    }
  }

  setTranscript(newTranscript) {
    this.transcript = { ...this.transcript, ...newTranscript };
    this.listeners.onTranscriptChange(this.transcript);
  }

  // Register event listeners
  on(event, callback) {
    if (event === "transcriptChange") {
      this.listeners.onTranscriptChange = callback;
    } else if (event === "speechErrMessage") {
      this.listeners.onSpeechErrMessage = callback;
    } else if (event === "listeningChange") {
      this.listeners.onListeningChange = callback;
    }
  }

  // Check if browser supports speech recognition
  static isSupported() {
    return "webkitSpeechRecognition" in window || "SpeechRecognition" in window;
  }
}

// Create and export a singleton instance
const speechRecognition = new SpeechRecognitionManager();

// Export functions for Rust to call via WebView
window.SpeakNotes = {
  isSupported: SpeechRecognitionManager.isSupported,
  startListening: () => speechRecognition.startSpeechRec(),
  stopListening: () => speechRecognition.stopSpeechRec(),
  getTranscript: () => speechRecognition.transcript,
  setTranscript: (newTranscript) =>
    speechRecognition.setTranscript(newTranscript),

  // Register callbacks from Rust
  onTranscriptChange: (callback) => {
    speechRecognition.on("transcriptChange", (transcript) => {
      // Convert to string to pass to Rust
      callback(JSON.stringify(transcript));
    });
  },
  onSpeechErrMessage: (callback) => {
    speechRecognition.on("speechErrMessage", callback);
  },
  onListeningChange: (callback) => {
    speechRecognition.on("listeningChange", callback);
  },
};

// Utility functions for file operations
window.SpeakNotes.utils = {
  downloadTranscript: (text) => {
    const blob = new Blob([text.split(".").join("\n")], {
      type: "text/plain",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "transcript.txt";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  },

  copyToClipboard: async (text) => {
    await navigator.clipboard.writeText(text);
    return true;
  },

  shareTranscript: async (text) => {
    const blob = new Blob([text.split(".").join("\n")], {
      type: "text/plain",
    });
    const file = new File([blob], "transcript.txt", {
      type: "text/plain",
    });

    const shareData = {
      title: "Speak-Notes",
      url: "https://speak-notes.pages.dev",
      files: [file],
    };

    try {
      await navigator.share(shareData);
      return true;
    } catch (e) {
      console.error("Share failed:", e);
      return false;
    }
  },
};
