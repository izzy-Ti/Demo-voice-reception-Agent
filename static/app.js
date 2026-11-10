/**
 * Grand Azure Hotel — Virtual Voice Receptionist Frontend
 * Handles speech recognition (STT), speech synthesis (TTS),
 * chat interactions, visualizer animations, and live hotel system dashboard.
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
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
  const toggleDashboardBtn = document.getElementById("toggle-dashboard-btn");
  const closeDashboardBtn = document.getElementById("close-dashboard-btn");
  const dashboardDrawer = document.getElementById("dashboard-drawer");
  const resetDbBtn = document.getElementById("reset-db-btn");
  const roomsList = document.getElementById("rooms-inventory-list");
  const resList = document.getElementById("reservations-list");
  const reqList = document.getElementById("requests-list");
  const resCountBadge = document.getElementById("res-count-badge");
  const reqCountBadge = document.getElementById("req-count-badge");
  const engineBadge = document.getElementById("engine-badge");

  // State
  let sessionId = "guest-" + Math.floor(Math.random() * 10000);
  let isVoiceOutputEnabled = true;
  let isListening = false;
  let recognition = null;
  let synth = window.speechSynthesis;
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
      livePreview.innerHTML = `<em>Listening to you... speak now</em>`;
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
        livePreview.innerHTML = `<span class="hint-text">Microphone access was denied. You can still type below or use suggestion chips.</span>`;
      } else {
        livePreview.innerHTML = `<span class="hint-text">Could not hear clearly. Try clicking the mic again or typing.</span>`;
      }
    };

    recognition.onend = () => {
      stopListening();
    };
  } else {
    micLabel.textContent = "Mic Not Supported";
    micBtn.title = "Web Speech API is not supported in this browser. Please use the text input below.";
    livePreview.innerHTML = `<span class="hint-text">Speech recognition is not supported in this browser. Please type or click the suggestion chips.</span>`;
  }

  // Toggle Microphone
  function toggleListening() {
    if (!recognition) {
      alert("Speech recognition is not supported in this browser. Please use Chrome, Edge, or type your message.");
      return;
    }

    if (isListening) {
      recognition.stop();
      stopListening();
    } else {
      // Cancel any ongoing speech synthesis first
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

  // Set Agent Visual State
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
      statusLabel.textContent = "Alex is processing...";
    } else if (state === "speaking") {
      heroSection.classList.add("state-speaking");
      statusPill.classList.add("speaking");
      statusLabel.textContent = "Alex is speaking...";
    } else {
      statusLabel.textContent = "Ready to assist you";
    }
  }

  // Speak response out loud using SpeechSynthesis
  function speakResponse(text) {
    if (!isVoiceOutputEnabled || !synth) {
      setAgentState("idle");
      return;
    }

    // Stop previous utterance
    synth.cancel();

    // Clean text: strip markdown characters or urls for smooth reading
    const cleanText = text
      .replace(/[*_#`~]/g, "")
      .replace(/https?:\/\/\S+/g, "")
      .trim();

    currentUtterance = new SpeechSynthesisUtterance(cleanText);
    currentUtterance.rate = 1.0;
    currentUtterance.pitch = 1.0;
    currentUtterance.lang = "en-US";

    // Select pleasant voice if available
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

  // Send message to backend API
  async function handleUserMessage(message) {
    if (!message || !message.trim()) return;
    const userText = message.trim();

    // Append user message bubble to chat
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

      // Append Alex response bubble
      appendBubble("agent", reply, "Alex (Reception)", data.actions);

      // Speak response out loud
      speakResponse(reply);

      // Refresh hotel monitor status
      fetchHotelStatus();
    } catch (error) {
      console.error("API error:", error);
      setAgentState("idle");
      appendBubble(
        "agent",
        "I apologize, but I encountered a momentary connection issue. Please allow me to assist you again in a moment.",
        "Alex (Reception)"
      );
    }
  }

  // Append Chat Bubble
  function appendBubble(role, text, senderName, actions = []) {
    const bubble = document.createElement("div");
    bubble.className = `message-bubble ${role === "user" ? "user-bubble" : "agent-bubble"}`;

    const now = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

    let actionsHtml = "";
    if (actions && actions.length > 0) {
      actionsHtml = `<div class="bubble-actions">`;
      actions.forEach((a) => {
        let label = a.tool || "Action";
        if (label === "check_room_availability") label = "Checked Availability";
        else if (label === "book_room") label = "Room Booked";
        else if (label === "lookup_reservation") label = "Reservation Looked Up";
        else if (label === "request_hotel_service") label = "Service Dispatched";
        else if (label === "get_hotel_amenity_info") label = "Amenities Info";
        actionsHtml += `<span class="action-tag">✓ ${label}</span>`;
      });
      actionsHtml += `</div>`;
    }

    bubble.innerHTML = `
      <div class="bubble-sender">
        ${role === "agent" ? '<span class="sender-avatar">🛎️</span> ' : ""}${senderName}
      </div>
      <div class="bubble-content">${escapeHtml(text)}</div>
      ${actionsHtml}
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

  // Fetch Hotel System Status
  async function fetchHotelStatus() {
    try {
      const res = await fetch("/api/hotel/status");
      if (!res.ok) return;
      const data = await res.json();

      // Engine badge
      if (data.active_gemini) {
        engineBadge.textContent = `Agent: Gemini (${data.model})`;
        engineBadge.style.color = "var(--accent-emerald)";
      } else {
        engineBadge.textContent = `Agent: Built-in Hotel Reception Engine`;
        engineBadge.style.color = "var(--accent-gold)";
      }

      // Rooms inventory
      roomsList.innerHTML = "";
      Object.entries(data.rooms || {}).forEach(([k, r]) => {
        const item = document.createElement("div");
        item.className = "room-card";
        const isLow = r.available <= 2;
        item.innerHTML = `
          <div>
            <div class="room-card-name">${r.name}</div>
            <div class="room-card-price">$${r.price_per_night} / night • Max ${r.capacity} guests</div>
          </div>
          <div class="room-card-avail ${isLow ? "low" : ""}">${r.available} left</div>
        `;
        roomsList.appendChild(item);
      });

      // Reservations
      resList.innerHTML = "";
      const reservations = data.reservations || [];
      resCountBadge.textContent = reservations.length;
      reservations.slice().reverse().forEach((r) => {
        const item = document.createElement("div");
        item.className = "res-card";
        item.innerHTML = `
          <div class="res-card-top">
            <span>${r.guest_name}</span>
            <span>${r.confirmation_code}</span>
          </div>
          <div class="res-card-sub">
            Room #${r.room_number || "TBD"} (${r.room_type})<br>
            ${r.check_in} → ${r.check_out} • <strong>${r.status}</strong>
          </div>
        `;
        resList.appendChild(item);
      });

      // Service Requests
      reqList.innerHTML = "";
      const requests = data.service_requests || [];
      reqCountBadge.textContent = requests.length;
      requests.slice().reverse().forEach((q) => {
        const item = document.createElement("div");
        item.className = "req-card";
        item.innerHTML = `
          <div class="req-card-top">
            <span>Room ${q.room_number}: ${q.service_type}</span>
            <span>${q.id}</span>
          </div>
          <div class="req-card-sub">
            “${q.details}”<br>
            <span style="color:var(--accent-gold-light)">${q.status}</span> • ${q.timestamp}
          </div>
        `;
        reqList.appendChild(item);
      });
    } catch (e) {
      console.warn("Failed to fetch hotel monitor state:", e);
    }
  }

  // Reset Hotel Dummy Data
  async function resetHotelData() {
    if (!confirm("Reset hotel bookings and room availability to default dummy data?")) return;
    try {
      await fetch("/api/hotel/reset", { method: "POST" });
      fetchHotelStatus();
      appendBubble(
        "agent",
        "Hotel dummy database has been reset to its default state.",
        "Alex (Reception)"
      );
    } catch (e) {
      alert("Failed to reset database: " + e.message);
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

  // Suggestion chips
  document.querySelectorAll(".chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const prompt = chip.getAttribute("data-text");
      if (prompt) {
        handleUserMessage(prompt);
      }
    });
  });

  // Clear chat
  clearChatBtn.addEventListener("click", () => {
    chatMessages.innerHTML = "";
    sessionId = "guest-" + Math.floor(Math.random() * 10000);
    appendBubble(
      "agent",
      "Welcome to Grand Azure Hotel & Suites! My name is Alex, your virtual front desk receptionist. How may I assist you today?",
      "Alex (Reception)"
    );
  });

  // Voice output toggle
  toggleVoiceBtn.addEventListener("click", () => {
    isVoiceOutputEnabled = !isVoiceOutputEnabled;
    if (!isVoiceOutputEnabled && synth && synth.speaking) {
      synth.cancel();
      setAgentState("idle");
    }
    voiceIcon.textContent = isVoiceOutputEnabled ? "🔊" : "🔇";
    toggleVoiceBtn.title = isVoiceOutputEnabled
      ? "Voice Audio Output: Enabled (Click to Mute)"
      : "Voice Audio Output: Muted (Click to Enable)";
  });

  // Dashboard Drawer Toggle
  toggleDashboardBtn.addEventListener("click", () => {
    dashboardDrawer.classList.toggle("open");
  });

  closeDashboardBtn.addEventListener("click", () => {
    dashboardDrawer.classList.remove("open");
  });

  resetDbBtn.addEventListener("click", resetHotelData);

  // Initial load
  fetchHotelStatus();
});
