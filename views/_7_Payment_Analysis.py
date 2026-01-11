# =====================================================
# SMART TRAFFIC VIOLATION – PAYMENT ANALYSIS DASHBOARD

# =====================================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")

def app(df):
    from utils import load_global_css
    load_global_css()

    # ---------------- TIME OF DAY ----------------
    df["Time"] = pd.to_datetime(df["Time"], errors="coerce")

    def categorize_time(hour):
        if 5 <= hour < 12:
            return "Morning"
        elif 12 <= hour < 17:
            return "Afternoon"
        elif 17 <= hour < 21:
            return "Evening"
        else:
            return "Night"

    df["Time_of_Day"] = df["Time"].dt.hour.apply(categorize_time)

    # ---------------- TITLE ----------------
    st.markdown("""
        <h2 style="text-align:center; display:flex; justify-content:center; align-items:center; gap:12px;">
            <i class="bi bi-cash-stack" style="font-size:28px; color:#22c55e;"></i>
            Payment Analysis Dashboard
        </h2>

        <p style="text-align:center; color:gray; margin-top:4px;">
            Traffic Violation Payment & Revenue Insights
        </p>
        """, unsafe_allow_html=True)
    st.caption(
        "Insight: This dashboard provides a data-driven overview of traffic violation payments, "
        "helping authorities analyze revenue, compliance behavior, and enforcement effectiveness."
    )
    st.divider()

    # =====================================================
    # GLOBAL FILTERS
    # =====================================================
    st.subheader("Global Filters")
    st.caption(
        "Insight: Global filters dynamically update all KPIs and visualizations, enabling focused "
        "analysis based on payment method, location, and time of day."
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        pay_global = st.multiselect(
            "Payment Method",
            df["Payment_Method"].unique(),
            default=[],
            key="pay_global"
        )

    with c2:
        loc_global = st.multiselect(
            "Location",
            df["Location"].unique(),
            default=[],
            key="loc_global"
        )

    with c3:
        time_global = st.multiselect(
            "Time of Day",
            df["Time_of_Day"].unique(),
            default=[],
            key="time_global"
        )
    global_df = df.copy()

    if pay_global:
        global_df = global_df[global_df["Payment_Method"].isin(pay_global)]

    if loc_global:
        global_df = global_df[global_df["Location"].isin(loc_global)]

    if time_global:
        global_df = global_df[global_df["Time_of_Day"].isin(time_global)]

    # =====================================================
    # KPI SECTION
    # =====================================================
    total_revenue = global_df["Fine_Amount"].sum()
    avg_fine = global_df["Fine_Amount"].mean()
    total_cases = len(global_df)

    k1, k2, k3 = st.columns(3)

    k1.metric("Total Revenue (₹)", f"{total_revenue:,.0f}")
    k2.metric("Average Fine (₹)", f"{avg_fine:,.0f}")
    k3.metric("Total Violations", total_cases)

    st.caption(
        "Insight: KPIs summarize overall payment performance. Total Revenue reflects collection efficiency, "
        "Average Fine indicates violation severity, and Total Violations show enforcement volume."
    )

    st.divider()

    # -----------------------------------------------------
    # CREATE RISK SCORE
    # -----------------------------------------------------
    global_df = global_df.copy()
    global_df["Risk_Score"] = (
        global_df["Fine_Amount"] / global_df["Fine_Amount"].max()
    ) * 100

    st.caption(
        "Insight: Risk Score is a derived metric based on fine severity, helping identify "
        "payment methods associated with high-risk or serious violations."
    )

    # =====================================================
    # PAYMENT ANALYSIS FILTERS
    # =====================================================
    st.subheader("Payment Analysis Filters")

    pay_filter = st.multiselect(
        "Select Payment Method",
        global_df["Payment_Method"].unique(),
        default=[],
        key="pay_graphs"
    )
    g1_df = global_df.copy()

    # ✅ BASE DATA (IMPORTANT)
    if pay_filter:
        g1_df = global_df[global_df["Payment_Method"].isin(pay_filter)]
    else:
        g1_df = global_df.copy()
    col1, col2 = st.columns(2, gap="large")

    # =====================================================
    # GRAPH 1 — PAYMENT METHOD DISTRIBUTION
    # =====================================================
    with col1:
        st.markdown("#### Payment Method Distribution")
        payment_counts = g1_df["Payment_Method"].value_counts()

        fig, ax = plt.subplots(figsize=(4.6, 3.4))
        sns.barplot(
            x=payment_counts.index,
            y=payment_counts.values,
            palette=["#1F4ED8", "#FF8C00", "#2E8B57", "#C0392B"],
            ax=ax
        )

        ax.set_xlabel("Payment Method", fontweight="bold")
        ax.set_ylabel("Transactions", fontweight="bold")
        ax.set_title("Payment Method Distribution", fontweight="bold")
        sns.despine()
        st.pyplot(fig)

        st.caption(
            "Insight: This bar chart shows the frequency of each payment method. "
            "Higher usage indicates preferred payment modes."
        )

        with st.expander("View Filtered Data"):
            st.dataframe(g1_df[["Payment_Method", "Fine_Amount"]], use_container_width=True)

    # =====================================================
    # GRAPH 2 — FINE AMOUNT SEVERITY
    # =====================================================
    with col2:
        st.markdown("#### Fine Amount Severity")

        g2_df = g1_df.copy()

        fig, ax = plt.subplots(figsize=(4.6, 3.4))
        sns.boxplot(
            data=g2_df,
            x="Payment_Method",
            y="Fine_Amount",
            palette="Set2",
            ax=ax
        )

        ax.set_xlabel("Payment Method", fontweight="bold")
        ax.set_ylabel("Fine Amount (₹)", fontweight="bold")
        ax.set_title("Fine Amount Distribution", fontweight="bold")
        sns.despine()
        st.pyplot(fig)

        st.caption(
            "Insight: Wider boxes and higher medians indicate severe violations."
        )

        with st.expander("View Filtered Data"):
            st.dataframe(g2_df[["Payment_Method", "Fine_Amount"]], use_container_width=True)

    # =====================================================
    # RISK & FINE ANALYSIS
    # =====================================================
    st.markdown("---")
    st.markdown("## Risk & Fine Analysis by Payment Method")

    col1, col2 = st.columns(2, gap="medium")

    # ---------------- RISK SCORE ----------------
    with col1:
        st.markdown("### Average Risk Score by Payment Method")

        pay_filter_risk = st.multiselect(
            "Payment Method",
            global_df["Payment_Method"].unique(),
            default=[],
            key="risk_lollipop"
        )

        risk_df = global_df.copy()

        if pay_filter_risk:
            risk_df = risk_df[risk_df["Payment_Method"].isin(pay_filter_risk)]

        avg_risk = (
            risk_df
            .groupby("Payment_Method")["Risk_Score"]
            .mean()
            .sort_values()
        )
        fig1, ax1 = plt.subplots(figsize=(5.0, 3.6))
        ax1.hlines(avg_risk.index, 0, avg_risk.values, color="#FF8C00", linewidth=3)
        ax1.plot(avg_risk.values, avg_risk.index, "o", color="#1F4ED8", markersize=8)
        ax1.set_xlabel("Average Risk Score", fontweight="bold")
        ax1.set_ylabel("Payment Method", fontweight="bold")
        ax1.set_title("Average Risk Score by Payment Method", fontweight="bold")
        sns.despine()
        st.pyplot(fig1)

        st.caption(
            "Insight: Higher risk scores are associated with serious traffic violations."
        )

    # ---------------- LINE CHART ----------------
    with col2:
        st.markdown("### Trend of Average Fine by Payment Method")

        pay_filter_fine = st.multiselect(
            "Payment Method",
            global_df["Payment_Method"].unique(),
            default=[],
            key="fine_line"
        )
        fine_df = global_df.copy()
        if pay_filter_fine:
            fine_df = fine_df[fine_df["Payment_Method"].isin(pay_filter_fine)]

        avg_fine_df = fine_df.groupby("Payment_Method")["Fine_Amount"].mean().reset_index()

        fig2, ax2 = plt.subplots(figsize=(5.0, 3.6))
        ax2.plot(
            avg_fine_df["Payment_Method"],
            avg_fine_df["Fine_Amount"],
            marker="o"
        )

        ax2.set_title("Average Fine Trend by Payment Method", fontweight="bold")
        ax2.set_xlabel("Payment Method", fontsize=12, fontweight="bold")
        ax2.set_ylabel("Average Fine (₹)", fontsize=12, fontweight="bold")
        sns.despine()
        st.pyplot(fig2)

        st.caption(
            "Insight: Line chart shows comparative trend of average fine amounts."
        )

    # =====================================================
    #Payment Method with time of day and violation type
    # =====================================================
    st.markdown("---")
    col1, col2 = st.columns(2, gap="large")

    # ✅ STEP 1: define heat_left FIRST
    heat_left = pd.crosstab(
        global_df["Payment_Method"],
        global_df["Time_of_Day"],
        normalize="index"
    ) * 100
    bar_df = (
        global_df
        .groupby(["Violation_Type", "Payment_Method"])
        .size()
        .reset_index(name="Count")
    )

    # ================= LEFT: HEATMAP =================
    with col1:
        st.markdown(
            "<h2 style='font-size:28px;'>Payment Method vs Time of Day</h2>",
            unsafe_allow_html=True
        )

        fig, ax = plt.subplots(figsize=(6.0, 4.2))

        sns.heatmap(
            heat_left,
            annot=True,
            fmt=".1f",
            cmap="Blues",
            square=False,
            linewidths=0.4,
            linecolor="white",
            cbar=False,
            ax=ax
        )

        ax.set_xlabel("Time of Day", fontsize=11, fontweight="bold")
        ax.set_ylabel("Payment Method", fontsize=11, fontweight="bold")

        plt.subplots_adjust(top=0.92, bottom=0.15)
        st.pyplot(fig)

        st.write(
            "<span style='color:gray;font-size:13px;'>"
            "Insight: Reveals peak payment activity across different times of day."
            "</span>",
            unsafe_allow_html=True
        )

    # ================= RIGHT: BAR GRAPH =================
    with col2:
        st.markdown(
            "<h2 style='font-size:28px;'>Violation Type vs Payment Method</h2>",
            unsafe_allow_html=True
        )

        fig, ax = plt.subplots(figsize=(6.0, 6.0))

        sns.barplot(
            data=bar_df,
            y="Violation_Type",
            x="Count",
            hue="Payment_Method",
            palette="Blues",
            ax=ax
        )

        ax.legend(
            title="Payment Method",
            fontsize=8,
            title_fontsize=9,
            loc="center left",
            bbox_to_anchor=(1.02, 0.5),
            frameon=False
        )

        ax.set_xlabel("Number of Violations", fontsize=11, fontweight="bold")
        ax.set_ylabel("Violation Type", fontsize=11, fontweight="bold")

        sns.despine(left=True, bottom=True)
        plt.subplots_adjust(top=0.92, bottom=0.15, right=0.78)

        st.pyplot(fig)

        st.write(
            "<span style='color:gray;font-size:13px;'>"
            "Insight: Horizontal bar chart comparing payment method usage across violation types."
            "</span>",
            unsafe_allow_html=True
        )

