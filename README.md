# IAMpact — AI-Powered IAM Log Analyzer

IAMpact is a lightweight AI-powered IAM security analysis dashboard that helps security teams analyze AWS CloudTrail IAM logs, detect suspicious identity activity, prioritize alerts, and generate remediation recommendations.

Current version works as an interactive **CloudTrail Log Analyzer** where users can paste AWS IAM logs and instantly receive risk-scored alerts.

---

## Current Features

- Paste AWS CloudTrail IAM logs directly into the dashboard
- Parse and normalize IAM events
- Detect sensitive IAM actions
- Assign risk scores to each event
- Classify alerts as LOW, MEDIUM, HIGH, or CRITICAL
- Highlight the highest-risk alert
- Display detection reasons
- Generate AI-style remediation recommendations
- Visual SOC-style dashboard UI
- FastAPI backend with React frontend

---

## How It Works
```
CloudTrail Logs
      ↓
Paste into Dashboard
      ↓
FastAPI Analyzer API
      ↓
Log Parsing & Normalization
      ↓
Rule-Based Risk Scoring
      ↓
Alert Prioritization
      ↓
AI Recommendation Engine
      ↓
SOC Dashboard Visualization
```

Example Detection
```
Input CloudTrail event:

{
  "eventTime": "2026-05-26T10:20:00Z",
  "eventName": "CreateAccessKey",
  "sourceIPAddress": "45.67.89.10",
  "awsRegion": "us-east-1",
  "userIdentity": {
    "userName": "admin"
  }
}
```
Output:

Priority: HIGH
Risk Score: 65
User: admin
Action: CreateAccessKey
Source IP: 45.67.89.10

Reasons:
- Sensitive IAM action detected
- External source IP detected

Recommendations:
- Investigate user session
- Verify whether the activity was authorized
- Monitor additional IAM activity

## Project Structure
```
cloud_sec_intel/
│
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   ├── api/
│   │   ├── core/
│   │   ├── detection/
│   │   ├── ingestion/
│   │   ├── models/
│   │   ├── parsing/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── threat_intel/
│   │   ├── websocket/
│   │   └── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   └── Dashboard.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
│
├── docker-compose.yml
├── .gitignore
└── README.md
```
## Tech Stack
```
Backend
Python
FastAPI
Uvicorn
Rule-based risk scoring
IAM event parsing
AI-style recommendation engine
Frontend
React
Vite
JavaScript
```

Custom SOC dashboard UI

▶ How to Run Locally
```
1. Clone the Repository
git clone https://github.com/mithra916/IAMpact.git
cd IAMpact
2. Run Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

Backend will run at:

http://127.0.0.1:8000

API docs:

http://127.0.0.1:8000/docs
3. Run Frontend

Open new terminal:

cd frontend
npm install
npm run dev

Frontend will run at:

http://localhost:5173
```
## Test Logs

Paste this into the dashboard:
```
[
  {
    "eventTime": "2026-05-26T10:20:00Z",
    "eventName": "CreateAccessKey",
    "sourceIPAddress": "45.67.89.10",
    "awsRegion": "us-east-1",
    "userIdentity": {
      "userName": "admin"
    }
  },
  {
    "eventTime": "2026-05-26T10:25:00Z",
    "eventName": "DeleteTrail",
    "sourceIPAddress": "185.220.101.45",
    "awsRegion": "ap-south-1",
    "userIdentity": {
      "userName": "cloud-admin"
    }
  },
  {
    "eventTime": "2026-05-26T10:30:00Z",
    "eventName": "ListUsers",
    "sourceIPAddress": "192.168.1.20",
    "awsRegion": "ap-south-1",
    "userIdentity": {
      "userName": "auditor"
    }
  }
]
 ```
## Current Dashboard Panels
```
Total logs analyzed
Alerts detected
Highest risk score
Top priority level
Severity breakdown
Risk score trend
IAM action breakdown
Top security alert
Detected alerts list
AI recommendations
```
## Detection Logic
```
IAMpact currently uses rule-based security scoring.

Risk factors include:

Sensitive IAM actions
External source IPs
Failed authentication attempts
CloudTrail tampering events
High-risk AWS API calls

Example high-risk actions:

CreateAccessKey
DeleteAccessKey
AttachUserPolicy
AttachRolePolicy
CreateUser
DeleteUser
DeactivateMFADevice
DeleteTrail
StopLogging
AssumeRole
ConsoleLogin
```
### Roadmap

Planned future upgrades:
```
Real AWS CloudTrail integration
STS AssumeRole-based AWS account connection
Multi-account monitoring
WebSocket live alert streaming
Threat intelligence enrichment using AbuseIPDB
GeoIP visualization
ML-based anomaly detection
PostgreSQL alert storage
SOC analyst case management
Slack or email notifications
```
## Project Status

Current status:
```
✅ Working CloudTrail Log Analyzer
✅ FastAPI backend
✅ React SOC dashboard
✅ Risk scoring engine
✅ AI recommendation output
🚧 Real-time AWS integration planned
🚧 Threat intelligence enrichment planned
🚧 ML anomaly detection planned
```
```
Author
Loga Mithra R
Cybersecurity Student | AI & Security Automation

```
