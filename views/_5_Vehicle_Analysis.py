import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def app(df):
    from utils import load_global_css
    load_global_css()

    # ---------------- DATA CHECK ----------------
    if df is None or df.empty:
        st.error("No data available. Please check the data source.")
        st.stop()

    if "Vehicle_Type" not in df.columns:
        st.error("Vehicle Type column not found in dataset.")
        st.stop()

    # ---------------- TITLE ----------------
    st.markdown("""
    <h2 style="display:flex; align-items:center; gap:12px;">
        <i class="bi bi-car-front-fill" style="font-size:28px; color:#f97316;"></i>
        Vehicle Analysis Dashboard
    </h2>
    """, unsafe_allow_html=True)
    st.caption(
        "Analysis of traffic violations based on vehicle categories, speed behavior, "
        "and safety compliance."
    )

    st.divider()

    # ---------------- FILTERS ----------------
    st.subheader("Vehicle Filters")

    vehicle_options = sorted(df["Vehicle_Type"].dropna().unique())

    selected_vehicles = st.multiselect(
        "Vehicle Type",
        vehicle_options,
        placeholder="Select vehicle types"
    )

    vehicle_filter = selected_vehicles if selected_vehicles else vehicle_options
    filtered_df = df[df["Vehicle_Type"].isin(vehicle_filter)]

    if filtered_df.empty:
        st.warning("No data available for the selected vehicle types.")
        st.stop()

    st.divider()

    # ---------------- KPI TABLE ----------------
    st.subheader("Vehicle Risk Summary")

    kpi_table = pd.DataFrame({
        "Metric": [
            "Total Violations",
            "Vehicle Categories"
        ],
        "Value": [
            len(filtered_df),
            filtered_df["Vehicle_Type"].nunique()
        ]
    })

    st.table(kpi_table)

    st.divider()

    # =====================================================
    # GRAPH 1: Vehicle Type vs Violations
    # =====================================================
    st.subheader("Violations by Vehicle Type")

    vehicle_counts = filtered_df["Vehicle_Type"].value_counts()

    fig1, ax1 = plt.subplots(figsize=(7, 4))
    bars = ax1.bar(
        vehicle_counts.index,
        vehicle_counts.values,
        color="#4C72B0"
    )

    ax1.set_title("Number of Violations per Vehicle Type", fontsize=13, fontweight="bold")
    ax1.set_xlabel("Vehicle Type", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Number of Violations", fontsize=11, fontweight="bold")

    ax1.tick_params(axis="x", rotation=30, labelsize=10)
    ax1.tick_params(axis="y", labelsize=10)

    plt.tight_layout()
    st.pyplot(fig1)
    plt.close(fig1)

    st.divider()

    # =====================================================
    # GRAPH 2: Speed Violations
    # =====================================================
    if "Speed_Violation" in filtered_df.columns:

        st.subheader("Speed Violation Distribution by Vehicle Type")

        speed_data = pd.crosstab(
            filtered_df["Vehicle_Type"],
            filtered_df["Speed_Violation"]
        )

        fig2, ax2 = plt.subplots(figsize=(8, 4.5))
        speed_data.plot(
            kind="bar",
            ax=ax2,
            color=["#55A868", "#C44E52"]
        )

        ax2.set_title("Speed Violation Comparison", fontsize=13, fontweight="bold")
        ax2.set_xlabel("Vehicle Type", fontsize=11, fontweight="bold")
        ax2.set_ylabel("Violation Count", fontsize=11, fontweight="bold")

        ax2.tick_params(axis="x", rotation=30, labelsize=10)
        ax2.tick_params(axis="y", labelsize=10)

        ax2.legend(
            title="Speed Violation",
            fontsize=10,
            title_fontsize=11,
            bbox_to_anchor=(1.02, 1),
            loc="upper left"
        )

        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

    else:
        st.info("Speed Violation information is not available.")

    st.divider()

    # =====================================================
    # GRAPH 3: Safety Compliance
    # =====================================================
    safety_columns = []

    if "Helmet_Compliance" in filtered_df.columns:
        safety_columns.append("Helmet_Compliance")

    if "Seatbelt_Compliance" in filtered_df.columns:
        safety_columns.append("Seatbelt_Compliance")

    if safety_columns:

        st.subheader("Safety Compliance by Vehicle Type")

        safety_data = filtered_df.groupby("Vehicle_Type")[safety_columns].count()

        fig3, ax3 = plt.subplots(figsize=(8, 4.5))
        safety_data.plot(
            kind="bar",
            ax=ax3,
            color=["#8172B2", "#CCB974"]
        )

        ax3.set_title("Safety Compliance Records", fontsize=13, fontweight="bold",color="black")
        ax3.set_xlabel("Vehicle Type", fontsize=11, fontweight="bold")
        ax3.set_ylabel("Record Count", fontsize=11, fontweight="bold")

        ax3.tick_params(axis="x", rotation=30, labelsize=10)
        ax3.tick_params(axis="y", labelsize=10)

        ax3.legend(
            title="Compliance Type",
            fontsize=10,
            title_fontsize=11,
            bbox_to_anchor=(1.02, 1),
            loc="upper left",
            frameon=True
        )

        plt.tight_layout()
        st.pyplot(fig3)
        plt.close(fig3)

    else:
        st.info("Safety compliance data is not available.")

    st.divider()

    # ---------------- DATA PREVIEW ----------------
    with st.expander("View Filtered Data"):
        st.dataframe(filtered_df.head(10))

    # ---------------- CONCLUSION ----------------
    st.subheader("Conclusion")
    st.markdown("""
    - Violation frequency varies significantly across vehicle categories  
    - Speed-related violations are more prominent for specific vehicle types  
    - Safety compliance analysis highlights risk-prone vehicle segments  
    - These insights support targeted enforcement and awareness programs  
    """)
