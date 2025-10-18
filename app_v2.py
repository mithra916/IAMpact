import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ---------- PAGE SETUP ----------
st.set_page_config(
    page_title="IAMpact SIEM Dashboard v2.0",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🛡️ IAMpact - Intelligent IAM SIEM Dashboard v2.0")

# ---------- DATA LOADING ----------
@st.cache_data
def load_data():
    # Try both possible file names
    for f in ["../data/final_alerts.csv", "../data/scored_logs.csv"]:
        try:
            df = pd.read_csv(f)
            st.sidebar.success(f"✅ Loaded data from: {f}")
            return df
        except FileNotFoundError:
            continue
    st.sidebar.error("❌ No log file found! Please ensure the CSV exists in ../data/")
    return pd.DataFrame()

df = load_data()

# ---------- BASIC VALIDATION ----------
if df.empty:
    st.warning("No data loaded. Please check your data folder path.")
    st.stop()

# Ensure timestamp is datetime
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

# ---------- FILTERS ----------
st.sidebar.header("🔍 Filters")
users = st.sidebar.multiselect("Select Users", sorted(df["user"].unique()))
priorities = st.sidebar.multiselect("Select Priorities", sorted(df["final_priority"].unique()))
time_range = st.sidebar.slider("Select Time Range (Hours)", 1, 720, 24)

# Apply filters
filtered_df = df.copy()
if users:
    filtered_df = filtered_df[filtered_df["user"].isin(users)]
if priorities:
    filtered_df = filtered_df[filtered_df["final_priority"].isin(priorities)]

latest_time = df["timestamp"].max()
if pd.notna(latest_time):
    filtered_df = filtered_df[filtered_df["timestamp"] >= latest_time - timedelta(hours=time_range)]

# ---------- METRICS ----------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Alerts", len(filtered_df))
col2.metric("Unique Users", filtered_df["user"].nunique())
col3.metric("Unique Actions", filtered_df["action"].nunique())
col4.metric("Critical Alerts", (filtered_df["final_priority"] == "Critical").sum())

# ---------- RADAR CHART ----------
st.subheader("🎯 User Risk Radar")

if not filtered_df.empty:
    risk_data = filtered_df.groupby("user")["final_risk_score"].mean().reset_index()
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=risk_data["final_risk_score"],
        theta=risk_data["user"],
        fill='toself'
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        showlegend=False,
        template="plotly_dark",
        height=500
    )
    st.plotly_chart(fig_radar, use_container_width=True)
else:
    st.info("⚠️ No user risk data available for radar chart.")

# ---------- TREND OVER TIME ----------
st.subheader("📈 Alert Trend Over Time")
if "timestamp" in filtered_df.columns and not filtered_df.empty:
    trend_data = (
        filtered_df.groupby(filtered_df["timestamp"].dt.date)["final_risk_score"]
        .mean().reset_index()
    )
    fig_trend = px.line(
        trend_data,
        x="timestamp",
        y="final_risk_score",
        title="Average Risk Score Trend",
        markers=True,
        template="plotly_dark"
    )
    st.plotly_chart(fig_trend, use_container_width=True)
else:
    st.info("⚠️ No timestamp data for trend chart.")

# ---------- AGENT INSIGHTS ----------
st.subheader("🧠 Agentic AI Insights")
if "auto_recommendation" in filtered_df.columns and not filtered_df.empty:
    for _, row in filtered_df.head(5).iterrows():
        st.markdown(f"**{row['user']}** — {row['auto_recommendation']}")
else:
    st.info("⚠️ No agent insights found yet. Run the agent_core.py process.")

# ---------- ALERT TABLE ----------
st.subheader("📋 Filtered Alerts")
if not filtered_df.empty:
    st.dataframe(filtered_df, use_container_width=True)
else:
    st.warning("⚠️ No alerts found for the selected filters/time range.")
