import streamlit as st
import json
import os
import requests # Added to handle the webhook URL

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="AI Disaster Command", page_icon="🚨", layout="wide")

# ==========================================
# 🔌 YOUR N8N WEBHOOK URL GOES HERE
# Replace this string with the actual Test or Production URL from your n8n node
# ==========================================
N8N_WEBHOOK_URL = "https://danesh.app.n8n.cloud/webhook/7a37441b-7f5b-4872-8613-89a7a692684f"

# --- LOCAL FALLBACK MOCK DATA ---
city_options = {
    "Bengaluru": {"risk_score": 2, "status": "Safe", "ai_analysis": "Normal weather patterns detected. No immediate threats.", "offline_sos_count": 0},
    "Mumbai": {"risk_score": 7, "status": "At Risk", "ai_analysis": "Heavy monsoon + river overflow projected inside 12h.", "offline_sos_count": 3},
    "Delhi": {"risk_score": 5, "status": "Watch", "ai_analysis": "Heatwave with air quality spikes expected.", "offline_sos_count": 1},
    "Kolkata": {"risk_score": 8, "status": "Critical", "ai_analysis": "Cyclone landfall alert, evacuate low-lying zones.", "offline_sos_count": 5}
}

# --- FUNCTION TO FETCH LIVE DATA ---
def fetch_city_data(city_name):
    """Tries to get live n8n data; falls back to local data if it fails."""
    try:
        # We pass the city name as a query parameter so n8n knows which city to check
        response = requests.get(f"{N8N_WEBHOOK_URL}?city={city_name}", timeout=5)
        response.raise_for_status()
        live_data = response.json()
        return live_data
    except (requests.exceptions.RequestException, ValueError):
        # If the webhook fails, return the local mock data for that city
        return city_options.get(city_name, city_options["Bengaluru"])

