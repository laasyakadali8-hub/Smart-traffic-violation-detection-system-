import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime


def app(df):
    from utils import load_global_css
    load_global_css()



    # Main Title (NO st.title)
    st.markdown("""
    <h1 style="display:flex; align-items:center; gap:14px; margin:0; padding:0;">
        <i class="bi bi-speedometer2"></i>
        Traffic Violation Analytics Dashboard
    </h1>
    """, unsafe_allow_html=True)

    # --------------------------------------------------
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    # len(df) == 4000
    # --------------------------------------------------
    # --------------------------------------------------
    # GLOBAL GRAPH CONFIG
    # --------------------------------------------------
    GRAPH_W = 7.6
    GRAPH_H = 4.6

    plt.rcParams.update({
        "axes.titlesize": 12,
        "axes.labelsize": 11,
        "axes.titleweight": "bold",
        "axes.labelweight": "bold",
        "grid.alpha": 0.3
    })

    filtered_df = df

    # --------------------------------------------------
    # KPI MATRIX
    # --------------------------------------------------
    st.markdown('---')
    st.markdown("""
    <h2 style="display:flex; align-items:center; gap:10px; margin-top:20px;">
        <i class="bi bi-clipboard-data"></i>
        Key Metrics Summary
    </h2>
    """, unsafe_allow_html=True)
    # ---------------- KPI CALCULATIONS ----------------

    total_violations = len(df)

    total_fines = df["Fine_Amount"].sum()

    average_fine = int(df["Fine_Amount"].mean())

    top_violation = df["Violation_Type"].value_counts().idxmax()

    top_location = df["Location"].value_counts().idxmax()

    locations_covered = df["Location"].nunique()

    total_fines_fmt = f"₹{total_fines:,.0f}"
    average_fine_fmt = f"₹{average_fine:,.0f}"

    r1c1, r1c2, r1c3, = st.columns(3)
    r2c1, r2c2, r2c3 = st.columns(3)

    r1c1, r1c2, r1c3 = st.columns(3)
    r2c1, r2c2, r2c3 = st.columns(3)

    with r1c1:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-icon">
                <i class="bi bi-exclamation-triangle"></i>
            </div>
            <div class="kpi-title">Total Violations</div>
            <div class="kpi-value">{total_violations:,}</div>
        </div>
        """, unsafe_allow_html=True)

    with r1c2:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-icon">
                <i class="bi bi-currency-rupee"></i>
            </div>
            <div class="kpi-title">Total Fines</div>
            <div class="kpi-value">{total_fines_fmt}</div>
        </div>
        """, unsafe_allow_html=True)

    with r1c3:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-icon">
                <i class="bi bi-calculator"></i>
            </div>
            <div class="kpi-title">Average Fine</div>
            <div class="kpi-value">{average_fine_fmt}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)

    with r2c1:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-icon">
                <i class="bi bi-bar-chart"></i>
            </div>
            <div class="kpi-title">Top Violation</div>
            <div class="kpi-value">{top_violation}</div>
        </div>
        """, unsafe_allow_html=True)

    with r2c2:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-icon">
                <i class="bi bi-person-badge"></i>
            </div>
            <div class="kpi-title">Top Location</div>
            <div class="kpi-value">{top_location}</div>
        </div>
        """, unsafe_allow_html=True)

    with r2c3:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-icon">
                <i class="bi bi-geo-alt"></i>
            </div>
            <div class="kpi-title">Locations Covered</div>
            <div class="kpi-value">{locations_covered}</div>
        </div>
        """, unsafe_allow_html=True)

    # ==================================================
    # ROW 1 VISUALS
    # ==================================================
    st.markdown("---")
    st.markdown("""
    <h2 style="display:flex; align-items:center; gap:10px;">
        <i class="bi bi-graph-up"></i>
        Visualisations
    </h2>
    """, unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    # --------------------------------------------------
    # GRAPH 1
    # --------------------------------------------------
    with c1:
        with st.expander(" Total Violations vs Violation Type", expanded=True):
            st.caption("Horizontal Bar Graph displays the number of violations for each violation category.")

            vt_filter = st.multiselect(
                "Filter Violation Type",
                df['Violation_Type'].unique()
            )

            data_vt = df[df['Violation_Type'].isin(vt_filter)] if vt_filter else df
            vt_counts = data_vt['Violation_Type'].value_counts()

            fig, ax = plt.subplots(figsize=(GRAPH_W + 2, GRAPH_H + 2.8))

            bar_height = 0.85  # 👈 key control (try 0.8–0.95)

            ax.barh(
                vt_counts.index,
                vt_counts.values,
                height=bar_height,
                color=sns.color_palette("viridis", len(vt_counts))
            )

            ax.set_xlabel("Number of Violations", fontweight="bold")
            ax.set_ylabel("Violation Type", fontweight="bold")
            ax.grid(axis="x", linestyle="--", alpha=0.4)
            ax.set_position([0.1, 0.1, 0.85, 0.85])

            st.pyplot(fig)

            with st.expander("⬇ View Table"):
                st.dataframe(vt_counts.reset_index(name="Violations"))

    # --------------------------------------------------
    # GRAPH 2
    # --------------------------------------------------
    with c2:
        with st.expander("Total Violations vs Vehicle Type", expanded=True):
            st.caption("Line graph displays the number of violations by vehicle type.")

            vehicle_filter = st.multiselect(
                "Filter Vehicle Type",
                df["Vehicle_Type"].unique(),
                key="vehicle_filter"
            )

            plot_df = df[df["Vehicle_Type"].isin(vehicle_filter)] if vehicle_filter else df

            vehicle_counts = (
                plot_df.groupby("Vehicle_Type")
                .size()
                .reset_index(name="Violation Count")
            )

            # ✅ SAME HEIGHT AS LEFT GRAPH
            fig, ax = plt.subplots(figsize=(GRAPH_W, GRAPH_H))

            ax.plot(
                vehicle_counts["Vehicle_Type"],
                vehicle_counts["Violation Count"],
                marker="o",
                linewidth=2,
                color="#16a34a"
            )

            ax.set_xlabel("Vehicle Type", fontweight="bold")
            ax.set_ylabel("Violation Count", fontweight="bold")
            ax.grid(True, linestyle="--", alpha=0.4)
            ax.tick_params(axis="x", rotation=20)

            st.pyplot(fig)

            with st.expander("⬇ View Table"):
                st.dataframe(
                    vehicle_counts.rename(columns={"Violation Count": "Violations"})
                )

    # ==================================================
    # Issuing Authority
    # ==================================================
    st.markdown("---")
    agency_counts = df["Issuing_Agency"].value_counts()
    top_agency = agency_counts.idxmax()

    st.markdown("""
    <h3 style="display:flex; align-items:center; gap:10px;">
        <i class="bi bi-building"></i>
        Issuing Authority Enforcement Summary
    </h3>
    """, unsafe_allow_html=True)

    # Derived metrics
    license_actions = df[df['Violation_Type'].isin(
        ['No License', 'Drunk Driving', 'Signal Jumping']
    )].shape[0]

    repeat_actions = df[df['Is_Repeat_Offender'] == 1].shape[0]

    top_vehicle_agency = (
        df.groupby("Vehicle_Type")
        .size()
        .idxmax()
    )

    a1, a2, a3, a4 = st.columns(4)
    with a1:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-icon">
                <i class="bi bi-card-text"></i>
            </div>
            <div class="kpi-title">License-Related Actions</div>
            <div class="kpi-value">{license_actions:,}</div>
        </div>
        """, unsafe_allow_html=True)

    with a2:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-icon">
                <i class="bi bi-arrow-repeat"></i>
            </div>
            <div class="kpi-title">Repeat Offender Actions</div>
            <div class="kpi-value">{repeat_actions:,}</div>
        </div>
        """, unsafe_allow_html=True)

    with a3:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-icon">
                <i class="bi bi-truck-front"></i>
            </div>
            <div class="kpi-title">Most Violated Vehicle</div>
            <div class="kpi-value">{top_vehicle_agency}</div>
        </div>
        """, unsafe_allow_html=True)

    with a4:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-icon">
                <i class="bi bi-building"></i>
            </div>
            <div class="kpi-title">Top Issuing Agency</div>
            <div class="kpi-value">{top_agency}</div>
        </div>
        """, unsafe_allow_html=True)

    # ==================================================
    # ROW 2 VISUALS
    # ==================================================
    st.markdown("---")
    st.markdown("""
    <h3 style="display:flex; align-items:center; gap:10px;">
        <i class="bi bi-cloud-sun"></i>
        Time and Weather Condition
    </h3>
    """, unsafe_allow_html=True)
    c3, c4 = st.columns(2)

    # --------------------------------------------------
    # GRAPH 3
    # --------------------------------------------------
    with c3:
        with st.expander("Total Violations Over Time (Monthly)", expanded=True):
            st.caption("Line Graph showing monthly trends in traffic violations over the selected year range.")

            year_min = int(df['Date'].dt.year.min())
            year_max = int(df['Date'].dt.year.max())

            # Default to 2025 if it exists in dataset
            default_year = 2025 if year_min <= 2025 <= year_max else year_max


            year_range = st.slider(
                "Select Year Range ",
                min_value=2023,
                max_value=2033,
                value=(2025, 2025),
                key="year_range"
            )

            st.markdown("</div>", unsafe_allow_html=True)

            data_time = df[
                (df['Date'].dt.year >= year_range[0]) &
                (df['Date'].dt.year <= year_range[1])
                ]

            monthly = data_time.groupby(data_time['Date'].dt.to_period("M")).size()

            fig, ax = plt.subplots(figsize=(GRAPH_W, GRAPH_H+0.41))
            ax.plot(monthly.index.astype(str), monthly.values, marker='o')

            step = max(1, len(monthly) // 10)
            ax.set_xticks(range(0, len(monthly), step))
            ax.set_xticklabels(
                monthly.index.astype(str)[::step],
                rotation=45,
                ha='right'
            )

            ax.set_xlabel("Month")
            ax.set_ylabel("Total Violations")
            plt.grid(True)
            st.pyplot(fig)

            with st.expander("⬇ View Table"):
                st.dataframe(monthly.reset_index(name="Violations"))
    # --------------------------------------------------
    # GRAPH 4
    # --------------------------------------------------
    with c4:
        if 'Weather_Condition' in df.columns:
            with st.expander("Weather Condition vs Total Violations", expanded=True):
                st.caption(
                    "Bar Graph shows how different weather conditions influence the number of traffic violations.")

                weather_filter = st.multiselect(
                    "Filter Weather Condition",
                    df['Weather_Condition'].unique()
                )

                data_weather = (
                    df[df['Weather_Condition'].isin(weather_filter)]
                    if weather_filter else df
                )

                weather_counts = data_weather['Weather_Condition'].value_counts()

                fig, ax = plt.subplots(figsize=(GRAPH_W+0.02, GRAPH_H-0.1))
                sns.barplot(
                    x=weather_counts.index,
                    y=weather_counts.values,
                    ax=ax
                )
                ax.set_xlabel("Weather Condition")
                ax.set_ylabel("Total Violations")
                ax.tick_params(axis='x', rotation=30)
                st.pyplot(fig)

                with st.expander("⬇ View Table"):
                    st.dataframe(weather_counts.reset_index(name="Violations"))
        else:
            st.info("Weather condition data not available in this dataset.")

    # --------------------------------------------------
    # Today/this month snapshot
    # --------------------------------------------------
    st.markdown('---')
    today_short = datetime.today().strftime("%a").upper()

    st.markdown("""
    <h2><i class="bi bi-calendar-check"></i> Today's / This Month Vilations </h2>
    """, unsafe_allow_html=True)

    today = datetime.today().date()
    month = datetime.today().month
    year = datetime.today().year

    today_df = df[df['Date'].dt.date == today]
    month_df = df[(df['Month'] == month) & (df['Year'] == year)]

    c1, c2, c3, c4 = st.columns(4)
    snapshots = [
        ("Today Violations", len(today_df)),
        ("This Month Violations", len(month_df)),
        ("High Risk Cases", (month_df['Risk_Category'] == "High Risk").sum()),
        ("Repeat Offenders", month_df['Is_Repeat_Offender'].sum())
    ]

    for col, (title, value) in zip([c1, c2, c3, c4], snapshots):
        with col:
            st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-title">{title}</div>
                <div class="kpi-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ==================================================
    # ROW 3 VISUALS
    # ==================================================
    st.markdown("---")
    st.markdown("""
    <h3 style="display:flex; align-items:center; gap:10px;">
        <i class="bi bi-exclamation-triangle"></i>
        Payment and Risk Category
    </h3>
    """, unsafe_allow_html=True)
    c5, c6 = st.columns(2)

    # --------------------------------------------------
    # GRAPH 5: WEATHER CONDITION vs VIOLATIONS
    # --------------------------------------------------
    with c5:
        with st.expander(" Payment Method Distribution", expanded=True):
            st.caption("Represents the proportion of different payment methods used.")

            pay_filter = st.multiselect(
                "Filter Payment Method",
                df['Payment_Method'].unique()
            )

            data_pay = df[df['Payment_Method'].isin(pay_filter)] if pay_filter else df
            pay_dist = data_pay['Payment_Method'].value_counts()
            fig, ax = plt.subplots(figsize=(GRAPH_W, GRAPH_H))

            # Donut parameters
            outer_radius = 1.0
            width = 0.4
            inner_radius = outer_radius - width

            # Create donut (no labels)
            wedges, _ = ax.pie(
                pay_dist.values,
                startangle=140,
                wedgeprops=dict(width=width, edgecolor='white')
            )

            # Exact center of donut ring (KEY FIX)
            label_radius = inner_radius + width / 2

            total = pay_dist.sum()

            for wedge, value in zip(wedges, pay_dist.values):
                angle = (wedge.theta1 + wedge.theta2) / 2
                x = label_radius * np.cos(np.deg2rad(angle))
                y = label_radius * np.sin(np.deg2rad(angle))

                ax.text(
                    x, y,
                    f"{value / total * 100:.1f}%",
                    ha='center',
                    va='center',
                    fontsize=11,
                    fontweight='bold',
                    color='black'
                )

            # Legend for categories (clean)
            ax.legend(
                wedges,
                pay_dist.index,
                title="Payment Method",
                loc="center left",
                bbox_to_anchor=(1.02, 0.95)
            )
            # FORCE DONUT TO USE FULL HEIGHT
            ax.set_position([0.12, 0.12, 0.82, 0.82])
            # MOVE PIE UP
            plt.subplots_adjust(top=0.85)
            ax.set_aspect('equal')
            plt.tight_layout()
            st.pyplot(fig)

            with st.expander("⬇ View Table"):
                st.dataframe(pay_dist.reset_index(name="Count"))

    with c6:
        with st.expander("Risk Category vs  Driver Age Group", expanded=True):
            st.caption("Shows how risk levels are distributed across driver age groups.")

            age_filter = st.multiselect(
                "Filter Age Group",
                df['Age_Group'].unique()
            )

            data_ra = df[df['Age_Group'].isin(age_filter)] if age_filter else df
            risk_age = pd.crosstab(data_ra['Age_Group'], data_ra['Risk_Category'])

            fig, ax = plt.subplots(figsize=(GRAPH_W, GRAPH_H + 3.1))
            risk_age.plot(kind='bar', stacked=True, ax=ax)
            ax.set_xlabel("Driver Age Group")
            ax.set_ylabel("Number of Violations")
            ax.legend(
                title="Risk Category",
                bbox_to_anchor=(1.05, 1),
                loc="upper left",
                borderaxespad=0.
            )

            st.pyplot(fig)

            with st.expander("⬇ View Table"):
                st.dataframe(risk_age)

    st.markdown("---")

    # ==================================================
    # HEATMAP: VIOLATION TYPE vs VEHICLE TYPE
    # ==================================================
    st.markdown("---")
    st.markdown("""
    <h3 style="display:flex; align-items:center; gap:10px;">
        <i class="bi bi-grid-3x3"></i>
        Violation Type vs Vehicle Type Frequency Heatmap
    </h3>
    """, unsafe_allow_html=True)

    # -------------------------------
    # YEAR FILTER
    # -------------------------------
    year_min = int(filtered_df['Date'].dt.year.min())
    year_max = int(filtered_df['Date'].dt.year.max())

    selected_year = st.slider(
        "Select Year",
        year_min,
        year_max,
        year_max
    )

    year_df = filtered_df[filtered_df['Date'].dt.year == selected_year]

    # -------------------------------
    # CREATE CROSSTAB
    # -------------------------------
    heatmap_df = pd.crosstab(
        year_df['Violation_Type'],
        year_df['Vehicle_Type']
    )

    # -------------------------------
    # APPLY RULE CONSTRAINTS
    # -------------------------------
    RULES = {
        'No Helmet': ['Car', 'Truck', 'Bus', 'Auto Rickshaw'],
        'No Seatbelt': ['Bike', 'Scooter', 'Auto Rickshaw']
    }

    for violation, invalid_vehicles in RULES.items():
        if violation in heatmap_df.index:
            for vehicle in invalid_vehicles:
                if vehicle in heatmap_df.columns:
                    heatmap_df.loc[violation, vehicle] = 0

    heatmap_df = heatmap_df.sort_index()
    heatmap_df = heatmap_df[sorted(heatmap_df.columns)]


    left, center, right = st.columns([1, 6, 1])

    with center:
        fig, ax = plt.subplots(figsize=(8.5, 4.8))

        sns.heatmap(
            heatmap_df,
            annot=True,
            fmt="d",
            cmap="Blues",
            linewidths=0.5,
            cbar=True,
            ax=ax
        )

        ax.set_xlabel("Vehicle Type", fontweight="bold")
        ax.set_ylabel("Violation Type", fontweight="bold")
        ax.set_title(f"Violation Frequency Heatmap ({selected_year})", fontweight="bold")

        st.pyplot(fig, width="content")

    # -------------------------------
    # OPTIONAL DATA VIEW
    # -------------------------------
    with st.expander("⬇ View Heatmap Data Table"):
        st.dataframe(heatmap_df, width="stretch")

    # --------------------------------------------------
    # ACTIONABLE RECOMMENDATIONS (WITH ICONS + SEVERITY)
    # --------------------------------------------------
    st.markdown("---")
    st.markdown("""
    <h3>
        <i class="bi bi-compass"></i> Actionable Recommendations
    </h3>
    """, unsafe_allow_html=True)

    # ---------------- HELPERS ----------------
    def severity_label(level):
        return f"<span class='severity-label'>{level}</span>"

    # ---------------- METRICS ----------------
    top_loc = filtered_df['Location'].value_counts().idxmax()
    top_vio = filtered_df['Violation_Type'].value_counts().idxmax()

    high_risk_pct = (
                            (filtered_df['Risk_Category'] == 'High Risk').sum() / len(filtered_df)
                    ) * 100

    repeat_pct = (
                         filtered_df['Is_Repeat_Offender'].sum() / len(filtered_df)
                 ) * 100

    cash_pct = (
                       (filtered_df['Payment_Method'] == 'Cash').sum() / len(filtered_df)
               ) * 100

    # ---------------- RECOMMENDATIONS ----------------
    c1, c2 = st.columns(2)
    with c1:
        # 1. Location enforcement
        loc_severity = "CRITICAL" if high_risk_pct > 30 else "HIGH"
        st.markdown(f"""
        <div class="reco-card severity-{loc_severity.lower()}">
            <div class="reco-title">
                <i class="bi bi-geo-alt"></i> High Violation Zone Detected
            </div>
            <div class="reco-text">
                Increase enforcement in <b>{top_loc}</b>
            </div>
            Severity: {severity_label(loc_severity)}
        </div>
        """, unsafe_allow_html=True)

    with c2:
        # 2. Violation awareness
        vio_severity = "HIGH" if filtered_df['Violation_Type'].value_counts().max() > 0.3 * len(
            filtered_df) else "MEDIUM"
        st.markdown(f"""
        <div class="reco-card severity-{vio_severity.lower()}">
            <div class="reco-title">
                <i class="bi bi-exclamation-triangle"></i> Dominant Violation Pattern
            </div>
            <div class="reco-text">
                Conduct awareness campaigns for <b>{top_vio}</b> violations
            </div>
            Severity: {severity_label(vio_severity)}
        </div>
        """, unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        # 3. High-risk behaviour
        risk_severity = "CRITICAL" if high_risk_pct > 40 else "HIGH" if high_risk_pct > 25 else "MEDIUM"
        st.markdown(f"""
        <div class="reco-card severity-{risk_severity.lower()}">
            <div class="reco-title">
                <i class="bi bi-shield-exclamation"></i> High-Risk Behaviour Observed
            </div>
            <div class="reco-text">
                Deploy targeted patrols during peak and weekend hours
            </div>
            Severity: {severity_label(risk_severity)}
        </div>
        """, unsafe_allow_html=True)

    with c4:
        # 4. Repeat offenders
        repeat_severity = "HIGH" if repeat_pct > 20 else "MEDIUM"
        st.markdown(f"""
        <div class="reco-card severity-{repeat_severity.lower()}">
            <div class="reco-title">
                <i class="bi bi-arrow-repeat"></i> Repeat Offender Concern
            </div>
            <div class="reco-text">
                Introduce stricter penalties or counselling programs
            </div>
            Severity: {severity_label(repeat_severity)}
        </div>
        """, unsafe_allow_html=True)
    c5, c6 = st.columns(2)
    with c5:
        # 5. Payment optimization
        pay_severity = "LOW" if cash_pct < 30 else "MEDIUM"
        st.markdown(f"""
        <div class="reco-card severity-{pay_severity.lower()}">
            <div class="reco-title">
                <i class="bi bi-credit-card"></i> Payment Process Optimization
            </div>
            <div class="reco-text">
                Encourage digital payments in high-cash locations
            </div>
            Severity: {severity_label(pay_severity)}
        </div>
        """, unsafe_allow_html=True)
    # --------------------------------------------------
    # EXTENDED TOP CONTRIBUTORS
    # --------------------------------------------------
    st.markdown("---")
    st.markdown("""
    <h3 style="font-weight:700; display:flex; align-items:center; gap:8px;">
        <i class="bi bi-star"></i>
        Top Contributors
    </h3>
    """, unsafe_allow_html=True)

    def styled_top_table(df):
        return (
            df.style
            .set_properties(**{
                "text-align": "center",
                "font-size": "14px",
                "font-weight": "500"
            })
            .set_table_styles([
                {
                    "selector": "th",
                    "props": [
                        ("font-weight", "700"),
                        ("text-align", "center"),
                        ("background-color", "#f9fafb")
                    ]
                },
                {
                    "selector": "tr:hover",
                    "props": [("background-color", "#f3f4f6")]
                }
            ])
        )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("**Top Violation Types**")
        vt_counts = filtered_df['Violation_Type'].value_counts().head(3)
        st.dataframe(
            styled_top_table(vt_counts.reset_index(name="Count")),
            width="stretch",
            hide_index=True
        )

    with c2:
        st.markdown("**Top Locations**")
        loc_counts = filtered_df['Location'].value_counts().head(3)
        st.dataframe(
            styled_top_table(loc_counts.reset_index(name="Count")),
            width="stretch",
            hide_index=True
        )

    with c3:
        st.markdown("**Top Vehicle Types**")
        veh_counts = filtered_df['Vehicle_Type'].value_counts().head(3)
        st.dataframe(
            styled_top_table(veh_counts.reset_index(name="Count")),
            width="stretch",
            hide_index=True
        )

    # ==================================================
    # ===== ADDITIONS END HERE =====
    # ==================================================


