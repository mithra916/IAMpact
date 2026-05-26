const API_BASE = "http://127.0.0.1:5000/api";

async function fetchJSON(path) {
  try {
    const res = await fetch(`${API_BASE}${path}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error("❌ Fetch failed:", path, err);
    return null;
  }
}

function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

// Add this near top:
let currentRange = "30d";
const timeSelect = document.getElementById("timeRange");

// Listen for changes
if (timeSelect) {
  timeSelect.addEventListener("change", async (e) => {
    currentRange = e.target.value;
    await loadTrendChart(currentRange);
  });
}

async function loadTrendChart(range = "30d") {
  const data = await fetchJSON("/alerts/");
  if (!data || !Array.isArray(data)) return;

  const now = new Date();
  const filterDate = new Date();
  if (range === "24h") filterDate.setDate(now.getDate() - 1);
  else if (range === "7d") filterDate.setDate(now.getDate() - 7);
  else if (range === "30d") filterDate.setDate(now.getDate() - 30);
  else if (range === "365d") filterDate.setFullYear(now.getFullYear() - 1);

  // Filter by time range
  const filtered = data.filter(r => {
    if (!r.timestamp) return false;
    const d = new Date(r.timestamp);
    return d >= filterDate;
  });

  const byDate = {};
  filtered.forEach(r => {
    const d = r.timestamp ? r.timestamp.split("T")[0] : "unknown";
    if (!byDate[d]) byDate[d] = { count: 0, riskSum: 0, riskN: 0 };
    byDate[d].count++;
    if (r.alert_score) {
      const score = parseFloat(r.alert_score);
      if (!isNaN(score)) {
        byDate[d].riskSum += score;
        byDate[d].riskN++;
      }
    }
  });

  const labels = Object.keys(byDate).sort();
  const counts = labels.map(l => byDate[l].count);
  const avgRisk = labels.map(l =>
    byDate[l].riskN ? (byDate[l].riskSum / byDate[l].riskN).toFixed(2) : 0
  );

  const ctx = document.getElementById("trendChart").getContext("2d");
  if (window.chartInstance) window.chartInstance.destroy();

  window.chartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Alert Count",
          data: counts,
          borderColor: "rgba(59,130,246,0.8)",
          backgroundColor: "rgba(59,130,246,0.3)",
          fill: true,
          tension: 0.3
        },
        {
          label: "Avg Risk",
          data: avgRisk,
          borderColor: "rgba(239,68,68,0.9)",
          fill: false,
          tension: 0.3,
          yAxisID: "y1"
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        title: { display: true, text: `Alert Trends (${range})`, color: "#fff" },
        legend: { labels: { color: "#fff" } }
      },
      scales: {
        x: { ticks: { color: "#fff" }, grid: { color: "rgba(255,255,255,0.1)" } },
        y: { title: { display: true, text: "Count" }, ticks: { color: "#fff" }, grid: { color: "rgba(255,255,255,0.1)" } },
        y1: {
          position: "right",
          title: { display: true, text: "Avg Risk" },
          grid: { drawOnChartArea: false },
          ticks: { color: "#fff" }
        }
      }
    }
  });
}



// ---- METRICS ----
// ---- METRICS ----
async function loadStats() {
  const stats = await fetchJSON("/stats/");
  if (!stats || stats.status === "error") return;

  setText("totalAlerts", stats.total_alerts ?? "0");
  setText("criticalAlerts", stats.critical_alerts ?? "0");
  setText("uniqueUsers", stats.unique_users ?? "—");

  // avg risk value
  const avgRiskValue = parseFloat(stats.avg_risk_score || 0);
  const avgRiskElement = document.getElementById("avgRisk");
  avgRiskElement.textContent = avgRiskValue.toFixed(2);

  // color-code risk
  if (avgRiskValue >= 0.7) {
    avgRiskElement.style.color = "red";
  } else if (avgRiskValue >= 0.3) {
    avgRiskElement.style.color = "orange";
  } else {
    avgRiskElement.style.color = "limegreen";
  }
}


// ---- ALERTS ----
async function loadAlerts() {
  const alerts = await fetchJSON("/alerts/");
  const list = document.getElementById("alertsList");
  list.innerHTML = "";

  if (!alerts || alerts.status === "error" || !Array.isArray(alerts)) {
    list.innerHTML = "<li>⚠️ Unable to fetch alerts</li>";
    return;
  }

  if (alerts.length === 0) {
    list.innerHTML = "<li>No recent alerts</li>";
    return;
  }

  alerts.slice(0, 30).forEach(a => {
    const li = document.createElement("li");
    const priorityColor =
      a.prelim_priority === "HIGH" ? "#ef4444" :
      a.prelim_priority === "MEDIUM" ? "#f59e0b" : "#22c55e";

    li.innerHTML = `
  <div class="alert-item">
    <div class="alert-header">
      <strong style="color:#93c5fd;">${a.user || "—"}</strong>
      <span class="priority" style="color:${priorityColor}">
        ${a.prelim_priority || "—"}
      </span>
    </div>
    <div class="alert-meta">
      <span>${a.action || "—"}</span> • 
      <span>${a.src_ip || "—"}</span> • 
      <span>${a.timestamp ? new Date(a.timestamp).toLocaleString() : "—"}</span>
    </div>
  </div>
`;
    list.appendChild(li);
  });
}

// ---- AI INSIGHTS ----

async function loadInsights() {
  const res = await fetch("/api/insights/agentic");
  const data = await res.json();
  const list = document.getElementById("insightsList");
  list.innerHTML = "";
  data.insights.forEach(i => {
    const li = document.createElement("li");
    li.innerHTML = `
  <div class="insight-item">
    <strong style="color:#60a5fa;">${i.user}</strong><br>
    <span>${i.recommendation}</span>
  </div>
`;

    list.appendChild(li);
  });
}


// ---- TREND CHART ----
async function loadTrendChart() {
  const data = await fetchJSON("/alerts/");
  if (!data || !Array.isArray(data)) return;

  // Simulate daily buckets using alert ID order
  const days = 30;
  const now = new Date();
  const labels = [];
  const counts = [];
  const avgRisk = [];

  for (let i = days - 1; i >= 0; i--) {
    const d = new Date(now);
    d.setDate(now.getDate() - i);
    const label = d.toISOString().split("T")[0];
    labels.push(label);
    // Fake data simulation: randomize from actual alert_score average
    const dailyAlerts = Math.floor(Math.random() * 100);
    const dailyRisk = (Math.random() * 0.85).toFixed(2);
    counts.push(dailyAlerts);
    avgRisk.push(dailyRisk);
  }

  const ctx = document.getElementById("trendChart").getContext("2d");
  if (window.chartInstance) window.chartInstance.destroy();

  window.chartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Alert Count",
          data: counts,
          borderColor: "rgba(59,130,246,0.9)",
          backgroundColor: "rgba(59,130,246,0.2)",
          fill: true,
          tension: 0.4,
          yAxisID: "y"
        },
        {
          label: "Avg Risk",
          data: avgRisk,
          borderColor: "rgba(239,68,68,0.9)",
          backgroundColor: "rgba(239,68,68,0.2)",
          fill: false,
          tension: 0.4,
          yAxisID: "y1"
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "top", labels: { color: "#ccc" } },
        title: {
          display: true,
          text: "Alert Trends — Last 30 Days",
          color: "#fff",
          font: { size: 16 }
        }
      },
      interaction: { mode: "index", intersect: false },
      scales: {
        x: {
          ticks: { color: "#aaa" },
          grid: { color: "rgba(255,255,255,0.05)" }
        },
        y: {
          title: { display: true, text: "Alert Count", color: "#aaa" },
          ticks: { color: "#aaa" },
          grid: { color: "rgba(255,255,255,0.05)" }
        },
        y1: {
          position: "right",
          title: { display: true, text: "Avg Risk", color: "#aaa" },
          ticks: { color: "#aaa" },
          grid: { drawOnChartArea: false }
        }
      }
    }
  });
}


// ---- AUTO REFRESH ----
async function refreshAll() {
  console.log("🔄 Refreshing dashboard data...");
  await loadStats();
  await loadAlerts();
  await loadInsights();
  await loadTrendChart();
}

refreshAll();
setInterval(refreshAll, 30000);
