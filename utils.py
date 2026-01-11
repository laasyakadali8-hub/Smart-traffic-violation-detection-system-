import pandas as pd
import streamlit as st
import os

def load_data():
    df = pd.read_csv("Indian_Traffic_Violations_Dataset.csv")

    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    return df


def apply_filters(
    df,
    date_range,
    selected_location,
    selected_violation,
    selected_vehicle,
    selected_gender,
    age_range
):
    filtered_df = df.copy()

    # Date filter
    if date_range[0] and date_range[1] and 'Date' in df.columns:
        filtered_df = filtered_df[
            (filtered_df['Date'].dt.date >= date_range[0]) &
            (filtered_df['Date'].dt.date <= date_range[1])
        ]

    # Location filter
    if "All" not in selected_location and 'Location' in df.columns:
        filtered_df = filtered_df[filtered_df['Location'].isin(selected_location)]

    # Violation filter
    if "All" not in selected_violation and 'Violation_Type' in df.columns:
        filtered_df = filtered_df[filtered_df['Violation_Type'].isin(selected_violation)]

    # Vehicle filter
    if "All" not in selected_vehicle and 'Vehicle_Type' in df.columns:
        filtered_df = filtered_df[filtered_df['Vehicle_Type'].isin(selected_vehicle)]

    # Gender filter
    if "All" not in selected_gender and 'Driver_Gender' in df.columns:
        filtered_df = filtered_df[filtered_df['Driver_Gender'].isin(selected_gender)]

    # Age filter
    if 'Driver_Age' in df.columns:
        filtered_df = filtered_df[
            (filtered_df['Driver_Age'] >= age_range[0]) &
            (filtered_df['Driver_Age'] <= age_range[1])
        ]

    return filtered_df


