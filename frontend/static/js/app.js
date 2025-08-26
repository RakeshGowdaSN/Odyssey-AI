/**
 * app.js: DEBUGGING version to trace message handling in the console.
 */

// Connect the server with a WebSocket connection
const sessionId = Math.random().toString(36).substring(2);
const ws_protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
const ws_url = ws_protocol + window.location.host + "/ws/" + sessionId;


let websocket = null;
let is_audio = false;

// Get DOM elements
const messageForm = document.getElementById("messageForm");
const messageInput = document.getElementById("message");
const messagesDiv = document.getElementById("messages");
const connectionStatusDiv = document.getElementById("connectionStatus");

// --- State Tracking ---
let currentAgentMessageId = null;
let currentUserMessageId = null;

// Function to update connection status display
function updateConnectionStatus(status, isConnecting = false, isError = false) {
    connectionStatusDiv.textContent = "Connection status: " + status;
    connectionStatusDiv.classList.remove('connected', 'disconnected', 'connecting', 'error');
    if (isConnecting) { connectionStatusDiv.classList.add('connecting'); }
    else if (isError) { connectionStatusDiv.classList.add('error'); }
    else if (websocket && websocket.readyState === WebSocket.OPEN) { connectionStatusDiv.classList.add('connected'); }
    else { connectionStatusDiv.classList.add('disconnected'); }
}

// WebSocket handlers
function connectWebsocket() {
  updateConnectionStatus("Connecting...", true);
  websocket = new WebSocket(ws_url + "?is_audio=" + is_audio);

  websocket.onopen = function () {
    console.log("WebSocket connection opened.");
    updateConnectionStatus("Connected", false);
    document.getElementById("sendButton").disabled = false;
    if (!messageForm.dataset.submitHandlerAdded) {
        addSubmitHandler();
        messageForm.dataset.submitHandlerAdded = 'true';
    }
  };

  websocket.onmessage = function (event) {
    try {
        const message_from_server = JSON.parse(event.data);
        // console.log("[AGENT TO CLIENT] ", message_from_server);
  
        // When a turn is complete, clear the active message IDs for the next turn.
        if (message_from_server.turn_complete) {
          currentUserMessageId = null;
          currentAgentMessageId = null;
          return;
        }
  
        // --- USER'S SPEECH TRANSCRIPT (RIGHT SIDE) ---
        if (message_from_server.mime_type === "text/input_transcription") {
          let userMessageElement = document.getElementById(currentUserMessageId);
          if (!userMessageElement) {
            currentAgentMessageId = null;
            currentUserMessageId = "user-msg-" + Math.random().toString(36).substring(7);
            userMessageElement = document.createElement("p");
            userMessageElement.id = currentUserMessageId;
            userMessageElement.classList.add("user-message");
            messagesDiv.appendChild(userMessageElement);
          }
          userMessageElement.textContent = message_from_server.data;
          messagesDiv.scrollTo({ top: messagesDiv.scrollHeight, behavior: 'smooth' });
          return; 
        }
  
        // --- AGENT'S MESSAGES (LEFT SIDE) ---
        
        // If the agent sends anything, the user's turn is officially over.
        if (currentUserMessageId) {
            const userMessageElement = document.getElementById(currentUserMessageId);
            if(userMessageElement) userMessageElement.classList.remove("transcription");
            currentUserMessageId = null;
        }
  
        // Handler for AGENT'S audio
        if (message_from_server.mime_type === "audio/pcm" && audioPlayerNode) {
          if (audioPlayerContext && audioPlayerContext.state === 'suspended') {
              audioPlayerContext.resume().catch(e => console.error("Failed to resume AudioContext:", e));
          }
          audioPlayerNode.port.postMessage(base64ToArray(message_from_server.data));
          return;
        }

        // --- ADD THIS NEW BLOCK to handle a list of images ---
        if (message_from_server.mime_type === "image/url_list") {
          // Create a container for the photo gallery
          const galleryContainer = document.createElement("div");
          galleryContainer.classList.add("agent-message", "image-gallery-container");
          
          // Loop through the list of URLs in the message data
          message_from_server.data.forEach(imageUrl => {
              const imageElement = document.createElement("img");
              imageElement.src = imageUrl;
              imageElement.alt = "Generated Place Image";
              imageElement.classList.add("agent-image"); // Use existing style for individual images
              imageElement.onload = () => {
                  messagesDiv.scrollTo({ top: messagesDiv.scrollHeight, behavior: 'smooth' });
              };
              galleryContainer.appendChild(imageElement);
          });
        
          messagesDiv.appendChild(galleryContainer);
          // An image gallery is a final response, so reset the agent's active message ID
          currentAgentMessageId = null; 
          return;
        }
  
        // --- IMAGE HANDLER (This was the missing part) ---
        if (message_from_server.mime_type === "image/url") {
            const imageContainer = document.createElement("p");
            imageContainer.classList.add("agent-message");
            const imageElement = document.createElement("img");
            imageElement.src = message_from_server.data;
            imageElement.alt = "Generated Image";
            imageElement.classList.add("agent-image");
            imageElement.onload = () => {
                messagesDiv.scrollTo({ top: messagesDiv.scrollHeight, behavior: 'smooth' });
            };
            imageContainer.appendChild(imageElement);
            messagesDiv.appendChild(imageContainer);
            // An image is a final response, so reset the agent's active message ID
            currentAgentMessageId = null; 
            return;
        }
  
        // Handler for AGENT'S text (live transcript and final text)
        if (message_from_server.mime_type === 'text/transcription' || message_from_server.mime_type === 'text/plain') {
            let agentMessageElement = document.getElementById(currentAgentMessageId);
  
            if (!agentMessageElement) {
                currentAgentMessageId = "agent-msg-" + Math.random().toString(36).substring(7);
                agentMessageElement = document.createElement("p");
                agentMessageElement.id = currentAgentMessageId;
                agentMessageElement.classList.add("agent-message");
                messagesDiv.appendChild(agentMessageElement);
            }
  
            if (message_from_server.mime_type === 'text/transcription') {
                agentMessageElement.classList.add("transcription");
                agentMessageElement.textContent += message_from_server.data;
            } 
            else if (message_from_server.mime_type === 'text/plain') {
                agentMessageElement.classList.remove("transcription");
                agentMessageElement.textContent = message_from_server.data;
            }
            
            messagesDiv.scrollTo({ top: messagesDiv.scrollHeight, behavior: 'smooth' });
            return;
        }
    } catch (error) {
        console.error("Error processing incoming message:", error);
    }
  };

  websocket.onclose = function (event) {
    console.log("WebSocket connection closed.", event);
    updateConnectionStatus("Disconnected", false, event.code !== 1000);
    document.getElementById("sendButton").disabled = true;
    currentAgentMessageId = null;
    currentUserMessageId = null;
    setTimeout(() => connectWebsocket(), 3000);
  };

  websocket.onerror = function (e) {
    console.error("WebSocket error: ", e);
    updateConnectionStatus("Error", false, true);
  };
}

