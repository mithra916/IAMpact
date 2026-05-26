import { useState, useEffect } from "react";

const COLORS = {
  bg: "#0d1117",
  panel: "#161b22",
  border: "#21262d",
  text: "#e6edf3",
  muted: "#7d8590",
  accent: "#58a6ff",
  green: "#3fb950",
  red: "#f85149",
  yellow: "#d29922",
  orange: "#ffa657",
  purple: "#bc8cff",
};

function Header() {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  return (
    <div style={styles.header}>
      <div style={styles.headerLeft}>
        <div style={styles.logo}>🛡️</div>
        <div>
          <div style={styles.title}>IAMpact Dashboard</div>
          <div style={styles.subTitle}>Log Analyzer</div>
        </div>
        <span style={styles.liveBadge}>● ANALYZER MODE</span>
      </div>

      <div style={styles.time}>{time.toLocaleTimeString()}</div>
    </div>
  );
}

function StatCard({ title, value, subtitle, color }) {
  return (
    <div style={styles.card}>
      <div style={styles.cardTitle}>{title}</div>
      <div style={{ ...styles.cardValue, color }}>{value}</div>
      <div style={styles.cardSub}>{subtitle}</div>
    </div>
  );
}

function priorityColor(priority) {
  if (priority === "CRITICAL") return COLORS.red;
  if (priority === "HIGH") return COLORS.orange;
  if (priority === "MEDIUM") return COLORS.yellow;
  return COLORS.green;
}

