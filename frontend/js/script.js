const API_BASE = "http://127.0.0.1:8000";
//const API_BASE = "https://phish-shield-ai.onrender.com";
/**
 * URL Scanner Logic
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
    
    // 1. Lock UI
    btn.disabled = true;
    input.readOnly = true;
    btn.innerHTML = `<span class="loader"></span> Analyzing...`;

    // 1. Enter "Thinking" State
    resultBox.classList.remove('hidden','safe-mode','danger-mode');
    title.classList.add('analyzing-text');
    title.style.color = "#3498db";
    let dotCount = 0;
    const loadingInterval = setInterval(() => {
        dotCount = (dotCount +1) % 4;
        title.innerText = "🔍 AI is analyzing URL structure" + ".".repeat(dotCount);
    },300);
    desc.innerText = "Extracting features and checking brand reputation...";

    try {
        const response = await 
            fetch(`${API_BASE}/predict/url`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: urlInput })
        });
        await new Promise(resolve => setTimeout(resolve, 1500));
     
        if (!response.ok) {
            throw new Error("Server responded with an error status");
        }
        const data = await response.json();
        clearInterval(loadingInterval);
        displayResult(data);
        addToHistory("URL", urlInput, data);

    } catch (error) {
        console.error("Connection Error:", error);
        title.innerText = "❌ Connection Error";
        desc.innerText = "Is your FastAPI server running? Check terminal for errors.";
        resultBox.classList.add('danger-mode');
    } finally {
        // 2. Unlock UI after 1.5s delay
        btn.disabled = false;
        input.readOnly = false;
        btn.innerHTML = "Analyze Link";
    }
}

/**
 * Text Scanner Logic
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

    // 1. Enter "Thinking" State
    resultBox.classList.remove('hidden');
    resultBox.classList.remove('safe-mode', 'danger-mode');
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
        console.error("Error:", error);
        title.innerText = "⚠️ Backend Offline";
        desc.innerText = "Please ensure your Python FastAPI server is running.";
        resultBox.classList.add('danger-mode');
    }
}

/**
 * Universal Result Display Handler
 */
function displayResult(data) {
    const box = document.getElementById('result-container');
    const title = document.getElementById('result-title');
    const desc = document.getElementById('result-desc');
    const bar = document.getElementById('confidence-bar');
    const scoreValue= data.score || 0;
    bar.style.width = scoreValue + "%";
    // 1. Reset state
    box.classList.remove('hidden', 'safe-mode', 'danger-mode');

    // 2. Extract data from API response
    const prediction = data.prediction || "Unknown";
    const method = data.method || "AI Analysis";
    const reason = data.reason || "Analysis Complete";

    // 3. Update Text Content
    // This will now show: "Engine: 🤖 Random Forest AI"
    // and "🛡️ AI is 98.5% confident..."
    title.innerText = prediction.toUpperCase();
    desc.innerHTML = `<strong>Engine:</strong> ${method}<br>${reason}`;
    
    // 4. Apply colors based on prediction
    const verdict = prediction.toLowerCase();
    if (verdict.includes("safe")) {
        box.classList.add('safe-mode'); // Turns green
    } else {
        box.classList.add('danger-mode'); // Turns red
    }
}

/**
 * Tab Navigation Logic
 */
function showTab(type) {
    document.getElementById('url-tab').style.display = type === 'url' ? 'block' : 'none';
    document.getElementById('text-tab').style.display = type === 'text' ? 'block' : 'none';
    
    const buttons = document.querySelectorAll('.tab-btn');
    buttons[0].classList.toggle('active', type === 'url');
    buttons[1].classList.toggle('active', type === 'text');
    
    // Clear results when switching views
    document.getElementById('result-container').classList.add('hidden');
}
 /** an Array to store scan history */
let scanHistory = JSON.parse(localStorage.getItem('phish_history')) || [];
// Function to add a scan to the list
function addToHistory(type, target, data){
    const newScan = {
        type:type.toUpperCase(),
        target:target.length > 30 ? target.substring(0,27) + "..." : target,
        prediction:data.prediction,
        score:data.score ? data.score + "%" : "N/A",
        timestamp: new Date().toLocaleTimeString()
    };
    scanHistory.unshift(newScan);
    if (scanHistory.length > 5) scanHistory.pop(); //only last 5 scans
    localStorage.setItem('phish_history', JSON.stringify(scanHistory));
    renderHistory();
}
//Function for rendering history
function renderHistory() {
    const historySection = document.getElementById('history-section');
    const body = document.getElementById('history-body');
    if (!historySection || !body) {
        console.warn("History HTML elements not found. Skipping render.");
        return;
    }

    if (scanHistory.length === 0) {
        console.log("ℹ️ History is empty. Hiding section")
        historySection.classList.add('hidden');
        return;
    }
    console.log("✅ History found. Updating table with", scanHistory.length, "items.");
    historySection.classList.remove('hidden');
    body.innerHTML = scanHistory.map(scan => `
        <tr>
            <td>${scan.type}</td>
            <td>${scan.target}</td>
            <td class="${scan.prediction.toLowerCase()}">${scan.prediction.toUpperCase()}</td>
            <td>${scan.score}</td>
        </tr>
    `).join('');
}

function clearHistory() {
    scanHistory = [];
    localStorage.removeItem('phish_history');
    renderHistory();
}

// Initial render on page load
document.addEventListener('DOMContentLoaded', renderHistory);

function copyResult() {
    const prediction = document.getElementById('result-title').innerText;
    const details = document.getElementById('result-desc').innerText;
    const url = document.getElementById('url-input').value || "Scanned Text";

    const report = `🛡️ Phish-Shield AI Report\n--------------------------\nTarget: ${url}\nVerdict: ${prediction}\nAnalysis: ${details}\n--------------------------\nScan Date: ${new Date().toLocaleString()}`;

    navigator.clipboard.writeText(report).then(() => {
        const copyBtn = document.getElementById('copy-btn');
        copyBtn.innerText = "✅ Copied!";
        setTimeout(() => { copyBtn.innerText = "📋 Copy Detailed Report"; }, 2000);
    });
}