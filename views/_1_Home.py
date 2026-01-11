import streamlit as st

def app(df):
    from utils import load_global_css
    load_global_css()

    # ---------------- TITLE ----------------
    st.markdown(
        """
        <div style="margin-bottom:14px;">
            <h1 style="margin:0; line-height:1.2;">
            <i class="bi bi-car-front-fill" style="margin-right:10px; color:#0f172a;"></i>
                Smart Traffic Violation Pattern Detector
            </h1>
            <p style="margin-top:8px; padding-left:46px; color:#475569; font-size:25px;">
                Interactive analytics system for traffic violation pattern analysis
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------- PROJECT OVERVIEW ----------------
    st.markdown(
        """
        <div class="project-card">
            <h4><i class="bi bi-pin-angle-fill"></i> Project Overview</h4>
            <p>
                A data-driven dashboard that analyzes traffic violation data to identify common violations,
                vehicle involvement, fine distribution patterns, and risky behaviors, supporting data-driven
                decisions for improved road safety.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------- IMAGE ----------------
    img_col1, img_col2, img_col3 = st.columns([1, 3, 1])
    with img_col2:
        st.image("images/smart_traffic.jpg", width=850)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------- WHAT SYSTEM DOES ----------------
    st.markdown(
        """
        <h3><i class="bi bi-info-circle-fill"></i> What This System Does</h3>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <i class="bi bi-check-circle-fill"></i> Analyzes traffic violation datasets<br>
        <i class="bi bi-bar-chart-fill"></i> Identifies frequently occurring violations<br>
        <i class="bi bi-car-front-fill"></i> Studies vehicle-wise patterns<br>
        <i class="bi bi-currency-rupee"></i> Examines fine amount distributions<br>
        <i class="bi bi-lightbulb-fill"></i> Supports data-driven traffic decisions
        """,
        unsafe_allow_html=True
    )

    st.info("ℹ️ Use the sidebar navigation to explore analysis pages.")
