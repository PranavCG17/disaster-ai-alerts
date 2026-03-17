import streamlit as st
import json
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="AI Disaster Command", page_icon="🚨", layout="wide")

# --- MOCK DATA FUNCTION (n8n will replace this later) ---
DATA_FILE = "disaster_status.json"

def load_data():
    # If n8n hasn't created the file yet, return a safe default
    if not os.path.exists(DATA_FILE):
        return {
            "location": "Bengaluru",
            "risk_score": 2,
            "status": "Safe",
            "ai_analysis": "Normal weather patterns detected. No immediate threats.",
            "offline_sos_count": 0
        }
    # Read the real data from n8n
    with open(DATA_FILE, "r") as file:
        return json.load(file)

data = load_data()

# --- DASHBOARD UI ---
st.title("🚨 Regional Disaster & Offline Triage Center")
st.markdown("---")

# Top Row: Metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="📍 Target Region", value=data["location"])
with col2:
    st.metric(label="⚠️ AI Risk Score (1-10)", value=data["risk_score"])
with col3:
    st.metric(label="📡 Offline SOS Pings", value=data["offline_sos_count"])

st.markdown("---")

# AI Alert Banner
st.subheader("🤖 AI Predictive Analysis")
if data["risk_score"] >= 7:
    st.error(f"**CRITICAL ALERT:** {data['ai_analysis']}")
    st.warning("Initiating offline SMS broadcast via Twilio...")
elif data["risk_score"] >= 4:
    st.warning(f"**WATCH:** {data['ai_analysis']}")
else:
    st.success(f"**ALL CLEAR:** {data['ai_analysis']}")

st.markdown("---")

# The X-Factor: Offline Triage Feed
st.subheader("📶 Local Mesh Network (Offline SOS Feed)")
st.info("This panel simulates incoming text alerts routed through the offline Wi-Fi/Bluetooth mesh network when cellular towers fail.")

# Mock SOS queue for the UI
sos_messages = [
    {"id": "001", "msg": "Trapped under debris near Main St.", "severity": "High"},
    {"id": "002", "msg": "Need medical supplies, road blocked.", "severity": "Medium"}
]

if data["offline_sos_count"] > 0:
    for sos in sos_messages:
        st.error(f"**Priority {sos['severity']}** | Node {sos['id']}: {sos['msg']}")
else:
    st.write("No offline distress signals detected in the mesh network.")

# Refresh Button
if st.button("🔄 Refresh System Data"):
    st.rerun()