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

# --- MAIN PAGE HEADING ---
st.title("🚨 Regional Disaster & Offline Triage Center")
st.markdown("---")

# --- CITY SELECTOR (click a location to show data) ---
city_options = {
    "Bengaluru": {"risk_score": 2, "status": "Safe", "ai_analysis": "Normal weather patterns detected. No immediate threats.", "offline_sos_count": 0},
    "Mumbai": {"risk_score": 7, "status": "At Risk", "ai_analysis": "Heavy monsoon + river overflow projected inside 12h.", "offline_sos_count": 3},
    "Delhi": {"risk_score": 5, "status": "Watch", "ai_analysis": "Heatwave with air quality spikes expected.", "offline_sos_count": 1},
    "Kolkata": {"risk_score": 8, "status": "Critical", "ai_analysis": "Cyclone landfall alert, evacuate low-lying zones.", "offline_sos_count": 5}
}

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

if "selected_city" not in st.session_state:
    st.session_state.selected_city = ""

# only for future extension: we can track which tab is active by choices
if "active_section" not in st.session_state:
    st.session_state.active_section = "Home"

default_cities = ["Bengaluru", "Mumbai", "Delhi"]
city_choices = ["-- Select city --"] + list(city_options.keys())

if "current_view" not in st.session_state:
    st.session_state.current_view = "Home"

if st.session_state.selected_city in city_options:
    st.session_state.current_view = "City Details"
else:
    st.session_state.current_view = "Home"

view = st.session_state.current_view

if view == "Home":
    st.markdown("## Quick City Picks")
    quick_cols = st.columns(len(default_cities))
    for i, city in enumerate(default_cities):
        if quick_cols[i].button(city, key=f"quick_{city}", help="Click to open city details"):
            st.session_state.selected_city = city
            st.session_state.current_view = "City Details"

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

    st.markdown("---")
    st.info("Select a city to load analysis and mesh network data in the City Details tab.")

else:
    if st.session_state.selected_city in city_options:
        city_data = city_options[st.session_state.selected_city]
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
        st.subheader(f"Data for {city_data['location']}")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="📍 Target Region", value=city_data["location"])
        with col2:
            st.metric(label="⚠️ AI Risk Score (1-10)", value=city_data["risk_score"])
        with col3:
            st.metric(label="📡 Offline SOS Pings", value=city_data["offline_sos_count"])

        st.markdown("---")
        city_tabs = st.tabs(["🤖 AI Predictive Analysis", "📶 Local Mesh Network"])

        with city_tabs[0]:
            if city_data["risk_score"] >= 7:
                st.error(f"**CRITICAL ALERT:** {city_data['ai_analysis']}")
                st.warning("Initiating offline SMS broadcast via Twilio...")
            elif city_data["risk_score"] >= 4:
                st.warning(f"**WATCH:** {city_data['ai_analysis']}")
            else:
                st.success(f"**ALL CLEAR:** {city_data['ai_analysis']}")

        with city_tabs[1]:
            st.info("Mesh network traffic from offline nodes.")
            sos_messages = [
                {"id": "001", "msg": "Trapped under debris near Main St.", "severity": "High"},
                {"id": "002", "msg": "Need medical supplies, road blocked.", "severity": "Medium"},
                {"id": "003", "msg": "Child missing, last seen near market.", "severity": "High"}
            ]
            if city_data["offline_sos_count"] > 0:
                for sos in sos_messages[: city_data["offline_sos_count"]]:
                    st.error(f"**Priority {sos['severity']}** | Node {sos['id']}: {sos['msg']}")
            else:
                st.write("No offline distress signals detected in the mesh network.")

        st.markdown("---")
        if st.button("🔄 Refresh Data", key="refresh_city"):
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.warning("No city selected. Please select one from Home.")

    if st.button("⬅️ Back to Home", key="back_home"):
        st.session_state.current_view = "Home"
        st.session_state.selected_city = ""
        st.rerun()