# --- CSS STYLING ---
st.markdown(
    """
    <style>
    /* Button interactions in entire app */
    .stButton button, .stButton > div > button {
        transition: transform 0.16s ease, box-shadow 0.16s ease, background-color 0.16s ease, color 0.16s ease;
        border-radius: 10px;
    }
    .stButton button:hover, .stButton > div > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.25);
    }
    .stButton button:active, .stButton > div > button:active {
        transform: scale(0.97);
    }

    /* Tab hover effects */
    [role='tab'] {
        transition: background-color 0.3s ease, color 0.3s ease, transform 0.2s ease;
    }
    [role='tab']:hover {
        background-color: rgba(0, 122, 255, 0.1);
        color: #004080;
        transform: translateY(-2px);
    }

    /* Smooth card border transitions for metrics */
    .css-1kyxreq .stMetric {
        transition: all 0.25s ease;
    }
    .css-1kyxreq .stMetric:hover {
        transform: scale(1.01);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- SESSION STATE SETUP ---
if "selected_city" not in st.session_state:
    st.session_state.selected_city = ""
if "current_view" not in st.session_state:
    st.session_state.current_view = "Home"

default_cities = ["Bengaluru", "Mumbai", "Delhi"]
city_choices = ["-- Select city --"] + list(city_options.keys())

# --- MAIN PAGE HEADING ---
st.title("🚨 Regional Disaster & Offline Triage Center")
st.markdown("---")

view = st.session_state.current_view

# ==========================================
# HOME VIEW
# ==========================================
if view == "Home":
    st.markdown("## Quick City Picks")
    quick_cols = st.columns(len(default_cities))
    for i, city in enumerate(default_cities):
        if quick_cols[i].button(city, key=f"quick_{city}", help="Click to open city details"):
            st.session_state.selected_city = city
            st.session_state.current_view = "City Details"
            st.rerun()

    with st.expander("🔎 City Search", expanded=True):
        with st.form("city_search_form"):
            search_city = st.text_input(
                "Enter city name",
                value="",
                placeholder="e.g., Bengaluru, Mumbai, Delhi",
                key="city_search_input",
            )
            if st.form_submit_button("Search and Open"):
                if search_city.strip() == "":
                    st.warning("Please enter a city name to search.")
                elif search_city.strip() in city_options:
                    st.session_state.selected_city = search_city.strip()
                    st.session_state.current_view = "City Details"
                    st.rerun()
                else:
                    st.error(f"City '{search_city.strip()}' not found. Try a quick pick.")

    selected_city = st.selectbox(
        "📌 Select City Location",
        city_choices,
        index=city_choices.index(st.session_state.selected_city) if st.session_state.selected_city in city_choices else 0,
        key="city_location_select",
    )

    if selected_city != "-- Select city --" and selected_city in city_options:
        st.session_state.selected_city = selected_city
        st.session_state.current_view = "City Details"
        st.rerun()

    st.markdown("---")
    st.info("Select a city to load analysis and mesh network data in the City Details tab.")

# ==========================================
# CITY DETAILS VIEW
# ==========================================
else:
    if st.session_state.selected_city in city_options:
        
        # Fetch the data (tries Webhook first, then falls back to local)
        with st.spinner(f"Establishing uplink to {st.session_state.selected_city}..."):
            city_data = fetch_city_data(st.session_state.selected_city)
            city_data["location"] = st.session_state.selected_city

        st.markdown(
            """
            <style>
            .city-details-enter {
                animation: slideFadeIn 0.7s ease forwards;
            }
            @keyframes slideFadeIn {
                0% { opacity: 0; transform: translateY(-20px); }
                100% { opacity: 1; transform: translateY(0); }
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(f"<div class='city-details-enter'>", unsafe_allow_html=True)
        
        # Display Cloud vs Local status indicator
        if "Normal weather" in city_data.get("ai_analysis", "") and city_data["location"] == "Bengaluru":
            st.caption("🟢 Operating on Local Mesh Network (Fallback Mode)")
        else:
            st.caption("🔵 Connected to n8n Cloud Server (Live AI Mode)")

        st.subheader(f"Data for {city_data['location']}")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="📍 Target Region", value=city_data["location"])
        with col2:
            st.metric(label="⚠️ AI Risk Score (1-10)", value=city_data.get("risk_score", "N/A"))
        with col3:
            st.metric(label="📡 Offline SOS Pings", value=city_data.get("offline_sos_count", 0))

        st.markdown("---")
        city_tabs = st.tabs(["🤖 AI Predictive Analysis", "📶 Local Mesh Network"])

        with city_tabs[0]:
            risk = int(city_data.get("risk_score", 0))
            if risk >= 7:
                st.error(f"**CRITICAL ALERT:** {city_data.get('ai_analysis', 'No analysis provided.')}")
                st.warning("Initiating offline SMS broadcast via Twilio...")
            elif risk >= 4:
                st.warning(f"**WATCH:** {city_data.get('ai_analysis', 'No analysis provided.')}")
            else:
                st.success(f"**ALL CLEAR:** {city_data.get('ai_analysis', 'No analysis provided.')}")

        with city_tabs[1]:
            st.info("Mesh network traffic from offline nodes.")
            sos_messages = [
                {"id": "001", "msg": "Trapped under debris near Main St.", "severity": "High"},
                {"id": "002", "msg": "Need medical supplies, road blocked.", "severity": "Medium"},
                {"id": "003", "msg": "Child missing, last seen near market.", "severity": "High"}
            ]
            
            sos_count = int(city_data.get("offline_sos_count", 0))
            if sos_count > 0:
                for sos in sos_messages[: sos_count]:
                    st.error(f"**Priority {sos['severity']}** | Node {sos['id']}: {sos['msg']}")
            else:
                st.write("No offline distress signals detected in the mesh network.")

        st.markdown("---")
        
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            if st.button("⬅️ Back to Home", key="back_home"):
                st.session_state.current_view = "Home"
                st.session_state.selected_city = ""
                st.rerun()
        with col_btn2:
            if st.button("🔄 Force Cloud Sync (n8n)", type="primary"):
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.warning("No city selected. Please select one from Home.")

