import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="IAMpact Dashboard", layout="wide")

st.title("🛡️ IAMpact - Mini IAM SIEM Dashboard")
st.subheader("🚨 Showing prioritized IAM alerts with ML scoring and recommendations")

# ==============================
# LOAD DATA
# ==============================
DATA_PATH = "../data/final_alerts.csv"

try:
    df = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    st.error("❌ final_alerts.csv not found. Please run alert_prioritize.py first.")
    st.stop()

# ==============================
# FILTER SECTION
# ==============================
col1, col2 = st.columns(2)
with col1:
    priorities = df["final_priority"].unique().tolist()
    priority_filter = st.multiselect(
        "Filter by Priority Level",
        options=priorities,
        default=[p for p in ["CRITICAL", "HIGH"] if p in priorities],
    )

with col2:
    users = df["user"].unique().tolist() if "user" in df.columns else []
    user_filter = st.multiselect("Filter by User", options=users, default=users[:3])

filtered_df = df[
    (df["final_priority"].isin(priority_filter))
    & (df["user"].isin(user_filter) if "user" in df.columns else True)
]

st.markdown("---")

# ==============================
# METRICS SUMMARY
# ==============================
col1, col2, col3 = st.columns(3)
col1.metric("Total Alerts", len(df))
col2.metric("Unique Users", df["user"].nunique() if "user" in df.columns else 0)
col3.metric("Unique Actions", df["action"].nunique() if "action" in df.columns else 0)

# ==============================
# ALERT DISTRIBUTION
# ==============================
st.markdown("### 📊 Alert Priority Distribution")
priority_counts = df["final_priority"].value_counts()

fig, ax = plt.subplots()
priority_counts.plot(kind="bar", color="tomato", ax=ax)
ax.set_xlabel("Priority Level")
ax.set_ylabel("Count")
st.pyplot(fig)

# ==============================
# TOP CRITICAL ALERTS
# ==============================
st.markdown("### 🔥 Top 5 Critical Alerts")
top_alerts = (
    df[df["final_priority"] == "CRITICAL"]
    .sort_values(by="final_risk_score", ascending=False)
    .head(5)
)

st.dataframe(top_alerts[["timestamp", "user", "action", "final_risk_score", "auto_recommendation"]])

# ==============================
# RECOMMENDATIONS TABLE
# ==============================
st.markdown("### 🧠 AI-Generated Response Recommendations")
st.dataframe(filtered_df[["user", "action", "final_priority", "auto_recommendation"]])

st.success("✅ Dashboard loaded successfully!")
