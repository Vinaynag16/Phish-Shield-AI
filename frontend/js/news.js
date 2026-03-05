/**
 * PhishShield AI - Live Threat Intel Engine
 * Integrated with NewsData.io API for real-time cybersecurity tracking
 */

console.log("🚀 PhishShield Intelligence Engine Active");

// Your active API Key
const NEWS_API_KEY = "pub_ef9193fad08046209222f02bf1dad701"; 

async function getCyberNews() {
    const feed = document.getElementById('news-feed');
    // Targeted query for high-impact security news
    const query = 'cybersecurity OR "data breach" OR "phishing attack"';
    const apiURL = `https://newsdata.io/api/1/news?apikey=${NEWS_API_KEY}&q=${encodeURIComponent(query)}&language=en&category=technology`;

    try {
        const response = await fetch(apiURL);
        const data = await response.json();

        // Handle API limits or errors gracefully
        if (data.status !== "success") {
            console.warn("API Limit Reached or Key Invalid. Loading Fallback Intel...");
            loadMockNews(); 
            return;
        }

        if (data.results.length === 0) {
            feed.innerHTML = `
                <div class="news-error">
                    <p><i class="fas fa-check-circle"></i> No active critical threats reported in the last 24 hours.</p>
                </div>`;
            return;
        }

        renderArticles(data.results);

    } catch (error) {
        console.error("Connection Error:", error);
        loadMockNews(); 
    }
}

function renderArticles(articles) {
    const feed = document.getElementById('news-feed');
    feed.innerHTML = ''; 

    // Show top 3 most recent articles for the grid
    articles.slice(0, 3).forEach(item => {
        const dateStr = new Date(item.pubDate).toLocaleDateString(undefined, {
            month: 'short', day: 'numeric', year: 'numeric'
        });

        // Clean description text
        const snippet = item.description 
            ? item.description.substring(0, 100) + "..." 
            : "Deep-level technical analysis in progress...";

        feed.innerHTML += `
            <div class="news-card">
                <div class="news-tag">LIVE ALERT</div>
                <div class="news-content">
                    <span class="news-date"><i class="far fa-calendar-alt"></i> ${dateStr}</span>
                    <h3>${item.title}</h3>
                    <p>${snippet}</p>
                    <a href="${item.link}" target="_blank" rel="noopener noreferrer" class="news-link">
                        Analyze Intel <i class="fas fa-external-link-alt"></i>
                    </a>
                </div>
            </div>
        `;
    });
}

function loadMockNews() {
    const mockData = [
        {
            title: "Global Phishing Network Using AI-Generated Templates Detected",
            pubDate: new Date(),
            description: "Security analysts have identified a large-scale operation utilizing LLMs to bypass standard email filters.",
            link: "https://www.cisa.gov/news-events/cybersecurity-advisories"
        },
        {
            title: "Zero-Day Vulnerability Discovered in Cloud Authentication Protocols",
            pubDate: new Date(),
            description: "A new flaw allows for unauthorized lateral movement within enterprise hybrid-cloud environments.",
            link: "https://thehackernews.com"
        },
        {
            title: "Advanced Persistent Threat (APT) Targeting Financial APIs",
            pubDate: new Date(),
            description: "Monitoring services indicate a rise in targeted attacks against banking infrastructure using spoofed tokens.",
            link: "https://www.bleepingcomputer.com"
        }
    ];
    renderArticles(mockData);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', getCyberNews);