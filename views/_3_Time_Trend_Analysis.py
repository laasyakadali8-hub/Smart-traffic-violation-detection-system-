import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import cm
from matplotlib.patches import Rectangle
import warnings
warnings.filterwarnings('ignore')

def app(df):
    from utils import load_global_css, bootstrap_icon
    load_global_css()

    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df["Year"] = df["Date"].dt.year

    # ---------------- PAGE TITLE ----------------
    st.markdown(f"""
    {bootstrap_icon('graph-up', 28)}<span style='color:#E8DED9; font-size:28px; font-weight:700; vertical-align:middle;'> Time and Trend Analysis</span>
    <p style='text-align:center;color:#A08692;font-size:16px; margin-top:6px;'>
    Analyze traffic violations over time to identify peak hours, high-risk days, and yearly trends for better planning and monitoring.
    </p>
    """, unsafe_allow_html=True)

    st.divider()

    # ---------------- OVERVIEW ----------------
    total_violations = len(df)
    peak_hour = df["Hour"].mode()[0]
    peak_day = df["Day_of_Week"].mode()[0]
    most_common_violation = df['Violation_Type'].mode()[0]

    # ---------------- KEY INSIGHTS ----------------
    st.subheader("Key Analytical Insights")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class='reco-card'>
        <b>Peak Violation Time</b><br>
        Most traffic violations happen around {peak_hour}:00 hours. 
        This time has heavy traffic and needs extra monitoring.
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class='reco-card'>
        <b>High-Risk Day</b><br>
        {peak_day} has the highest number of violations.
        Traffic rules should be strictly enforced on this day.
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class='reco-card'>
        <b>Overall Trend</b><br>
        Traffic violations show a regular pattern.
        Better awareness and preventive steps can help reduce them.
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ---------------- VIOLATION TRENDS ----------------
    st.markdown(f"{bootstrap_icon('calendar3',18)}{bootstrap_icon('bar-chart',18)} <span style='color:#E8DED9; font-weight:700;'>Violation Trends Over Time</span>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # Monthly Trend
    with col1:
        with st.expander("Monthly Violation Trend", expanded=True):
            selected_year = st.selectbox(
                "Select Year",
                sorted(df["Year"].dropna().unique())
            )
            year_df = df[df["Year"] == selected_year]
            monthly = year_df.groupby(year_df["Date"].dt.month).size().reindex(range(1, 13), fill_value=0)
            months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(months, monthly.values, marker="o", linewidth=3, color="#f0f921", markersize=8)
            ax.set_xlabel("Month", color="#E8DED9", fontsize=12, fontweight='bold')
            ax.set_ylabel("Violations", color="#E8DED9", fontsize=12, fontweight='bold')
            ax.grid(True, linestyle="--", alpha=0.5, color="#4B5563")
            ax.set_facecolor('#2A2533')
            fig.patch.set_facecolor('none')
            
            # Fix label visibility
            ax.tick_params(axis='both', colors='#F5F5F5', labelsize=12)
            for spine in ax.spines.values():
                spine.set_color('#4B5563')
            
            st.pyplot(fig)
            plt.clf()

    with col2:
        with st.expander("Yearly Violation Trend", expanded=True):

            yearly = df.groupby("Year").size().reset_index(name="Violations")

            min_year = int(yearly["Year"].min())
            max_year = int(yearly["Year"].max())

            year_range = st.slider(
                "Select Year Range",
                min_year,
                max_year,
                (min_year, max_year),
            )

            filtered_year = yearly[
                (yearly["Year"] >= year_range[0]) &
                (yearly["Year"] <= year_range[1])
            ]

            fig, ax = plt.subplots(figsize=(8, 4))



            # Line on top
            ax.plot(
                filtered_year["Year"],
                filtered_year["Violations"],
                linewidth=3,
                color='#fde725',
                marker="o",
                markersize=8
            )

            ax.set_xlabel("Year", color="#E8DED9", fontsize=12, fontweight='bold')
            ax.set_ylabel("Number of Violations", color="#E8DED9", fontsize=12, fontweight='bold')
            ax.set_title("Traffic Violations", color="#E8DED9", fontsize=13, fontweight='bold')
            ax.grid(True, linestyle="--", alpha=0.5, color="#4B5563")
            ax.set_facecolor('#2A2533')
            fig.patch.set_facecolor('none')
            
            # Fix label visibility
            ax.tick_params(axis='both', colors='#F5F5F5', labelsize=12)
            for spine in ax.spines.values():
                spine.set_color('#4B5563')

            st.pyplot(fig)
            plt.clf()

    # ------------------HOURLY HISTOGRAM --------
    st.markdown('---')
    st.markdown(f"{bootstrap_icon('clock',20)} <span style='color:#E8DED9; font-size:18px; font-weight:700;'>Violations by Hour of Day</span>", unsafe_allow_html=True)
    with st.expander("Violations by Hour of Day", expanded=True):

        # ---- Hour slider for this graph only ----
        hour_range = st.slider(
            "Select Hour Range for Hourly Analysis",
            min_value=0,
            max_value=23,
            value=(0, 23),
            step=1,
            key="hour_hist_slider"
        )

        # Filter data using slider
        df_hour = df[
            (df["Hour"] >= hour_range[0]) &
            (df["Hour"] <= hour_range[1])
        ]

        # ----  hours Plot ----
        fig, ax = plt.subplots(figsize=(12, 5))
        color = sns.color_palette("magma", 1)[0]

        sns.histplot(
            data=df_hour,
            x="Hour",
            bins=24,
            color="#3b528b",
            edgecolor="#fde725",
            kde=True,
            line_kws={"linewidth": 2, "color": "#f0f921"},
            ax=ax
        )

        ax.set_xlabel("Hour", color="#E8DED9", fontsize=12, fontweight='bold')
        ax.set_ylabel("Number of Violations", color="#E8DED9", fontsize=12, fontweight='bold')
        ax.set_title(f"Hourly Violation Pattern ({hour_range[0]}–{hour_range[1]} hrs)", color="#E8DED9", fontsize=13, fontweight='bold')
        ax.set_xticks(range(0, 24))
        ax.set_facecolor('#2A2533')
        fig.patch.set_facecolor('none')
        
        # Fix label visibility
        ax.tick_params(axis='both', colors='#F5F5F5', labelsize=12)
        for spine in ax.spines.values():
            spine.set_color('#4B5563')

        st.pyplot(fig)
        plt.clf()

        st.info(f"💡 Analysis Tip: The peak violation hours are around {peak_hour}:00 hrs. Consider extra monitoring during these times.")
        
    st.divider()

    # --------------- DAY-WISE OVERVIEW ----------------
    st.markdown(f"{bootstrap_icon('calendar3',18)} <span style='color:#E8DED9; font-size:18px; font-weight:700;'>Day-wise Violations Overview</span>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        with st.expander("Day Distribution", expanded=True):

            day_counts = df["Day_of_Week"].value_counts()

            colors = [
                "#440154", "#3b528b", "#55ae92",
                "#fde725", "#cb4679", "#f8953b", "#7f00ff"
            ]

            fig, ax = plt.subplots(figsize=(4, 16))
            ax.pie(
                day_counts,
                labels=day_counts.index,
                autopct="%1.0f%%",
                startangle=90,
                colors=colors,
                textprops={'color': '#F5F5F5', 'fontsize': 12, 'fontweight': 'bold'}
            )
            ax.set_title("Violations by Day of Week", color="#E8DED9", fontweight='bold')
            fig.patch.set_facecolor('none')

            st.pyplot(fig)
            plt.clf()

    with col2:
        with st.expander("Weekday vs Weekend", expanded=True):

            # Create DayType
            df_hour["DayType"] = df_hour["Day_of_Week"].apply(
                lambda x: "Weekend" if x in ["Saturday", "Sunday"] else "Weekday"
            )

            # Violation Type Filter
            violation_options = sorted(df_hour["Violation_Type"].unique())

            selected_violations = st.multiselect(
                "Select Violation Types",
                options=violation_options,
                default=[],  # ✅ empty default
                key="violation_filter_weekday_weekend"
            )

            # ✅ SAFE FILTERING
            filtered_df = df_hour.copy()

            if selected_violations:
                filtered_df = filtered_df[
                    filtered_df["Violation_Type"].isin(selected_violations)
                ]
            # Crosstab
            stacked_data = pd.crosstab(
                filtered_df["DayType"],
                filtered_df["Violation_Type"]
            )

            fig, ax = plt.subplots(figsize=(10, 6))

            stacked_data.plot(
                kind="bar",
                stacked=True,
                ax=ax,
                width=0.5,
                color=['#440154', '#3b528b', '#55ae92', '#fde725', '#cb4679']
            )

            ax.set_xlabel("Day Type", fontsize=12, color="#F5F5F5", fontweight='bold')
            ax.set_ylabel("Violations", fontsize=12, color="#F5F5F5", fontweight='bold')
            ax.set_title("Weekday vs Weekend Violations", fontsize=13, color="#E8DED9", fontweight='bold')

            ax.legend(
                title="Violation Type",
                fontsize=10,
                title_fontsize=11,
                loc="upper right",
                labelcolor='#F5F5F5',
                facecolor='#2A2533',
                edgecolor='#F5F5F5',
                framealpha=0.95
            )

            ax.set_facecolor('#2A2533')
            fig.patch.set_facecolor('none')

            # Fix all label visibility
            ax.tick_params(axis='both', colors='#F5F5F5', labelsize=12)
            for spine in ax.spines.values():
                spine.set_color('#4B5563')

            # Rotate x-axis labels for readability
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', color='#F5F5F5', fontsize=12)
            plt.setp(ax.yaxis.get_majorticklabels(), color='#F5F5F5', fontsize=12)

            # Add margins to prevent label clipping
            plt.subplots_adjust(bottom=0.2, left=0.1)
            plt.tight_layout()
            st.pyplot(fig, width="content")
            plt.clf()

    # ------------ TIME OF DAY ----------------
    st.markdown('---')
    st.markdown(f"{bootstrap_icon('clock',18)} <span style='color:#E8DED9; font-size:18px; font-weight:700;'>Violations by Time of Day</span>", unsafe_allow_html=True)

    def time_of_day(hour):
        if 5 <= hour < 12:
            return "Morning"
        elif 12 <= hour < 17:
            return "Afternoon"
        elif 17 <= hour < 21:
            return "Evening"
        else:
            return "Night"

    df_hour["TimeOfDay"] = df_hour["Hour"].apply(time_of_day)
    time_data = pd.crosstab(df_hour["TimeOfDay"], df_hour["Violation_Type"])
    
    if not time_data.empty:
        with st.expander("Violations by Time of Day", expanded=True):
            # Ensure index is not empty
            if len(time_data.index) > 0:
                selected_time = st.selectbox("Select Time of Day", time_data.index, key="time_selectbox")
                selected_values = time_data.loc[selected_time]

            col1, col2 = st.columns([2, 1])

            # GRAPH CARD
            with col1:
                plt.rcParams['text.color'] = '#F5F5F5'
                fig, ax = plt.subplots(figsize=(8, 4))
                
                # Use plasma palette for brighter colors
                n_violations = len(selected_values)
                palette = sns.color_palette('plasma', n_colors=n_violations)

                # Add a subtle shaded highlight behind the bars (keeps bars visible)
                ymax = selected_values.max() if n_violations > 0 else 1
                ax.add_patch(Rectangle((-0.5, 0), len(selected_values), ymax * 1.15, facecolor='#E1C8C2', alpha=0.06, zorder=0, edgecolor='none'))

                sns.barplot(x=selected_values.index, y=selected_values.values, palette=palette, ax=ax, zorder=2)
                ax.set_xlabel("Violation Type", color="#F5F5F5", fontsize=13, fontweight='bold')
                ax.set_ylabel("Violations", color="#F5F5F5", fontsize=13, fontweight='bold')
                ax.set_facecolor('#2A2533')
                fig.patch.set_facecolor('none')
                
                # Explicitly set X-axis labels with violation type names
                ax.set_xticklabels(
                    ax.get_xticklabels(),
                    color='#F5F5F5',
                    rotation=45,
                    ha='right',
                    fontsize=11,
                    fontweight='bold'
                )
                
                # Fix ALL label visibility with bright white
                ax.tick_params(axis='both', colors='#F5F5F5', labelsize=12)
                ax.xaxis.label.set_color('#F5F5F5')
                ax.yaxis.label.set_color('#F5F5F5')
                
                # Add spines for better visibility
                for spine in ax.spines.values():
                    spine.set_color('#4B5563')
                
                plt.xticks(rotation=45, ha='right', color='#F5F5F5', fontsize=12)
                plt.yticks(color='#F5F5F5', fontsize=12)
                plt.subplots_adjust(bottom=0.2, left=0.1)
                plt.tight_layout()
                st.pyplot(fig)
                plt.clf()

            # STATS CARD
            with col2:
                st.markdown("### Time-of-Day Statistics")
                total_cases = int(selected_values.sum())
                max_violation = selected_values.idxmax()
                max_count = int(selected_values.max())
                avg_cases = round(selected_values.mean(), 2)
                st.markdown(f"""
                **Selected Time:** {selected_time}  
                **Total Violations:** {total_cases}  
                **Most Common Violation:** {max_violation} ({max_count})  
                **Average per Violation Type:** {avg_cases}
                """)
    else:
        st.warning("No time-of-day data available for the selected hour range.")

    # -------- FINE TREND  ----------------
    st.divider()
    st.markdown(f"{bootstrap_icon('cash',22)} <span style='color:#E8DED9; font-size:18px; font-weight:700;'>Year-wise Average Fine Trend</span>", unsafe_allow_html=True)

    # Year filter
    year_filter = st.multiselect(
        "Filter by Year",
        options=sorted(df["Year"].dropna().unique())
    )

    # Show graph only when filter is applied
    # ✅ Default behavior — show all years if no filter selected
    if year_filter:
        filtered_df = df[df["Year"].isin(year_filter)]
        title_suffix = " (Filtered Years)"
    else:
        filtered_df = df.copy()
        title_suffix = " (All Years)"

    fine_trend = (
        filtered_df
        .groupby("Year")["Fine_Amount"]
        .mean()
        .reset_index()
    )

    col1, col2 = st.columns([2, 1])

    with col1:
            plt.rcParams['text.color'] = '#F5F5F5'
            fig, ax = plt.subplots(figsize=(9, 4))

            sns.lineplot(
                data=fine_trend,
                x="Year",
                y="Fine_Amount",
                marker="o",
                linewidth=3,
                ax=ax,
                color="#fde725"
            )

            ax.set_title(f"Average Fine Amount{title_suffix}", color="#E8DED9", fontsize=14, fontweight='bold')
            ax.set_xlabel("Year", color="#F5F5F5", fontsize=14, fontweight='bold')
            ax.set_ylabel("Average Fine (₹)", color="#F5F5F5", fontsize=14, fontweight='bold')
            ax.set_xticks(fine_trend["Year"])
            ax.grid(True, alpha=0.3, color="#4B5563")
            ax.set_facecolor('#2A2533')
            fig.patch.set_facecolor('none')

            # Fix all axis visibility and labels
            ax.tick_params(axis='both', colors='#F5F5F5', labelsize=14)
            ax.spines['bottom'].set_color('#E8DED9')
            ax.spines['left'].set_color('#E8DED9')
            ax.spines['top'].set_color('#2A2533')
            ax.spines['right'].set_color('#2A2533')
            ax.spines['bottom'].set_linewidth(1.5)
            ax.spines['left'].set_linewidth(1.5)

            st.pyplot(fig)
            plt.clf()


    with col2:
        st.markdown("### Summary")
        st.dataframe(
            fine_trend.style.format({"Fine_Amount": "₹{:.2f}"}),
            hide_index=True
        )
        if st.button("Show Max Fine Year"):
            max_fine_year = fine_trend.loc[fine_trend["Fine_Amount"].idxmax(), "Year"]
            st.success(f"Year with highest average fine: {int(max_fine_year)}")

    # -------- FINAL INSIGHTS & RECOMMENDATIONS ----------------
    st.markdown("---")
    st.markdown("### Strategic Recommendations")

    # Custom styled recommendations box using beige palette (with lightbulb SVG)
    st.markdown(f"""
    <div style='background: rgba(225,200,194,0.12); border: 2px solid #A08692; border-radius: 10px; padding: 20px; box-shadow: 0 0 18px rgba(160,134,146,0.12); color: #E8DED9;'>
        <div style='font-size:16px; margin-bottom:8px;'>{bootstrap_icon('lightbulb-fill',18)}<b style='color:#A08692; margin-right:8px;'>Actionable Insights</b></div>
        <div style='line-height:1.6;'>
            • Focus monitoring during the busiest hours around <b>{peak_hour}</b>:00 and on <b>{peak_day}</b>s.<br>
            • Pay extra attention to the most common violation: <b>{most_common_violation}</b>.<br>
            • Plan awareness campaigns or enforcement in months or years where violations are increasing.<br>
            • Use violation patterns to place resources efficiently and reduce accidents.
        </div>
    </div>
    """, unsafe_allow_html=True)