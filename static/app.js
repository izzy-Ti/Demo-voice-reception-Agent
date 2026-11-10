/**
 * Grand Azure Hotel — AI Voice Receptionist Client
 * Connects directly to backend Gemini API with Speech-to-Text & Text-to-Speech
 */

document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const heroSection = document.querySelector(".receptionist-hero");
  const statusLabel = document.getElementById("status-label");
  const statusPill = document.getElementById("agent-status-pill");
  const micBtn = document.getElementById("mic-btn");
  const micLabel = document.getElementById("mic-label");
  const livePreview = document.getElementById("live-speech-preview");
  const chatMessages = document.getElementById("chat-messages");
  const chatForm = document.getElementById("chat-form");
  const textInput = document.getElementById("text-input");
  const clearChatBtn = document.getElementById("clear-chat-btn");
  const toggleVoiceBtn = document.getElementById("toggle-voice-btn");
  const voiceIcon = document.getElementById("voice-icon");
  const apiStatusBadge = document.getElementById("api-status-badge");

  // State
  let sessionId = "guest-" + Math.floor(Math.random() * 10000);
  let isVoiceOutputEnabled = true;
  let isListening = false;
  let recognition = null;
  const synth = window.speechSynthesis;
  let currentUtterance = null;

  // Initialize Speech Recognition
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onstart = () => {
      isListening = true;
      setAgentState("listening");
      micBtn.classList.add("active");
      micLabel.textContent = "Listening...";
      livePreview.innerHTML = `<em>Listening to your voice...</em>`;
    };

    recognition.onresult = (event) => {
      let interim = "";
      let finalTranscript = "";

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        } else {
          interim += event.results[i][0].transcript;
        }
      }

      if (interim) {
        livePreview.innerHTML = `“${interim}”`;
      }

      if (finalTranscript) {
        livePreview.innerHTML = `“${finalTranscript}”`;
        handleUserMessage(finalTranscript);
      }
    };

    recognition.onerror = (event) => {
      console.warn("Speech recognition notice:", event.error);
      stopListening();
      if (event.error === "not-allowed") {
        livePreview.innerHTML = `<span class="hint-text">Microphone permission denied. You can type below or click suggested chips.</span>`;
      } else {
        livePreview.innerHTML = `<span class="hint-text">Click the microphone to speak, or select a suggested topic below</span>`;
      }
    };

    recognition.onend = () => {
      stopListening();
    };
  } else {
    micLabel.textContent = "Mic Not Supported";
    micBtn.title = "Web Speech API is not supported in this browser. Please use Chrome/Edge or type below.";
    livePreview.innerHTML = `<span class="hint-text">Voice recognition not supported in this browser. Type below or use the suggestion chips.</span>`;
  }

  function toggleListening() {
    if (!recognition) {
      alert("Speech recognition is not supported in this browser. Please use Google Chrome or Microsoft Edge.");
      return;
    }

    if (isListening) {
      recognition.stop();
      stopListening();
    } else {
      if (synth && synth.speaking) {
        synth.cancel();
      }
      try {
        recognition.start();
      } catch (err) {
        console.error("Error starting speech recognition:", err);
      }
    }
  }

  function stopListening() {
    isListening = false;
    micBtn.classList.remove("active");
    micLabel.textContent = "Press & Speak";
    if (heroSection.classList.contains("state-listening")) {
      setAgentState("idle");
    }
  }

  function setAgentState(state) {
    heroSection.classList.remove("state-listening", "state-thinking", "state-speaking");
    statusPill.classList.remove("listening", "thinking", "speaking");

    if (state === "listening") {
      heroSection.classList.add("state-listening");
      statusPill.classList.add("listening");
      statusLabel.textContent = "Listening to you...";
    } else if (state === "thinking") {
      heroSection.classList.add("state-thinking");
      statusPill.classList.add("thinking");
      statusLabel.textContent = "Alex is thinking...";
    } else if (state === "speaking") {
      heroSection.classList.add("state-speaking");
      statusPill.classList.add("speaking");
      statusLabel.textContent = "Alex is speaking...";
    } else {
      statusLabel.textContent = "Ready to assist you";
    }
  }

  function speakResponse(text) {
    if (!isVoiceOutputEnabled || !synth) {
      setAgentState("idle");
      return;
    }

    synth.cancel();

    // Clean text for speech
    const cleanText = text
      .replace(/[*_#`~]/g, "")
      .replace(/https?:\/\/\S+/g, "")
      .trim();

    currentUtterance = new SpeechSynthesisUtterance(cleanText);
    currentUtterance.rate = 1.0;
    currentUtterance.pitch = 1.0;
    currentUtterance.lang = "en-US";

    // Select pleasant natural voice if available
    const voices = synth.getVoices();
    const preferredVoice = voices.find(
      (v) =>
        v.lang.startsWith("en") &&
        (v.name.includes("Natural") ||
          v.name.includes("Google") ||
          v.name.includes("Samantha") ||
          v.name.includes("Daniel") ||
          v.name.includes("Alex"))
    );
    if (preferredVoice) {
      currentUtterance.voice = preferredVoice;
    }

    currentUtterance.onstart = () => {
      setAgentState("speaking");
    };

    currentUtterance.onend = () => {
      setAgentState("idle");
    };

    currentUtterance.onerror = (e) => {
      console.warn("Speech synthesis notice:", e);
      setAgentState("idle");
    };

    synth.speak(currentUtterance);
  }

  async function handleUserMessage(message) {
    if (!message || !message.trim()) return;
    const userText = message.trim();

    appendBubble("user", userText, "You");
    setAgentState("thinking");

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userText, session_id: sessionId }),
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const data = await response.json();
      const reply = data.reply || "I am at your service. How else may I assist you?";

      appendBubble("agent", reply, "Alex (Reception)");
      speakResponse(reply);
    } catch (error) {
      console.error("API error:", error);
      setAgentState("idle");
      appendBubble(
        "agent",
        "I apologize, but I encountered an error communicating with the server. Please check your connection or GEMINI_API_KEY in .env.",
        "Alex (Reception)"
      );
    }
  }

  function appendBubble(role, text, senderName) {
    const bubble = document.createElement("div");
    bubble.className = `message-bubble ${role === "user" ? "user-bubble" : "agent-bubble"}`;

    const now = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

    bubble.innerHTML = `
      <div class="bubble-sender">
        ${role === "agent" ? '<span class="sender-avatar">🛎️</span> ' : ""}${senderName}
      </div>
      <div class="bubble-content">${escapeHtml(text)}</div>
      <div class="bubble-meta">${now}</div>
    `;

    chatMessages.appendChild(bubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function escapeHtml(text) {
    const div = document.createElement("div");
    div.innerText = text;
    return div.innerHTML;
  }

  // Check backend API & Key status
  async function checkApiStatus() {
    try {
      const res = await fetch("/api/status");
      if (!res.ok) return;
      const data = await res.json();
      if (data.has_api_key) {
        apiStatusBadge.textContent = `🟢 Gemini Active (${data.model})`;
        apiStatusBadge.classList.add("active");
        apiStatusBadge.title = "Connected to Gemini API";
      } else {
        apiStatusBadge.textContent = "⚠️ Set GEMINI_API_KEY in .env";
        apiStatusBadge.classList.remove("active");
        apiStatusBadge.title = "GEMINI_API_KEY is missing. Add it to your .env file.";
      }
    } catch (e) {
      apiStatusBadge.textContent = "🔴 Server Offline";
    }
  }

  // Event Listeners
  micBtn.addEventListener("click", toggleListening);

  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const val = textInput.value;
    if (val.trim()) {
      handleUserMessage(val);
      textInput.value = "";
    }
  });

  document.querySelectorAll(".chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const prompt = chip.getAttribute("data-text");
      if (prompt) {
        handleUserMessage(prompt);
      }
    });
  });

  clearChatBtn.addEventListener("click", () => {
    chatMessages.innerHTML = "";
    sessionId = "guest-" + Math.floor(Math.random() * 10000);
    appendBubble(
      "agent",
      "Welcome to Grand Azure Hotel & Suites! My name is Alex, your virtual front desk receptionist. How may I assist you today?",
      "Alex (Reception)"
    );
  });

  toggleVoiceBtn.addEventListener("click", () => {
    isVoiceOutputEnabled = !isVoiceOutputEnabled;
    if (!isVoiceOutputEnabled && synth && synth.speaking) {
      synth.cancel();
      setAgentState("idle");
    }
    voiceIcon.textContent = isVoiceOutputEnabled ? "🔊" : "🔇";
    toggleVoiceBtn.title = isVoiceOutputEnabled
      ? "Voice Audio Output: Enabled"
      : "Voice Audio Output: Muted";
  });

  // Initial status check
  checkApiStatus();
});
