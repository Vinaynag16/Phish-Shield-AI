/* =====================================
   PhishShield Chatbot Final Stable
===================================== */

const CHAT_API = "http://127.0.0.1:8000";

/* ---------------------------------
GLOBAL TOGGLE FUNCTION
--------------------------------- */
function toggleChat() {

    const chatBox = document.getElementById("chat-box");
    const chatInput = document.getElementById("chat-input");

    if (
        chatBox.style.display === "flex" ||
        chatBox.style.display === "block"
    ) {
        chatBox.style.display = "none";
    } else {
        chatBox.style.display = "flex";

        setTimeout(() => {
            chatInput.focus();
        }, 150);
    }
}


window.toggleChat = toggleChat;

/* ---------------------------------
LOAD AFTER PAGE READY
--------------------------------- */
window.onload = function () {

    const chatToggle = document.getElementById("chat-toggle");
    const chatInput = document.getElementById("chat-input");

    /* icon click */
    if (chatToggle) {
        chatToggle.onclick = toggleChat;
    }

    /* enter key */
    if (chatInput) {
        chatInput.addEventListener("keypress", function (e) {
            if (e.key === "Enter") {
                sendChat();
            }
        });
    }
};

/* ---------------------------------
SEND CHAT
--------------------------------- */
async function sendChat() {

    const chatInput = document.getElementById("chat-input");
    const chatMessages = document.getElementById("chat-messages");
    const latestScan = localStorage.getItem("latestScan");
    console.log("Chatbot Scan Context:", latestScan);

    const msg = chatInput.value.trim();

    if (!msg) return;

    addMessage(msg, "user");

    chatInput.value = "";

    addMessage("...", "bot");

    try {
        const latestScan = localStorage.getItem("latestScan");
        const res = await fetch(`${CHAT_API}/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: msg,
                scan_context: latestScan ? JSON.parse(latestScan) : null
            })
        });

        const data = await res.json();

        removeLast();

        addMessage(data.reply, "bot");

    } catch (error) {

        removeLast();

        addMessage("⚠️ Backend unavailable.", "bot");
    }
}

window.sendChat = sendChat;

/* ---------------------------------
CHAT HELPERS
--------------------------------- */
function addMessage(text, type) {

    const chatMessages = document.getElementById("chat-messages");

    const div = document.createElement("div");

    div.className = `chat-message ${type}`;

    div.innerText = text;

    chatMessages.appendChild(div);

    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeLast() {

    const chatMessages = document.getElementById("chat-messages");

    if (chatMessages.lastChild) {
        chatMessages.lastChild.remove();
    }
}