// --- The rest of the file (addSubmitHandler, sendMessage, audio functions, etc.) is unchanged. ---
// --- You can copy it from the previous complete version I sent if needed. ---
function addSubmitHandler() {
  messageForm.onsubmit = function (e) {
    e.preventDefault();
    const messageText = messageInput.value.trim();
    if (messageText && websocket && websocket.readyState === WebSocket.OPEN) {
      if (currentUserMessageId) {
          const oldTranscript = document.getElementById(currentUserMessageId);
          if (oldTranscript) oldTranscript.remove();
          currentUserMessageId = null;
      }
      const userMessageElement = document.createElement("p");
      userMessageElement.textContent = messageText;
      userMessageElement.classList.add("user-message");
      messagesDiv.appendChild(userMessageElement);
      sendMessage({ mime_type: "text/plain", data: messageText });
      console.log("[CLIENT TO AGENT] " + messageText);
      messageInput.value = "";
      messagesDiv.scrollTo({ top: messagesDiv.scrollHeight, behavior: 'smooth' });
    }
  };
}

function sendMessage(message) {
  if (websocket && websocket.readyState === WebSocket.OPEN) {
    websocket.send(JSON.stringify(message));
  }
}

function base64ToArray(base64) {
  try {
      if (typeof base64 !== 'string' || base64.length === 0) { return new ArrayBuffer(0); }
      const binaryString = window.atob(base64);
      const len = binaryString.length;
      const bytes = new Uint8Array(len);
      for (let i = 0; i < len; i++) { bytes[i] = binaryString.charCodeAt(i); }
      return bytes.buffer;
  } catch (e) { console.error("Error decoding base64:", e); return new ArrayBuffer(0); }
}

let audioPlayerNode, audioPlayerContext, audioRecorderNode, audioRecorderContext, micStream;
import { startAudioPlayerWorklet } from "./audio-player.js";
import { startAudioRecorderWorklet } from "./audio-recorder.js";

async function startAudio() {
  try {
      [audioPlayerNode, audioPlayerContext] = await startAudioPlayerWorklet();
      [audioRecorderNode, audioRecorderContext, micStream] = await startAudioRecorderWorklet(audioRecorderHandler);
      const successMsg = document.createElement("p");
      successMsg.textContent = "Audio setup complete. Ready for voice.";
      successMsg.style.fontStyle = "italic";
      messagesDiv.appendChild(successMsg);
  } catch (error) {
      const errorMsg = document.createElement("p");
      errorMsg.textContent = `Audio setup failed: ${error.message || error}.`;
      errorMsg.style.color = "red";
      messagesDiv.appendChild(errorMsg);
      startAudioButton.disabled = false;
  }
}

const startAudioButton = document.getElementById("startAudioButton");
startAudioButton.addEventListener("click", async () => {
  startAudioButton.disabled = true;
  await startAudio();
  is_audio = true;
  if (websocket && websocket.readyState === WebSocket.OPEN) {
       websocket.close(1000, "Switching to audio mode");
  } else {
      connectWebsocket();
  }
});

function audioRecorderHandler(pcmData) {
  if (websocket && websocket.readyState === WebSocket.OPEN && is_audio) {
      sendMessage({ mime_type: "audio/pcm", data: arrayBufferToBase64(pcmData) });
  }
}

function arrayBufferToBase64(buffer) {
  let binary = "";
  const bytes = new Uint8Array(buffer);
  for (let i = 0; i < bytes.byteLength; i++) { binary += String.fromCharCode(bytes[i]); }
  return window.btoa(binary);
}

updateConnectionStatus("Disconnected");
connectWebsocket();
