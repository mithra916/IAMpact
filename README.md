#  IAMpact — Mini SIEM for Cloud IAM Threat Detection

**IAMpact** is a prototype Security Information and Event Management (SIEM) tool focused on **cloud Identity & Access Management (IAM)** activity monitoring and threat enrichment.  
Built for the hackathon as a lightweight, intelligent security analytics system that identifies **suspicious user behavior, privilege escalation, and credential abuse** in real-time.


##  Project Overview

Modern cloud environments generate huge volumes of IAM logs — but raw logs alone don't reveal risks.  
**IAMpact** bridges that gap by analyzing IAM events, enriching them with threat intelligence (TI) data, and prioritizing incidents based on contextual risk scoring.



##  Key Features

**Log Ingestion & Normalization**
 Parses raw IAM activity logs (CSV/JSON) and standardizes the fields. 
**Threat Intelligence Enrichment** 
Enriches IP addresses using threat feeds (reputation, geolocation, risk). 
**Risk Scoring Engine** 
Dynamically calculates `final_risk_score` and `final_priority` for each event. 
**Alert Generation** 
Classifies alerts as *Informational*, *Medium*, *High*, or *Critical*.
**Interactive Dashboard (Streamlit)**
Displays visual insights — trends, high-risk users, and top alert categories.
**Auto Recommendations**
Suggests response actions based on alert context. 



## Tech Stack

- **Language:** Python 3.10+
- **Libraries:** pandas, numpy, matplotlib / plotly, Streamlit
- **Data Enrichment:** custom TI API lookups
- **Storage:** Local CSV / JSON
- **Visualization:** Streamlit dashboard



## Project Structure
IAMpact/
│
├── data/
│ ├── enriched_logs.csv # Logs enriched with threat intelligence (TI data)
│ ├── filtered_logs.csv # Logs filtered based on specific criteria (e.g., failed logins, anomalies)
│ ├── final_alerts.csv # Final prioritized alerts generated after scoring and correlation
│ ├── logs.csv # Raw IAM logs (original dataset, excluded from GitHub due to size)
│ ├── normalized_logs.csv # Normalized dataset after field mapping and cleaning
│ └── scored_logs.csv # Logs with computed risk and alert scores
│
│
├── src/
│ ├── agent_core.py # Core logic for data processing, orchestration, and alert generation
│ ├── agentic.py # Agent-based automation logic for enrichment and response
│ ├── alert_score.py # Calculates event-level and aggregated alert scores
│ ├── alert_prioritize.py # Assigns final priority levels (Critical, High, Medium, Low)
│ ├── app.py # Basic Streamlit dashboard interface
│ ├── app_v2.py # Enhanced Streamlit dashboard with metrics and visualization
│ ├── filter.py # Applies filters for suspicious patterns or specific IAM actions
│ ├── ml_score.py # (Optional) Machine learning module for anomaly detection or scoring
│ ├── normalize.py # Cleans and normalizes raw logs for downstream processing
│ └── ti_enrich.py # Threat intelligence enrichment for IPs, geolocation, and reputation
│
├── venv/ # Local virtual environment (excluded from GitHub)
│
├── .gitignore # Excludes unnecessary files (venv, large data, cache)
├── README.md # Project documentation (this file)
└── requirements.txt # Python dependencies
<<<<<<< HEAD
```
=======

>>>>>>> e11b704 (Adding datasets)

## Future Enhancements

Integrate live AWS CloudTrail or Azure AD logs

Deploy centralized dashboard with role-based access

Add machine learning–based anomaly detection

Enable SOC-style alert triage workflow

Implement secure API-based TI feed integration

## Dataset Information
<<<<<<< HEAD
```
AWS cloudtrail dataset has been taken from the kaggle
dataset link -> https://drive.google.com/drive/folders/1-7dTb29QkDtAzpbENK_wunM-QJaWPseB?usp=drive_link
kaggle link -> https://www.kaggle.com/datasets/nobukim/aws-cloudtrails-dataset-from-flaws-cloud
```
=======

AWS cloudtrail dataset has been taken from the kaggle
>>>>>>> e11b704 (Adding datasets)
