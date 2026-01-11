import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# ---------------- CONFIG ----------------
sns.set_style("whitegrid")
FIG_W, FIG_H = 5, 3.6

# ---------------- MAIN FUNCTION ----------------
def app(df):
    from utils import load_global_css
    load_global_css()

    # ---------------- TITLE ----------------
    st.markdown("""
    <h2 style="display:flex; align-items:center; gap:12px;">
        <i class="bi bi-globe-asia-australia" style="font-size:28px; color:#16a34a;"></i>
        Environment Impact Analysis
    </h2>
    """, unsafe_allow_html=True)

    st.caption(
        "Analysis of how weather, road conditions, time of day, and seasonal factors "
        "influence traffic violations, speed behavior, and risk severity."
    )

    # ---------------- FILTERS ----------------
    st.subheader("Environmental Filters")

    f1, f2, f3, f4 = st.columns(4)

    with f1:
        weather = st.multiselect(
            "Weather Condition",
            sorted(df["Weather_Condition"].unique()),
            placeholder="Select weather conditions"
        )

    with f2:
        road = st.multiselect(
            "Road Condition",
            sorted(df["Road_Condition"].unique()),
            placeholder="Select road conditions"
        )

    with f3:
        time_day = st.multiselect(
            "Time of Day",
            sorted(df["Time_of_Day"].unique()),
            placeholder="Select time of day"
        )

    with f4:
        year = st.multiselect(
            "Year",
            sorted(df["Year"].unique()),
            placeholder="Select year"
        )

    # ---------------- SAFE FILTER LOGIC ----------------
    weather_filter = weather if weather else df["Weather_Condition"].unique()
    road_filter = road if road else df["Road_Condition"].unique()
    time_filter = time_day if time_day else df["Time_of_Day"].unique()
    year_filter = year if year else df["Year"].unique()

    filtered = df[
        (df["Weather_Condition"].isin(weather_filter)) &
        (df["Road_Condition"].isin(road_filter)) &
        (df["Time_of_Day"].isin(time_filter)) &
        (df["Year"].isin(year_filter))
    ]

    if filtered.empty:
        st.warning("No data available for the selected environmental conditions.")
        st.stop()

    # ---------------- KPI TABLE ----------------
    st.subheader("Environmental Risk Summary")

    kpi_table = pd.DataFrame({
        "Metric": [
            "Total Violations",
            "Speed Violation Percentage",
            "Average Speed Excess",
            "Average Risk Score"
        ],
        "Value": [
            len(filtered),
            f"{filtered['Speed_Violation'].mean() * 100:.2f} %",
            round(filtered["Speed_Excess"].mean(), 2),
            round(filtered["Risk_Score"].mean(), 2)
        ]
    })

    st.table(kpi_table)
    st.divider()

    # ---------------- ENVIRONMENTAL DISTRIBUTION ----------------
    st.subheader("Environmental Distribution Analysis")

    c1, c2 = st.columns(2)

    with c1:
        fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
        wc = filtered["Weather_Condition"].value_counts()
        sns.barplot(x=wc.values, y=wc.index, palette="Blues_r", ax=ax)
        ax.set_title("Traffic Violations by Weather Condition", fontsize=12, fontweight="bold")
        ax.set_xlabel("Number of Violations", fontsize=10, fontweight="bold")
        ax.set_ylabel("Weather Condition", fontsize=10, fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig)

    with c2:
        fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
        rc = filtered["Road_Condition"].value_counts()
        sns.barplot(x=rc.values, y=rc.index, palette="Greens_r", ax=ax)
        ax.set_title("Traffic Violations by Road Condition", fontsize=12, fontweight="bold")
        ax.set_xlabel("Number of Violations", fontsize=10, fontweight="bold")
        ax.set_ylabel("Road Condition", fontsize=10, fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig)

    st.divider()

    # ---------------- SEVERITY ANALYSIS ----------------
    st.subheader("Violation Severity Analysis")

    c1, c2 = st.columns(2)

    with c1:
        fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
        sns.boxplot(
            data=filtered,
            x="Weather_Condition",
            y="Risk_Score",
            palette="Reds",
            ax=ax
        )
        ax.set_title("Risk Score Distribution by Weather Condition", fontsize=12, fontweight="bold")
        ax.set_xlabel("Weather Condition", fontsize=10, fontweight="bold")
        ax.set_ylabel("Risk Score", fontsize=10, fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig)

    with c2:
        fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
        sns.boxplot(
            data=filtered,
            x="Road_Condition",
            y="Speed_Excess",
            palette="Oranges",
            ax=ax
        )
        ax.set_title("Speed Excess Distribution by Road Condition", fontsize=12, fontweight="bold")
        ax.set_xlabel("Road Condition", fontsize=10, fontweight="bold")
        ax.set_ylabel("Speed Excess", fontsize=10, fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig)

    st.divider()

    # ---------------- WEATHER × ROAD HEATMAP ----------------
    st.subheader("Combined Environmental Risk Analysis")

    pivot = pd.pivot_table(
        filtered,
        values="Risk_Score",
        index="Weather_Condition",
        columns="Road_Condition",
        aggfunc="mean"
    )

    fig, ax = plt.subplots(figsize=(9, 4))
    sns.heatmap(pivot, annot=True, cmap="magma", linewidths=0.4, ax=ax)
    ax.set_title("Average Risk Score by Weather and Road Condition", fontsize=13, fontweight="bold")
    ax.set_xlabel("Road Condition", fontsize=11, fontweight="bold")
    ax.set_ylabel("Weather Condition", fontsize=11, fontweight="bold")
    plt.tight_layout()
    st.pyplot(fig)

    st.divider()

    # ---------------- TEMPORAL ANALYSIS ----------------
    st.subheader("Temporal Environmental Impact")

    time_order = [
        "Morning (6-12)",
        "Afternoon (12-18)",
        "Evening (18-24)",
        "Night (0-6)"
    ]

    filtered = filtered.copy()
    filtered["Time of Day"] = pd.Categorical(
        filtered["Time_of_Day"],
        categories=time_order,
        ordered=True
    )

    c1, c2 = st.columns(2)

    with c1:
        time_risk = (
            filtered
            .groupby("Time of Day", observed=True)["Risk_Score"]
            .mean()
            .reindex(time_order)
        )

        fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
        sns.lineplot(
            x=time_risk.index,
            y=time_risk.values,
            marker="o",
            linewidth=2.5,
            color="purple",
            ax=ax
        )
        ax.set_title("Average Risk Score by Time of Day", fontsize=12, fontweight="bold")
        ax.set_xlabel("Time of Day", fontsize=10, fontweight="bold")
        ax.set_ylabel("Average Risk Score", fontsize=10, fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig)

    with c2:
        season_map = {1: "Spring", 2: "Summer", 3: "Rainy", 4: "Winter"}
        filtered["Season"] = filtered["Quarter"].map(season_map)

        fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
        sns.barplot(
            data=filtered,
            x="Season",
            y="Risk_Score",
            estimator="mean",
            order=["Spring", "Summer", "Rainy", "Winter"],
            palette="coolwarm",
            ax=ax
        )
        ax.set_title("Average Risk Score by Season", fontsize=12, fontweight="bold")
        ax.set_xlabel("Season", fontsize=10, fontweight="bold")
        ax.set_ylabel("Average Risk Score", fontsize=10, fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig)

    st.divider()

    # ---------------- FINAL INSIGHTS ----------------
    st.subheader("Key Observations")

    st.markdown("""
    - Weather and road conditions significantly influence both violation frequency and severity.
    - Risk levels increase during adverse environmental and low-visibility periods.
    - Speed-related violations show higher severity under poor road and weather conditions.
    - Seasonal and time-based patterns help identify high-risk periods for targeted enforcement.
    """)