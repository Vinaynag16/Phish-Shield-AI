console.log("🚀 PhishShield Intelligence Engine Active");

// Cleaned API Key (No extra URL parameters)
const NEWS_API_KEY = "pub_ef9193fad08046209222f02bf1dad701"; 

async function getCyberNews() {
    const feed = document.getElementById('news-feed');
    const query = 'cybersecurity OR "data breach" OR "AI security"';
    const apiURL = `https://newsdata.io/api/1/news?apikey=${NEWS_API_KEY}&q=${encodeURIComponent(query)}&language=en&category=technology`;

    try {
        const response = await fetch(apiURL);
        const data = await response.json();

        // If Quota is full or Key is invalid, use Fallback
        if (data.status !== "success") {
            console.warn("API Limit Reached. Loading Fallback Intel...");
            loadMockNews(); 
            return;
        }

        if (data.results.length === 0) {
            feed.innerHTML = "<p>No active threats found in the last 24 hours.</p>";
            return;
        }

        renderArticles(data.results);

    } catch (error) {
        console.error("News Fetch Error:", error);
        loadMockNews(); 
    }
}

function renderArticles(articles) {
    const feed = document.getElementById('news-feed');
    feed.innerHTML = ''; 
    articles.slice(0, 3).forEach(item => {
        feed.innerHTML += `
            <div class="news-card">
                <div class="news-badge">LIVE ALERT</div>
                <span class="date">${new Date(item.pubDate).toLocaleDateString()}</span>
                <h4>${item.title}</h4>
                <p>${item.description ? item.description.substring(0, 100) : "Analyzing full intelligence report..."}...</p>
                <a href="${item.link}" target="_blank" rel="noopener noreferrer" class="news-link">Analyze Intel →</a>
            </div>
        `;
    });
}

function loadMockNews() {
    const mockData = [
        {
            title: "Global Phishing Network Detected Using AI-Generated Templates",
            pubDate: new Date(),
            description: "Security analysts have identified a large-scale operation utilizing LLMs to bypass filters...",
            link: "https://www.cisa.gov/news-events/cybersecurity-advisories"
        },
        {
            title: "Critical Vulnerability Discovered in Cloud Storage Protocols",
            pubDate: new Date(),
            description: "A new zero-day flaw allows for unauthorized lateral movement within enterprise networks...",
            link: "https://thehackernews.com"
        },
        {
            title: "State-Sponsored Group Targeting Financial Infrastructure",
            pubDate: new Date(),
            description: "Monitoring services indicate a rise in advanced persistent threats targeting banking APIs...",
            link: "https://www.bleepingcomputer.com"
        }
    ];
    renderArticles(mockData);
}

document.addEventListener('DOMContentLoaded', getCyberNews);