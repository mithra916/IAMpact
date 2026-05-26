import { useState, useEffect } from "react";
import {
  AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from "recharts";

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
    <div style={{
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      padding: "12px 20px",
      background: COLORS.panel,
      borderBottom: `1px solid ${COLORS.border}`,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <div style={{
          width: 32,
          height: 32,
          borderRadius: 8,
          background: COLORS.accent,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontWeight: 900,
        }}>
          🛡️
        </div>

        <div>
          <div style={{ fontFamily: "monospace", fontWeight: 700 }}>
            IAMpact SOC Dashboard
          </div>
          <div style={{ fontSize: 11, color: COLORS.muted }}>
            AWS IAM Threat Analysis Platform
          </div>
        </div>

        <span style={{
          background: "#1c3a2a",
          color: COLORS.green,
          padding: "3px 10px",
          borderRadius: 20,
          fontSize: 10,
          fontFamily: "monospace",
        }}>
          ● ANALYZER MODE
        </span>
      </div>

      <div style={{ color: COLORS.accent, fontFamily: "monospace", fontSize: 12 }}>
        {time.toLocaleTimeString()}
      </div>
    </div>
  );
}

function StatCard({ title, value, subtitle, color }) {
  return (
    <div style={{
      background: COLORS.panel,
      border: `1px solid ${COLORS.border}`,
      borderRadius: 10,
      padding: 16,
    }}>
      <div style={{
        fontSize: 11,
        color: COLORS.muted,
        fontFamily: "monospace",
        textTransform: "uppercase",
        letterSpacing: 1,
      }}>
        {title}
      </div>

      <div style={{
        fontSize: 34,
        fontWeight: 800,
        color,
        fontFamily: "monospace",
        marginTop: 8,
      }}>
        {value}
      </div>

      <div style={{ fontSize: 11, color: COLORS.muted }}>
        {subtitle}
      </div>
    </div>
  );
}

function priorityColor(priority) {
  if (priority === "CRITICAL") return COLORS.red;
  if (priority === "HIGH") return COLORS.orange;
  if (priority === "MEDIUM") return COLORS.yellow;
  return COLORS.green;
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

  const riskTrend = alerts.map((a, i) => ({
    t: i + 1,
    v: a.risk_score,
  }));

  const actionData = Object.values(
    alerts.reduce((acc, alert) => {
      acc[alert.action] = acc[alert.action] || { name: alert.action, v: 0 };
      acc[alert.action].v += 1;
      return acc;
    }, {})
  );

  return (
    <div style={{
      background: COLORS.bg,
      minHeight: "100vh",
      color: COLORS.text,
      fontFamily: "Inter, Arial, sans-serif",
    }}>
      <style>{`
        * { box-sizing: border-box; }
        textarea:focus { outline: none; border-color: ${COLORS.accent}; }
        button { cursor: pointer; }
      `}</style>

      <Header />

      <div style={{ padding: 18, display: "flex", flexDirection: "column", gap: 14 }}>

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: 14,
        }}>
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

        <div style={{
          display: "grid",
          gridTemplateColumns: "1.2fr 1fr",
          gap: 14,
        }}>
          <div style={{
            background: COLORS.panel,
            border: `1px solid ${COLORS.border}`,
            borderRadius: 10,
            padding: 16,
          }}>
            <div style={{
              display: "flex",
              justifyContent: "space-between",
              marginBottom: 12,
            }}>
              <div>
                <h2>IAM Log Analyzer</h2>
                <p style={{ color: COLORS.muted, fontSize: 12 }}>
                  Paste AWS CloudTrail JSON logs and detect risky IAM activity.
                </p>
              </div>

              <span style={{
                height: 26,
                padding: "5px 10px",
                borderRadius: 20,
                background: "#10233f",
                color: COLORS.accent,
                fontFamily: "monospace",
                fontSize: 11,
              }}>
                POST /api/analyze-logs
              </span>
            </div>

            <textarea
              value={logs}
              onChange={(e) => setLogs(e.target.value)}
              placeholder="Paste CloudTrail JSON array here..."
              style={{
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
              }}
            />

            <button
              onClick={analyzeLogs}
              disabled={loading}
              style={{
                marginTop: 12,
                background: COLORS.accent,
                color: "#fff",
                border: "none",
                padding: "11px 18px",
                borderRadius: 8,
                fontWeight: 700,
              }}
            >
              {loading ? "Analyzing..." : "Analyze Logs"}
            </button>
          </div>

          <div style={{
            background: COLORS.panel,
            border: `1px solid ${COLORS.border}`,
            borderRadius: 10,
            padding: 16,
          }}>
            <div style={{
              color: COLORS.muted,
              fontSize: 11,
              fontFamily: "monospace",
              textTransform: "uppercase",
              marginBottom: 10,
            }}>
              Severity Breakdown
            </div>

            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={severityData}>
                <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
                <XAxis dataKey="name" stroke={COLORS.muted} fontSize={11} />
                <YAxis stroke={COLORS.muted} fontSize={11} />
                <Tooltip />
                <Bar dataKey="v" fill={COLORS.red} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {analysis?.top_alert && (
          <div style={{
            background: "linear-gradient(90deg, #3b0d0d, #161b22)",
            border: `1px solid ${priorityColor(analysis.top_alert.priority)}`,
            borderRadius: 10,
            padding: 18,
          }}>
            <div style={{
              display: "flex",
              justifyContent: "space-between",
              marginBottom: 14,
            }}>
              <h2>🔥 Top Security Alert</h2>

              <span style={{
                background: priorityColor(analysis.top_alert.priority),
                color: "#fff",
                padding: "6px 14px",
                borderRadius: 20,
                fontWeight: 800,
                fontSize: 12,
              }}>
                {analysis.top_alert.priority}
              </span>
            </div>

            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(5, 1fr)",
              gap: 12,
              marginBottom: 14,
            }}>
              <StatCard title="Risk Score" value={analysis.top_alert.risk_score} subtitle="Threat score" color={priorityColor(analysis.top_alert.priority)} />
              <StatCard title="User" value={analysis.top_alert.user} subtitle="IAM identity" color={COLORS.text} />
              <StatCard title="Action" value={analysis.top_alert.action} subtitle="AWS API call" color={COLORS.orange} />
              <StatCard title="Source IP" value={analysis.top_alert.src_ip} subtitle="Origin address" color={COLORS.purple} />
              <StatCard title="Region" value={analysis.top_alert.region} subtitle="AWS region" color={COLORS.green} />
            </div>

            <p style={{ color: COLORS.text }}>
              <b>AI Summary:</b> {analysis.top_alert.explanation.summary}
            </p>
          </div>
        )}

        <div style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 14,
        }}>
          <div style={{
            background: COLORS.panel,
            border: `1px solid ${COLORS.border}`,
            borderRadius: 10,
            padding: 16,
          }}>
            <div style={{
              color: COLORS.muted,
              fontSize: 11,
              fontFamily: "monospace",
              textTransform: "uppercase",
              marginBottom: 10,
            }}>
              Risk Score Trend
            </div>

            <ResponsiveContainer width="100%" height={180}>
              <AreaChart data={riskTrend.length ? riskTrend : [{ t: 0, v: 0 }]}>
                <defs>
                  <linearGradient id="riskGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={COLORS.red} stopOpacity={0.4} />
                    <stop offset="95%" stopColor={COLORS.red} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
                <XAxis dataKey="t" stroke={COLORS.muted} fontSize={11} />
                <YAxis stroke={COLORS.muted} fontSize={11} />
                <Tooltip />
                <Area type="monotone" dataKey="v" stroke={COLORS.red} fill="url(#riskGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div style={{
            background: COLORS.panel,
            border: `1px solid ${COLORS.border}`,
            borderRadius: 10,
            padding: 16,
          }}>
            <div style={{
              color: COLORS.muted,
              fontSize: 11,
              fontFamily: "monospace",
              textTransform: "uppercase",
              marginBottom: 10,
            }}>
              IAM Action Breakdown
            </div>

            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={actionData.length ? actionData : [{ name: "No Data", v: 0 }]}>
                <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
                <XAxis dataKey="name" stroke={COLORS.muted} fontSize={10} />
                <YAxis stroke={COLORS.muted} fontSize={11} />
                <Tooltip />
                <Bar dataKey="v" fill={COLORS.accent} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div style={{
          background: COLORS.panel,
          border: `1px solid ${COLORS.border}`,
          borderRadius: 10,
          padding: 16,
        }}>
          <h2 style={{ marginBottom: 12 }}>Detected Alerts</h2>

          {alerts.length === 0 && (
            <p style={{ color: COLORS.muted }}>
              No alerts detected. Paste CloudTrail logs and click Analyze Logs.
            </p>
          )}

          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {alerts.map((alert, index) => (
              <div
                key={index}
                style={{
                  background: "#0f172a",
                  border: `1px solid ${COLORS.border}`,
                  borderLeft: `5px solid ${priorityColor(alert.priority)}`,
                  borderRadius: 8,
                  padding: 14,
                }}
              >
                <div style={{
                  display: "flex",
                  justifyContent: "space-between",
                  marginBottom: 8,
                }}>
                  <h3>{alert.action}</h3>

                  <span style={{
                    color: priorityColor(alert.priority),
                    fontWeight: 800,
                    fontFamily: "monospace",
                  }}>
                    {alert.priority} · {alert.risk_score}
                  </span>
                </div>

                <div style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(4, 1fr)",
                  gap: 10,
                  fontSize: 13,
                  color: COLORS.muted,
                  marginBottom: 10,
                }}>
                  <p><b>User:</b> {alert.user}</p>
                  <p><b>IP:</b> {alert.src_ip}</p>
                  <p><b>Region:</b> {alert.region}</p>
                  <p><b>Result:</b> {alert.result}</p>
                </div>

                <p style={{ fontWeight: 700, marginBottom: 4 }}>Detection Reasons</p>
                <ul style={{ color: COLORS.muted, paddingLeft: 20 }}>
                  {alert.reasons.map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>

                <p style={{ fontWeight: 700, marginTop: 10, marginBottom: 4 }}>
                  AI Recommendations
                </p>
                <ul style={{ color: COLORS.muted, paddingLeft: 20 }}>
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