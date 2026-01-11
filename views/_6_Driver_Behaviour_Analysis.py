import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.ticker as ticker
import warnings
warnings.filterwarnings("ignore")
from datetime import timedelta , datetime

#-------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------Driver Behaviour Analysis---------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------

def app(df):
    from utils import load_global_css
    load_global_css()

    st.markdown("""
    <h2 style="display:flex; align-items:center; gap:12px;">
        <i class="bi bi-person-lines-fill" style="font-size:28px; color:#ef4444;"></i>
        Driver Behaviour Profiling System / Analysis
    </h2>
    """, unsafe_allow_html=True)
    st.write(
        'Divides the driver into one of four categoriesas Safe Driver, Risky Driver, Alcohol Risk Driver, Repeat Offender by using factors like: Previous violations, Alcohol consumption , Overspeeding , Helmet and seatbelt usage')
    st.divider()
    # safety violation
    df['Safety_Violation'] = ((df['Helmet_Worn'] == 'No') | (df['Seatbelt_Worn'] == 'No'))

    # --------logic-----------
    def driver_profile(row):
        if row['Previous_Violations'] >= 3:
            return "Repeat Offender"
        elif row['Alcohol_Level'] > 0:
            return 'Alcohol Risk Driver'
        elif row['Speed_Excess'] > 0 and row['Safety_Violation']:
            return 'Risky Driver'
        else:
            return 'Safe Driver'

    df['Driver_Profile'] = df.apply(driver_profile, axis=1)
    # -------------metrics----------------
    # -----------------------------------------------------------------------------------------------------
    total_drivers = df["Violation_ID"].nunique()

    repeat_offenders = df[df["Driver_Profile"] == "Repeat Offender"]["Violation_ID"].nunique()
    repeat_offender_percentage = (repeat_offenders / total_drivers) * 100

    speed_violation_rate = ((df["Speed_Excess"] > 0).sum() / len(df)) * 100

    alcohol_violation_rate = (df["Alcohol_Level"] > 0).mean() * 100

    average_fine = df["Fine_Amount"].mean()

    average_risk_score = df["Risk_Score"].mean()

    with st.expander(" Key Metrics", expanded=True):
        # put ALL metric code here
        col1, col2, col3 = st.columns(3)
        col4, col5, col6 = st.columns(3)
        col7, col8, col9 = st.columns(3)
        with col1:
            with st.container(border=True):
                st.metric("🚗 Total Drivers", f"{total_drivers}")
        with col4:
            with st.container(border=True):
                st.metric("🔁 Repeat Offenders (%)", f"{repeat_offender_percentage:.2f}%")
        with col2:
            with st.container(border=True):
                st.metric("🏎️ Speed Violation Rate", f"{speed_violation_rate:.2f}%")
        with col5:
            with st.container(border=True):
                st.metric("⚠️Risky Drivers (%)", f"{(df['Driver_Profile'] == 'Risky Driver').mean() * 100:.1f}%")
        with col6:
            with st.container(border=True):
                st.metric("🍷Alcohol Risk Drivers(%)",
                          f"{(df['Driver_Profile'] == 'Alcohol Risk Driver').mean() * 100:.1f}%")
        with col7:
            with st.container(border=True):
                st.metric("🦺Safe Drivers (%)", f"{(df['Driver_Profile'] == 'Safe Driver').mean() * 100:.1f}%")
        with col3:
            with st.container(border=True):
                st.metric("🛟Safety Non-Compliance (%)",
                          f"{((df['Helmet_Worn'] == 'No') | (df['Seatbelt_Worn'] == 'No')).mean() * 100:.1f}%")
        with col9:
            with st.container(border=True):
                st.metric("🍺 Alcohol Violation Rate", f"{alcohol_violation_rate:.2f}%")
        with col8:
            with st.container(border=True):
                st.metric("💰 Avg Fine Amount", f"{average_fine:.2f}")
    st.divider()
    # visual
    # Create two columns: left (chart), right (table)
    col_left, col_right = st.columns([2, 1])
    # -------- LEFT: GRAPH --------
    with col_left:
        plt.figure(figsize=(5, 4))
        st.subheader('1. Driver Type Count')
        st.success(
            "🚗 This shows the types of drivers involved in violations based on their violation history,Alcohol Levels, Overspeeding and Safety Compliance. This shows the driver type count. ")
        ax = sns.countplot(x='Driver_Profile', data=df, palette='inferno')
        plt.yscale('log')
        # Format y-axis to show normal numbers instead of 10^x
        ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
        ax.yaxis.set_minor_formatter(ticker.NullFormatter())
        plt.title('Driver Behaviour Categories')
        plt.xlabel('Driver Profile')
        plt.ylabel("Count")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()  # prevents overlap
        st.pyplot(plt)
    # table
    # -------- RIGHT: TABLE --------
    with col_right:
        st.subheader("Table")
        st.success(
            "This table shows the exact count of drivers that each category have.                                                            ")
        driver_counts = df['Driver_Profile'].value_counts().reset_index()
        driver_counts.columns = ['Driver Profile', 'Count']
        st.table(driver_counts)
    st.divider()
    # Create two columns: left (chart), right (table)
    col_left, col_right = st.columns([2, 1])
    # -------- LEFT: GRAPH --------
    with col_left:
        st.subheader('2. Driver Behaviour by Vehicle Type')
        st.success(
            'Shows which type of vehicle is involved in Violations, shows behaviour differences between vehicle types')
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.countplot(data=df, x='Vehicle_Type', hue='Driver_Profile', palette='viridis', ax=ax)
        if ax.legend_:
            ax.legend_.remove()
        ax.set_xlabel("Vehicle Type")
        ax.set_ylabel("Number of Drivers")
        plt.tight_layout()
        plt.xticks(rotation=0)
        st.pyplot(fig)

    # -------- RIGHT: TABLE --------
    with col_right:
        st.subheader("Vehicle Type vs Driver Behaviour (Count Table)")
        st.success('Shows the exact count of vehicles involved in each type of driver.')
        vehicle_driver_table = pd.crosstab(df['Vehicle_Type'], df['Driver_Profile'])
        st.table(vehicle_driver_table)

    st.markdown("**🎨 Driver Profiles:**")
    driver_profiles = df['Driver_Profile'].unique()
    colors = sns.color_palette("viridis", len(driver_profiles))
    # Display legend as colored text
    legend_html = ""
    for profile, color in zip(driver_profiles, colors):
        hex_color = "#%02x%02x%02x" % tuple(int(c * 255) for c in color)
        legend_html += f"<span style='color:{hex_color}; font-size:40px; '>■</span> {profile}  &nbsp;&nbsp;"
    st.markdown(legend_html, unsafe_allow_html=True)
    st.divider()

    from matplotlib.colors import LogNorm
    # Create two columns: left (chart), right (table)
    col_left, col_right = st.columns([2, 1])
    # -------- LEFT: GRAPH --------
    with col_left:
        st.subheader('3. Driver Profile VS Risk Category')
        plt.figure(figsize=(10, 6))
        pivot = pd.crosstab(df['Driver_Profile'], df['Risk_Category'])
        sns.heatmap(pivot, annot=True, fmt='d', cmap='cividis', annot_kws={"color": "black"}, norm=LogNorm())
        plt.title("Driver Profile vs Risk Category")
        plt.xlabel("Risk Category")
        plt.ylabel("Driver Profile")
        st.pyplot(plt)
    # -------- RIGHT: TABLE --------
    with col_right:
        st.markdown(
            """
            <div style="margin-top:100px;">
                <div class="glass-card">
                    It visualizes the relationship between:<br>
                    <b>Driver Profile</b> and <b>Risk Category</b> (Low, Medium, High).<br>
                    Darker colors indicate a higher number of violations.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.divider()
    # Create two columns: left (chart), right (table)
    col_left, col_right = st.columns([2, 1])
    # -------- LEFT: GRAPH --------
    with col_left:
        st.subheader("4. Repeat Offenders by Age Group")
        plt.figure(figsize=(8, 4))
        # Use repeat offenders,# Order age groups
        sns.countplot(data=df, x="Age_Group", palette="crest")
        plt.xlabel("Driver Age Group")
        plt.ylabel("Number of Repeat Violations")
        plt.title("Repeat Offenders Distribution by Age Group")
        st.pyplot(plt)
        plt.clf()
    # -------- RIGHT: TABLE --------

    with col_right:
        st.markdown(
            """
            <div style="margin-top:100px;">
                <div class="glass-card">
                    Repeat violations are most common among middle-aged drivers.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.divider()
    # summary of driver profile
    st.subheader("5. Summary Table:")
    st.info(
        "📊The summary table shows Driver profile average penalty points, total violations, average penalty violations. These drivers should be fined for strict penalties.")
    sum = df.groupby("Driver_Profile").agg(Total_Violations=("Violation_ID", 'count'),
                                             Avg_Penalty_Points=('Penalty_Points', 'mean'),
                                             Avg_Penalty_Violations=("Previous_Violations", "mean")).reset_index()
    st.dataframe(sum)
    st.divider()

