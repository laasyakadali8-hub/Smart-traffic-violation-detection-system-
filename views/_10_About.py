import streamlit as st

def app(df):
    from utils import load_global_css
    load_global_css()

    # Title
    st.markdown(
        """
        <h1><i class="bi bi-info-circle-fill"></i> About – Smart Traffic Violation Pattern Detector</h1>
        """,
        unsafe_allow_html=True
    )

    # What this project does
    st.markdown(
        """
        <h3><i class="bi bi-traffic-cone"></i> What this project does</h3>
        """,
        unsafe_allow_html=True
    )
    st.write(
        "This system analyzes real-world Indian traffic violation records to "
        "find when, where, and how violations occur. It converts a large CSV "
        "dataset into an interactive dashboard so traffic officers and policy "
        "makers can quickly see risky time periods, locations, vehicle types, "
        "driver behaviours, and payment patterns."
    )

    # Problem statement & goal
    st.markdown(
        """
        <h3><i class="bi bi-bullseye"></i> Problem statement & goal</h3>
        """,
        unsafe_allow_html=True
    )
    st.write(
        "Unstructured challan data is usually stored but not fully used for "
        "decision-making. The goal of this project is to detect violation "
        "patterns and high-risk behaviours so that enforcement, awareness "
        "campaigns, and fines can be planned using evidence rather than guesswork."
    )

    # Key analytical modules
    st.markdown(
        """
        <h3><i class="bi bi-puzzle-fill"></i> Key analytical modules</h3>
        """,
        unsafe_allow_html=True
    )
    st.write(
        "- **Time & Trend Analysis** – peak hours, busy days, monthly and yearly trends.\n"
        "- **Vehicle Analysis** – which vehicle classes break rules most often and how.\n"
        "- **Driver Behaviour Analysis** – safe, risky, alcohol-risk and repeat-offender profiles.\n"
        "- **Environment Behaviour Analysis** – impact of weather, road condition and season.\n"
        "- **Payment Trend Analysis** – how fines are paid and average fine evolution.\n"
        "- **Reports** – one consolidated analytical report for viva / documentation."
    )

    # Technologies & tools
    st.markdown(
        """
        <h3><i class="bi bi-tools"></i> Technologies & tools</h3>
        """,
        unsafe_allow_html=True
    )
    st.write(
        "The dashboard is built using Python and Streamlit for the UI, with "
        "Pandas and NumPy for data processing and Matplotlib/Seaborn for "
        "visualizations. The design follows a modular structure so each "
        "analysis page is maintained by a different team member and integrated "
        "into a single cohesive application."
    )