function BarPanel({ data }) {
  const max = Math.max(...data.map((d) => d.v), 1);

  return (
    <div style={styles.panel}>
      <div style={styles.panelTitle}>Severity Breakdown</div>

      {data.map((item) => (
        <div key={item.name} style={{ marginBottom: 12 }}>
          <div style={styles.barLabel}>
            <span>{item.name}</span>
            <span style={{ color: priorityColor(item.name) }}>{item.v}</span>
          </div>

          <div style={styles.barTrack}>
            <div
              style={{
                ...styles.barFill,
                width: `${(item.v / max) * 100}%`,
                background: priorityColor(item.name),
              }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

function RiskTrend({ alerts }) {
  const data = alerts.length ? alerts : [{ risk_score: 0 }];

  return (
    <div style={styles.panel}>
      <div style={styles.panelTitle}>Risk Score Trend</div>

      <div style={styles.trendBox}>
        {data.map((a, i) => (
          <div
            key={i}
            title={`Risk: ${a.risk_score}`}
            style={{
              ...styles.trendBar,
              height: `${Math.max(a.risk_score, 5)}%`,
              background: priorityColor(a.priority || "LOW"),
            }}
          />
        ))}
      </div>
    </div>
  );
}

function ActionBreakdown({ alerts }) {
  const grouped = alerts.reduce((acc, alert) => {
    acc[alert.action] = (acc[alert.action] || 0) + 1;
    return acc;
  }, {});

  const data = Object.entries(grouped).map(([name, v]) => ({ name, v }));
  const max = Math.max(...data.map((d) => d.v), 1);

  return (
    <div style={styles.panel}>
      <div style={styles.panelTitle}>IAM Action Breakdown</div>

      {data.length === 0 && <p style={styles.empty}>No action data</p>}

      {data.map((item) => (
        <div key={item.name} style={{ marginBottom: 12 }}>
          <div style={styles.barLabel}>
            <span>{item.name}</span>
            <span style={{ color: COLORS.accent }}>{item.v}</span>
          </div>

          <div style={styles.barTrack}>
            <div
              style={{
                ...styles.barFill,
                width: `${(item.v / max) * 100}%`,
                background: COLORS.accent,
              }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

export default function Dashboard() {
  const [logs, setLogs] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyzeLogs = async () => {
    try {
      setLoading(true);

      const response = await fetch("http://127.0.0.1:8000/api/analyze-logs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          logs: JSON.parse(logs),
        }),
      });

      const data = await response.json();
      setAnalysis(data);
    } catch (error) {
      alert("Invalid JSON or backend not running");
    } finally {
      setLoading(false);
    }
  };

  const alerts = analysis?.alerts || [];

  const severityData = ["CRITICAL", "HIGH", "MEDIUM", "LOW"].map((p) => ({
    name: p,
    v: alerts.filter((a) => a.priority === p).length,
  }));

  return (
    <div style={styles.page}>
      <Header />

      <div style={styles.container}>
        <div style={styles.statsGrid}>
          <StatCard
            title="Total Logs"
            value={analysis?.total_logs || 0}
            subtitle="Parsed CloudTrail events"
            color={COLORS.accent}
          />

          <StatCard
            title="Alerts Detected"
            value={analysis?.total_alerts || 0}
            subtitle="Risk-scored IAM events"
            color={COLORS.orange}
          />

          <StatCard
            title="Highest Risk"
            value={analysis?.top_alert?.risk_score || 0}
            subtitle="Top incident score"
            color={analysis?.top_alert ? priorityColor(analysis.top_alert.priority) : COLORS.green}
          />

          <StatCard
            title="Top Priority"
            value={analysis?.top_alert?.priority || "SAFE"}
            subtitle="Current incident level"
            color={analysis?.top_alert ? priorityColor(analysis.top_alert.priority) : COLORS.green}
          />
        </div>

        <div style={styles.mainGrid}>
          <div style={styles.panel}>
            <div style={styles.panelHeader}>
              <div>
                <h2>IAM Log Analyzer</h2>
                <p style={styles.empty}>
                  Paste AWS CloudTrail JSON logs and detect risky IAM activity.
                </p>
              </div>

              <span style={styles.endpoint}>POST /api/analyze-logs</span>
            </div>

            <textarea
              value={logs}
              onChange={(e) => setLogs(e.target.value)}
              placeholder="Paste CloudTrail JSON array here..."
              style={styles.textarea}
            />

            <button onClick={analyzeLogs} disabled={loading} style={styles.button}>
              {loading ? "Analyzing..." : "Analyze Logs"}
            </button>
          </div>

          <BarPanel data={severityData} />
        </div>

        {analysis?.top_alert && (
          <div style={styles.topAlert}>
            <div style={styles.alertHeader}>
              <h2>🔥 Top Security Alert</h2>

              <span
                style={{
                  ...styles.priorityBadge,
                  background: priorityColor(analysis.top_alert.priority),
                }}
              >
                {analysis.top_alert.priority}
              </span>
            </div>

            <div style={styles.topAlertGrid}>
              <StatCard
                title="Risk Score"
                value={analysis.top_alert.risk_score}
                subtitle="Threat score"
                color={priorityColor(analysis.top_alert.priority)}
              />

              <StatCard
                title="User"
                value={analysis.top_alert.user}
                subtitle="IAM identity"
                color={COLORS.text}
              />

              <StatCard
                title="Action"
                value={analysis.top_alert.action}
                subtitle="AWS API call"
                color={COLORS.orange}
              />

              <StatCard
                title="Source IP"
                value={analysis.top_alert.src_ip}
                subtitle="Origin address"
                color={COLORS.purple}
              />

              <StatCard
                title="Region"
                value={analysis.top_alert.region}
                subtitle="AWS region"
                color={COLORS.green}
              />
            </div>

            <p style={{ marginTop: 14 }}>
              <b>AI Summary:</b> {analysis.top_alert.explanation.summary}
            </p>
          </div>
        )}

        <div style={styles.twoGrid}>
          <RiskTrend alerts={alerts} />
          <ActionBreakdown alerts={alerts} />
        </div>

        <div style={styles.panel}>
          <h2 style={{ marginBottom: 12 }}>Detected Alerts</h2>

          {alerts.length === 0 && (
            <p style={styles.empty}>
              No alerts detected. Paste CloudTrail logs and click Analyze Logs.
            </p>
          )}

          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {alerts.map((alert, index) => (
              <div
                key={index}
                style={{
                  ...styles.alertCard,
                  borderLeft: `5px solid ${priorityColor(alert.priority)}`,
                }}
              >
                <div style={styles.alertHeader}>
                  <h3>{alert.action}</h3>

                  <span
                    style={{
                      color: priorityColor(alert.priority),
                      fontWeight: 800,
                      fontFamily: "monospace",
                    }}
                  >
                    {alert.priority} · {alert.risk_score}
                  </span>
                </div>

                <div style={styles.alertMeta}>
                  <p><b>User:</b> {alert.user}</p>
                  <p><b>IP:</b> {alert.src_ip}</p>
                  <p><b>Region:</b> {alert.region}</p>
                  <p><b>Result:</b> {alert.result}</p>
                </div>

                <p style={styles.sectionTitle}>Detection Reasons</p>
                <ul style={styles.list}>
                  {alert.reasons.map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>

                <p style={styles.sectionTitle}>AI Recommendations</p>
                <ul style={styles.list}>
                  {alert.explanation.recommendations.map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  page: {
    background: COLORS.bg,
    minHeight: "100vh",
    color: COLORS.text,
    fontFamily: "Inter, Arial, sans-serif",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "12px 20px",
    background: COLORS.panel,
    borderBottom: `1px solid ${COLORS.border}`,
  },
  headerLeft: {
    display: "flex",
    alignItems: "center",
    gap: 12,
  },
  logo: {
    width: 32,
    height: 32,
    borderRadius: 8,
    background: COLORS.accent,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  title: {
    fontFamily: "monospace",
    fontWeight: 700,
  },
  subTitle: {
    fontSize: 11,
    color: COLORS.muted,
  },
  liveBadge: {
    background: "#1c3a2a",
    color: COLORS.green,
    padding: "3px 10px",
    borderRadius: 20,
    fontSize: 10,
    fontFamily: "monospace",
  },
  time: {
    color: COLORS.accent,
    fontFamily: "monospace",
    fontSize: 12,
  },
  container: {
    padding: 18,
    display: "flex",
    flexDirection: "column",
    gap: 14,
  },
  statsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    gap: 14,
  },
  mainGrid: {
    display: "grid",
    gridTemplateColumns: "1.2fr 1fr",
    gap: 14,
  },
  twoGrid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: 14,
  },
  card: {
    background: COLORS.panel,
    border: `1px solid ${COLORS.border}`,
    borderRadius: 10,
    padding: 16,
  },
  cardTitle: {
    fontSize: 11,
    color: COLORS.muted,
    fontFamily: "monospace",
    textTransform: "uppercase",
    letterSpacing: 1,
  },
  cardValue: {
    fontSize: 28,
    fontWeight: 800,
    fontFamily: "monospace",
    marginTop: 8,
    wordBreak: "break-word",
  },
  cardSub: {
    fontSize: 11,
    color: COLORS.muted,
  },
  panel: {
    background: COLORS.panel,
    border: `1px solid ${COLORS.border}`,
    borderRadius: 10,
    padding: 16,
  },
  panelHeader: {
    display: "flex",
    justifyContent: "space-between",
    marginBottom: 12,
  },
  panelTitle: {
    color: COLORS.muted,
    fontSize: 11,
    fontFamily: "monospace",
    textTransform: "uppercase",
    marginBottom: 14,
  },
  endpoint: {
    height: 26,
    padding: "5px 10px",
    borderRadius: 20,
    background: "#10233f",
    color: COLORS.accent,
    fontFamily: "monospace",
    fontSize: 11,
  },
  textarea: {
    width: "100%",
    height: 270,
    background: "#010409",
    color: COLORS.green,
    border: `1px solid ${COLORS.border}`,
    borderRadius: 8,
    padding: 14,
    fontFamily: "monospace",
    fontSize: 13,
    resize: "vertical",
  },
  button: {
    marginTop: 12,
    background: COLORS.accent,
    color: "#fff",
    border: "none",
    padding: "11px 18px",
    borderRadius: 8,
    fontWeight: 700,
  },
  barLabel: {
    display: "flex",
    justifyContent: "space-between",
    fontFamily: "monospace",
    fontSize: 11,
    color: COLORS.muted,
    marginBottom: 4,
  },
  barTrack: {
    height: 6,
    background: COLORS.border,
    borderRadius: 10,
    overflow: "hidden",
  },
  barFill: {
    height: "100%",
    borderRadius: 10,
    transition: "width 0.3s",
  },
  trendBox: {
    height: 180,
    display: "flex",
    alignItems: "flex-end",
    gap: 6,
    borderBottom: `1px solid ${COLORS.border}`,
  },
  trendBar: {
    flex: 1,
    minHeight: 6,
    borderRadius: "5px 5px 0 0",
  },
  topAlert: {
    background: "linear-gradient(90deg, #3b0d0d, #161b22)",
    border: `1px solid ${COLORS.red}`,
    borderRadius: 10,
    padding: 18,
  },
  alertHeader: {
    display: "flex",
    justifyContent: "space-between",
    marginBottom: 8,
  },
  priorityBadge: {
    color: "#fff",
    padding: "6px 14px",
    borderRadius: 20,
    fontWeight: 800,
    fontSize: 12,
  },
  topAlertGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(5, 1fr)",
    gap: 12,
  },
  alertCard: {
    background: "#0f172a",
    border: `1px solid ${COLORS.border}`,
    borderRadius: 8,
    padding: 14,
  },
  alertMeta: {
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    gap: 10,
    fontSize: 13,
    color: COLORS.muted,
    marginBottom: 10,
  },
  sectionTitle: {
    fontWeight: 700,
    marginTop: 10,
    marginBottom: 4,
  },
  list: {
    color: COLORS.muted,
    paddingLeft: 20,
  },
  empty: {
    color: COLORS.muted,
    fontSize: 12,
  },
};