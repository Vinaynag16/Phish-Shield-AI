const API_BASE = "http://127.0.0.1:8000";

/**
 * URL Scanner Logic - Upgraded for Deep Learning Engine
 */
async function scanURL() {
    const urlInput = document.getElementById('url-input').value;
    const resultBox = document.getElementById('result-container');
    const title = document.getElementById('result-title');
    const desc = document.getElementById('result-desc');
    const btn = document.getElementById('url-btn');
    const input = document.getElementById('url-input');
    
    if (!urlInput.includes('.') || urlInput.length < 4) {
        alert("❌ Please enter a valid URL (e.g., google.com)");
        return;
    }
    
    // 1. UI Lock & Initial "Thinking" State
    btn.disabled = true;
    input.readOnly = true;
    btn.innerHTML = `<span class="loader"></span> Analyzing...`;

    resultBox.classList.remove('hidden', 'safe-mode', 'danger-mode', 'warning-mode');
    title.classList.add('analyzing-text');
    title.style.color = "#3498db";
    
    let dotCount = 0;
    const loadingInterval = setInterval(() => {
        dotCount = (dotCount + 1) % 4;
        title.innerText = "🔍 AI is scanning URL structure" + ".".repeat(dotCount);
    }, 300);
    desc.innerText = "Extracting deep features and checking reputation...";

    try {
        const response = await fetch(`${API_BASE}/predict/url`, {
            method: 'POST',
            mode: 'cors',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: urlInput })
        });

        if (!response.ok) throw new Error("Server reached but returned error");
        
        const data = await response.json();
        
        // Artificial delay for "Professional Feel" (optional)
        await new Promise(resolve => setTimeout(resolve, 800));

        clearInterval(loadingInterval);
        displayResult(data);
        addToHistory("URL", urlInput, data);

    } catch (error) {
        console.error("Connection Detailed Error:", error);
        clearInterval(loadingInterval);
        title.innerText = "⚠️ Backend Offline";
        desc.innerText = "Ensure your FastAPI server is running in the terminal.";
        resultBox.classList.add('danger-mode');
    } finally {
        btn.disabled = false;
        input.readOnly = false;
        btn.innerHTML = "Analyze Link";
    }
}

/**
 * Text Scanner Logic - Upgraded for NLP Neural Engine
 */
async function scanText() {
    const messageText = document.getElementById('text-input').value;
    const resultBox = document.getElementById('result-container');
    const title = document.getElementById('result-title');
    const desc = document.getElementById('result-desc');
    
    if (!messageText.trim()) {
        alert("Please paste a message first!");
        return;
    }

    resultBox.classList.remove('hidden', 'safe-mode', 'danger-mode', 'warning-mode');
    title.innerText = "🧠 AI is reading intent...";
    desc.innerText = "Scanning for social engineering patterns...";

    try {
        const response = await fetch(`${API_BASE}/predict/text`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: messageText }) 
        });
        
        const data = await response.json();
        displayResult(data);
        addToHistory('TEXT', messageText, data);

    } catch (error) {
        title.innerText = "⚠️ Backend Offline";
        resultBox.classList.add('danger-mode');
    }
}

/**
 * Universal Result Display Handler - Logic for Threat Levels
 */
function displayResult(data) {
    const box = document.getElementById('result-container');
    const title = document.getElementById('result-title');
    const desc = document.getElementById('result-desc');
    const bar = document.getElementById('confidence-bar');
    
    // 1. Reset Classes
    box.classList.remove('hidden', 'safe-mode', 'danger-mode', 'warning-mode');

    // 2. Extract AI Metadata
    const prediction = data.prediction || "Unknown";
    const threatLevel = data.threat_level || "Low";
    const method = data.method || "AI Analysis";
    const reason = data.reason || "Analysis Complete";
    const scoreText = data.score || "0%";
    const scoreValue = parseFloat(scoreText.toString().replace('%',''));

    // 3. Update Visuals
    if (bar) bar.style.width = scoreValue + "%";
    title.innerText = prediction.toUpperCase();
    title.style.color = "white";
    
    desc.innerHTML = `
        <div class="risk-badge badge-${threatLevel.toLowerCase()}">RISK: ${threatLevel}</div>
        <strong>Engine:</strong> ${method} (${scoreText})<br>
        <p class="advice-text">${reason}</p>
    `;
    
    // 4. Color Coding Logic
    const verdict = prediction.toLowerCase();
    if (verdict.includes("safe")) {
        box.classList.add('safe-mode');
    } else if (threatLevel === "High") {
        box.classList.add('danger-mode');
    } else {
        box.classList.add('warning-mode'); // Medium/Caution items
    }
}

/**
 * History Management (Persistent LocalStorage)
 */
let scanHistory = JSON.parse(localStorage.getItem('phish_history')) || [];

function addToHistory(type, target, data){
    const newScan = {
        type: type.toUpperCase(),
        target: target.length > 30 ? target.substring(0,27) + "..." : target,
        prediction: data.prediction,
        threat: data.threat_level || "Low",
        score: data.score || "N/A",
        timestamp: new Date().toLocaleTimeString()
    };
    scanHistory.unshift(newScan);
    if (scanHistory.length > 5) scanHistory.pop(); 
    localStorage.setItem('phish_history', JSON.stringify(scanHistory));
    renderHistory();
}

function renderHistory() {
    const body = document.getElementById('history-body');
    const section = document.getElementById('history-section');
    if (!body || !section) return;

    if (scanHistory.length === 0) {
        section.classList.add('hidden');
        return;
    }
    
    section.classList.remove('hidden');
    body.innerHTML = scanHistory.map(scan => `
        <tr>
            <td>${scan.type}</td>
            <td title="${scan.target}">${scan.target}</td>
            <td class="status-${scan.prediction.toLowerCase()}">${scan.prediction.toUpperCase()}</td>
            <td><span class="dot dot-${scan.threat.toLowerCase()}"></span> ${scan.threat}</td>
        </tr>
    `).join('');
}

/**
 * Navigation & Utilities
 */
function showTab(type) {
    document.getElementById('url-tab').style.display = type === 'url' ? 'block' : 'none';
    document.getElementById('text-tab').style.display = type === 'text' ? 'block' : 'none';
    const buttons = document.querySelectorAll('.tab-btn');
    buttons[0].classList.toggle('active', type === 'url');
    buttons[1].classList.toggle('active', type === 'text');
    document.getElementById('result-container').classList.add('hidden');
}

function clearHistory() {
    scanHistory = [];
    localStorage.removeItem('phish_history');
    renderHistory();
}

function copyResult() {
    const prediction = document.getElementById('result-title').innerText;
    const details = document.getElementById('result-desc').innerText;
    const report = `🛡️ Phish-Shield AI Report\nVerdict: ${prediction}\n${details}\nDate: ${new Date().toLocaleString()}`;
    navigator.clipboard.writeText(report).then(() => {
        const btn = document.getElementById('copy-btn');
        btn.innerText = "✅ Copied!";
        setTimeout(() => { btn.innerText = "📋 Copy Detailed Report"; }, 2000);
    });
}

document.addEventListener('DOMContentLoaded', renderHistory);