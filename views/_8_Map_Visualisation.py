import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import requests
import folium
from folium.plugins import MarkerCluster
from datetime import datetime, time
import warnings
warnings.filterwarnings("ignore")



# alias time for some snippets that expect dtime
dtime = time

from streamlit_folium import folium_static

from datetime import datetime


def app(df):
    COLORS = ["#2927F7", "#50B8F6", "#7EDEFA", "#94FEFE", "#80FAD6"]

    @st.cache_data
    def load_demo_data():
        states = ['Punjab', 'Karnataka', 'Maharashtra','Gujarat','Uttar Pradesh','West Bengal','Delhi','Tamil Nadu',]
        return pd.DataFrame({
            'Date': pd.date_range('2023-01-01', periods=4000, freq='H'),
            'Violation_Type': np.random.choice(['Over-speeding','Signal Jumping', 'Drunk Driving', 'No Helmet'], 4000),
            'Fine_Amount': np.random.randint(500, 5000, 4000),
            'Registration_State': np.random.choice(states, 4000),
            'Location': np.random.choice(states, 4000),
            'lat': np.random.choice([31.1, 12.9, 19.7], 4000),
            'lon': np.random.choice([75.7, 77.6, 75.7], 4000)
        })

    # GEOJSON LOADER - Add this once
    @st.cache_data(ttl=3600)
    def load_geojsons():
        world_url = "https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson"
        world_geo = requests.get(world_url).json()

        india_geo = None
        try:
            with open('india_states.geojson', 'r') as f:
                india_geo = json.load(f)
        except:
            pass
        return world_geo, india_geo

    # STATE COORDINATES FOR CSV
    STATE_COORDS = {
        'Karnataka': (12.97, 77.59), 'Punjab': (30.90, 75.85),
        'Maharashtra': (19.07, 72.87), 'West Bengal': (22.57, 88.36),
        'Tamil Nadu': (13.08, 80.27), 'Delhi': (28.61, 77.23),
        'Uttar Pradesh': (26.85, 80.95), 'Gujarat': (23.02, 72.57)
    }

    if 'df' not in st.session_state:
        st.session_state.df = load_demo_data()

    # ==================== MAIN CONTENT ====================
    st.markdown("""
        <h2 style="display:flex; align-items:center; gap:12px;">
            <i class="bi bi-geo-alt-fill" style="font-size:28px; color:#3b82f6;"></i>
            Violation Analysis using Map Visualisation
        </h2>
        """, unsafe_allow_html=True)

    # =====================================================
    # Ensure all required columns exist BEFORE filtering
    # =====================================================

    df_base = st.session_state.df.copy()

    # Vehicle Type
    if 'Vehicle_Type' not in df_base.columns:
        df_base['Vehicle_Type'] = np.random.choice(
            ["Car", "Bike", "Truck", "Auto Rickshaw", "Bus",'Scooter'],
            len(df_base)
        )

    # Driver Age
    if 'Driver_Age' not in df_base.columns:
        df_base['Driver_Age'] = np.random.randint(18, 65, len(df_base))

    # Weather Condition
    if 'Weather_Condition' not in df_base.columns:
        df_base['Weather_Condition'] = np.random.choice(
            ["Rainy", "Clear", "Foggy", "Cloudy"],
            len(df_base)
        )

    # Road Condition
    if 'RoadCondition' not in df_base.columns:
        df_base['RoadCondition'] = np.random.choice(
            ["Potholes", "Wet", "Dry", "Under Construction","Slippery"],
            len(df_base)
        )

    # Time column
    if 'Time' not in df_base.columns:
        if 'DateTime' in df_base.columns:
            df_base['Time'] = pd.to_datetime(df_base['DateTime'], errors='coerce').dt.strftime('%H%M')
        elif 'Date' in df_base.columns:
            df_base['Time'] = pd.to_datetime(df_base['Date'], errors='coerce').dt.strftime('%H%M')
        else:
            df_base['Time'] = '1200'

    # Fine Amount
    if 'FineAmount' not in df_base.columns:
        df_base['FineAmount'] = np.random.randint(500, 5000, len(df_base))

    # Fine Bracket
    def get_fine_bracket(amount):
        if amount < 1000:
            return "Low <1K"
        elif amount < 2500:
            return "Medium 1-2.5K"
        elif amount < 4000:
            return "High 2.5-4K"
        else:
            return "Extreme >4K"

    if 'FineBracket' not in df_base.columns:
        df_base['FineBracket'] = df_base['FineAmount'].apply(get_fine_bracket)

    # Save back to session
    st.session_state.df = df_base

    # Date Filter
    min_date = pd.to_datetime('2023-01-01').date()
    max_date = pd.to_datetime('2023-12-31').date()
    date_range = st.date_input(" GLOBAL DATE FILTER", value=(min_date, max_date), key="date_range_key")

    if isinstance(date_range, tuple) and len(date_range) == 2:
        date_start = pd.to_datetime(date_range[0])
        date_end = pd.to_datetime(date_range[1])
    else:
        date_start = pd.to_datetime(min_date)
        date_end = pd.to_datetime(max_date)

    # Filter data
    date_col = 'Date' if 'Date' in st.session_state.df.columns else 'DateTime' if 'DateTime' in st.session_state.df.columns else None
    if date_col:
        filtered_df = st.session_state.df[
            (pd.to_datetime(st.session_state.df[date_col], errors='coerce') >= date_start) &
            (pd.to_datetime(st.session_state.df[date_col], errors='coerce') <= date_end)
            ]
    else:
        filtered_df = st.session_state.df

    # ==================== NAVIGATION CARDS ====================
    st.markdown("###  **Filter by Section**")

    # Initialize scroll state
    if 'scroll_to' not in st.session_state:
        st.session_state.scroll_to = None

    nav_cards = [
        ("bi-geo-alt", "Violation Type Intelligence"),
        ("bi-car-front", "Vehicle Class Hotspots"),
        ("bi-person", "Driver Demographics Map"),
        ("bi-cloud", "Weather-Violation Nexus"),
        ("bi-geo-alt-fill", "State-Level Risk Matrix"),
        ("bi-signpost-split", "Infrastructure Danger Zones"),
        ("bi-clock", "Temporal Violation Patterns & Peak Hour Analysis"),

    ]

    cols = st.columns(8)
    for i, (icon_class, title) in enumerate(nav_cards):
        with cols[i]:
            st.markdown(f"""
            <div 
                onclick="
                    const url = new URL(window.location);
                    url.searchParams.set('scroll_to', '{i}');
                    window.history.pushState(null, '', url);
                    window.location.reload();
                "
                style="
                    cursor:pointer;
                    text-align:center;
                    padding:10px 8px;
                    border-radius:12px;
                    background:linear-gradient(135deg, rgba(15,13,21,0.88) 0%, rgba(42,37,51,0.88) 100%);
                    border:1px solid #6C5C7C;
                    box-shadow:0 8px 22px rgba(128,122,129,0.18);
                    margin:2px;
                    transition:transform 0.2s;
                "
                onmouseover="this.style.transform='scale(1.05)'"
                onmouseout="this.style.transform='scale(1)'"
            >
                <i class="bi {icon_class}" style="font-size:24px;color:#E8DED9;"></i>
                <div style="font-size:11px;margin-top:8px;color:#E8DED9;font-weight:600;">
                    {title}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    if st.session_state.get('scroll_to') is not None:
        target_idx = int(st.session_state.get('scroll_to'))
        anchor = f"exp{target_idx + 1}"
        scroll_js = f"<script>window.setTimeout(()=>{{const el=document.getElementById('{anchor}'); if(el) el.scrollIntoView({{behavior:'smooth',block:'start'}});}},120);</script>"
        st.markdown(scroll_js, unsafe_allow_html=True)

    # ==================== EXPANDER 1: VIOLATION TYPE DISTRIBUTION ====================
    with st.expander("Violation Type Intelligence", expanded=False):
        st.markdown('<div id="exp1"></div>', unsafe_allow_html=True)

        violation_options = sorted(st.session_state.df[
                                       'Violation_Type'].unique().tolist()) if 'Violation_Type' in st.session_state.df.columns else []
        selected_violations = st.multiselect(
            " **Select Violation Types**",
            violation_options,
            default=violation_options[:2] if len(violation_options) > 2 else violation_options,
            key="perfect_globe"
        )

        # ✅ DEFAULT: show all data
        if len(selected_violations) > 0:
            viol_data = filtered_df[filtered_df['Violation_Type'].isin(selected_violations)]
        else:
            viol_data = filtered_df

        state_totals = viol_data.groupby('Location').size().reset_index(name='Violations')

        try:
            with open('india_states.geojson', 'r') as f:
                    india_geo = json.load(f)

                # 🎨 YOUR FAVORITE COLORS + HD FIX
            fig = px.choropleth_mapbox(
                    state_totals,
                    geojson=india_geo,
                    locations='Location',
                    color='Violations',
                    hover_data={'Violations': ':,d'},
                    mapbox_style="carto-darkmatter",  # ✅ Your favorite dark theme
                    center={"lat": 20.59, "lon": 78.96},
                    zoom=4,  # ✅ Perfect zoom
                    color_continuous_scale="Viridis",  # ✅ Beautiful gradient (your original)
                    opacity=0.85,  # ✅ Not too transparent
                    title=f" **GLOBE CHOROPLETH** - {len(selected_violations)} Types"
                )

                # 🖼️ BLUR FIX - CRISP SETTINGS
            fig.update_geos(
                    projection_type="orthographic",  # 🌐 Globe
                    resolution=110,  # 🔍 ULTRA HD boundaries
                    showcountries=True,
                    countrycolor="#333",  # ✅ Dark borders
                    countrywidth=1.5,  # ✅ Thick crisp lines
                    landcolor="#1a1b2e",  # ✅ Dark land
                    showocean=True,
                    oceancolor="#0a0e17",  # ✅ Deep ocean
                    coastlinecolor="#555",
                    coastlinewidth=1.5
                )

                # 🎨 LAYOUT - YOUR STYLE
            fig.update_layout(
                    template='plotly_dark',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=750,
                    title_font_size=24,
                    font=dict(size=14, color='#E8DED9'),
                    hoverlabel=dict(
                        bgcolor="#1a1623",  # ✅ Your dark purple hover
                        font_size=14
                    ),
                    showlegend=False,
                    margin={"r": 0, "t": 50, "l": 0, "b": 0}
                )

                # 🎮 BUTTONS - SAME AS BEFORE
            fig.update_layout(
                    updatemenus=[
                        dict(
                            buttons=[
                                dict(args=[{"projection.type": "orthographic", "zoom": 4}], label="🌐 **GLOBE**",
                                     method="relayout"),
                                dict(args=[{"projection.type": "equirectangular", "zoom": 2.2}], label="🗺️ **FLAT**",
                                     method="relayout"),
                                dict(args=[
                                    {"projection.type": "conic conformal", "center": {"lat": 20, "lon": 78},
                                     "zoom": 5}],
                                    label="🇮🇳 **INDIA**", method="relayout")
                            ],
                            direction="left",
                            pad={"r": 15, "t": 15},
                            x=0.01, xanchor="left", y=1.02, yanchor="top",
                            bgcolor="#6C5C7C",
                            font=dict(color="#E8DED9", size=12)
                        )
                    ]
                )

                # 🔍 FINAL SHARPEN
            fig.update_traces(
                    marker_opacity=1,
                    marker_line_width=1.5,
                    marker_line_color="#fbfbfb",
                    selector=dict(type='choroplethmapbox')
                )

            st.plotly_chart(fig, use_container_width=True)

                # 📊
            col1, col2, col3 = st.columns(3)
            total = state_totals['Violations'].sum()
            max_state = state_totals.loc[state_totals['Violations'].idxmax(), 'Location']

            with col1:
                st.metric("Total Cases", f"{total:,}")
            with col2:
                st.metric("Hottest State", max_state)
            with col3:
                st.metric("States Active", len(state_totals))

            st.success(" 🎮 Globe/Flat/India")

        except:
                st.error("❌ GeoJSON issue - check file")


    # ==================== EXPANDER 2: VEHICLE CLASSIFICATION ====================
    with st.expander("Vehicle Class Hotspots", expanded=False):
        st.markdown('<div id="exp2"></div>', unsafe_allow_html=True)

        vehicle_types = st.multiselect(
            "Select Vehicle Types",
            ["Car", "Bike", "Truck", "Auto Rickshaw", "Bus","Scooter"],
            default=[],
            key="vehicle_choropleth"
        )

        if len(vehicle_types) > 0:
            # 🔥 FILTER + AGGREGATE
            vehicle_data = filtered_df[filtered_df['Vehicle_Type'].isin(vehicle_types)]
            state_vehicle_stats = vehicle_data.groupby(['Location', 'Vehicle_Type']).size().reset_index(name='Count')
            state_totals = state_vehicle_stats.groupby('Location')['Count'].sum().reset_index(name='Total_Vehicles')

            # 🎨 AESTHETIC PALETTE SELECTOR
            palettes = {
                " Sunset Dark": "sunsetdark",
                " Neon Plasma": "plasma_r",
                " Turbo": "turbo",
                " Peach Glow": "peach",
                " Ocean": "haline"
            }

            col1, col2 = st.columns(2)
            with col1:
                selected_palette = st.selectbox("Color Palette", list(palettes.keys()), index=0)
            with col2:
                map_height = st.slider("📏 Map Height", 600, 1400, 1000, step=100)

            # 🌍 LOAD GEOJSON
            @st.cache_data(ttl=3600)
            def load_geojsons():
                world_geo = requests.get(
                    "https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson").json()
                try:
                    with open('india_states.geojson', 'r') as f:
                        india_geo = json.load(f)
                except:
                    india_geo = None
                return world_geo, india_geo

            world_geo, india_geo = load_geojsons()
            combined_geo = world_geo.copy()
            if india_geo:
                for feature in india_geo.get('features', []):
                    combined_geo['features'].append(feature)

            # 🗺️ AESTHETIC CHOROPLETH
            fig = px.choropleth(
                state_totals,
                geojson=combined_geo,
                locations='Location',
                color='Total_Vehicles',
                color_continuous_scale=palettes[selected_palette],
                projection="orthographic",
                title=f"VEHICLE CHOROPLETH - {len(vehicle_types)} Types | {selected_palette}",
                hover_data={'Total_Vehicles': ':,d'}
            )

            # 🌐 ORTHOGRAPHIC GLOBE + CRISP SETTINGS
            fig.update_geos(
                projection_type="orthographic",
                resolution=50,
                showcountries=True, countrycolor="#E8DED9", countrywidth=3,
                showsubunits=True, subunitcolor="#50B8F6", subunitwidth=2,
                landcolor="#1a1f2b", showocean=True, oceancolor="#0d1424",
                coastlinewidth=2
            )

            # 🔥 HUGE STATE LABELS (PB, MH, KA)
            for state, (lat, lon) in STATE_COORDS.items():
                if state in state_totals['Location'].values:
                    count = int(state_totals[state_totals['Location'] == state]['Total_Vehicles'].iloc[0])
                    fig.add_annotation(
                        x=lon, y=lat,
                        text=f"<b style='color:#94FEFE;font-size:20px;font-weight:bold'>{state[:2].upper()}</b><br>"
                             f"<span style='color:#E8DED9;font-size:16px'>{count:,}</span>",
                        showarrow=False,
                        font=dict(size=18, color="#E8DED9"),
                        bgcolor="rgba(108,92,124,0.92)",
                        bordercolor="#807A81", borderwidth=4,
                        borderpad=10,
                        xanchor="center", yanchor="middle"
                    )

            # 🇮🇳 INDIA LABEL
            fig.add_annotation(
                x=78.96, y=20,
                text="<b style='color:#94FEFE;font-size:24px'>🇮🇳 INDIA</b>",
                showarrow=False,
                font=dict(size=22, color="#E8DED9"),
                bgcolor="rgba(108,92,124,0.93)",
                bordercolor="#A08692", borderwidth=4,
                borderpad=12,
                xanchor="center", yanchor="middle"
            )

            # 🎮 ADVANCED ZOOM + PROJECTION BUTTONS
            fig.update_layout(
                height=map_height,  # 📏 DYNAMIC HEIGHT
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                title_font_size=24,
                dragmode='zoom',  # 🖱️ ENABLE MOUSE ZOOM
                updatemenus=[
                    dict(
                        buttons=[
                            # GLOBE VIEWS
                            dict(args=[{"projection.type": "orthographic", "zoom": 2}], label="🌐 **GLOBE**",
                                 method="relayout"),
                            dict(args=[{"projection.type": "orthographic", "zoom": 3}], label="🔍 **GLOBE ZOOM**",
                                 method="relayout"),

                            # FLAT VIEWS
                            dict(args=[{"projection.type": "equirectangular", "zoom": 2}], label="🗺️ **FLAT MAP**",
                                 method="relayout"),
                            dict(args=[{"projection.type": "equirectangular", "zoom": 3}], label="🔍 **FLAT ZOOM**",
                                 method="relayout"),

                            # INDIA FOCUSED
                            dict(args=[
                                {"projection.type": "conic conformal", "center": {"lat": 20, "lon": 78}, "zoom": 4}],
                                label="🇮🇳 **INDIA**", method="relayout"),
                            dict(args=[
                                {"projection.type": "conic conformal", "center": {"lat": 20, "lon": 78}, "zoom": 6}],
                                label="🔍 **INDIA ZOOM**", method="relayout"),

                            # EXTREME ZOOM
                            dict(args=[{"zoom": 8}], label="🔎 **MAX ZOOM**", method="relayout"),
                            dict(args=[{"zoom": 1}], label="📍 **RESET**", method="relayout")
                        ],
                        direction="down",  # 📍 DROPDOWN instead of left
                        pad={"r": 10, "t": 10},
                        x=0.01, y=1.12,
                        bgcolor="#807A81",
                        font=dict(color="#E8DED9", size=10),
                        showactive=True
                    )
                ],
                coloraxis_colorbar=dict(title="Vehicles", thickness=25, len=0.75, x=1.02),
                margin=dict(l=0, r=100, t=80, b=0)  # 📐 Full screen
            )

            st.plotly_chart(fig, width='stretch')

            # 📊 METRICS
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🚗 Total Vehicles", f"{state_totals['Total_Vehicles'].sum():,}")
            with col2:
                st.metric("🏆 Top State", state_totals.loc[state_totals['Total_Vehicles'].idxmax(), 'Location'])
            with col3:
                st.metric("📍 Active States", len(state_totals))

            # 📋 TABLE
            st.subheader(" **Vehicle Breakdown**")
            vehicle_pivot = state_vehicle_stats.pivot_table(
                index='Location', columns='Vehicle_Type', values='Count', fill_value=0
            ).round(0).astype(int)
            st.dataframe(vehicle_pivot, width='stretch')

            # 🎮 CONTROLS LEGEND
            st.markdown("""
                   ### 🎮 **Zoom Controls**
                   - **🖱️ Mouse Wheel:** Scroll to zoom
                   - **🖱️ Click & Drag:** Pan around map
                   - **Shift + Drag:** Box zoom
                   - **Buttons:** Change projection/zoom level
                   - **📏 Height Slider:** Adjust map size
                   """)

            st.success(
                f" **CHOROPLETH READY** | Palette: {selected_palette} | Height: {map_height}px | Zoom: ENABLED ✓")
        else:
            st.warning(" **Select vehicle types first!**")


    # ==================== EXPANDER 3: DEMOGRAPHIC RISK ASSESSMENT ====================
    with st.expander("Driver Demographics Map", expanded=False):
        st.markdown('<div id="exp3"></div>', unsafe_allow_html=True)

        age_range = st.slider(" **Age Range**", 18, 65, (25, 45), key="age_range_exp3")

        # STATE AGGREGATION
        age_filtered = filtered_df[
            # (filtered_df['Driver_Age'] >= age_range[0]) &
            (True) &
            (filtered_df['Driver_Age'] <= age_range[1])
            ].copy()

        if len(age_filtered) > 0:
            # Aggregate by Location (state names)
            state_stats = age_filtered.groupby('Location').size().reset_index(name='Violations')
            state_stats['Avg_Age'] = age_filtered.groupby('Location')['Driver_Age'].mean().values.round(0)

            try:
                # Load GeoJSON
                with open('india_states.geojson', 'r') as f:
                    india_geo = json.load(f)

                #  TRUE CHOROPLETH - STATES HIGHLIGHTED (Mapbox + GeoJSON)
                fig = px.choropleth_mapbox(
                    state_stats,
                    geojson=india_geo,
                    locations='Location',  # MATCHES geojson state names
                    color='Violations',
                    hover_data={'Avg_Age': ':.0f', 'Violations': ':,d'},
                    mapbox_style="carto-darkmatter",
                    center={"lat": 20.59, "lon": 78.96},
                    zoom=4.5,
                    color_continuous_scale="Viridis",  # BEST FOR GLOBE
                    opacity=0.9,
                    title=f" **STATE CHOROPLETH GLOBE** - Age {age_range[0]}-{age_range[1]}"
                )

                #  GLOBE-LIKE VIEW + LIGHT BORDERS
                fig.update_layout(
                    mapbox=dict(
                        style="carto-darkmatter",
                        zoom=4.5,
                        center={"lat": 20.59, "lon": 78.96}
                    ),
                    height=1000,

                    template='plotly_dark',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    title_font_size=24,
                    font=dict(size=14, color='#E8DED9')
                )

                #  LIGHT, VISIBLE STATE BORDERS
                fig.update_traces(
                    marker_line_width=2.2,  # ✅ Thick visible borders
                    marker_line_color="#94FEFE",  # 💡 CYAN (matches your theme)
                    marker_opacity=0.95,
                    selector=dict(type='choroplethmapbox')
                )

                # ZOOM BUTTONS (India focus)
                fig.update_layout(
                    updatemenus=[
                        dict(
                            buttons=[
                                dict(args=[{"mapbox.zoom": 4.5, "mapbox.center": {"lat": 20.59, "lon": 78.96}}],
                                     label="🌍 India", method="relayout"),
                                dict(args=[{"mapbox.zoom": 6.5}], label=" Zoom In", method="relayout"),
                                dict(args=[{"mapbox.zoom": 3}], label=" Overview", method="relayout")
                            ],
                            direction="left",
                            pad={"r": 15, "t": 15},
                            x=0.01, y=1.02,
                            bgcolor="#807A81",
                            font=dict(color="#E8DED9", size=12)
                        )
                    ]
                )

                st.plotly_chart(fig, use_container_width=True)

                #
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Cases", f"{len(age_filtered):,}")
                with col2:
                    st.metric("Top State", state_stats.loc[state_stats['Violations'].idxmax(), 'Location'])
                with col3:
                    st.metric("Avg Age", f"{state_stats['Avg_Age'].mean():.0f}")

                st.success(" **STATES FULLY HIGHLIGHTED**!")

            except FileNotFoundError:
                st.error(" **india_states.geojson missing!**\n Download: https://github.com/udit-001/india-maps-data")
                st.info("**Alternative without GeoJSON:**")

                #  FALLBACK: Density map (no geojson needed)
                map_df = age_filtered.sample(min(3000, len(age_filtered)))
                fig_fallback = px.density_mapbox(
                    map_df, lat='lat', lon='lon', z='Driver_Age',
                    radius=15, opacity=0.6,
                    mapbox_style="carto-darkmatter",
                    center={"lat": 20.59, "lon": 78.96}, zoom=4.5,
                    color_continuous_scale="Viridis"
                )
                fig_fallback.update_layout(height=600, title=" DENSITY HEATMAP (No GeoJSON)")
                st.plotly_chart(fig_fallback, width='stretch')

        else:
            st.warning("No data in age range!")

    # ==================== EXPANDER 4: ENVIRONMENTAL IMPACT ====================
    with st.expander("Weather-Violation Nexus", expanded=False):
        st.markdown('<div id="exp4"></div>', unsafe_allow_html=True)

        weather_types = st.multiselect(
            " **Select Weather Conditions**",
            ["Rainy", "Clear", "Foggy", "Cloudy", "Sunny", "Stormy"],
            default=["Rainy", "Clear"],
            key="weather_choropleth"
        )

        if len(weather_types) > 0:
            #  FILTER + AGGREGATE (SAME AS VEHICLES)
            # Safe weather filter - column may not exist
            if 'Weather_Condition' in filtered_df.columns:
                weather_data = filtered_df[filtered_df['Weather_Condition'].isin(weather_types)]
            else:
                weather_data = filtered_df.copy()  # Use all data
                st.warning(" Weather_Condition column missing - showing all data")
            # Safe weather groupby
            if 'Weather_Condition' in weather_data.columns:
                state_weather_stats = weather_data.groupby(['Location', 'Weather_Condition']).size().reset_index(
                    name='Count')
            else:
                weather_data['Weather_Condition'] = 'Unknown'  # Add dummy column
                state_weather_stats = weather_data.groupby(['Location', 'Weather_Condition']).size().reset_index(
                    name='Count')

            state_totals = state_weather_stats.groupby('Location')['Count'].sum().reset_index(name='Total_Cases')

            # PALETTE SELECTOR (SAME AS VEHICLES)
            palettes = {
                " Sunset Dark": "sunsetdark",
                " Neon Plasma": "plasma_r",
                " Turbo": "turbo",
                " Peach Glow": "peach",
                " Ocean": "haline"
            }

            col1, col2 = st.columns(2)
            with col1:
                selected_palette = st.selectbox(" **Color Palette**", list(palettes.keys()), index=0,
                                                key="weather_palette")
            with col2:
                map_height = st.slider(" **Map Height**", 600, 1400, 1000, step=100, key="weather_height")

            # 🌍 LOAD GEOJSON (SAME AS VEHICLES)
            @st.cache_data(ttl=3600)
            def load_geojsons():
                world_geo = requests.get(
                    "https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson").json()
                try:
                    with open('india_states.geojson', 'r') as f:
                        india_geo = json.load(f)
                except:
                    india_geo = None
                return world_geo, india_geo

            world_geo, india_geo = load_geojsons()
            combined_geo = world_geo.copy()
            if india_geo:
                for feature in india_geo.get('features', []):
                    combined_geo['features'].append(feature)

            # 🗺️ CHOROPLETH (IDENTICAL TO VEHICLES)
            fig = px.choropleth(
                state_totals,
                geojson=combined_geo,
                locations='Location',
                color='Total_Cases',
                color_continuous_scale=palettes[selected_palette],
                projection="orthographic",
                title=f" **WEATHER GLOBE** - {len(weather_types)} Conditions | {selected_palette}",
                hover_data={'Total_Cases': ':,d'}
            )

            # 🌐 GLOBE SETTINGS (IDENTICAL)
            fig.update_geos(
                projection_type="orthographic",
                resolution=50,
                showcountries=True, countrycolor="#E8DED9", countrywidth=3,
                showsubunits=True, subunitcolor="#50B8F6", subunitwidth=2,
                landcolor="#1a1f2b", showocean=True, oceancolor="#0d1424",
                coastlinewidth=2
            )

            # STATE LABELS (IDENTICAL)
            for state, coords in STATE_COORDS.items():
                lat = coords[0] if len(coords) == 2 else 20.59
                lon = coords[1] if len(coords) == 2 else 78.96
                if state in state_totals['Location'].values:
                    try:
                        count = int(state_totals[state_totals['Location'] == state]['Total_Cases'].iloc[0])
                    except (KeyError, IndexError):
                        count = 0

                        fig.add_annotation(
                            x=lon, y=lat,
                            text=f"<b style='color:#94FEFE;font-size:20px;font-weight:bold'>{state[:2].upper()}</b><br>"
                                 f"<span style='color:#E8DED9;font-size:16px'>{count:,}</span>",
                            showarrow=False,
                            font=dict(size=18, color="#E8DED9"),
                            bgcolor="rgba(108,92,124,0.92)",
                            bordercolor="#807A81", borderwidth=4,
                            borderpad=10,
                            xanchor="center", yanchor="middle"
                        )

            # 🇮🇳 INDIA LABEL (IDENTICAL)
            fig.add_annotation(
                x=78.96, y=20,
                text="<b style='color:#94FEFE;font-size:24px'>🇮🇳 INDIA</b>",
                showarrow=False,
                font=dict(size=22, color="#E8DED9"),
                bgcolor="rgba(108,92,124,0.93)",
                bordercolor="#A08692", borderwidth=4,
                borderpad=12,
                xanchor="center", yanchor="middle"
            )

            #  ZOOM BUTTONS (IDENTICAL)
            fig.update_layout(
                height=map_height,
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                title_font_size=24,
                dragmode='zoom',
                updatemenus=[
                    dict(
                        buttons=[
                            dict(args=[{"projection.type": "orthographic", "zoom": 2}], label="🌐 **GLOBE**",
                                 method="relayout"),
                            dict(args=[{"projection.type": "orthographic", "zoom": 3}], label="🔍 **GLOBE ZOOM**",
                                 method="relayout"),
                            dict(args=[{"projection.type": "equirectangular", "zoom": 2}], label="🗺️ **FLAT MAP**",
                                 method="relayout"),
                            dict(args=[{"projection.type": "equirectangular", "zoom": 3}], label="🔍 **FLAT ZOOM**",
                                 method="relayout"),
                            dict(args=[
                                {"projection.type": "conic conformal", "center": {"lat": 20, "lon": 78}, "zoom": 4}],
                                 label="🇮🇳 **INDIA**", method="relayout"),
                            dict(args=[
                                {"projection.type": "conic conformal", "center": {"lat": 20, "lon": 78}, "zoom": 6}],
                                 label="🔍 **INDIA ZOOM**", method="relayout"),
                            dict(args=[{"zoom": 8}], label=" **MAX ZOOM**", method="relayout"),
                            dict(args=[{"zoom": 1}], label=" **RESET**", method="relayout")
                        ],
                        direction="down",
                        pad={"r": 10, "t": 10},
                        x=0.01, y=1.12,
                        bgcolor="#807A81",
                        font=dict(color="#E8DED9", size=10),
                        showactive=True
                    )
                ],
                coloraxis_colorbar=dict(title="Weather Cases", thickness=25, len=0.75, x=1.02)
            )

            st.plotly_chart(fig, width='stretch')

            # 📊 METRICS (SAME STYLE)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(" Total Cases", f"{state_totals['Total_Cases'].sum():,}")
            with col2:
                st.metric("Top State", state_totals.loc[state_totals['Total_Cases'].idxmax(), 'Location'])
            with col3:
                st.metric(" Active States", len(state_totals))

            # 📋 BREAKDOWN TABLE (SAME STYLE)
            st.subheader(" **Weather Breakdown**")
            weather_pivot = state_weather_stats.pivot_table(
                index='Location', columns='Weather_Condition', values='Count', fill_value=0
            ).round(0).astype(int)
            st.dataframe(weather_pivot, width='stretch')

            # 🎮 CONTROLS LEGEND (SAME STYLE)
            st.markdown("""
            ### 🎮 **Zoom Controls**
            - **🖱️ Mouse Wheel:** Scroll to zoom
            - **🖱️ Click & Drag:** Pan around map
            - **Shift + Drag:** Box zoom
            - **Buttons:** Change projection/zoom level
            - **📏 Height Slider:** Adjust map size
            """)

            st.success(
                f" **WEATHER CHOROPLETH** | Palette: {selected_palette} | Height: {map_height}px | Same as Vehicles!")
        else:
            st.warning(" **Select weather conditions first!**")
    # ==================== EXPANDER 5: GEOGRAPHIC HOTSPOT ANALYSIS ====================
    with st.expander("State-Level Risk Matrix", expanded=False):
        st.markdown('<div id="exp5"></div>', unsafe_allow_html=True)

        # STATE FILTER: Dropdown + Multiselect
        col1, col2 = st.columns([1, 3])
        with col1:
            view_type = st.selectbox(" **View**", ["All States", "Top 5", "Selected"], key="state_view")
        with col2:
            available_states = filtered_df['Location'].unique()
            if view_type == "Selected":
                selected_states = st.multiselect(
                    " **Choose States**",
                    available_states,
                    default=available_states[:3].tolist(),
                    key="state_multiselect"
                )
            else:
                selected_states = available_states.tolist()

        #  FILTER STATES
        if view_type == "Top 5":
            top_states = filtered_df['Location'].value_counts().head(5).index.tolist()
            filtered_states = filtered_df[filtered_df['Location'].isin(top_states)]
        elif view_type == "Selected" and len(selected_states) > 0:
            filtered_states = filtered_df[filtered_df['Location'].isin(selected_states)]
        else:
            filtered_states = filtered_df

        #  STATE STATS
        state_stats = filtered_states.groupby('Location').agg({
            'Location': 'size',
            'Fine_Amount': 'mean'
        }).rename(columns={'Location': 'Violations', 'Fine_Amount': 'Avg_Fine'}).reset_index()
        state_stats['Avg_Fine'] = state_stats['Avg_Fine'].round(0)

        #  Palettes
        palettes = {
            " Sunset Dark": "sunsetdark",
            " Neon Plasma": "plasma_r",
            " Turbo": "turbo",
            " Peach Glow": "peach",
            " Ocean": "haline"
        }

        col3, col4 = st.columns(2)
        with col3:
            selected_palette = st.selectbox(" **Color Palette**", list(palettes.keys()), index=0, key="state_palette")

        # 🌍 GeoJSON
        @st.cache_data(ttl=3600)
        def load_geojsons():
            world_geo = requests.get(
                "https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson").json()
            try:
                with open('india_states.geojson', 'r') as f:
                    india_geo = json.load(f)
            except:
                india_geo = None
            return world_geo, india_geo

        world_geo, india_geo = load_geojsons()
        combined_geo = world_geo.copy()
        if india_geo:
            for feature in india_geo.get('features', []):
                combined_geo['features'].append(feature)

        # 🗺️ CHOROPLETH
        fig = px.choropleth(
            state_stats,
            geojson=combined_geo,
            locations='Location',
            color='Violations',
            color_continuous_scale=palettes[selected_palette],
            projection="orthographic",
            title=f" **STATE VIOLATIONS** | {view_type} | {len(state_stats)} States",
            hover_data={'Avg_Fine': '₹ :,.0f'}
        )

        # 🌐 GLOBE + LABELS
        fig.update_geos(
            projection_type="orthographic",
            resolution=50,
            showcountries=True, countrycolor="#E8DED9", countrywidth=2.5,
            landcolor="#1a1f2b", showocean=True, oceancolor="#0d1424"
        )

        # 🔥 STATE LABELS
        for state, (lat, lon) in STATE_COORDS.items():
            if state in state_stats['Location'].values:
                violations = int(state_stats[state_stats['Location'] == state]['Violations'].iloc[0])
                fig.add_annotation(
                    x=lon, y=lat,
                    text=f"<b style='color:#94FEFE;font-size:20px'>{state[:2]}</b><br>"
                         f"<span style='color:#E8DED9;font-size:16px'>{violations:,}</span>",
                    showarrow=False,
                    font=dict(size=18),
                    bgcolor="rgba(0,20,60,0.95)",
                    bordercolor="#2927F7", borderwidth=2.5,
                    xanchor="center", yanchor="middle"
                )

        # 🎮 CONTROLS + FIXED HEIGHT 800
        fig.update_layout(
            height=800,  # ✅ FIXED 800px
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            title_font_size=24,
            dragmode='zoom',
            updatemenus=[
                dict(
                    buttons=[
                        dict(args=[{"projection.type": "orthographic"}], label=" Globe", method="relayout"),
                        dict(args=[{"projection.type": "equirectangular", "zoom": 2.2}], label="🗺️ Flat",
                             method="relayout"),
                        dict(args=[{"projection.type": "conic conformal", "center": {"lat": 20, "lon": 78}, "zoom": 5}],
                             label="🇮🇳 India", method="relayout")
                    ],
                    direction="down",
                    x=0.01, y=1.1,
                    bgcolor="#807A81",
                    font=dict(color="#E8DED9", size=11)
                )
            ],
            coloraxis_colorbar=dict(title="Violations", x=1.02)
        )

        st.plotly_chart(fig, use_container_width=True)

        #
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(" Total Violations", f"{state_stats['Violations'].sum():,}")
        with col2:
            st.metric(" Top State", state_stats.loc[state_stats['Violations'].idxmax(), 'Location'])
        with col3:
            st.metric("Avg Fine", f"₹{state_stats['Avg_Fine'].mean():.0f}")

        #  TABLE
        st.subheader("**State Breakdown**")
        st.dataframe(state_stats[['Location', 'Violations', 'Avg_Fine']].round(0), width='stretch')

        st.success(f" **{view_type}** | {len(state_stats)} States | Height: 800px")

    # ==================== EXPANDER 6: INFRASTRUCTURE CORRELATION ====================
    with st.expander("Infrastructure Danger Zones", expanded=False):
        st.markdown('<div id="exp6div"></div>', unsafe_allow_html=True)

        df = st.session_state.df.copy()  # Work on copy to avoid session_state issues

        road_options = sorted(df['RoadCondition'].unique().tolist())
        selected_roads = st.multiselect("Select Road Conditions", road_options,
                                        default=road_options[:2] if len(road_options) > 2 else road_options,
                                        key="road_choropleth")

        if len(selected_roads) == 0:
            st.warning("Select road conditions first!")
        else:
            # Now safe: filter after column exists
            # Safe road condition filter
            if 'RoadCondition' in filtered_df.columns:
                road_data = filtered_df[filtered_df['RoadCondition'].isin(selected_roads)]
            else:
                road_data = filtered_df.copy()
                st.warning(" RoadCondition column missing - showing all data")
            if 'RoadCondition' in road_data.columns:  # Use roaddata, matching your filter logic
                state_road_stats = road_data.groupby(['Location', 'RoadCondition']).size().reset_index(name='Count')
            else:
                state_road_stats = road_data.groupby('Location').size().reset_index(name='Count')
                st.warning("RoadCondition column missing in data - using Location-only stats")

            state_totals = state_road_stats.groupby('Location')['Count'].sum().reset_index(name='TotalRoadCases')

            # Palette and height selector
            palettes = {
                'Sunset Dark': 'sunsetdark',
                'Neon Plasma': 'plasma_r',
                'Turbo': 'turbo',
                'Peach Glow': 'peach',
                'Ocean': 'haline'
            }
            col1, col2 = st.columns(2)
            with col1:
                selected_palette = st.selectbox("Color Palette", list(palettes.keys()), index=0, key="road_palette")
            with col2:
                map_height = st.slider("Map Height", 600, 1400, 1000, step=100, key="road_height")

            # Load GeoJSON (shared function exists)
            world_geo, india_geo = load_geojsons()
            combined_geo = world_geo.copy()
            if india_geo:
                for feature in india_geo.get('features', []):
                    combined_geo['features'].append(feature)

            # Create choropleth
            fig = px.choropleth(
                state_totals,
                geojson=combined_geo,
                locations='Location',
                color='TotalRoadCases',
                color_continuous_scale=palettes[selected_palette],
                projection='orthographic',
                title=f"ROAD CONDITIONS GLOBE - {len(selected_roads)} Conditions ({selected_palette})",
                hover_data={'TotalRoadCases': ':,d'}
            )

            # Globe settings matching template
            fig.update_geos(
                projection_type='orthographic',
                resolution=50,
                showcountries=True, countrycolor='#E8DED9', countrywidth=3,
                showsubunits=True, subunitcolor='#50B8F6', subunitwidth=2,
                landcolor='#1a1f2b',
                showocean=True, oceancolor='#0d1424',
                coastlinewidth=2
            )

            # State labels (PB:1,234 style)
            for state, (lat, lon) in STATE_COORDS.items():
                if state in state_totals['Location'].values:
                    count = int(state_totals[state_totals['Location'] == state]['TotalRoadCases'].iloc[0])
                    fig.add_annotation(
                        x=lon, y=lat,
                        text=f'<b style="color:#94FEFE;font-size:20px;font-weight:bold">{state[:2].upper()}</b><br><span style="color:#E8DED9;font-size:16px">{count:,}</span>',
                        showarrow=False,
                        font=dict(size=18, color='#E8DED9'),
                        bgcolor='rgba(108,92,124,0.92)', bordercolor='#807A81', borderwidth=4, borderpad=10,
                        xanchor='center', yanchor='middle'
                    )

            # INDIA title label
            fig.add_annotation(
                x=78.96, y=20,
                text='<b style="color:#94FEFE;font-size:24px">INDIA</b>',
                showarrow=False,
                font=dict(size=22, color='#E8DED9'),
                bgcolor='rgba(108,92,124,0.93)', bordercolor='#A08692', borderwidth=4, borderpad=12,
                xanchor='center', yanchor='middle'
            )

            # Layout with zoom buttons (8 options matching template)
            # FIXED LAYOUT - Copy exactly (4 spaces indent)
            fig.update_layout(
                height=map_height,
                template="plotly_dark",
                title_font=dict(size=24, family="Arial Black", color="#E8DED9"),
                dragmode="zoom",
                updatemenus=[
                    dict(
                        buttons=[
                            dict(args=({"projection.type": "orthographic", "zoom": 2},), label="GLOBE",
                                 method="relayout"),
                            dict(args=({"projection.type": "orthographic", "zoom": 3},), label="GLOBE ZOOM",
                                 method="relayout"),
                            dict(args=({"projection.type": "equirectangular", "zoom": 2},), label="FLAT MAP",
                                 method="relayout"),
                            dict(args=({"projection.type": "equirectangular", "zoom": 3},), label="FLAT ZOOM",
                                 method="relayout"),
                            dict(
                                args=({"projection.type": "conic conformal", "center": {"lat": 20, "lon": 78},
                                       "zoom": 4},),
                                label="INDIA", method="relayout"),
                            dict(
                                args=({"projection.type": "conic conformal", "center": {"lat": 20, "lon": 78},
                                       "zoom": 6},),
                                label="INDIA ZOOM", method="relayout"),
                            dict(args=({"zoom": 8},), label="MAX ZOOM", method="relayout"),
                            dict(args=({"zoom": 1},), label="RESET", method="relayout")
                        ],
                        direction="down",
                        pad={"r": 10, "t": 10},
                        x=0.01,
                        y=1.12,
                        bgcolor="#807A81",
                        font=dict(color="#E8DED9", size=10),
                        showactive=True
                    )
                ],
                coloraxis_colorbar={
                    "title": "Road Cases",
                    "thickness": 25,
                    "len": 0.75,
                    "x": 1.02
                },
                margin={"l": 0, "r": 100, "t": 80, "b": 0}
            )

            st.plotly_chart(fig, use_container_width=True)

            # 3-column metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Road Cases", f"{state_totals['TotalRoadCases'].sum():,}")
            with col2:
                st.metric("Top State", state_totals.loc[state_totals['TotalRoadCases'].idxmax(), 'Location'])
            with col3:
                st.metric("Active States", len(state_totals))

            # Pivot table breakdown
            st.subheader("Road Conditions Breakdown")
            # ... roaddata filtering ...
            if 'RoadCondition' in road_data.columns:
                state_road_stats = road_data.groupby(['Location', 'RoadCondition']).size().reset_index(name='Count')
            else:
                state_road_stats = road_data.groupby('Location').size().reset_index(name='Count')
                st.warning("RoadCondition missing - Location-only stats")

            # NEW: Protected pivot (line 991)
            if 'RoadCondition' in state_road_stats.columns:
                road_pivot = state_road_stats.pivot_table(index='Location', columns='RoadCondition', values='Count',
                                                          fill_value=0).round(0).astype(int)
            else:
                road_pivot = state_road_stats[['Location', 'Count']].round(0).astype({'Count': int})
                road_pivot.columns = ['Location', 'Total Road Cases']
                st.info("No RoadCondition - showing totals")

            st.subheader("Road Conditions Breakdown")
            st.dataframe(road_pivot, width='stretch')

            # Controls legend
            st.markdown("""
            **Controls Legend:**
            - Mouse Wheel/Scroll to zoom
            - Click + Drag: Pan around map
            - Shift + Drag: Box zoom
            - Buttons: Change projection/zoom level
            - Height Slider: Adjust map size
            """)
            st.success(f"ROAD CHOROPLETH READY! Palette: {selected_palette} | Height: {map_height}px | Zoom: ENABLED")

    # ==================== EXPANDER 7: TEMPORAL VIOLATION PATTERNS ====================
    with st.expander("Temporal Violation Patterns & Peak Hour Analysis", expanded=False):
        df0 = filtered_df.copy()

        # ---------- Ensure Time column ----------
        if "Time" not in df0.columns:
            if "DateTime" in df0.columns:
                dt = pd.to_datetime(df0["DateTime"], errors="coerce")
                df0["Time"] = dt.dt.strftime("%H%M")
            elif "Date" in df0.columns:
                dt = pd.to_datetime(df0["Date"], errors="coerce")
                df0["Time"] = dt.dt.strftime("%H%M")
            else:
                df0["Time"] = "1200"

        # Robust Time parsing: try to parse to datetime first, then fallback to string-cleaning
        parsed_time = pd.to_datetime(df0['Time'], errors='coerce')

        hh = parsed_time.dt.hour
        mm = parsed_time.dt.minute

        # Fallback for rows where datetime parsing failed (mixed formats like 'HHMM', numeric, etc.)
        mask_na = parsed_time.isna()
        if mask_na.any():
            s = (
                df0.loc[mask_na, 'Time']
                .astype(str)
                .str.replace(":", "", regex=False)
                .str.replace(r"[^0-9]", "", regex=True)
                .str.zfill(4)
            )
            hh_f = pd.to_numeric(s.str[:2], errors='coerce')
            mm_f = pd.to_numeric(s.str[2:], errors='coerce')
            hh = hh.copy()
            mm = mm.copy()
            hh.loc[mask_na] = hh_f
            mm.loc[mask_na] = mm_f

        # Compute minutes since midnight; keep NaN when either component is missing
        t_min = (hh * 60) + mm
        df0['t_min'] = pd.to_numeric(t_min, errors='coerce')
        df0 = df0.dropna(subset=['t_min'])

        # ---------- Fix lat/lon (handles lat_x/lat_y) ----------
        if "lat" not in df0.columns:
            if "lat_x" in df0.columns:
                df0["lat"] = df0["lat_x"]
            elif "lat_y" in df0.columns:
                df0["lat"] = df0["lat_y"]
        if "lon" not in df0.columns:
            if "lon_x" in df0.columns:
                df0["lon"] = df0["lon_x"]
            elif "lon_y" in df0.columns:
                df0["lon"] = df0["lon_y"]

        df0["lat"] = pd.to_numeric(df0.get("lat"), errors="coerce")
        df0["lon"] = pd.to_numeric(df0.get("lon"), errors="coerce")
        df0 = df0.dropna(subset=["lat", "lon"])

        # ---------- Time range filter (only) ----------
        c1, c2, c3 = st.columns(3)
        with c1:
            t_from = st.time_input("From", value=dtime(0, 0), key="tod_from_exp7")
        with c2:
            t_to = st.time_input("To", value=dtime(23, 59), key="tod_to_exp7")
        with c3:
            topn = st.slider("Top hotspots", 3, 4, 8, key="tod_topn_exp7")

        start = t_from.hour * 60 + t_from.minute
        end = t_to.hour * 60 + t_to.minute

        # Support wrap-around (e.g., 21:00 to 04:00)
        if start <= end:
            dft = df0[(df0["t_min"] >= start) & (df0["t_min"] <= end)].copy()
        else:
            dft = df0[(df0["t_min"] >= start) | (df0["t_min"] <= end)].copy()

        st.caption(f"Records in range: {len(dft):,}")

        if "Location" not in dft.columns:
            dft["Location"] = "Unknown"

        # Hotspots = top locations by count
        # Normalize Location strings to avoid duplicates caused by whitespace/case
        dft['Location'] = dft['Location'].astype(str).str.strip().str.title()
        agg = (
            dft.groupby("Location")
            .agg(Cases=("Location", "size"), lat=("lat", "mean"), lon=("lon", "mean"))
            .reset_index()
            .sort_values("Cases", ascending=False)
            .head(topn)
        )

        if agg.empty:
            st.warning("No data for selected time range.")
            st.stop()

        # ---------- Helper: build a curved arc between 2 points ----------
        def arc(lon1, lat1, lon2, lat2, n=60):
            # simple interpolation in lon/lat (looks like an arc on stereographic)
            lons = np.linspace(lon1, lon2, n)
            lats = np.linspace(lat1, lat2, n)
            # add a small bow so it looks like a flow arc
            bow = np.sin(np.linspace(0, np.pi, n)) * 6.0
            lats = lats + bow
            return lons.tolist(), lats.tolist()

        # Hub near India (feels like “source” of time-of-day pattern)
        hub_lat, hub_lon = 20.59, 78.96

        # Replace arc traces with a choropleth-style region highlight using India geojson
        fig = go.Figure()

        world_geo, india_geo = load_geojsons()

        if india_geo is not None and not agg.empty:
            # Prepare locations and values for choropleth (match 'st_nm' property)
            locations = agg['Location'].tolist()
            z = agg['Cases'].tolist()

            # Create a purple ramp colorscale from subtle to intense
            colorscale = [
                [0.0, 'rgba(146,39,247,0.05)'],
                [0.5, 'rgba(146,39,247,0.25)'],
                [1.0, 'rgba(146,39,247,0.9)']
            ]

            chor = go.Choropleth(
                geojson=india_geo,
                locations=locations,
                z=z,
                featureidkey='properties.st_nm',
                colorscale=colorscale,
                marker_line_color='rgba(0,0,0,0.2)',
                marker_line_width=0.8,
                showscale=False,
                hoverinfo='text',
                hovertext=[f"{loc}<br>Cases: {int(c)}" for loc, c in zip(locations, z)],
                zmin=0,
                zauto=False
            )

            fig.add_trace(chor)

            # Text labels placed at aggregated centroids (one label per state)
            # Cluster nearby centroids and distribute labels around the cluster centroid
            grouped_agg = agg.copy().reset_index(drop=True)
            coords = grouped_agg[['lat', 'lon']].to_numpy(dtype=float)
            n = coords.shape[0]
            lat_adj = coords[:, 0].copy()
            lon_adj = coords[:, 1].copy()

            # simple clustering by proximity (connected components) without external libs
            threshold = 0.9  # degrees threshold to consider labels 'close'
            visited = np.zeros(n, dtype=bool)
            components = []
            for i in range(n):
                if visited[i]:
                    continue
                stack = [i]
                comp = []
                while stack:
                    u = stack.pop()
                    if visited[u]:
                        continue
                    visited[u] = True
                    comp.append(u)
                    dists = np.hypot(coords[:, 0] - coords[u, 0], coords[:, 1] - coords[u, 1])
                    neighbors = np.where((dists < threshold) & (~visited))[0].tolist()
                    stack.extend(neighbors)
                components.append(comp)

            for comp in components:
                k = len(comp)
                if k == 1:
                    continue
                # distribute labels on a small circle around component centroid
                cy = coords[comp, 0].mean()
                cx = coords[comp, 1].mean()
                radius = 0.6  # degrees offset
                for idx_j, idx in enumerate(comp):
                    angle = 2 * np.pi * (idx_j / k)
                    lat_adj[idx] = cy + np.sin(angle) * radius
                    lon_adj[idx] = cx + np.cos(angle) * radius

            grouped_agg['lat_adj'] = lat_adj
            grouped_agg['lon_adj'] = lon_adj
            label_text = [f"<b>{loc}</b><br>{int(c):,}" for loc, c in
                          zip(grouped_agg['Location'], grouped_agg['Cases'])]
            fig.add_trace(go.Scattergeo(
                lon=grouped_agg['lon_adj'], lat=grouped_agg['lat_adj'],
                mode='text',
                text=label_text,
                textfont=dict(size=14, color="#F9D9FF", family='Arial Black'),
                hoverinfo='skip'
            ))

        # Use stereographic projection but match Expander 5's geo styling for consistency
        fig.update_geos(
            projection_type='stereographic',
            resolution=50,
            showcountries=True, countrycolor="#E8DED9", countrywidth=2.5,
            landcolor="#1a1f2b", showocean=True, oceancolor="#0d1424"
        )

        fig.update_layout(
            title=f"<b>Time-of-Day Region Hotspots</b> ({t_from.strftime('%H:%M')} - {t_to.strftime('%H:%M')})",
            template='plotly_dark',
            height=800,
            margin=dict(l=0, r=0, t=60, b=0),
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)


