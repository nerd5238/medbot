// =============================
// Select Elements
// =============================
const botBox = document.getElementById("chatbot-box");
const toggleBtn = document.getElementById("chatbot-open");
const closeBtn = document.getElementById("chatbot-close");

const msgBox = document.getElementById("chatbot-messages");
const msgInput = document.getElementById("chatbot-input");
const sendBtn = document.getElementById("chatbot-send");

const darkToggle = document.getElementById("chatbot-dark-toggle");

// =============================
// Sounds
// =============================
const sendSound = new Audio("/static/sounds/send.mp3");
const receiveSound = new Audio("/static/sounds/receive.wav");

// =============================
// Session flags (using variables instead of sessionStorage)
// =============================
let greeted = false;
let isDarkMode = false;

// =============================
// Toggle Popup (Enhanced)
// =============================
toggleBtn.addEventListener("click", () => {
    const isOpen = botBox.classList.contains("active");
    
    if (isOpen) {
        // Close the chatbot
        botBox.classList.remove("active");
        setTimeout(() => {
            botBox.classList.add("hidden");
        }, 300);
        toggleBtn.innerHTML = "💬";
    } else {
        // Open the chatbot
        botBox.classList.remove("hidden");
        // Small delay to trigger animation
        setTimeout(() => {
            botBox.classList.add("active");
        }, 10);
        toggleBtn.innerHTML = "✕";

        // 👋 Greeting only once per session
        if (!greeted) {
            greetBot();
            greeted = true;
        }
        
        // Focus input when opened
        msgInput.focus();
    }
});

closeBtn.addEventListener("click", () => {
    botBox.classList.remove("active");
    setTimeout(() => {
        botBox.classList.add("hidden");
    }, 300);
    toggleBtn.innerHTML = "💬";
});

// =============================
// Dark Mode Toggle (Enhanced)
// =============================
if (darkToggle) {
    darkToggle.addEventListener("click", () => {
        botBox.classList.toggle("dark");
        isDarkMode = !isDarkMode;

        // Change icon
        darkToggle.innerHTML = isDarkMode ? "☀️" : "🌙";
        
        // Add smooth transition effect
        darkToggle.style.transform = "rotate(360deg)";
        setTimeout(() => {
            darkToggle.style.transform = "rotate(0deg)";
        }, 300);
    });
}

// =============================
// Add message bubbles (Enhanced)
// =============================
function addMessage(sender, text) {
    const div = document.createElement("div");
    div.className = `msg ${sender}`;
    div.innerText = text;
    
    // Add timestamp (optional)
    const now = new Date();
    const time = now.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    div.setAttribute('data-time', time);
    
    msgBox.appendChild(div);

    // Smooth scroll to bottom
    msgBox.scrollTo({
        top: msgBox.scrollHeight,
        behavior: 'smooth'
    });

    // Play sound
    if (sender === "user") {
        sendSound.play().catch(() => {});
    } else {
        receiveSound.play().catch(() => {});
    }
}

// =============================
// Typing Indicator (Enhanced)
// =============================
function showTyping() {
    const typing = document.createElement("div");
    typing.className = "msg bot typing";
    typing.id = "typing-indicator";
    
    // Create animated dots
    typing.innerHTML = `
        MedBot is typing
        <span class="typing-dots">
            <span></span>
            <span></span>
            <span></span>
        </span>
    `;
    
    msgBox.appendChild(typing);
    msgBox.scrollTo({
        top: msgBox.scrollHeight,
        behavior: 'smooth'
    });
}

function removeTyping() {
    const t = document.getElementById("typing-indicator");
    if (t) {
        t.style.animation = "messageSlideIn 0.2s reverse";
        setTimeout(() => t.remove(), 200);
    }
}

// =============================
// Greeting from backend (Enhanced)
// =============================
async function greetBot() {
    // Show typing indicator
    showTyping();
    
    try {
        const res = await fetch("/chatbot/greet", {
            method: "POST",
            headers: { "Content-Type": "application/json" }
        });

        const data = await res.json();
        removeTyping();
        
        if (data.reply) {
            addMessage("bot", data.reply);
        }
    } catch {
        removeTyping();
        addMessage("bot", "👋 Hey there! I'm MedBot 🤖\n\nHow can I assist you with your medical queries today?");
    }
    
    // Optional: Show quick replies after greeting
    showQuickReplies();
}

// =============================
// Quick Replies (Optional Feature)
// =============================
function showQuickReplies() {
    const quickRepliesContainer = document.getElementById("quick-replies");
    if (!quickRepliesContainer) return;
    
    const replies = [
        "📋 Check appointment status",
        "🏥 Clinic information",
        "📅 Book appointment"
    ];
    
    quickRepliesContainer.innerHTML = "";
    
    replies.forEach(reply => {
        const btn = document.createElement("button");
        btn.className = "quick-reply-btn";
        btn.textContent = reply;
        btn.onclick = () => {
            msgInput.value = reply;
            sendMessage();
            quickRepliesContainer.style.display = "none";
        };
        quickRepliesContainer.appendChild(btn);
    });
    
    quickRepliesContainer.style.display = "flex";
}

// =============================
// Send Message to Flask (Enhanced)
// =============================
async function sendMessage() {
    const message = msgInput.value.trim();
    if (!message) return;

    addMessage("user", message);
    msgInput.value = "";
    
    // Disable input while processing
    msgInput.disabled = true;
    sendBtn.disabled = true;

    showTyping();

    try {
        const res = await fetch("/chatbot", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });

        const data = await res.json();
        removeTyping();

        if (data.reply) {
            addMessage("bot", data.reply);
        }

    } catch (err) {
        removeTyping();
        addMessage("bot", "⚠️ Oops! Something went wrong. Please try again.");
        console.error("Chat error:", err);
    } finally {
        // Re-enable input
        msgInput.disabled = false;
        sendBtn.disabled = false;
        msgInput.focus();
    }
}

// =============================
// Events
// =============================
sendBtn.addEventListener("click", sendMessage);

msgInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Auto-resize input (optional enhancement)
msgInput.addEventListener("input", () => {
    // Could add auto-height adjustment here if needed
});

// =============================
// Keyboard Navigation (Accessibility)
// =============================
document.addEventListener("keydown", (e) => {
    // ESC to close chatbot
    if (e.key === "Escape" && botBox.classList.contains("active")) {
        closeBtn.click();
    }
});

// =============================
// Initialize on page load
// =============================
document.addEventListener("DOMContentLoaded", () => {
    console.log("MedBot initialized ✓");
});