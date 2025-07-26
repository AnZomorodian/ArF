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
from utils.constants import TEAM_COLORS, DRIVER_TEAMS, GRANDS_PRIX, SESSIONS, TIRE_COLORS
from utils.formatters import format_lap_time, format_sector_time, get_lap_time_color_class, get_position_change_text, format_average_lap_time
from utils.advanced_analytics import AdvancedF1Analytics
from utils.weather_analytics import WeatherAnalytics
from utils.race_strategy import RaceStrategyAnalyzer
from utils.tire_performance import TirePerformanceAnalyzer
from utils.stress_index import DriverStressAnalyzer
from utils.downforce_analysis import DownforceAnalyzer
from utils.driver_manager import DynamicDriverManager
from utils.enhanced_analytics import EnhancedF1Analytics

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
    
    /* Enhanced Position Badges */
    .position-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        font-weight: 700;
        font-size: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    }
    
    .position-badge.fastest-lap {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        color: #000;
        animation: pulse 2s infinite;
    }
    
    .position-badge.second-lap {
        background: linear-gradient(135deg, #C0C0C0, #A0A0A0);
        color: #000;
    }
    
    .position-badge.third-lap {
        background: linear-gradient(135deg, #CD7F32, #B8860B);
        color: #000;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); box-shadow: 0 4px 16px rgba(255, 215, 0, 0.3); }
        50% { transform: scale(1.05); box-shadow: 0 6px 20px rgba(255, 215, 0, 0.5); }
        100% { transform: scale(1); box-shadow: 0 4px 16px rgba(255, 215, 0, 0.3); }
    }
    
    /* Enhanced Driver Selection */
    .driver-selection-container {
        background: linear-gradient(135deg, rgba(35, 39, 47, 0.6), rgba(24, 25, 26, 0.8));
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid rgba(0, 210, 190, 0.2);
        margin: 1rem 0 2rem 0;
        backdrop-filter: blur(10px);
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
    
    /* Force Dark Background */
    .main .block-container {
        background-color: #0E1117 !important;
    }
    
    .stApp {
        background-color: #0E1117 !important;
    }
    
    /* Enhanced Driver Selection with Minimal Design */
    .driver-selection-container {
        background: linear-gradient(135deg, rgba(35, 39, 47, 0.95), rgba(24, 25, 26, 0.98));
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(0, 210, 190, 0.2);
        backdrop-filter: blur(15px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
    
    .driver-selection-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .driver-option {
        background: linear-gradient(135deg, rgba(35, 39, 47, 0.8), rgba(24, 25, 26, 0.9));
        border: 2px solid rgba(0, 210, 190, 0.2);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .driver-option:hover {
        border-color: rgba(0, 210, 190, 0.5);
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
    }
    
    .driver-option.selected {
        border-color: #00D2BE;
        background: linear-gradient(135deg, rgba(0, 210, 190, 0.1), rgba(35, 39, 47, 0.9));
        box-shadow: 0 0 20px rgba(0, 210, 190, 0.3);
    }
    
    .driver-number {
        font-size: 2rem;
        font-weight: 900;
        opacity: 0.3;
        position: absolute;
        top: 0.5rem;
        right: 0.5rem;
        line-height: 1;
    }
    
    .driver-info {
        position: relative;
        z-index: 2;
    }
    
    .driver-name {
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: white;
    }
    
    .driver-team {
        font-size: 0.85rem;
        opacity: 0.8;
        margin-bottom: 0.3rem;
    }
    
    /* Sidebar Enhancement */
    .css-1d391kg {
        background: linear-gradient(180deg, rgba(14, 17, 23, 0.98), rgba(24, 25, 26, 0.95)) !important;
    }
    
    /* Multiselect styling */
    .stMultiSelect > label {
        color: white !important;
        font-weight: 600;
    }
    
    .stMultiSelect [data-baseweb=select] {
        background: rgba(35, 39, 47, 0.9) !important;
        border: 1px solid rgba(0, 210, 190, 0.3) !important;
        border-radius: 8px !important;
    }
    
    .stMultiSelect [data-baseweb=tag] {
        background-color: rgba(0, 210, 190, 0.2) !important;
        border: 1px solid rgba(0, 210, 190, 0.4) !important;
        color: #00D2BE !important;
    }
    
    /* Selectbox styling */
    .stSelectbox > label {
        color: white !important;
        font-weight: 600;
    }
    
    .stSelectbox [data-baseweb=select] {
        background: rgba(35, 39, 47, 0.9) !important;
        border: 1px solid rgba(0, 210, 190, 0.3) !important;
        border-radius: 8px !important;
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
        
        # Enhanced Driver Selection (only show if session is loaded)
        if hasattr(st.session_state.data_loader, 'session') and st.session_state.data_loader.session is not None:
            st.markdown('<div class="driver-selection-container">', unsafe_allow_html=True)
            st.markdown("### 🏁 Driver Selection")
            st.markdown("Choose drivers to compare in the analysis below")
            
            # Use dynamic driver manager to get current session driver info
            driver_manager = DynamicDriverManager(st.session_state.data_loader.session)
            driver_info = driver_manager.get_driver_info()
            team_mappings = driver_manager.get_team_mappings()
            team_colors = driver_manager.get_team_colors()
            
            available_drivers = list(driver_info.keys())
            
            if available_drivers:
                # Enhanced driver selection with no default selection
                selected_drivers = st.multiselect(
                    "Select Drivers for Comparison",
                    available_drivers,
                    default=[],  # Start with no drivers selected
                    format_func=lambda x: f"{driver_info[x]['abbreviation']} - {driver_info[x]['team_name']}",
                    help="Select 2-4 drivers for optimal comparison visualization"
                )
                
                # Display selected drivers with enhanced cards showing current team info
                if selected_drivers:
                    st.markdown("### 🎯 Selected Drivers")
                    driver_cols = st.columns(len(selected_drivers))
                    
                    for idx, driver in enumerate(selected_drivers):
                        with driver_cols[idx]:
                            driver_data = driver_info[driver]
                            team_name = driver_data['team_name']
                            team_color = team_colors.get(team_name, '#808080')
                            
                            st.markdown(f"""
                            <div class="driver-card" style="border-left: 4px solid {team_color};">
                                <div class="driver-info">
                                    <div class="driver-name">{driver_data['abbreviation']}</div>
                                    <div class="driver-team" style="color: {team_color};">{team_name}</div>
                                    <div style="font-size: 0.75rem; opacity: 0.7;">#{driver_data.get('driver_number', 'N/A')}</div>
                                </div>
                                <div class="driver-number">#{driver_data.get('driver_number', 'N/A')}</div>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("👆 Select drivers above to begin analysis")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
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
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "📈 Telemetry Analysis", 
        "🗺️ Track Dominance", 
        "⏱️ Lap Comparison", 
        "🔧 Tire Strategy", 
        "📊 Race Progression",
        "🧠 Advanced Analytics",
        "🛞 Tire Performance",
        "⚡ Stress Analysis",
        "🏎️ Downforce Config"
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
        st.header("🔧 Enhanced Tire Strategy Analysis")
        
        if selected_drivers:
            with st.spinner("Analyzing enhanced tire strategies..."):
                try:
                    fig = create_tire_strategy_plot(st.session_state.data_loader, selected_drivers)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Enhanced tire strategy statistics
                        st.subheader("📊 Detailed Tire Strategy Statistics")
                        tire_data = st.session_state.data_loader.get_tire_data(selected_drivers)
                        if tire_data is not None and not tire_data.empty:
                            
                            # Create tire usage summary with enhanced styling
                            tire_usage = tire_data.groupby(['Driver', 'Compound']).size().reset_index(name='Laps')
                            
                            # Display statistics in columns
                            stat_cols = st.columns(len(selected_drivers))
                            
                            for i, driver in enumerate(selected_drivers):
                                with stat_cols[i]:
                                    driver_tire_data = tire_usage[tire_usage['Driver'] == driver]
                                    team = DRIVER_TEAMS.get(driver, 'Unknown')
                                    team_color = TEAM_COLORS.get(team, '#FFFFFF')
                                    
                                    st.markdown(f"""
                                    <div class="metric-card">
                                        <div style="background: linear-gradient(135deg, {team_color}20, {team_color}40); border-left: 4px solid {team_color}; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                                            <h4 style="color: {team_color}; margin: 0; font-size: 1.2rem;">{driver}</h4>
                                            <span style="color: #888; font-size: 0.9rem;">{team}</span>
                                        </div>
                                    """, unsafe_allow_html=True)
                                    
                                    if not driver_tire_data.empty:
                                        total_laps = driver_tire_data['Laps'].sum()
                                        st.metric("Total Race Laps", total_laps)
                                        
                                        st.markdown("**Tire Compound Usage:**")
                                        for _, row in driver_tire_data.iterrows():
                                            compound = row['Compound']
                                            laps = row['Laps']
                                            percentage = (laps / total_laps * 100) if total_laps > 0 else 0
                                            tire_color = TIRE_COLORS.get(compound, '#808080')
                                            
                                            st.markdown(f"""
                                            <div style="display: flex; align-items: center; margin: 0.5rem 0; padding: 0.5rem; background: rgba(255,255,255,0.05); border-radius: 8px;">
                                                <div style="width: 24px; height: 24px; background-color: {tire_color}; border-radius: 50%; margin-right: 0.75rem; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>
                                                <span style="flex: 1; font-weight: 500;">{compound}</span>
                                                <div style="text-align: right;">
                                                    <div style="font-weight: 600; color: white;">{laps} laps</div>
                                                    <div style="font-size: 0.85rem; color: #888;">{percentage:.1f}%</div>
                                                </div>
                                            </div>
                                            """, unsafe_allow_html=True)
                                    else:
                                        st.info("No tire data available for this driver")
                                    
                                    st.markdown("</div>", unsafe_allow_html=True)
                            
                            # Compound performance comparison
                            st.subheader("🔍 Compound Performance Analysis")
                            if 'LapTime' in tire_data.columns:
                                # Filter out invalid lap times
                                valid_tire_data = tire_data[tire_data['LapTime'].notna()].copy()
                                if not valid_tire_data.empty:
                                    # Convert lap times to seconds for analysis
                                    valid_tire_data['LapTimeSeconds'] = valid_tire_data['LapTime'].dt.total_seconds()
                                    # Filter reasonable lap times (between 1 and 3 minutes)
                                    valid_tire_data = valid_tire_data[
                                        (valid_tire_data['LapTimeSeconds'] > 60) & 
                                        (valid_tire_data['LapTimeSeconds'] < 180)
                                    ]
                                    
                                    if not valid_tire_data.empty:
                                        compound_stats = valid_tire_data.groupby('Compound').agg({
                                            'LapTimeSeconds': ['mean', 'min', 'count', 'std']
                                        }).round(3)
                                        
                                        compound_stats.columns = ['Average Lap Time (s)', 'Best Lap Time (s)', 'Total Laps', 'Std Dev (s)']
                                        
                                        # Create enhanced dataframe display
                                        performance_data = []
                                        for compound in compound_stats.index:
                                            tire_color = TIRE_COLORS.get(compound, '#808080')
                                            avg_time = compound_stats.loc[compound, 'Average Lap Time (s)']
                                            best_time = compound_stats.loc[compound, 'Best Lap Time (s)']
                                            total_laps = int(compound_stats.loc[compound, 'Total Laps'])
                                            std_dev = compound_stats.loc[compound, 'Std Dev (s)']
                                            
                                            performance_data.append({
                                                'Compound': compound,
                                                'Color': tire_color,
                                                'Avg Time': f"{avg_time:.3f}s",
                                                'Best Time': f"{best_time:.3f}s",
                                                'Total Laps': total_laps,
                                                'Consistency': f"±{std_dev:.3f}s"
                                            })
                                        
                                        # Display performance table with colors
                                        for data in performance_data:
                                            st.markdown(f"""
                                            <div style="display: flex; align-items: center; padding: 0.75rem; margin: 0.5rem 0; background: rgba(255,255,255,0.05); border-radius: 12px; border-left: 4px solid {data['Color']};">
                                                <div style="width: 32px; height: 32px; background-color: {data['Color']}; border-radius: 50%; margin-right: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.3);"></div>
                                                <div style="flex: 1;">
                                                    <div style="font-weight: 600; font-size: 1.1rem; margin-bottom: 0.25rem;">{data['Compound']}</div>
                                                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 1rem; font-size: 0.9rem; color: #ccc;">
                                                        <div><strong>Avg:</strong> {data['Avg Time']}</div>
                                                        <div><strong>Best:</strong> {data['Best Time']}</div>
                                                        <div><strong>Laps:</strong> {data['Total Laps']}</div>
                                                        <div><strong>±:</strong> {data['Consistency']}</div>
                                                    </div>
                                                </div>
                                            </div>
                                            """, unsafe_allow_html=True)
                                    else:
                                        st.info("No valid lap time data available for compound analysis")
                                else:
                                    st.info("No lap time data available for performance analysis")
                            else:
                                st.info("Lap time data not available in the current dataset")
                        
                        # Export functionality
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("💾 Export Strategy Chart", use_container_width=True):
                                fig.write_html("enhanced_tire_strategy.html")
                                st.success("Enhanced strategy chart exported as enhanced_tire_strategy.html")
                        
                        with col2:
                            if st.button("📋 Export Strategy Data", use_container_width=True):
                                if tire_data is not None and not tire_data.empty:
                                    tire_data.to_csv("tire_strategy_data.csv", index=False)
                                    st.success("Strategy data exported as tire_strategy_data.csv")
                    else:
                        st.error("Unable to generate tire strategy plot - no data available")
                except Exception as e:
                    st.error(f"Error analyzing tire strategy: {str(e)}")
        else:
            st.info("Please select at least one driver from the sidebar to view enhanced tire strategy analysis.")
    
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
    
    with tab6:
        st.header("🧠 Advanced Analytics - Enhanced Performance Intelligence")
        
        if selected_drivers:
            # Initialize enhanced analytics modules
            session = st.session_state.data_loader.session
            analytics = AdvancedF1Analytics(session)
            enhanced_analytics = EnhancedF1Analytics(session)
            weather_analytics = WeatherAnalytics(session)
            strategy_analyzer = RaceStrategyAnalyzer(session)
            
            # Enhanced analytics sub-tabs
            adv_tab1, adv_tab2, adv_tab3, adv_tab4, adv_tab5, adv_tab6 = st.tabs([
                "🎯 Performance Index", "🧪 ML Clustering", "📈 Radar Analysis", 
                "🏁 Race Evolution", "🌤️ Weather Impact", "📊 Strategy Analysis"
            ])
            
            with adv_tab1:
                st.subheader("🎯 Driver Performance Index Analysis")
                
                # Calculate enhanced performance index
                performance_data = enhanced_analytics.calculate_driver_performance_index(selected_drivers)
                
                if not performance_data.empty:
                    # Display performance index cards
                    for _, driver_perf in performance_data.iterrows():
                        team_color = TEAM_COLORS.get(driver_perf['Team'], '#808080')
                        
                        st.markdown(f"""
                        <div class="metric-card">
                            <div style="background: linear-gradient(135deg, {team_color}20, {team_color}40); 
                                        border-left: 4px solid {team_color}; padding: 1.5rem; border-radius: 12px;">
                                <h3 style="color: {team_color}; margin: 0 0 0.5rem 0;">{driver_perf['Driver']} - {driver_perf['Team']}</h3>
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 1rem; margin-top: 1rem;">
                                    <div style="text-align: center;">
                                        <div style="font-size: 1.8rem; font-weight: 700; color: {team_color};">{driver_perf['Performance_Index']:.3f}</div>
                                        <div style="color: #888; font-size: 0.8rem;">Performance Index</div>
                                    </div>
                                    <div style="text-align: center;">
                                        <div style="font-size: 1.2rem; font-weight: 700; color: white;">{driver_perf['Consistency_Score']:.3f}</div>
                                        <div style="color: #888; font-size: 0.8rem;">Consistency</div>
                                    </div>
                                    <div style="text-align: center;">
                                        <div style="font-size: 1.2rem; font-weight: 700; color: white;">{driver_perf['Pace_Quality']:.3f}</div>
                                        <div style="color: #888; font-size: 0.8rem;">Pace Quality</div>
                                    </div>
                                    <div style="text-align: center;">
                                        <div style="font-size: 1.2rem; font-weight: 700; color: white;">{driver_perf['Overtake_Score']:.3f}</div>
                                        <div style="color: #888; font-size: 0.8rem;">Racecraft</div>
                                    </div>
                                    <div style="text-align: center;">
                                        <div style="font-size: 1.2rem; font-weight: 700; color: white;">{driver_perf['Tire_Efficiency']:.3f}</div>
                                        <div style="color: #888; font-size: 0.8rem;">Tire Management</div>
                                    </div>
                                    <div style="text-align: center;">
                                        <div style="font-size: 1.2rem; font-weight: 700; color: white;">{format_average_lap_time(driver_perf['Best_Lap'])}</div>
                                        <div style="color: #888; font-size: 0.8rem;">Best Lap</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Unable to calculate performance index for selected drivers.")
            
            with adv_tab2:
                st.subheader("🧪 Machine Learning Driver Clustering")
                
                performance_data = enhanced_analytics.calculate_driver_performance_index(selected_drivers)
                
                if not performance_data.empty and len(performance_data) >= 3:
                    clustering_chart = enhanced_analytics.create_performance_clustering(performance_data)
                    if clustering_chart:
                        st.plotly_chart(clustering_chart, use_container_width=True)
                        
                        st.markdown("""
                        **Clustering Analysis**: Using machine learning to group drivers based on their performance characteristics:
                        - **Elite Performers**: High consistency and pace quality
                        - **Consistent Drivers**: Reliable lap times with steady performance
                        - **Aggressive Racers**: High overtaking scores and sector dominance
                        - **Developing Talent**: Emerging performance patterns
                        """)
                else:
                    st.info("Need at least 3 drivers for meaningful clustering analysis.")
            
            with adv_tab3:
                st.subheader("📈 Driver Performance Radar Analysis")
                
                performance_data = enhanced_analytics.calculate_driver_performance_index(selected_drivers)
                
                if not performance_data.empty:
                    radar_chart = enhanced_analytics.create_performance_radar(performance_data)
                    if radar_chart:
                        st.plotly_chart(radar_chart, use_container_width=True)
                        
                        st.markdown("""
                        **Radar Analysis**: Multi-dimensional performance comparison across key metrics:
                        - **Consistency**: Lap time variation and reliability
                        - **Speed Consistency**: Maintaining pace across different track sections
                        - **Pace Quality**: Overall speed relative to session best
                        - **Overtaking**: Racecraft and position-gaining ability
                        - **Sector Dominance**: Performance in different track segments
                        - **Tire Management**: Efficiency in tire usage and degradation
                        """)
                else:
                    st.info("Performance data not available for radar analysis.")
            
            with adv_tab4:
                st.subheader("🏁 Race Pace Evolution Analysis")
                
                pace_data = enhanced_analytics.analyze_race_pace_evolution(selected_drivers)
                
                if not pace_data.empty:
                    fig = go.Figure()
                    
                    for driver in selected_drivers:
                        driver_pace = pace_data[pace_data['Driver'] == driver]
                        if not driver_pace.empty:
                            team = DRIVER_TEAMS.get(driver, 'Unknown')
                            color = TEAM_COLORS.get(team, '#FFFFFF')
                            
                            fig.add_trace(go.Scatter(
                                x=driver_pace['Lap'],
                                y=driver_pace['Pace'],
                                mode='lines+markers',
                                name=f"{driver} ({team})",
                                line=dict(color=color, width=3),
                                marker=dict(size=6, color=color),
                                hovertemplate=f'<b>{driver}</b><br>Lap: %{{x}}<br>Pace: %{{y:.3f}}s<extra></extra>'
                            ))
                    
                    fig.update_layout(
                        title='Race Pace Evolution Throughout Session',
                        xaxis_title='Lap Number',
                        yaxis_title='Lap Time (seconds)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Pace evolution data not available for analysis.")
            
            with adv_tab5:
                
                consistency_data = []
                for driver in selected_drivers:
                    consistency = analytics.calculate_driver_consistency(driver)
                    if consistency:
                        team = DRIVER_TEAMS.get(driver, 'Unknown')
                        team_color = TEAM_COLORS.get(team, '#FFFFFF')
                        
                        consistency_data.append({
                            'driver': driver,
                            'team': team,
                            'team_color': team_color,
                            'consistency_score': consistency['consistency_score'],
                            'mean_lap_time': consistency['mean_lap_time'],
                            'std_deviation': consistency['std_deviation'],
                            'total_laps': consistency['total_laps']
                        })
                
                # Display consistency metrics
                for data in consistency_data:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="background: linear-gradient(135deg, {data['team_color']}20, {data['team_color']}40); 
                                    border-left: 4px solid {data['team_color']}; padding: 1.5rem; border-radius: 12px;">
                            <h3 style="color: {data['team_color']}; margin: 0 0 0.5rem 0;">{data['driver']} - {data['team']}</h3>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; margin-top: 1rem;">
                                <div style="text-align: center;">
                                    <div style="font-size: 1.5rem; font-weight: 700; color: white;">{data['consistency_score']:.3f}</div>
                                    <div style="color: #888; font-size: 0.9rem;">Consistency Score</div>
                                </div>
                                <div style="text-align: center;">
                                    <div style="font-size: 1.5rem; font-weight: 700; color: white;">{format_average_lap_time(data['mean_lap_time'])}</div>
                                    <div style="color: #888; font-size: 0.9rem;">Average Lap Time</div>
                                </div>
                                <div style="text-align: center;">
                                    <div style="font-size: 1.5rem; font-weight: 700; color: white;">±{data['std_deviation']:.3f}s</div>
                                    <div style="color: #888; font-size: 0.9rem;">Standard Deviation</div>
                                </div>
                                <div style="text-align: center;">
                                    <div style="font-size: 1.5rem; font-weight: 700; color: white;">{data['total_laps']}</div>
                                    <div style="color: #888; font-size: 0.9rem;">Total Laps</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Tire degradation analysis
                st.subheader("🛞 Tire Degradation Analysis")
                degradation_driver = st.selectbox("Select driver for tire degradation analysis:", selected_drivers)
                
                if degradation_driver:
                    degradation_data = analytics.analyze_tire_degradation(degradation_driver)
                    
                    if degradation_data:
                        for stint_data in degradation_data:
                            compound = stint_data['compound']
                            tire_color = TIRE_COLORS.get(compound, '#808080')
                            
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, rgba(35, 39, 47, 0.8), rgba(24, 25, 26, 0.9)); 
                                        border-left: 4px solid {tire_color}; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">
                                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                                    <div style="width: 24px; height: 24px; background-color: {tire_color}; border-radius: 50%; margin-right: 0.75rem;"></div>
                                    <h4 style="color: white; margin: 0;">{compound} Compound</h4>
                                </div>
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 0.5rem; font-size: 0.9rem;">
                                    <div><strong>Stint Length:</strong> {stint_data['stint_length']} laps</div>
                                    <div><strong>Degradation Rate:</strong> {stint_data['degradation_rate']:.3f}s/lap</div>
                                    <div><strong>Total Degradation:</strong> {stint_data['total_degradation']:.3f}s</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No tire degradation data available for this driver.")
            
            with adv_tab2:
                st.subheader("Weather Evolution")
                try:
                    weather_plot = weather_analytics.create_weather_evolution_plot()
                    st.plotly_chart(weather_plot, use_container_width=True)
                except Exception as e:
                    st.info("Weather data visualization not available for this session type.")
                
                st.subheader("Weather Summary")
                try:
                    weather_summary = weather_analytics.get_weather_summary()
                    
                    if isinstance(weather_summary, dict) and 'air_temperature' in weather_summary:
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>🌡️ Air Temperature</h4>
                                <div style="font-size: 1.2rem; font-weight: 600;">
                                    Min: {weather_summary['air_temperature']['min']:.1f}°C<br>
                                    Max: {weather_summary['air_temperature']['max']:.1f}°C<br>
                                    Avg: {weather_summary['air_temperature']['mean']:.1f}°C
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>🏁 Track Temperature</h4>
                                <div style="font-size: 1.2rem; font-weight: 600;">
                                    Min: {weather_summary['track_temperature']['min']:.1f}°C<br>
                                    Max: {weather_summary['track_temperature']['max']:.1f}°C<br>
                                    Avg: {weather_summary['track_temperature']['mean']:.1f}°C
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col3:
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>💨 Wind Conditions</h4>
                                <div style="font-size: 1.2rem; font-weight: 600;">
                                    Min: {weather_summary['wind_speed']['min']:.1f} km/h<br>
                                    Max: {weather_summary['wind_speed']['max']:.1f} km/h<br>
                                    Avg: {weather_summary['wind_speed']['mean']:.1f} km/h
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("Detailed weather data not available for this session.")
                except Exception as e:
                    st.info("Weather analysis not available for this session type.")
            
            with adv_tab3:
                st.subheader("Pit Stop Strategy Analysis")
                try:
                    strategy_timeline = strategy_analyzer.create_strategy_timeline_plot()
                    st.plotly_chart(strategy_timeline, use_container_width=True)
                    
                    st.subheader("Pace Evolution (Fuel Effect)")  
                    pace_evolution = strategy_analyzer.create_pace_evolution_plot()
                    st.plotly_chart(pace_evolution, use_container_width=True)
                    
                    # Strategy effectiveness analysis
                    st.subheader("Strategy Effectiveness")
                    pit_strategies = strategy_analyzer.analyze_pit_stop_strategies()
                    
                    strategy_summary = []
                    for driver in selected_drivers:
                        if driver in pit_strategies:
                            strategy = pit_strategies[driver]
                            team = DRIVER_TEAMS.get(driver, 'Unknown')
                            team_color = TEAM_COLORS.get(team, '#FFFFFF')
                            
                            strategy_summary.append({
                                'driver': driver,
                                'team': team,
                                'team_color': team_color,
                                'strategy_type': strategy['strategy_type'],
                                'total_pit_stops': strategy['total_pit_stops'],
                                'stints': len(strategy['stints'])
                            })
                    
                    # Display strategy summary
                    if strategy_summary:
                        cols = st.columns(min(3, len(strategy_summary)))
                        for i, data in enumerate(strategy_summary):
                            with cols[i % len(cols)]:
                                st.markdown(f"""
                                <div class="metric-card">
                                    <div style="background: linear-gradient(135deg, {data['team_color']}20, {data['team_color']}40); 
                                                border-left: 4px solid {data['team_color']}; padding: 1rem; border-radius: 8px;">
                                        <h4 style="color: {data['team_color']}; margin: 0 0 0.5rem 0;">{data['driver']}</h4>
                                        <div style="color: #ccc; font-size: 0.9rem; margin-bottom: 0.5rem;">{data['team']}</div>
                                        <div style="font-weight: 600; color: white;">{data['strategy_type']}</div>
                                        <div style="color: #888; font-size: 0.85rem;">{data['total_pit_stops']} pit stops</div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                except Exception as e:
                    st.info("Strategy analysis not available for this session type.")
            
            with adv_tab4:
                st.subheader("Advanced Telemetry Comparison")
                
                if len(selected_drivers) >= 2:
                    col1, col2 = st.columns(2)
                    with col1:
                        driver1 = st.selectbox("First driver:", selected_drivers, key="adv_driver1")
                    with col2:
                        available_drivers_2 = [d for d in selected_drivers if d != driver1]
                        driver2 = st.selectbox("Second driver:", available_drivers_2, key="adv_driver2") if available_drivers_2 else None
                    
                    if driver1 and driver2:
                        try:
                            advanced_telemetry = analytics.create_advanced_telemetry_comparison(driver1, driver2)
                            
                            if advanced_telemetry:
                                st.plotly_chart(advanced_telemetry, use_container_width=True)
                            else:
                                st.info("Unable to create telemetry comparison. Telemetry data may not be available.")
                        except Exception as e:
                            st.info(f"Advanced telemetry comparison not available: {str(e)}")
                else:
                    st.info("Select at least 2 drivers to enable advanced telemetry comparison.")
                
                # Sector dominance analysis
                st.subheader("📊 Sector Dominance Analysis")
                try:
                    sector_dominance = analytics.calculate_sector_dominance()
                    
                    if sector_dominance:
                        for sector, sector_data in sector_dominance.items():
                            st.markdown(f"**{sector} Leaders:**")
                            
                            # Sort drivers by best time in this sector and filter selected drivers
                            sorted_drivers = sorted(sector_data.items(), key=lambda x: x[1]['best_time'])
                            selected_sector_drivers = [(d, data) for d, data in sorted_drivers if d in selected_drivers]
                            
                            if selected_sector_drivers:
                                for i, (driver, data) in enumerate(selected_sector_drivers[:5]):
                                    team = DRIVER_TEAMS.get(driver, 'Unknown')
                                    team_color = TEAM_COLORS.get(team, '#FFFFFF')
                                    position_badge = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
                                    
                                    st.markdown(f"""
                                    <div style="display: flex; align-items: center; padding: 0.5rem; margin: 0.25rem 0; 
                                                background: rgba(255,255,255,0.05); border-radius: 8px; border-left: 3px solid {team_color};">
                                        <span style="margin-right: 0.5rem; font-size: 1.1rem;">{position_badge}</span>
                                        <span style="flex: 1; font-weight: 500; color: {team_color};">{driver}</span>
                                        <span style="font-family: monospace; color: white;">{data['best_time']:.3f}s</span>
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.info("No selected drivers found in sector data.")
                            
                            st.markdown("---")
                    else:
                        st.info("Sector dominance data not available.")
                except Exception as e:
                    st.info("Sector analysis not available for this session.")
        else:
            st.info("Please select drivers from the sidebar to access advanced analytics.")
    
    # Tire Performance Analysis Tab
    with tab7:
        st.header("🛞 Tire Performance Analysis")
        
        if hasattr(st.session_state.data_loader, 'session') and st.session_state.data_loader.session is not None:
            try:
                tire_analyzer = TirePerformanceAnalyzer(st.session_state.data_loader.session)
                tire_data = tire_analyzer.calculate_tire_performance()
                
                if not tire_data.empty:
                    # Session info for visualization titles
                    session_info_str = f"{session_info['event_name']} {session_info['date']}" if session_info else "Current Session"
                    
                    # Filter data for selected drivers
                    filtered_tire_data = tire_data[tire_data['Driver'].isin(selected_drivers)]
                    
                    if not filtered_tire_data.empty:
                        st.subheader("📊 Comprehensive Tire Performance Metrics")
                        
                        # Create main visualization
                        tire_performance_chart = tire_analyzer.create_enhanced_tire_performance_visualizations(
                            filtered_tire_data, session_info_str
                        )
                        st.plotly_chart(tire_performance_chart, use_container_width=True)
                        
                        # Tire comparison heatmap
                        st.subheader("🔥 Tire Performance Heatmap")
                        tire_heatmap = tire_analyzer.create_tire_comparison_heatmap(filtered_tire_data)
                        st.plotly_chart(tire_heatmap, use_container_width=True)
                        
                        # Performance metrics table
                        st.subheader("📋 Detailed Tire Metrics")
                        
                        # Format the data for display
                        display_data = filtered_tire_data.copy()
                        display_data['Tire_Stress_Index'] = display_data['Tire_Stress_Index'].round(2)
                        display_data['Tire_Temperature'] = display_data['Tire_Temperature'].round(1).astype(str) + '°C'
                        display_data['Tire_Efficiency'] = display_data['Tire_Efficiency'].round(3)
                        display_data['Tire_Wear_Index'] = display_data['Tire_Wear_Index'].round(2)
                        display_data['Grip_Level'] = display_data['Grip_Level'].round(1).astype(str) + '%'
                        
                        # Display table with custom styling
                        tire_display_df = display_data[['Driver', 'Team', 'Tire_Stress_Index', 'Tire_Temperature', 
                                                       'Tire_Efficiency', 'Tire_Wear_Index', 'Grip_Level']].copy()
                        tire_display_df.columns = ['Driver', 'Team', 'Stress Index', 'Temperature', 'Efficiency', 'Wear Index', 'Grip Level']
                        st.dataframe(tire_display_df, use_container_width=True)
                        
                        # Performance insights
                        st.subheader("💡 Performance Insights")
                        
                        # Find best performers
                        best_efficiency_idx = filtered_tire_data['Tire_Efficiency'].idxmax()
                        lowest_stress_idx = filtered_tire_data['Tire_Stress_Index'].idxmin()
                        highest_grip_idx = filtered_tire_data['Grip_Level'].idxmax()
                        
                        best_efficiency = filtered_tire_data.loc[best_efficiency_idx]
                        lowest_stress = filtered_tire_data.loc[lowest_stress_idx]
                        highest_grip = filtered_tire_data.loc[highest_grip_idx]
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>🎯 Most Efficient</h4>
                                <div style="font-size: 1.4rem; font-weight: 700; color: #00D2BE;">
                                    {best_efficiency['Driver']}
                                </div>
                                <div style="color: #888; font-size: 0.9rem;">
                                    Efficiency: {best_efficiency['Tire_Efficiency']:.3f}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>😌 Smoothest Style</h4>
                                <div style="font-size: 1.4rem; font-weight: 700; color: #4ECDC4;">
                                    {lowest_stress['Driver']}
                                </div>
                                <div style="color: #888; font-size: 0.9rem;">
                                    Stress: {lowest_stress['Tire_Stress_Index']:.2f}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col3:
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>🏎️ Best Grip</h4>
                                <div style="font-size: 1.4rem; font-weight: 700; color: #FFD700;">
                                    {highest_grip['Driver']}
                                </div>
                                <div style="color: #888; font-size: 0.9rem;">
                                    Grip: {highest_grip['Grip_Level']:.1f}%
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No tire performance data available for selected drivers.")
                else:
                    st.info("Unable to calculate tire performance data for this session.")
            except Exception as e:
                st.error(f"Error in tire performance analysis: {str(e)}")
        else:
            st.info("Please load session data to access tire performance analysis.")
    
    # Driver Stress Analysis Tab
    with tab8:
        st.header("⚡ Driver Stress Analysis")
        
        if hasattr(st.session_state.data_loader, 'session') and st.session_state.data_loader.session is not None:
            try:
                stress_analyzer = DriverStressAnalyzer(st.session_state.data_loader.session)
                stress_data = stress_analyzer.calculate_driver_stress_index()
                
                if not stress_data.empty:
                    # Session info for visualization titles
                    session_info_str = f"{session_info['event_name']} {session_info['date']}" if session_info else "Current Session"
                    
                    # Filter data for selected drivers
                    filtered_stress_data = stress_data[stress_data['Driver'].isin(selected_drivers)]
                    
                    if not filtered_stress_data.empty:
                        st.subheader("📈 Comprehensive Stress Analysis")
                        
                        # Create main stress analysis visualization
                        stress_analysis_chart = stress_analyzer.create_stress_analysis_visualizations(
                            filtered_stress_data, session_info_str
                        )
                        st.plotly_chart(stress_analysis_chart, use_container_width=True)
                        
                        # Stress ranking chart
                        st.subheader("🏆 Driver Stress Index Ranking")
                        stress_ranking = stress_analyzer.create_stress_ranking_chart(filtered_stress_data)
                        st.plotly_chart(stress_ranking, use_container_width=True)
                        
                        # Detailed stress metrics table
                        st.subheader("📋 Detailed Stress Metrics")
                        
                        # Format the data for display
                        display_stress = filtered_stress_data.copy()
                        display_stress['Driver_Stress_Index'] = display_stress['Driver_Stress_Index'].round(3)
                        display_stress['Braking_Percentage'] = display_stress['Braking_Percentage'].round(1).astype(str) + '%'
                        display_stress['High_Throttle_Percentage'] = display_stress['High_Throttle_Percentage'].round(1).astype(str) + '%'
                        display_stress['Critical_Speed_Median'] = display_stress['Critical_Speed_Median'].round(1).astype(str) + ' km/h'
                        display_stress['Consistency_Index'] = display_stress['Consistency_Index'].round(1).astype(str) + '%'
                        display_stress['Aggression_Index'] = display_stress['Aggression_Index'].round(2)
                        
                        # Display table
                        stress_display_df = display_stress[['Driver', 'Team', 'Driver_Stress_Index', 'Braking_Percentage', 
                                                           'High_Throttle_Percentage', 'Critical_Speed_Median', 'Consistency_Index', 
                                                           'Aggression_Index']].copy()
                        stress_display_df.columns = ['Driver', 'Team', 'Stress Index', 'Braking %', 'High Throttle %', 'Critical Speed', 'Consistency', 'Aggression']
                        st.dataframe(stress_display_df, use_container_width=True)
                        
                        # Stress analysis insights
                        st.subheader("🧠 Driving Style Insights")
                        
                        # Find performance characteristics
                        most_stressed_idx = filtered_stress_data['Driver_Stress_Index'].idxmax()
                        most_consistent_idx = filtered_stress_data['Consistency_Index'].idxmax()
                        most_aggressive_idx = filtered_stress_data['Aggression_Index'].idxmax()
                        smoothest_idx = filtered_stress_data['Smoothness_Index'].idxmax()
                        
                        most_stressed = filtered_stress_data.loc[most_stressed_idx]
                        most_consistent = filtered_stress_data.loc[most_consistent_idx]
                        most_aggressive = filtered_stress_data.loc[most_aggressive_idx]
                        smoothest = filtered_stress_data.loc[smoothest_idx]
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>🔥 Highest Stress</h4>
                                <div style="font-size: 1.4rem; font-weight: 700; color: #FF6B6B;">
                                    {most_stressed['Driver']}
                                </div>
                                <div style="color: #888; font-size: 0.9rem;">
                                    Stress Index: {most_stressed['Driver_Stress_Index']:.3f}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>🎯 Most Consistent</h4>
                                <div style="font-size: 1.4rem; font-weight: 700; color: #4ECDC4;">
                                    {most_consistent['Driver']}
                                </div>
                                <div style="color: #888; font-size: 0.9rem;">
                                    Consistency: {most_consistent['Consistency_Index']:.1f}%
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>⚡ Most Aggressive</h4>
                                <div style="font-size: 1.4rem; font-weight: 700; color: #FFD700;">
                                    {most_aggressive['Driver']}
                                </div>
                                <div style="color: #888; font-size: 0.9rem;">
                                    Aggression: {most_aggressive['Aggression_Index']:.2f}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>🌊 Smoothest Style</h4>
                                <div style="font-size: 1.4rem; font-weight: 700; color: #00D2BE;">
                                    {smoothest['Driver']}
                                </div>
                                <div style="color: #888; font-size: 0.9rem;">
                                    Smoothness: {smoothest['Smoothness_Index']:.1f}%
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No stress analysis data available for selected drivers.")
                else:
                    st.info("Unable to calculate driver stress data for this session.")
            except Exception as e:
                st.error(f"Error in stress analysis: {str(e)}")
        else:
            st.info("Please load session data to access driver stress analysis.")
    
    # Downforce Configuration Analysis Tab
    with tab9:
        st.header("🏎️ Downforce Configuration Analysis")
        
        if hasattr(st.session_state.data_loader, 'session') and st.session_state.data_loader.session is not None:
            try:
                downforce_analyzer = DownforceAnalyzer(st.session_state.data_loader.session)
                downforce_data = downforce_analyzer.calculate_downforce_metrics()
                
                if not downforce_data.empty:
                    # Session info for visualization titles
                    session_info_str = f"{session_info['event_name']} {session_info['date']}" if session_info else "Current Session"
                    
                    # Filter data for selected drivers
                    filtered_downforce_data = downforce_data[downforce_data['Driver'].isin(selected_drivers)]
                    
                    if not filtered_downforce_data.empty:
                        st.subheader("📊 Comprehensive Downforce Analysis")
                        
                        # Create main downforce visualization
                        downforce_chart = downforce_analyzer.create_downforce_visualizations(
                            filtered_downforce_data, session_info_str
                        )
                        if downforce_chart:
                            st.plotly_chart(downforce_chart, use_container_width=True)
                        
                        # Downforce efficiency ranking
                        st.subheader("🏆 Downforce Efficiency Ranking")
                        ranking_chart = downforce_analyzer.create_downforce_ranking_chart(filtered_downforce_data)
                        if ranking_chart:
                            st.plotly_chart(ranking_chart, use_container_width=True)
                        
                        # Detailed metrics table
                        st.subheader("📋 Detailed Downforce Metrics")
                        
                        # Format the data for display
                        display_downforce = filtered_downforce_data.copy()
                        display_downforce['Downforce_Efficiency'] = display_downforce['Downforce_Efficiency'].round(2).astype(str) + '%'
                        display_downforce['Average_Speed'] = display_downforce['Average_Speed'].round(1).astype(str) + ' km/h'
                        display_downforce['Top_Speed'] = display_downforce['Top_Speed'].round(1).astype(str) + ' km/h'
                        display_downforce['Corner_Speed_Avg'] = display_downforce['Corner_Speed_Avg'].round(1).astype(str) + ' km/h'
                        display_downforce['Straight_Speed_Avg'] = display_downforce['Straight_Speed_Avg'].round(1).astype(str) + ' km/h'
                        display_downforce['Aero_Balance'] = display_downforce['Aero_Balance'].round(2).astype(str) + '%'
                        
                        # Display table
                        downforce_display_df = display_downforce[['Driver', 'Team', 'Downforce_Efficiency', 'Average_Speed', 
                                                                 'Top_Speed', 'Corner_Speed_Avg', 'Straight_Speed_Avg', 'Aero_Balance']].copy()
                        downforce_display_df.columns = ['Driver', 'Team', 'Efficiency', 'Avg Speed', 'Top Speed', 'Corner Speed', 'Straight Speed', 'Aero Balance']
                        st.dataframe(downforce_display_df, use_container_width=True)
                        
                        # Performance insights
                        st.subheader("🔍 Aerodynamic Insights")
                        
                        # Find best performers
                        best_efficiency_idx = filtered_downforce_data['Downforce_Efficiency'].idxmax()
                        best_corners_idx = filtered_downforce_data['Corner_Speed_Avg'].idxmax()
                        best_straights_idx = filtered_downforce_data['Straight_Speed_Avg'].idxmax()
                        best_balance_idx = filtered_downforce_data['Aero_Balance'].idxmax()
                        
                        best_efficiency = filtered_downforce_data.loc[best_efficiency_idx]
                        best_corners = filtered_downforce_data.loc[best_corners_idx]
                        best_straights = filtered_downforce_data.loc[best_straights_idx]
                        best_balance = filtered_downforce_data.loc[best_balance_idx]
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>🎯 Most Efficient Setup</h4>
                                <div style="font-size: 1.4rem; font-weight: 700; color: #00D2BE;">
                                    {best_efficiency['Driver']}
                                </div>
                                <div style="color: #888; font-size: 0.9rem;">
                                    Efficiency: {best_efficiency['Downforce_Efficiency']:.2f}%
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>🏁 Corner Speed King</h4>
                                <div style="font-size: 1.4rem; font-weight: 700; color: #4ECDC4;">
                                    {best_corners['Driver']}
                                </div>
                                <div style="color: #888; font-size: 0.9rem;">
                                    Corner Speed: {best_corners['Corner_Speed_Avg']:.1f} km/h
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>🚀 Straight Line Rocket</h4>
                                <div style="font-size: 1.4rem; font-weight: 700; color: #FFD700;">
                                    {best_straights['Driver']}
                                </div>
                                <div style="color: #888; font-size: 0.9rem;">
                                    Straight Speed: {best_straights['Straight_Speed_Avg']:.1f} km/h
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>⚖️ Best Aero Balance</h4>
                                <div style="font-size: 1.4rem; font-weight: 700; color: #FF6B6B;">
                                    {best_balance['Driver']}
                                </div>
                                <div style="color: #888; font-size: 0.9rem;">
                                    Balance: {best_balance['Aero_Balance']:.2f}%
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Technical explanation
                        st.subheader("📝 Technical Notes")
                        st.markdown("""
                        **Downforce Efficiency**: Calculated as 100 × (Average Speed / Top Speed). Higher values indicate better overall aerodynamic balance.
                        
                        **Aerodynamic Balance**: The ratio of corner speeds to straight-line speeds, indicating how well the car handles different track sections.
                        
                        **Speed Profiles**: Analysis of performance in different track zones helps understand aerodynamic setup preferences.
                        """)
                        
                    else:
                        st.info("No downforce analysis data available for selected drivers.")
                else:
                    st.info("Unable to calculate downforce configuration data for this session.")
            except Exception as e:
                st.error(f"Error in downforce analysis: {str(e)}")
        else:
            st.info("Please load session data to access downforce configuration analysis.")

if __name__ == "__main__":
    main()
