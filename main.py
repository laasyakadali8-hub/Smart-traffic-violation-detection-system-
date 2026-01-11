import streamlit as st
import pandas as pd
from utils import apply_theme

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Traffic Violation Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils import load_global_css
load_global_css()

# ==================================================
# SESSION STATE (SIDEBAR CONTROL)
# ==================================================
if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True

# ==================================================
# LOAD DATA (ONCE – FAST)
# ==================================================
@st.cache_resource
def load_data():
    return pd.read_csv("Indian_Traffic_Violations_Dataset.csv")

df = load_data()

# ==================================================
# THEME & ICONS
# ==================================================
apply_theme()

st.markdown(
    """
    <link rel="stylesheet"
    href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    """,
    unsafe_allow_html=True
)

# ==================================================
# CUSTOM CSS (OPTIONAL)
# ==================================================
try:
    with open("styles/main.css", "r", encoding="utf-8") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
except:
    pass

# ==================================================
# SIDEBAR
# ==================================================
with st.sidebar:
    page = st.radio(
        "Navigation",
        [
            "Home",
            "Dashboard",
            "Time Trend Analysis",
            "Environment Analysis",
            "Vehicle Analysis",
            "Driver Behaviour Analysis",
            "Payment Analysis",
            "Map Visualisation",
            "Report",
            "About"
        ]
    )

    st.markdown("---")
    st.caption("Smart Traffic Violation Pattern Detector")

# ==================================================
# SIDEBAR VISIBILITY (CSS ONLY)
# ==================================================
if not st.session_state.sidebar_open:
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# ==================================================
# ROUTING
# ==================================================
if page == "Home":
    from views._1_Home import app
    app(df)

elif page == "Dashboard":
    from views._2_Dashboard import app
    app(df)

elif page == "Time Trend Analysis":
    from views._3_Time_Trend_Analysis import app
    app(df)

elif page == "Environment Analysis":
    from views._4_Environment_Analysis import app
    app(df)

elif page == "Vehicle Analysis":
    from views._5_Vehicle_Analysis import app
    app(df)

elif page == "Driver Behaviour Analysis":
    from views._6_Driver_Behaviour_Analysis import app
    app(df)

elif page == "Payment Analysis":
    from views._7_Payment_Analysis import app
    app(df)

elif page == "Map Visualisation":
    from views._8_Map_Visualisation import app
    app(df)

elif page == "Report":
    from views._9_Report import app
    app(df)

elif page == "About":
    from views._10_About import app
    app(df)
