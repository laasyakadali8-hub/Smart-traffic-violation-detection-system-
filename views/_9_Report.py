import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# ---------------- CONFIGURATION ----------------
st.set_page_config(layout="wide")
sns.set_style("whitegrid")

FIG_W, FIG_H = 5, 3.4

def app(df):
    from utils import load_global_css
    load_global_css()

    # ---------------- TITLE ----------------
    st.markdown("""
    <h2 style="display:flex; align-items:center; gap:12px;">
        <i class="bi bi-file-earmark-text-fill" style="font-size:28px; color:#6366f1;"></i>
        Indian Traffic Violations – Analytical Report
    </h2>
    """, unsafe_allow_html=True)

    st.write(
        """
        This report provides a structured analysis of traffic violation data
        to identify patterns, contributing factors, and enforcement insights.
        """
    )

    # ---------------- DATASET SUMMARY (TABLE) ----------------
    st.subheader("Dataset Summary")

    summary_table = pd.DataFrame({
        "Metric": ["Total Records", "Total Columns", "Missing Values"],
        "Value": [df.shape[0], df.shape[1], df.isnull().sum().sum()]
    })

    st.dataframe(summary_table, use_container_width=True)

    st.divider()

    # ---------------- COLUMN INFO ----------------
    st.subheader("Column Information")
    st.dataframe(
        pd.DataFrame({
            "Column Name": df.columns,
            "Data Type": df.dtypes.astype(str)
        })
    )

    st.divider()

    # ---------------- SAMPLE DATA ----------------
    st.subheader("Sample Records")
    st.dataframe(df.head(8))

    st.divider()

    # ==================================================
    # ANALYTICAL VISUALS
    # ==================================================

    # -------- Row 1: Violation Type & Vehicle Type --------
    st.subheader("Violation and Vehicle Analysis")

    c1, c2 = st.columns(2)

    with c1:
        fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
        vc = df["Violation_Type"].value_counts().head(8)
        sns.barplot(x=vc.values, y=vc.index, palette="Spectral", ax=ax)
        ax.set_title("Top Violation Types", fontsize=12, fontweight="bold")
        ax.set_xlabel("Number of Violations", fontsize=10, fontweight="bold")
        ax.set_ylabel("Violation Type", fontsize=10, fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig)

    with c2:
        fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
        vt = df["Vehicle_Type"].value_counts().head(8)
        sns.barplot(x=vt.values, y=vt.index, palette="Blues_r", ax=ax)
        ax.set_title("Violations by Vehicle Type", fontsize=12, fontweight="bold")
        ax.set_xlabel("Number of Violations", fontsize=10, fontweight="bold")
        ax.set_ylabel("Vehicle Type", fontsize=10, fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig)

    st.divider()

    # -------- Row 2: Location & Fine Distribution --------
    st.subheader("Location and Fine Analysis")

    c1, c2 = st.columns(2)

    with c1:
        location_column = next(
            (c for c in ["State", "City", "Location"] if c in df.columns),
            None
        )

        if location_column:
            fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
            lc = df[location_column].value_counts().head(8)
            sns.barplot(x=lc.values, y=lc.index, palette="Greens_r", ax=ax)
            ax.set_title("Top Locations by Violations", fontsize=12, fontweight="bold")
            ax.set_xlabel("Number of Violations", fontsize=10, fontweight="bold")
            ax.set_ylabel("Location", fontsize=10, fontweight="bold")
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.info("Location data not available.")

    with c2:
        fine_cols = [c for c in df.columns if "fine" in c.lower()]
        if fine_cols:
            fine_col = fine_cols[0]
            fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
            sns.histplot(df[fine_col], bins=30, kde=True, color="purple", ax=ax)
            ax.set_title("Fine Amount Distribution", fontsize=12, fontweight="bold")
            ax.set_xlabel("Fine Amount", fontsize=10, fontweight="bold")
            ax.set_ylabel("Frequency", fontsize=10, fontweight="bold")
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.info("Fine data not available.")

    st.divider()

    # -------- Row 3: Time of Day Analysis (Compact with Explanation) --------
    st.subheader("Time of Day Violation Analysis")

    if "Time_of_Day" in df.columns:

        c1, c2 = st.columns([2, 3])

        with c1:
            fig, ax = plt.subplots(figsize=(5.5, 3.4))

            time_counts = df["Time_of_Day"].value_counts()

            sns.barplot(
                x=time_counts.index,
                y=time_counts.values,
                palette="coolwarm",
                ax=ax
            )

            ax.set_title(
                "Traffic Violations by Time of Day",
                fontsize=12,
                fontweight="bold"
            )
            ax.set_xlabel(
                "Time of Day",
                fontsize=10,
                fontweight="bold"
            )
            ax.set_ylabel(
                "Number of Violations",
                fontsize=10,
                fontweight="bold"
            )
            ax.tick_params(labelsize=9)

            plt.tight_layout()
            st.pyplot(fig)

        with c2:
            st.markdown(
                """
                <div style="font-size:16px; line-height:1.7">
                    <b>Interpretation</b>
                    <ul>
                        <li>Traffic violations are not evenly distributed throughout the day.</li>
                        <li>Higher violation counts are observed during peak activity periods such as 
                            <b>evening and night</b>.</li>
                        <li>Reduced visibility, fatigue, and lower enforcement presence may contribute 
                            to increased violations during late hours.</li>
                        <li>This analysis supports time-specific enforcement and awareness strategies.</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )

    else:
        st.info("Time of day data not available.")

    st.divider()

    # ---------------- KEY OBSERVATIONS ----------------
    st.subheader("Key Observations")

    st.markdown(
        """
        - Traffic violations are concentrated in specific locations and time periods  
        - Certain vehicle categories contribute more frequently to violations  
        - Fine amount distribution indicates varying severity levels  
        - Monthly trends suggest seasonal influence on traffic behavior  
        """
    )

    # ---------------- CONCLUSION ----------------
    st.subheader("Conclusion")

    st.markdown(
        """
        This analytical report highlights key traffic violation patterns
        and supports data-driven traffic management and enforcement planning.
        """
    )

# download the dataset used
    st.markdown('---')
    st.markdown("""
    <h4 style="display:flex; align-items:center; gap:8px;">
        <i class="bi bi-cloud-arrow-down-fill" style="color:#A08692;"></i>
        Download Dataset Used in Analysis
    </h4>
    """, unsafe_allow_html=True)

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="Indian_Traffic_Violations_Dataset.csv",
        mime="text/csv"
    )


