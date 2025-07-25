import streamlit as st
import fastf1
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import os
import tempfile
from datetime import datetime

# Import utility modules
from utils.data_loader import DataLoader
from utils.visualizations import create_telemetry_plot, create_tire_strategy_plot, create_race_progression_plot
from utils.track_dominance import create_track_dominance_map
from utils.constants import TEAM_COLORS, DRIVER_TEAMS, GRANDS_PRIX, SESSIONS
from utils.formatters import format_lap_time, format_sector_time, get_lap_time_color_class, get_position_change_text

# Configure page
st.set_page_config(
    page_title="F1 Data Analysis Platform",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Professional F1 Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #DC0000 0%, #FF4444 50%, #00D2BE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.8rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(35, 39, 47, 0.8), rgba(24, 25, 26, 0.9));
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(0, 210, 190, 0.2);
        margin: 0.5rem 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .driver-tag {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 0.3rem 0.2rem;
        color: white;
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .lap-time {
        font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
        font-weight: 600;
        font-size: 1.1rem;
        background: linear-gradient(135deg, #23272F, #2A2E36);
        padding: 0.5rem 1rem;
        border-radius: 8px;
        border: 1px solid rgba(0, 210, 190, 0.3);
        display: inline-block;
        margin: 0.2rem;
    }
    
    .sector-time {
        font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
        font-weight: 500;
        font-size: 0.9rem;
        color: #B0B8C3;
    }
    
    .position-badge {
        display: inline-block;
        width: 2rem;
        height: 2rem;
        border-radius: 50%;
        text-align: center;
        line-height: 2rem;
        font-weight: 700;
        font-size: 0.9rem;
        margin-right: 0.5rem;
    }
    
    .fastest-lap {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        color: #000;
    }
    
    .second-lap {
        background: linear-gradient(135deg, #C0C0C0, #A8A8A8);
        color: #000;
    }
    
    .third-lap {
        background: linear-gradient(135deg, #CD7F32, #B8860B);
        color: #fff;
    }
    
    .stSelectbox > div > div {
        background-color: rgba(35, 39, 47, 0.8);
        border: 1px solid rgba(0, 210, 190, 0.2);
        border-radius: 8px;
    }
    
    .stMultiSelect > div > div {
        background-color: rgba(35, 39, 47, 0.8);
        border: 1px solid rgba(0, 210, 190, 0.2);
        border-radius: 8px;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, rgba(35, 39, 47, 0.95), rgba(24, 25, 26, 0.95));
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(35, 39, 47, 0.6);
        border-radius: 8px;
        border: 1px solid rgba(0, 210, 190, 0.2);
        padding: 0.5rem 1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0, 210, 190, 0.2), rgba(220, 0, 0, 0.1));
        border: 1px solid rgba(0, 210, 190, 0.5);
    }
    
    /* Enhanced Table Styling */
    .stDataFrame {
        background: linear-gradient(135deg, rgba(35, 39, 47, 0.9), rgba(24, 25, 26, 0.95));
        border-radius: 12px;
        border: 1px solid rgba(0, 210, 190, 0.3);
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
    
    .stDataFrame thead tr th {
        background: linear-gradient(135deg, #DC0000, #FF4444);
        color: white !important;
        font-weight: 700;
        text-align: center !important;
        vertical-align: middle !important;
        padding: 1rem 0.5rem !important;
        border: none !important;
        font-size: 0.95rem;
        letter-spacing: 0.5px;
    }
    
    .stDataFrame tbody tr td {
        text-align: center !important;
        vertical-align: middle !important;
        padding: 0.8rem 0.5rem !important;
        border-bottom: 1px solid rgba(0, 210, 190, 0.1) !important;
        border-left: none !important;
        border-right: none !important;
        background: rgba(35, 39, 47, 0.7);
        color: #E8E8E8 !important;
        font-size: 0.9rem;
    }
    
    .stDataFrame tbody tr:nth-child(even) td {
        background: rgba(24, 25, 26, 0.8);
    }
    
    .stDataFrame tbody tr:hover td {
        background: rgba(0, 210, 190, 0.1) !important;
        transform: scale(1.01);
        transition: all 0.2s ease;
    }
    
    /* Enhanced Metric Cards */
    .driver-comparison-card {
        background: linear-gradient(135deg, rgba(35, 39, 47, 0.95), rgba(24, 25, 26, 0.98));
        padding: 1.8rem;
        border-radius: 16px;
        border: 1px solid rgba(0, 210, 190, 0.3);
        margin: 1rem 0;
        backdrop-filter: blur(15px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .driver-comparison-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
        border-color: rgba(0, 210, 190, 0.5);
    }
    
    .sector-comparison-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr 1fr 2fr;
        gap: 1rem;
        align-items: center;
        padding: 1rem;
        background: linear-gradient(135deg, rgba(35, 39, 47, 0.8), rgba(24, 25, 26, 0.9));
        border-radius: 12px;
        border: 1px solid rgba(0, 210, 190, 0.2);
        margin: 0.5rem 0;
        text-align: center;
    }
    
    .sector-comparison-grid:hover {
        background: linear-gradient(135deg, rgba(0, 210, 190, 0.1), rgba(220, 0, 0, 0.05));
        border-color: rgba(0, 210, 190, 0.4);
        transform: translateX(5px);
        transition: all 0.3s ease;
    }
    
    /* Enhanced Typography */
    .lap-time-large {
        font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
        font-weight: 700;
        font-size: 1.8rem;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .sector-time-enhanced {
        font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
        font-weight: 600;
        font-size: 1.1rem;
        color: #00D2BE;
        background: rgba(0, 210, 190, 0.1);
        padding: 0.5rem 1rem;
        border-radius: 8px;
        border: 1px solid rgba(0, 210, 190, 0.3);
        text-align: center;
        display: inline-block;
        min-width: 80px;
    }
    
    .team-badge-enhanced {
        display: inline-block;
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        font-weight: 700;
        font-size: 0.9rem;
        margin: 0.5rem;
        color: white;
        text-shadow: 0 1px 2px rgba(0,0,0,0.8);
        backdrop-filter: blur(10px);
        border: 2px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        text-align: center;
    }
    
    /* Enhanced Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #DC0000, #FF4444);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(220, 0, 0, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #FF4444, #DC0000);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(220, 0, 0, 0.4);
    }
    
    /* Loading Spinner Enhancement */
    .stSpinner {
        border-color: rgba(0, 210, 190, 0.3);
        border-top-color: #00D2BE;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_loader' not in st.session_state:
    st.session_state.data_loader = DataLoader()

def main():
    st.markdown('<h1 class="main-header">🏎️ Formula 1 Data Analysis Platform</h1>', unsafe_allow_html=True)
    
    # Sidebar for session selection
    with st.sidebar:
        st.header("📊 Session Selection")
        
        # Year selection
        current_year = datetime.now().year
        years = list(range(2018, current_year + 1))
        selected_year = st.selectbox("Season", years, index=len(years)-1)
        
        # Grand Prix selection
        selected_gp = st.selectbox("Grand Prix", GRANDS_PRIX)
        
        # Session type selection
        session_types = list(SESSIONS.keys())
        selected_session = st.selectbox("Session Type", session_types)
        
        # Load session button
        if st.button("🔄 Load Session Data", type="primary"):
            with st.spinner("Loading F1 session data..."):
                try:
                    success = st.session_state.data_loader.load_session(
                        selected_year, selected_gp, SESSIONS[selected_session]
                    )
                    if success:
                        st.success("✅ Session data loaded successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to load session data")
                except Exception as e:
                    st.error(f"❌ Error loading data: {str(e)}")
        
        # Driver selection (only show if session is loaded)
        if hasattr(st.session_state.data_loader, 'session') and st.session_state.data_loader.session is not None:
            st.header("🏁 Driver Selection")
            available_drivers = st.session_state.data_loader.get_available_drivers()
            
            if available_drivers:
                selected_drivers = st.multiselect(
                    "Select Drivers for Comparison",
                    available_drivers,
                    default=available_drivers[:2] if len(available_drivers) >= 2 else available_drivers
                )
                
                # Display selected drivers with team colors
                if selected_drivers:
                    st.markdown("**Selected Drivers:**")
                    for driver in selected_drivers:
                        team = DRIVER_TEAMS.get(driver, 'Unknown')
                        color = TEAM_COLORS.get(team, '#FFFFFF')
                        st.markdown(f'<span class="driver-tag" style="background-color: {color};">{driver} ({team})</span>', 
                                  unsafe_allow_html=True)
    
    # Main content area
    if not hasattr(st.session_state.data_loader, 'session') or st.session_state.data_loader.session is None:
        # Welcome screen
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.info("👈 Please select a season, Grand Prix, and session type from the sidebar to begin analysis.")
            
            st.markdown("""
            ### 🚀 Features Available:
            - **📈 Telemetry Analysis** - Speed traces, throttle/brake data, gear shifts
            - **🗺️ Track Dominance Maps** - Fastest mini-sector visualization
            - **⏱️ Lap Time Comparison** - Detailed timing analysis
            - **🔧 Tire Strategy** - Compound usage and pit stop analysis
            - **📊 Race Progression** - Position changes throughout the race
            - **💾 Data Export** - Download charts and data for further analysis
            
            ### 📋 Available Data:
            - **Seasons:** 2018 - Present
            - **Sessions:** Practice, Qualifying, Sprint, Race
            - **Telemetry:** Speed, throttle, brake, gear, tire data
            - **Live Data:** Available 30-120 minutes after session end
            """)
        return
    
    # Session info display
    session_info = st.session_state.data_loader.get_session_info()
    if session_info:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🏁 Event", session_info['event_name'])
        with col2:
            st.metric("📅 Date", session_info['date'])
        with col3:
            st.metric("🏎️ Session", session_info['session_name'])
        with col4:
            st.metric("🌍 Circuit", session_info['circuit'])
    
    # Check if drivers are selected
    selected_drivers = []
    if hasattr(st.session_state.data_loader, 'session') and st.session_state.data_loader.session is not None:
        available_drivers = st.session_state.data_loader.get_available_drivers()
        if available_drivers:
            selected_drivers = st.multiselect(
                "Select Drivers for Comparison",
                available_drivers,
                default=available_drivers[:2] if len(available_drivers) >= 2 else available_drivers,
                key="main_driver_selection"
            )
    
    if not selected_drivers:
        st.warning("⚠️ Please select at least one driver from the sidebar to view analysis.")
        return
    
    # Analysis tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Telemetry Analysis", 
        "🗺️ Track Dominance", 
        "⏱️ Lap Comparison", 
        "🔧 Tire Strategy", 
        "📊 Race Progression"
    ])
    
    with tab1:
        st.header("📈 Telemetry Analysis")
        
        if len(selected_drivers) >= 1:
            telemetry_type = st.selectbox(
                "Select Telemetry Data",
                ["Speed", "Throttle", "Brake", "RPM", "Gear"]
            )
            
            with st.spinner("Generating telemetry visualization..."):
                try:
                    fig = create_telemetry_plot(
                        st.session_state.data_loader,
                        selected_drivers,
                        telemetry_type.lower()
                    )
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Export button
                        if st.button("💾 Export Telemetry Chart"):
                            fig.write_html("telemetry_chart.html")
                            st.success("Chart exported as telemetry_chart.html")
                    else:
                        st.error("Unable to generate telemetry plot")
                except Exception as e:
                    st.error(f"Error generating telemetry plot: {str(e)}")
        else:
            st.info("Select at least one driver to view telemetry analysis.")
    
    with tab2:
        st.header("🗺️ Track Dominance Map")
        
        if len(selected_drivers) >= 2:
            col1, col2 = st.columns([3, 1])
            
            with col2:
                st.subheader("⚙️ Settings")
                num_sectors = st.slider("Mini-sectors", 50, 500, 200, 25)
                show_track_outline = st.checkbox("Show track outline", True)
            
            with col1:
                with st.spinner("Generating track dominance map..."):
                    try:
                        fig = create_track_dominance_map(
                            st.session_state.data_loader,
                            selected_drivers,
                            num_sectors,
                            show_track_outline
                        )
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Export button
                            if st.button("💾 Export Track Map"):
                                fig.write_html("track_dominance_map.html")
                                st.success("Map exported as track_dominance_map.html")
                        else:
                            st.error("Unable to generate track dominance map")
                    except Exception as e:
                        st.error(f"Error generating track map: {str(e)}")
        else:
            st.info("Select at least two drivers to view track dominance analysis.")
    
    with tab3:
        st.header("⏱️ Lap Time Comparison")
        
        if selected_drivers:
            with st.spinner("Analyzing lap times..."):
                try:
                    lap_data = st.session_state.data_loader.get_lap_comparison(selected_drivers)
                    
                    if lap_data is not None and not lap_data.empty:
                        # Professional Fastest Lap Times Display
                        st.subheader("🏆 Fastest Lap Times")
                        fastest_laps = lap_data.groupby('Driver')['LapTime_seconds'].min().sort_values()
                        
                        cols = st.columns(len(selected_drivers))
                        for i, (driver, lap_time_seconds) in enumerate(fastest_laps.items()):
                            with cols[i]:
                                team = DRIVER_TEAMS.get(driver, 'Unknown')
                                color = TEAM_COLORS.get(team, '#FFFFFF')
                                formatted_time = format_lap_time(lap_time_seconds)
                                
                                if i == 0:
                                    st.markdown(f"""
                                    <div class="driver-comparison-card">
                                        <div class="position-badge fastest-lap">1</div>
                                        <div class="team-badge-enhanced" style="background-color: {color};">{driver}</div>
                                        <div class="lap-time-large">{formatted_time}</div>
                                        <div style="color: #FFD700; font-weight: 600; font-size: 0.9rem; margin-top: 0.5rem;">FASTEST LAP</div>
                                        <div style="color: {color}; font-size: 0.8rem; margin-top: 0.2rem;">{team}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                elif i == 1:
                                    gap = lap_time_seconds - fastest_laps.iloc[0]
                                    st.markdown(f"""
                                    <div class="driver-comparison-card">
                                        <div class="position-badge second-lap">2</div>
                                        <div class="team-badge-enhanced" style="background-color: {color};">{driver}</div>
                                        <div class="lap-time-large">{formatted_time}</div>
                                        <div style="color: #C0C0C0; font-weight: 600; font-size: 0.9rem; margin-top: 0.5rem;">+{gap:.3f}s</div>
                                        <div style="color: {color}; font-size: 0.8rem; margin-top: 0.2rem;">{team}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                elif i == 2:
                                    gap = lap_time_seconds - fastest_laps.iloc[0]
                                    st.markdown(f"""
                                    <div class="driver-comparison-card">
                                        <div class="position-badge third-lap">3</div>
                                        <div class="team-badge-enhanced" style="background-color: {color};">{driver}</div>
                                        <div class="lap-time-large">{formatted_time}</div>
                                        <div style="color: #CD7F32; font-weight: 600; font-size: 0.9rem; margin-top: 0.5rem;">+{gap:.3f}s</div>
                                        <div style="color: {color}; font-size: 0.8rem; margin-top: 0.2rem;">{team}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    gap = lap_time_seconds - fastest_laps.iloc[0]
                                    st.markdown(f"""
                                    <div class="driver-comparison-card">
                                        <div class="position-badge" style="background: #404040; color: white;">{i+1}</div>
                                        <div class="team-badge-enhanced" style="background-color: {color};">{driver}</div>
                                        <div class="lap-time-large">{formatted_time}</div>
                                        <div style="color: #999; font-weight: 600; font-size: 0.9rem; margin-top: 0.5rem;">+{gap:.3f}s</div>
                                        <div style="color: {color}; font-size: 0.8rem; margin-top: 0.2rem;">{team}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                        
                        # Sector Analysis
                        st.subheader("🎯 Sector Analysis")
                        
                        sector_data = []
                        for driver in selected_drivers:
                            driver_data = lap_data[lap_data['Driver'] == driver]
                            if not driver_data.empty:
                                fastest_lap_idx = driver_data['LapTime_seconds'].idxmin()
                                fastest_lap = driver_data.loc[fastest_lap_idx]
                                
                                sector_data.append({
                                    'Driver': driver,
                                    'Team': DRIVER_TEAMS.get(driver, 'Unknown'),
                                    'S1': fastest_lap.get('Sector1Time', None),
                                    'S2': fastest_lap.get('Sector2Time', None),
                                    'S3': fastest_lap.get('Sector3Time', None),
                                    'LapTime': fastest_lap['LapTime_seconds']
                                })
                        
                        if sector_data:
                            # Create enhanced sector comparison table
                            for i, data in enumerate(sector_data):
                                driver = data['Driver']
                                team = data['Team']
                                color = TEAM_COLORS.get(team, '#FFFFFF')
                                
                                s1_time = format_sector_time(data['S1']) if data['S1'] else "N/A"
                                s2_time = format_sector_time(data['S2']) if data['S2'] else "N/A"
                                s3_time = format_sector_time(data['S3']) if data['S3'] else "N/A"
                                formatted_lap = format_lap_time(data['LapTime'])
                                
                                st.markdown(f"""
                                <div class="sector-comparison-grid">
                                    <div>
                                        <div class="team-badge-enhanced" style="background-color: {color};">
                                            {driver}
                                        </div>
                                    </div>
                                    <div>
                                        <div class="sector-time-enhanced">
                                            {s1_time}
                                        </div>
                                        <div style="font-size: 0.7rem; color: #888; margin-top: 0.2rem;">Sector 1</div>
                                    </div>
                                    <div>
                                        <div class="sector-time-enhanced">
                                            {s2_time}
                                        </div>
                                        <div style="font-size: 0.7rem; color: #888; margin-top: 0.2rem;">Sector 2</div>
                                    </div>
                                    <div>
                                        <div class="sector-time-enhanced">
                                            {s3_time}
                                        </div>
                                        <div style="font-size: 0.7rem; color: #888; margin-top: 0.2rem;">Sector 3</div>
                                    </div>
                                    <div>
                                        <div class="lap-time-large">
                                            {formatted_lap}
                                        </div>
                                        <div style="font-size: 0.7rem; color: #888; margin-top: 0.2rem;">Total Time</div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # Enhanced Lap Time Distribution
                        st.subheader("📊 Lap Time Distribution")
                        fig = px.box(
                            lap_data, 
                            x='Driver', 
                            y='LapTime_seconds',
                            color='Driver',
                            color_discrete_map={
                                driver: TEAM_COLORS.get(DRIVER_TEAMS.get(driver, 'Unknown'), '#FFFFFF')
                                for driver in selected_drivers
                            },
                            title="Lap Time Consistency Analysis"
                        )
                        fig.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font_color='white',
                            title_font_size=18,
                            xaxis_title="Driver",
                            yaxis_title="Lap Time (seconds)"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Professional Detailed Lap Times by Driver
                        st.subheader("📋 Detailed Lap Times by Driver")
                        
                        for driver in selected_drivers:
                            driver_data = lap_data[lap_data['Driver'] == driver].copy()
                            if not driver_data.empty:
                                team = DRIVER_TEAMS.get(driver, 'Unknown')
                                color = TEAM_COLORS.get(team, '#FFFFFF')
                                
                                with st.expander(f"🏎️ {driver} ({team}) - {len(driver_data)} laps", expanded=False):
                                    driver_data['Formatted_LapTime'] = driver_data['LapTime_seconds'].apply(format_lap_time)
                                    driver_data['Formatted_S1'] = driver_data['Sector1Time'].apply(lambda x: format_sector_time(x) if pd.notna(x) else "N/A")
                                    driver_data['Formatted_S2'] = driver_data['Sector2Time'].apply(lambda x: format_sector_time(x) if pd.notna(x) else "N/A")
                                    driver_data['Formatted_S3'] = driver_data['Sector3Time'].apply(lambda x: format_sector_time(x) if pd.notna(x) else "N/A")
                                    
                                    display_data = driver_data[['LapNumber', 'Formatted_LapTime', 'Formatted_S1', 'Formatted_S2', 'Formatted_S3', 'Compound', 'TyreLife']].copy()
                                    display_data.columns = ['Lap', 'Lap Time', 'Sector 1', 'Sector 2', 'Sector 3', 'Compound', 'Tyre Age']
                                    
                                    st.dataframe(
                                        display_data,
                                        use_container_width=True,
                                        hide_index=True
                                    )
                        
                    else:
                        st.error("No lap time data available for selected drivers")
                        
                except Exception as e:
                    st.error(f"Error analyzing lap times: {str(e)}")
    
    with tab4:
        st.header("🔧 Tire Strategy Analysis")
        
        if selected_drivers:
            with st.spinner("Analyzing tire strategies..."):
                try:
                    fig = create_tire_strategy_plot(st.session_state.data_loader, selected_drivers)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Tire compound usage summary
                        st.subheader("📊 Tire Compound Usage")
                        tire_data = st.session_state.data_loader.get_tire_data(selected_drivers)
                        if tire_data is not None and not tire_data.empty:
                            compound_summary = tire_data.groupby(['Driver', 'Compound']).size().unstack(fill_value=0)
                            st.dataframe(compound_summary, use_container_width=True)
                        
                        # Export button
                        if st.button("💾 Export Tire Strategy"):
                            fig.write_html("tire_strategy.html")
                            st.success("Strategy chart exported as tire_strategy.html")
                    else:
                        st.error("Unable to generate tire strategy plot")
                except Exception as e:
                    st.error(f"Error analyzing tire strategy: {str(e)}")
    
    with tab5:
        st.header("📊 Race Progression")
        
        if selected_drivers and SESSIONS[selected_session] == 'R':
            with st.spinner("Analyzing race progression..."):
                try:
                    fig = create_race_progression_plot(st.session_state.data_loader, selected_drivers)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Professional Position Changes Analysis
                        st.subheader("📈 Position Changes Summary")
                        position_data = st.session_state.data_loader.get_position_data(selected_drivers)
                        
                        if position_data is not None and not position_data.empty:
                            start_positions = position_data.groupby('Driver')['Position'].first()
                            end_positions = position_data.groupby('Driver')['Position'].last()
                            position_changes = start_positions - end_positions
                            
                            # Create professional cards for position changes
                            cols = st.columns(len(selected_drivers))
                            for i, driver in enumerate(selected_drivers):
                                if driver in position_changes:
                                    with cols[i]:
                                        change = position_changes[driver]
                                        start_pos = int(start_positions[driver])
                                        end_pos = int(end_positions[driver])
                                        team = DRIVER_TEAMS.get(driver, 'Unknown')
                                        color = TEAM_COLORS.get(team, '#FFFFFF')
                                        
                                        change_text, change_type = get_position_change_text(start_pos, end_pos)
                                        
                                        if change > 0:
                                            change_color = "#00FF88"
                                            arrow = "📈"
                                        elif change < 0:
                                            change_color = "#FF4444"
                                            arrow = "📉"
                                        else:
                                            change_color = "#888888"
                                            arrow = "➡️"
                                        
                                        st.markdown(f"""
                                        <div class="driver-comparison-card">
                                            <div class="team-badge-enhanced" style="background-color: {color};">
                                                {driver}
                                            </div>
                                            <div style="font-size: 2.5rem; margin: 1rem 0;">
                                                {arrow}
                                            </div>
                                            <div style="font-size: 1.4rem; font-weight: 700; margin: 0.5rem 0;">
                                                P{start_pos} → P{end_pos}
                                            </div>
                                            <div style="color: {change_color}; font-weight: 700; font-size: 1.1rem; margin: 0.5rem 0;">
                                                {change_text[2:]}
                                            </div>
                                            <div style="color: {color}; font-size: 0.8rem; margin-top: 0.5rem;">
                                                {team}
                                            </div>
                                        </div>
                                        """, unsafe_allow_html=True)
                            
                            # Add race statistics
                            st.subheader("🏁 Race Statistics")
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                biggest_gain = position_changes.max()
                                best_climber = position_changes.idxmax() if biggest_gain > 0 else None
                                if best_climber:
                                    team = DRIVER_TEAMS.get(best_climber, 'Unknown')
                                    st.markdown(f"""
                                    <div class="driver-comparison-card">
                                        <div style="color: #00FF88; font-size: 1.2rem; font-weight: 700; margin-bottom: 1rem;">
                                            🚀 BIGGEST CLIMBER
                                        </div>
                                        <div class="team-badge-enhanced" style="background-color: {TEAM_COLORS.get(team, '#FFFFFF')};">
                                            {best_climber}
                                        </div>
                                        <div style="color: #00FF88; font-size: 1.8rem; font-weight: 700; margin: 1rem 0;">
                                            +{biggest_gain} positions
                                        </div>
                                        <div style="color: {TEAM_COLORS.get(team, '#FFFFFF')}; font-size: 0.8rem;">
                                            {team}
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            with col2:
                                biggest_loss = position_changes.min()
                                worst_drop = position_changes.idxmin() if biggest_loss < 0 else None
                                if worst_drop:
                                    team = DRIVER_TEAMS.get(worst_drop, 'Unknown')
                                    st.markdown(f"""
                                    <div class="driver-comparison-card">
                                        <div style="color: #FF4444; font-size: 1.2rem; font-weight: 700; margin-bottom: 1rem;">
                                            📉 BIGGEST DROP
                                        </div>
                                        <div class="team-badge-enhanced" style="background-color: {TEAM_COLORS.get(team, '#FFFFFF')};">
                                            {worst_drop}
                                        </div>
                                        <div style="color: #FF4444; font-size: 1.8rem; font-weight: 700; margin: 1rem 0;">
                                            {biggest_loss} positions
                                        </div>
                                        <div style="color: {TEAM_COLORS.get(team, '#FFFFFF')}; font-size: 0.8rem;">
                                            {team}
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            with col3:
                                total_laps = position_data['LapNumber'].max()
                                avg_changes = abs(position_changes).mean()
                                st.markdown(f"""
                                <div class="driver-comparison-card">
                                    <div style="color: #00D2BE; font-size: 1.2rem; font-weight: 700; margin-bottom: 1rem;">
                                        📊 RACE STATISTICS
                                    </div>
                                    <div style="font-size: 1.1rem; line-height: 1.8; margin: 1rem 0;">
                                        <div style="color: #00D2BE; font-weight: 600;">
                                            <strong>Total Laps:</strong> <span style="color: white;">{total_laps}</span>
                                        </div>
                                        <div style="color: #00D2BE; font-weight: 600;">
                                            <strong>Avg Change:</strong> <span style="color: white;">{avg_changes:.1f} positions</span>
                                        </div>
                                        <div style="color: #00D2BE; font-weight: 600;">
                                            <strong>Drivers:</strong> <span style="color: white;">{len(selected_drivers)} tracked</span>
                                        </div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # Export button
                        if st.button("💾 Export Race Progression"):
                            fig.write_html("race_progression.html")
                            st.success("Progression chart exported as race_progression.html")
                    else:
                        st.error("Unable to generate race progression plot")
                except Exception as e:
                    st.error(f"Error analyzing race progression: {str(e)}")
        else:
            if SESSIONS[selected_session] != 'R':
                st.info("Race progression analysis is only available for Race sessions.")
            else:
                st.info("Select drivers to view race progression analysis.")

if __name__ == "__main__":
    main()
