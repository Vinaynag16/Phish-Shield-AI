const API_BASE = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", loadDashboard);

async function loadDashboard() {

    const loadingEl = document.getElementById("loading-state");
    const emptyEl = document.getElementById("empty-state");
    const contentEl = document.getElementById("dashboard-content");

    try {
        const res = await fetch(`${API_BASE}/stats`);
        if (!res.ok) throw new Error("Backend offline");
        const data = await res.json();

        loadingEl.style.display = "none";

        if (data.total_scans === 0) {
            emptyEl.style.display = "block";
            return;
        }

        contentEl.style.display = "block";

        document.getElementById("total-scans").textContent = data.total_scans.toLocaleString();
        document.getElementById("detection-rate").textContent = data.detection_rate + "%";

        const threatKeys = Object.keys(data.threat_distribution);
        document.getElementById("threat-count").textContent = threatKeys.length;

        renderScansPerDay(data.scans_per_day);
        renderThreatPie(data.threat_distribution);
        renderTopDomains(data.top_domains);
        renderRecentScans(data.recent_scans);

    } catch (err) {
        loadingEl.innerHTML = `
            <i class="fas fa-exclamation-circle" style="font-size:2rem;color:#f87171;"></i>
            <p style="margin-top:12px;color:#f87171;">Failed to load analytics. Is the backend running?</p>
        `;
    }
}


function getChartColors() {
    const style = getComputedStyle(document.body);
    return {
        text: style.getPropertyValue("--text").trim() || "#e2e8f0",
        muted: style.getPropertyValue("--muted").trim() || "#94a3b8",
        border: style.getPropertyValue("--border").trim() || "rgba(255,255,255,0.08)",
        accent: style.getPropertyValue("--accent").trim() || "#22d3ee",
        green: style.getPropertyValue("--accent-green").trim() || "#14f195"
    };
}


function renderScansPerDay(scansPerDay) {

    const ctx = document.getElementById("scans-per-day-chart").getContext("2d");
    const colors = getChartColors();

    const labels = scansPerDay.map(d => d.date.slice(5));
    const values = scansPerDay.map(d => d.count);

    new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: "Scans",
                data: values,
                borderColor: colors.accent,
                backgroundColor: colors.accent + "22",
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: colors.accent
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    ticks: { color: colors.muted },
                    grid: { color: colors.border }
                },
                y: {
                    beginAtZero: true,
                    ticks: { color: colors.muted, stepSize: 1 },
                    grid: { color: colors.border }
                }
            }
        }
    });
}


function renderThreatPie(distribution) {

    const ctx = document.getElementById("threat-pie-chart").getContext("2d");

    const levelColors = {
        High: "#f87171",
        Medium: "#fbbf24",
        Low: "#34d399"
    };

    const labels = Object.keys(distribution);
    const values = Object.values(distribution);
    const bgColors = labels.map(l => levelColors[l] || "#94a3b8");

    new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: bgColors,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: { color: getChartColors().muted, padding: 16 }
                }
            },
            cutout: "60%"
        }
    });
}


function renderTopDomains(topDomains) {

    const ctx = document.getElementById("top-domains-chart").getContext("2d");
    const colors = getChartColors();

    const labels = topDomains.map(d => d.domain.length > 20 ? d.domain.slice(0, 18) + "…" : d.domain);
    const values = topDomains.map(d => d.count);

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Flagged",
                data: values,
                backgroundColor: "#f87171aa",
                borderColor: "#f87171",
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: { color: colors.muted, stepSize: 1 },
                    grid: { color: colors.border }
                },
                y: {
                    ticks: { color: colors.muted },
                    grid: { display: false }
                }
            }
        }
    });
}


function renderRecentScans(scans) {

    const body = document.getElementById("dashboard-history-body");

    body.innerHTML = scans.map(scan => {

        const resultClass = scan.prediction === "phishing" ? "badge-phishing" : "badge-safe";
        const threatClass = scan.threat_level === "High" ? "badge-phishing"
            : scan.threat_level === "Medium" ? "badge-medium" : "badge-safe";

        const time = scan.timestamp ? new Date(scan.timestamp + "Z").toLocaleString() : "—";

        return `
            <tr>
                <td>${scan.type.toUpperCase()}</td>
                <td>${scan.target.length > 40 ? scan.target.substring(0, 37) + "…" : scan.target}</td>
                <td><span class="badge ${resultClass}">${scan.prediction.toUpperCase()}</span></td>
                <td><span class="badge ${threatClass}">${scan.threat_level}</span></td>
                <td>${scan.score}</td>
                <td>${time}</td>
            </tr>
        `;

    }).join("");
}
