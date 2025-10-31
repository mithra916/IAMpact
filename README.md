## IAMpact — Lightweight IAM SIEM Dashboard

IAMpact is a mini-SIEM (Security Information & Event Management) system built to monitor IAM activities, detect anomalies, and generate agentic AI insights on user behavior.
It combines Flask (Python) for backend, PostgreSQL for data storage, and a dynamic frontend dashboard with Chart.js visualization.

## Features
```
✅ Real-time dashboard for IAM alerts
✅ Agentic AI insights (risk-based recommendations)
✅ Dynamic trend visualization (with time filter — 24h / 7d / 30d / 1y)
✅ Aggregated metrics (Total Alerts, Critical Alerts, Users, Avg Risk Score)
✅ REST API endpoints for logs, stats, insights
✅ Clean modern UI with auto-refresh
```

## Tech Stack

Layer	Technology
Backend	Flask (Python 3.10+)
Database	PostgreSQL
Frontend	HTML, CSS, JavaScript, Chart.js
AI Logic	Python-based heuristic reasoning (Agentic layer)

## Project Structure
```
iampact/
│
├── backend/
│   ├── app.py                  # Main Flask application
│   ├── utils/
│   │   └── db_config.py        # Database connection
│   └── routes/
│       ├── alerts.py           # Alerts API
│       ├── logs.py             # Logs API
│       └── insights_ai.py      # Agentic AI insights API
│
├── static/
│   ├── app.js                  # Frontend logic (fetch + chart)
│   ├── styles.css              # Dashboard styles
│
├── templates/
│   └── index.html              # Main dashboard UI
│
└── README.md
```

## Future Enhancements

🔹 Integrate OpenAI API / LLM for contextual threat analysis
🔹 Add authentication (admin vs analyst roles)
🔹 Historical data archiving
🔹 Email / Slack alerting
🔹 SOC-style theme with dark mode and real-time websocket updates