def load_global_css():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    css_path = os.path.join(base_dir, "styles", "main.css")
    # Bootstrap Icons CDN
    st.markdown("""
        <link rel="stylesheet"
         href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
        <style>
            .bi {
                display: inline-block;
                vertical-align: -0.125em;
                fill: currentColor;
            }
        </style>
        """, unsafe_allow_html=True)
    with open("styles/main.css",encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def apply_theme():
    """Premium Purple Theme with Optimized Color Gradient Palette.
    
    Color progression: #0F0D15 → #1F1A28 → #2A2533 → #807A81 → #A08692 → #E8DED9
    Glassmorphic design with backdrop blur effects.
    """
    st.markdown(
        """
    <style>
    /* REMOVE STREAMLIT TOP WHITE HEADER */
header {
    visibility: hidden;
    height: 0px;
}

/* REMOVE EXTRA TOP SPACE */
.block-container {
    padding-top: 0rem !important;
}

    :root {
        --dark-navy: #0F0D15;
        --dark-purple: #1F1A28;
        --mid-purple: #2A2533;
        --primary: #807A81;
        --accent1: #6C5C7C;
        --accent2: #A08692;
        --light-beige: #E1C8C2;
        --text-white: #E8DED9;
        --bg-input: #2A2533;
    }

    /* ===== FULL PAGE BACKGROUND ===== */
    html, body {
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
        background: linear-gradient(180deg,
            #0F0D15 0%,
            #1F1A28 25%,
            #2A2533 50%,
            #1F1A28 75%,
            #0F0D15 100%) fixed !important;
        min-height: 100vh !important;
    }

    /* Main app background */
    .stApp {
        background: transparent !important;
        min-height: 100vh !important;
        position: relative !important;
        color: var(--text-white) !important;
    }

    /* Main content area */
    .main .block-container {
        max-width: 1200px !important;
        margin: 0 auto !important;
        padding: 2rem 2rem !important;
    }

    /* ===== GLOBAL TEXT ===== */
    .stApp, .stApp *, body, html {
        color: var(--text-white) !important;
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-white) !important;
        font-weight: 700 !important;
    }

    /* Paragraphs and text */
    p, span, div, label {
        color: var(--text-white) !important;
    }

    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1F1A28 0%, #2A2533 100%) !important;
        border-right: 2.5px solid #A08692 !important;
        box-shadow: inset -8px 0 32px rgba(0,0,0,0.5) !important;
    }

    section[data-testid="stSidebar"] * {
        color: var(--text-white) !important;
    }

    section[data-testid="stSidebar"] .css-1d391kg,
    section[data-testid="stSidebar"] .block-container {
        padding-top: 20px !important;
    }

    /* Selected sidebar item */
    section[data-testid="stSidebar"] label[data-selected="true"] {
        background: rgba(160,134,146,0.2) !important;
        border-left: 4px solid var(--accent2) !important;
        border-radius: 8px !important;
    }

    /* ===== METRIC BOXES ===== */
    [data-testid="metric-container"], [data-testid="stMetric"] {
        background: linear-gradient(135deg,
            rgba(42,37,51,0.95) 0%,
            rgba(32,27,41,0.95) 100%) !important;
        backdrop-filter: blur(25px) !important;
        -webkit-backdrop-filter: blur(25px) !important;
        border: 2px solid #A08692 !important;
        box-shadow: 
            0 20px 60px rgba(0,0,0,0.6),
            inset 0 1px 0 rgba(225,200,194,0.15) !important;
        padding: 20px !important;
        border-radius: 16px !important;
    }

    [data-testid="metric-container"] [data-testid="stMetricLabel"],
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: var(--text-white) !important;
    }

    /* ===== CARDS & CONTAINERS ===== */
    .glass-card, .card-container, .reco-card, .project-card {
        background: linear-gradient(135deg,
            rgba(42,37,51,0.92) 0%,
            rgba(32,27,41,0.92) 100%) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 2px solid #A08692 !important;
        box-shadow: 
            0 12px 40px rgba(0,0,0,0.5),
            inset 0 1px 0 rgba(225,200,194,0.1) !important;
        border-radius: 14px !important;
        padding: 18px 20px !important;
        margin-bottom: 16px !important;
        color: var(--text-white) !important;
    }

    .reco-card {
        border-left: 5px solid var(--primary) !important;
    }

    /* ===== EXPANDERS ===== */
    .stExpander, .streamlit-expanderHeader {
        background: rgba(42,37,51,0.88) !important;
    }

    .stExpander .stExpanderHeader {
        background: linear-gradient(135deg,
            rgba(42,37,51,0.95) 0%,
            rgba(32,27,41,0.95) 100%) !important;
        border: 2px solid #A08692 !important;
        border-bottom: none !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 12px 16px !important;
    }

    .stExpanderContent, .stExpander > div[role="region"] {
        background: rgba(32,27,41,0.88) !important;
        border: 2px solid #A08692 !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
        padding: 16px !important;
    }

    /* ===== BUTTONS ===== */
    div.stButton > button,
    button[kind="primary"],
    button[kind="secondary"] {
        background: linear-gradient(135deg,
            rgba(42,37,51,0.98) 0%,
            rgba(32,27,41,0.98) 100%) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 2px solid var(--accent2) !important;
        border-radius: 12px !important;
        color: var(--text-white) !important;
        font-weight: 600 !important;
        padding: 12px 24px !important;
        min-height: 44px !important;
        font-size: 14px !important;
        box-shadow: 
            0 8px 32px rgba(160,134,146,0.25),
            inset 0 1px 0 rgba(255,255,255,0.08) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    div.stButton > button:hover,
    button[kind="primary"]:hover,
    button[kind="secondary"]:hover {
        background: linear-gradient(135deg,
            rgba(52,47,61,1) 0%,
            rgba(42,37,51,1) 100%) !important;
        border-color: #C0A0B6 !important;
        transform: translateY(-2px) !important;
        box-shadow: 
            0 16px 48px rgba(160,134,146,0.4),
            inset 0 1px 0 rgba(255,255,255,0.12) !important;
    }

    div.stButton > button:active,
    button[kind="primary"]:active,
    button[kind="secondary"]:active {
        transform: translateY(0) !important;
        box-shadow: 
            0 4px 16px rgba(160,134,146,0.3),
            inset 0 1px 0 rgba(255,255,255,0.08) !important;
    }

    /* ===== INPUTS ===== */
    input, textarea, select, .stSelectbox, .stMultiSelect, .stTextInput {
        background: var(--bg-input) !important;
        color: var(--text-white) !important;
        border: 2px solid #A08692 !important;
        border-radius: 10px !important;
        padding: 10px 12px !important;
        font-size: 14px !important;
    }

    input::placeholder, textarea::placeholder {
        color: rgba(232,222,217,0.5) !important;
    }

    input:focus, textarea:focus, select:focus {
        border-color: var(--accent2) !important;
        box-shadow: 0 0 0 3px rgba(160,134,146,0.2) !important;
        outline: none !important;
    }

    /* ===== TABLES ===== */
    [data-testid="dataframe"] {
        color: var(--text-white) !important;
        background: rgba(32,27,41,0.8) !important;
    }

    [data-testid="dataframe"] table {
        background: transparent !important;
    }

    [data-testid="dataframe"] th {
        background: rgba(42,37,51,0.95) !important;
        color: var(--text-white) !important;
        border: 1.5px solid #A08692 !important;
        font-weight: 600 !important;
        padding: 12px !important;
    }

    [data-testid="dataframe"] td {
        background: transparent !important;
        color: var(--text-white) !important;
        border: 1.5px solid #A08692 !important;
        padding: 10px !important;
    }

    [data-testid="dataframe"] tbody tr:hover {
        background: rgba(160,134,146,0.1) !important;
    }

    /* ===== CHARTS ===== */
    .plotly-graph-div, .stPlotlyChart > div, [data-testid="stPlotlyChart"] {
        background: transparent !important;
        border-radius: 12px !important;
    }

    /* ===== DIVIDERS ===== */
    hr {
        border-color: #A08692 !important;
        border-width: 1.5px !important;
        margin: 1.5rem 0 !important;
    }

    /* ===== LINKS ===== */
    a {
        color: var(--accent2) !important;
        text-decoration: none !important;
        transition: color 0.2s !important;
    }

    a:hover {
        color: #C0A0B6 !important;
        text-decoration: underline !important;
    }

    /* ===== ALERTS ===== */
    .stAlert, .stSuccess, .stError, .stWarning, .stInfo {
        background: rgba(42,37,51,0.9) !important;
        border: 2px solid #A08692 !important;
        border-radius: 10px !important;
        color: var(--text-white) !important;
    }

    .stSuccess {
        border-color: #16a34a !important;
        background: rgba(22,163,74,0.15) !important;
    }

    .stError {
        border-color: #dc2626 !important;
        background: rgba(220,38,38,0.15) !important;
    }

    .stWarning {
        border-color: #eab308 !important;
        background: rgba(234,179,8,0.15) !important;
    }

    .stInfo {
        border-color: var(--accent2) !important;
        background: rgba(160,134,146,0.15) !important;
    }

    /* ===== RADIO BUTTONS ===== */
    .stRadio > div > label {
        color: var(--text-white) !important;
        border-left: 3px solid var(--primary) !important;
        padding-left: 12px !important;
        border-radius: 4px !important;
        transition: all 0.2s !important;
    }

    .stRadio > div > label:hover {
        border-left-color: var(--accent2) !important;
        background: rgba(160,134,146,0.1) !important;
    }

    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(42,37,51,0.5);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--primary);
        border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent2);
    }
    
    

    </style>
    """, unsafe_allow_html=True)


def get_theme_colors():
    """Returns the optimized color palette for consistent theming."""
    return {
        'DARK_NAVY': '#0F0D15',
        'DARK_PURPLE': '#1F1A28',
        'MID_PURPLE': '#2A2533',
        'PRIMARY': '#807A81',
        'ACCENT1': '#6C5C7C',
        'ACCENT2': '#A08692',
        'LIGHT_BEIGE': '#E1C8C2',
        'TEXT_WHITE': '#E8DED9',
        'INPUT_BG': '#2A2533'
    }


def svg_icon(name: str, size: int = 24, color: str = '#E8DED9') -> str:
        """Return an inline SVG string for a small set of flat-style icons.

        Supported icons: trending-up, trending-down, calendar, bar-chart,
        clock, lightbulb, target, puzzle, info-circle.
        """
        icons = {
                'trending-up': f"""
                <svg xmlns='http://www.w3.org/2000/svg' width='{size}' height='{size}' viewBox='0 0 24 24' fill='none' stroke='{color}' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round' style='vertical-align:middle; margin-right:8px;'>
                    <polyline points='23 6 13.5 15.5 8.5 10.5 1 18' />
                    <polyline points='17 6 23 6 23 12' />
                </svg>
                """,
                'trending-down': f"""
                <svg xmlns='http://www.w3.org/2000/svg' width='{size}' height='{size}' viewBox='0 0 24 24' fill='none' stroke='{color}' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round' style='vertical-align:middle; margin-right:8px;'>
                    <polyline points='23 18 13.5 8.5 8.5 13.5 1 6' />
                    <polyline points='7 18 1 18 1 12' />
                </svg>
                """,
                'calendar': f"""
                <svg xmlns='http://www.w3.org/2000/svg' width='{size}' height='{size}' viewBox='0 0 24 24' fill='none' stroke='{color}' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round' style='vertical-align:middle; margin-right:8px;'>
                    <rect x='3' y='4' width='18' height='18' rx='2' ry='2'/>
                    <line x1='16' y1='2' x2='16' y2='6'/>
                    <line x1='8' y1='2' x2='8' y2='6'/>
                    <line x1='3' y1='10' x2='21' y2='10'/>
                </svg>
                """,
                'bar-chart': f"""
                <svg xmlns='http://www.w3.org/2000/svg' width='{size}' height='{size}' viewBox='0 0 24 24' fill='none' stroke='{color}' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round' style='vertical-align:middle; margin-right:8px;'>
                    <line x1='12' y1='20' x2='12' y2='10'/>
                    <line x1='18' y1='20' x2='18' y2='4'/>
                    <line x1='6' y1='20' x2='6' y2='16'/>
                </svg>
                """,
                'clock': f"""
                <svg xmlns='http://www.w3.org/2000/svg' width='{size}' height='{size}' viewBox='0 0 24 24' fill='none' stroke='{color}' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round' style='vertical-align:middle; margin-right:8px;'>
                    <circle cx='12' cy='12' r='10'/>
                    <polyline points='12 6 12 12 16 14'/>
                </svg>
                """,
                'lightbulb': f"""
                <svg xmlns='http://www.w3.org/2000/svg' width='{size}' height='{size}' viewBox='0 0 24 24' fill='none' stroke='{color}' stroke-width='1.6' stroke-linecap='round' stroke-linejoin='round' style='vertical-align:middle; margin-right:8px;'>
                    <path d='M9 18h6'/>
                    <path d='M10 22h4'/>
                    <path d='M9 18a6 6 0 1 1 6 0'/>
                    <path d='M9 18v-1'/>
                </svg>
                """,
                'target': f"""
                <svg xmlns='http://www.w3.org/2000/svg' width='{size}' height='{size}' viewBox='0 0 24 24' fill='none' stroke='{color}' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round' style='vertical-align:middle; margin-right:8px;'>
                    <circle cx='12' cy='12' r='10'/>
                    <circle cx='12' cy='12' r='6'/>
                    <circle cx='12' cy='12' r='2'/>
                </svg>
                """,
                'puzzle': f"""
                <svg xmlns='http://www.w3.org/2000/svg' width='{size}' height='{size}' viewBox='0 0 24 24' fill='none' stroke='{color}' stroke-width='1.6' stroke-linecap='round' stroke-linejoin='round' style='vertical-align:middle; margin-right:8px;'>
                    <path d='M3 11h4v4H3z'/>
                    <path d='M9 3h6v6H9z'/>
                    <path d='M15 11h6v10H15z'/>
                </svg>
                """,
                'info-circle': f"""
                <svg xmlns='http://www.w3.org/2000/svg' width='{size}' height='{size}' viewBox='0 0 24 24' fill='none' stroke='{color}' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round' style='vertical-align:middle; margin-right:8px;'>
                    <circle cx='12' cy='12' r='10'/>
                    <line x1='12' y1='16' x2='12' y2='12'/>
                    <line x1='12' y1='8' x2='12.01' y2='8'/>
                </svg>
                """,
        }

        return icons.get(name, '')


def bootstrap_icon(name: str, size: int = 24, color: str = '#E8DED9') -> str:
        """Return a compact Bootstrap-style inline SVG for common icons.

        This provides crisp, filled/stroked icons sized consistently for headers.
        Supported: graph-up, graph-down, calendar3, bar-chart, clock, lightbulb-fill,
        info-circle-fill, bullseye, cash.
        """
        s = str(size)
        icons = {
                'graph-up': f"""
                <svg xmlns='http://www.w3.org/2000/svg' width='{s}' height='{s}' viewBox='0 0 16 16' fill='none' stroke='{color}' stroke-width='1.2' stroke-linecap='round' stroke-linejoin='round' style='vertical-align:middle; margin-right:8px;'>
                    <path d='M0 11h16' stroke='{color}'/>
                    <polyline points='2,9 6,5 10,9 14,3' stroke='{color}' fill='none'/>
                    <polyline points='11,4 14,4 14,1' stroke='{color}'/>
                </svg>
                """,
                'graph-down': f"""
                <svg xmlns='http://www.w3.org/2000/svg' width='{s}' height='{s}' viewBox='0 0 16 16' fill='none' stroke='{color}' stroke-width='1.2' stroke-linecap='round' stroke-linejoin='round' style='vertical-align:middle; margin-right:8px;'>
                    <path d='M0 5h16' stroke='{color}'/>
                    <polyline points='2,7 6,11 10,7 14,13' stroke='{color}' fill='none'/>
                    <polyline points='11,12 14,12 14,15' stroke='{color}'/>
                </svg>
                """,
                'calendar3': f"""
                <svg xmlns='http://www.w3.org/2000/svg' width='{s}' height='{s}' viewBox='0 0 16 16' fill='none' stroke='{color}' stroke-width='1.2' stroke-linecap='round' stroke-linejoin='round' style='vertical-align:middle; margin-right:8px;'>
                    <rect x='1' y='3' width='14' height='12' rx='2' stroke='{color}' fill='none'/>
                    <line x1='1' y1='6' x2='15' y2='6' stroke='{color}'/>
                    <path d='M4 1v4' stroke='{color}'/>
                    <path d='M12 1v4' stroke='{color}'/>
                </svg>
                """,
                'bar-chart': f"""
                <svg xmlns='http://www.w3.org/2000/svg' width='{s}' height='{s}' viewBox='0 0 16 16' fill='none' stroke='{color}' stroke-width='1.2' stroke-linecap='round' stroke-linejoin='round' style='vertical-align:middle; margin-right:8px;'>
                    <rect x='1' y='9' width='2' height='6' stroke='{color}'/>
                    <rect x='5' y='5' width='2' height='10' stroke='{color}'/>
                    <rect x='9' y='3' width='2' height='12' stroke='{color}'/>
                    <rect x='13' y='7' width='2' height='8' stroke='{color}'/>
                </svg>
                """,
                'clock': f"""
                <svg xmlns='http://www.w3.org/2000/svg' width='{s}' height='{s}' viewBox='0 0 16 16' fill='none' stroke='{color}' stroke-width='1.2' stroke-linecap='round' stroke-linejoin='round' style='vertical-align:middle; margin-right:8px;'>
                    <circle cx='8' cy='8' r='6' stroke='{color}' fill='none'/>
                    <path d='M8 4v5l3 2' stroke='{color}'/>
                </svg>
                """,
                'lightbulb-fill': f"""
                <svg xmlns='http://www.w3.org/2000/svg' width='{s}' height='{s}' viewBox='0 0 16 16' fill='{color}' style='vertical-align:middle; margin-right:8px;'>
                    <path d='M2 6a6 6 0 1 1 11.9 1.6c-.6 2-2 3.1-2.9 3.8-.3.2-.5.4-.5.6v1.2a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V12c0-.2-.2-.4-.5-.6C3.9 10.7 2.6 9.6 2 6z' />
                </svg>
                """,
                'info-circle-fill': f"""
                <svg xmlns='http://www.w3.org/2000/svg' width='{s}' height='{s}' viewBox='0 0 16 16' fill='{color}' style='vertical-align:middle; margin-right:8px;'>
                    <path d='M8 0a8 8 0 1 0 0 16A8 8 0 0 0 8 0zM8.93 6.588 8 6.588V5h-.5V4h1v2h-.57zM7.5 8h1v4h-1V8z' />
                </svg>
                """,
                'bullseye': f"""
                <svg xmlns='http://www.w3.org/2000/svg' width='{s}' height='{s}' viewBox='0 0 16 16' fill='none' stroke='{color}' stroke-width='1.2' stroke-linecap='round' stroke-linejoin='round' style='vertical-align:middle; margin-right:8px;'>
                    <circle cx='8' cy='8' r='6' stroke='{color}'/>
                    <circle cx='8' cy='8' r='3' stroke='{color}'/>
                    <circle cx='8' cy='8' r='1' fill='{color}' stroke='{color}'/>
                </svg>
                """,
                'cash': f"""
                <svg xmlns='http://www.w3.org/2000/svg' width='{s}' height='{s}' viewBox='0 0 16 16' fill='none' stroke='{color}' stroke-width='1.2' stroke-linecap='round' stroke-linejoin='round' style='vertical-align:middle; margin-right:8px;'>
                    <rect x='1' y='4' width='14' height='8' rx='1' stroke='{color}' fill='none'/>
                    <path d='M4 8h8' stroke='{color}'/>
                    <circle cx='8' cy='8' r='2' stroke='{color}' fill='none'/>
                </svg>
                """,
        }

        return icons.get(name, '')


        
