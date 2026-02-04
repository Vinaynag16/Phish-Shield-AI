console.log("🚀 PhishShield Intelligence Engine Active");
const NEWS_API_KEY = "pub_ef9193fad08046209222f02bf1dad701&q=Tech%20and%20cybersecurity%20"; // api key from newsdata.io

async function getCyberNews() {
    const feed = document.getElementById('news-feed');
    // Query focuses on Cyber Threats and Tech Evolution
    const query = 'cybersecurity OR "data breach" OR "AI security"';
    const apiURL = `https://newsdata.io/api/1/news?apikey=${NEWS_API_KEY}&q=${encodeURIComponent(query)}&language=en&category=technology`;

    try {
        const response = await fetch(apiURL);
        const data = await response.json();

        if (data.status !== "success") throw new Error(data.message || "API Error");

        if (data.results.length === 0) {
            feed.innerHTML = "<p>No active threats found in the last 24 hours.</p>";
            return;
        }

        feed.innerHTML = ''; 
        data.results.slice(0, 3).forEach(item => {
            const card = `
                <div class="news-card">
                    <div class="news-badge">LIVE ALERT</div>
                    <span class="date">${new Date(item.pubDate).toLocaleDateString()}</span>
                    <h4>${item.title}</h4>
                    <p>${item.description ? item.description.substring(0, 100) : "No summary available."}...</p>
                    <a href="${item.link}" target="_blank" class="news-link">Read Intelligence Report →</a>
                </div>
            `;
            feed.innerHTML += card;
        });
    } catch (error) {
        console.error("News Fetch Error:", error);
        feed.innerHTML = `<div class="news-error">
                <p>⚠️ Intelligence Feed Sync Interrupted</p>
                <button onclick="getCyberNews()" class="btn-secondary">Retry Connection</button>
            </div>`;
    }
}

document.addEventListener('DOMContentLoaded', getCyberNews);