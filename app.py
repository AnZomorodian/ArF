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
from utils.formatters import format_lap_time, format_sector_time, get_lap_time_color_class, get_position_change_text
from utils.advanced_analytics import AdvancedF1Analytics
from utils.weather_analytics import WeatherAnalytics
from utils.race_strategy import RaceStrategyAnalyzer
from utils.predictive_analytics import PredictiveF1Analytics
from utils.realtime_insights import RealTimeF1Insights
from utils.comparative_analytics import ComparativeF1Analytics

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
            st.markdown("Choose drivers to compare in the analysis below", unsafe_allow_html=True)
            
            available_drivers = st.session_state.data_loader.get_available_drivers()
            
            if available_drivers:
                selected_drivers = st.multiselect(
                    "Select Drivers for Comparison",
                    available_drivers,
                    default=available_drivers[:2] if len(available_drivers) >= 2 else available_drivers,
                    help="Select 2-4 drivers for optimal comparison visualization"
                )
                
                # Display selected drivers with enhanced cards
                if selected_drivers:
                    st.markdown("### 🎯 Selected Drivers")
                    driver_cols = st.columns(len(selected_drivers))
                    
                    for i, driver in enumerate(selected_drivers):
                        with driver_cols[i]:
                            team = DRIVER_TEAMS.get(driver, 'Unknown')
                            color = TEAM_COLORS.get(team, '#FFFFFF')
                            
                            st.markdown(f"""
                            <div class="driver-comparison-card" style="margin: 0.5rem 0;">
                                <div class="team-badge-enhanced" style="background-color: {color};">
                                    {driver}
                                </div>
                                <div style="color: {color}; font-size: 0.9rem; margin-top: 0.5rem; font-weight: 600;">
                                    {team}
                                </div>
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
    
    # Analysis tabs with enhanced analytics
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📈 Telemetry Analysis", 
        "🗺️ Track Dominance", 
        "⏱️ Lap Comparison", 
        "🔧 Tire Strategy", 
        "📊 Race Progression",
        "🧠 Advanced Analytics",
        "🔮 Predictive Insights",
        "⚡ Real-Time Analysis"
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
        st.header("🧠 Advanced Analytics")
        
        if selected_drivers:
            # Initialize analytics modules
            session = st.session_state.data_loader.session
            analytics = AdvancedF1Analytics(session)
            weather_analytics = WeatherAnalytics(session)
            strategy_analyzer = RaceStrategyAnalyzer(session)
            
            # Advanced analytics sub-tabs
            adv_tab1, adv_tab2, adv_tab3, adv_tab4 = st.tabs([
                "👤 Driver Performance", "🌤️ Weather Impact", "🏁 Strategy Analysis", "📊 Advanced Metrics"
            ])
            
            with adv_tab1:
                st.subheader("Driver Consistency Analysis")
                
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
                                    <div style="font-size: 1.5rem; font-weight: 700; color: white;">{data['mean_lap_time']:.3f}s</div>
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

    with tab7:
        st.header("🔮 Predictive Insights")
        st.markdown("Advanced machine learning insights for performance prediction")
        
        if selected_drivers and len(selected_drivers) >= 2:
            try:
                # Get laps data for prediction
                laps_data = st.session_state.data_loader.get_laps_data()
                
                if laps_data is not None and not laps_data.empty:
                    # Initialize predictive analytics
                    predictive_analytics = PredictiveF1Analytics(st.session_state.data_loader.session, laps_data)
                    
                    # Qualifying Performance Prediction
                    st.subheader("🏁 Qualifying Performance Prediction")
                    prediction_data = predictive_analytics.predict_qualifying_performance()
                    
                    if prediction_data is not None:
                        # Display prediction results
                        st.markdown("### Predicted Qualifying Order")
                        for i, row in prediction_data.head(8).iterrows():
                            driver = row['Driver']
                            team = DRIVER_TEAMS.get(driver, 'Unknown')
                            color = TEAM_COLORS.get(team, '#FFFFFF')
                            
                            st.markdown(f"""
                            <div class="metric-card" style="margin: 0.5rem 0;">
                                <div style="display: flex; align-items: center; justify-content: space-between;">
                                    <div style="display: flex; align-items: center;">
                                        <div class="position-badge" style="background: {color}; color: black; margin-right: 1rem;">P{row['Predicted_Position']}</div>
                                        <div>
                                            <div style="font-weight: 700; font-size: 1.1rem; color: white;">{driver}</div>
                                            <div style="color: {color}; font-size: 0.9rem;">{team}</div>
                                        </div>
                                    </div>
                                    <div style="text-align: right;">
                                        <div style="font-family: monospace; font-size: 1.1rem; color: white;">
                                            {format_lap_time(row['Best_Time'])}
                                        </div>
                                        <div style="font-size: 0.8rem; color: #888;">
                                            Consistency: ±{row['Consistency']:.3f}s
                                        </div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Create prediction visualization
                        pred_viz = predictive_analytics.create_prediction_visualization(prediction_data)
                        if pred_viz:
                            st.plotly_chart(pred_viz, use_container_width=True)
                    
                    # Tire Degradation Prediction
                    st.subheader("🛞 Advanced Tire Degradation Analysis")
                    degradation_data = predictive_analytics.analyze_tire_degradation_patterns()
                    
                    if degradation_data is not None and not degradation_data.empty:
                        # Show degradation summary
                        compound_summary = degradation_data.groupby('Compound').agg({
                            'Degradation_Rate': ['mean', 'std'],
                            'Stint_Length': 'mean',
                            'Total_Degradation': 'mean'
                        }).round(3)
                        
                        st.markdown("### Compound Performance Summary")
                        for compound in degradation_data['Compound'].unique():
                            compound_data = degradation_data[degradation_data['Compound'] == compound]
                            tire_color = TIRE_COLORS.get(compound, '#808080')
                            
                            avg_degradation = compound_data['Degradation_Rate'].mean()
                            avg_stint = compound_data['Stint_Length'].mean()
                            
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, rgba(35, 39, 47, 0.8), rgba(24, 25, 26, 0.9)); 
                                        border-left: 4px solid {tire_color}; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">
                                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                                    <div style="width: 24px; height: 24px; background-color: {tire_color}; border-radius: 50%; margin-right: 0.75rem;"></div>
                                    <h4 style="color: white; margin: 0;">{compound} Compound Analysis</h4>
                                </div>
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
                                    <div style="text-align: center;">
                                        <div style="font-size: 1.3rem; font-weight: 700; color: white;">{avg_degradation:.4f}s</div>
                                        <div style="color: #888; font-size: 0.9rem;">Avg Degradation/Lap</div>
                                    </div>
                                    <div style="text-align: center;">
                                        <div style="font-size: 1.3rem; font-weight: 700; color: white;">{avg_stint:.1f}</div>
                                        <div style="color: #888; font-size: 0.9rem;">Avg Stint Length</div>
                                    </div>
                                    <div style="text-align: center;">
                                        <div style="font-size: 1.3rem; font-weight: 700; color: white;">{len(compound_data)}</div>
                                        <div style="color: #888; font-size: 0.9rem;">Sample Size</div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Create degradation visualization
                        deg_viz = predictive_analytics.create_degradation_visualization(degradation_data)
                        if deg_viz:
                            st.plotly_chart(deg_viz, use_container_width=True)
                    
                else:
                    st.info("Loading session data for predictive analysis...")
            
            except Exception as e:
                st.error(f"Error in predictive analysis: {str(e)}")
        else:
            st.info("Select at least 2 drivers to enable predictive insights.")
    
    with tab8:
        st.header("⚡ Real-Time Analysis")
        st.markdown("Live performance insights and dynamic analytics")
        
        if selected_drivers:
            try:
                # Get laps data for real-time analysis
                laps_data = st.session_state.data_loader.get_laps_data()
                
                if laps_data is not None and not laps_data.empty:
                    # Initialize real-time analytics
                    realtime_analytics = RealTimeF1Insights(st.session_state.data_loader.session, laps_data)
                    
                    # Live Performance Dashboard
                    st.subheader("📊 Live Performance Dashboard")
                    dashboard_data = realtime_analytics.live_performance_dashboard()
                    
                    if dashboard_data:
                        session_stats = dashboard_data.get('session_stats', {})
                        performance_leaders = dashboard_data.get('performance_leaders', {})
                        
                        # Session statistics
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("📊 Total Laps", session_stats.get('total_laps', 0))
                        with col2:
                            st.metric("🏎️ Active Drivers", session_stats.get('active_drivers', 0))
                        with col3:
                            duration = session_stats.get('session_duration', 'Unknown')
                            st.metric("⏱️ Duration", str(duration))
                        with col4:
                            avg_lap = session_stats.get('avg_lap_time')
                            if avg_lap:
                                st.metric("📈 Avg Lap Time", format_lap_time(avg_lap.total_seconds()))
                        
                        # Performance leaders
                        st.subheader("🥇 Current Leaders")
                        
                        leader_cols = st.columns(3)
                        
                        # Fastest lap leader
                        with leader_cols[0]:
                            fastest_lap = performance_leaders.get('fastest_lap')
                            if fastest_lap:
                                driver = fastest_lap['driver']
                                team = DRIVER_TEAMS.get(driver, 'Unknown')
                                color = TEAM_COLORS.get(team, '#FFFFFF')
                                
                                st.markdown(f"""
                                <div class="metric-card">
                                    <h4 style="color: #FFD700;">🏆 Fastest Lap</h4>
                                    <div style="text-align: center;">
                                        <div class="team-badge-enhanced" style="background-color: {color};">{driver}</div>
                                        <div style="font-family: monospace; font-size: 1.2rem; margin: 0.5rem 0; color: white;">
                                            {format_lap_time(fastest_lap['time'].total_seconds())}
                                        </div>
                                        <div style="color: #888; font-size: 0.9rem;">Lap {fastest_lap.get('lap_number', 'N/A')}</div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # Most consistent driver
                        with leader_cols[1]:
                            most_consistent = performance_leaders.get('most_consistent')
                            if most_consistent:
                                driver = most_consistent['driver']
                                team = DRIVER_TEAMS.get(driver, 'Unknown')
                                color = TEAM_COLORS.get(team, '#FFFFFF')
                                
                                st.markdown(f"""
                                <div class="metric-card">
                                    <h4 style="color: #00D2BE;">📊 Most Consistent</h4>
                                    <div style="text-align: center;">
                                        <div class="team-badge-enhanced" style="background-color: {color};">{driver}</div>
                                        <div style="font-size: 1.2rem; margin: 0.5rem 0; color: white;">
                                            ±{most_consistent['consistency']:.3f}s
                                        </div>
                                        <div style="color: #888; font-size: 0.9rem;">{most_consistent['laps']} laps</div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # Current pace leader
                        with leader_cols[2]:
                            pace_setter = performance_leaders.get('pace_setter')
                            if pace_setter:
                                driver = pace_setter['driver']
                                team = DRIVER_TEAMS.get(driver, 'Unknown')
                                color = TEAM_COLORS.get(team, '#FFFFFF')
                                
                                st.markdown(f"""
                                <div class="metric-card">
                                    <h4 style="color: #DC0000;">⚡ Current Pace</h4>
                                    <div style="text-align: center;">
                                        <div class="team-badge-enhanced" style="background-color: {color};">{driver}</div>
                                        <div style="font-family: monospace; font-size: 1.2rem; margin: 0.5rem 0; color: white;">
                                            {format_lap_time(pace_setter['recent_pace'])}
                                        </div>
                                        <div style="color: #888; font-size: 0.9rem;">Last {pace_setter['recent_laps']} laps</div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    # Driver Momentum Analysis
                    st.subheader("📈 Driver Momentum Analysis")
                    momentum_data = realtime_analytics.momentum_analysis()
                    
                    if momentum_data is not None and not momentum_data.empty:
                        # Filter for selected drivers
                        filtered_momentum = momentum_data[momentum_data['Driver'].isin(selected_drivers)]
                        
                        for _, row in filtered_momentum.iterrows():
                            driver = row['Driver']
                            team = DRIVER_TEAMS.get(driver, 'Unknown')
                            color = TEAM_COLORS.get(team, '#FFFFFF')
                            
                            # Determine momentum color
                            momentum_score = row['Momentum_Score']
                            if momentum_score < -0.1:
                                momentum_color = '#00FF00'  # Improving - Green
                                momentum_text = 'IMPROVING'
                                momentum_icon = '📈'
                            elif momentum_score > 0.1:
                                momentum_color = '#FF0000'  # Declining - Red
                                momentum_text = 'DECLINING'
                                momentum_icon = '📉'
                            else:
                                momentum_color = '#FFD700'  # Stable - Yellow
                                momentum_text = 'STABLE'
                                momentum_icon = '➡️'
                            
                            st.markdown(f"""
                            <div class="metric-card" style="border-left: 4px solid {momentum_color};">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>
                                        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                                            <div class="team-badge-enhanced" style="background-color: {color}; margin-right: 1rem;">{driver}</div>
                                            <div style="color: {momentum_color}; font-weight: 700; font-size: 1rem;">
                                                {momentum_icon} {momentum_text}
                                            </div>
                                        </div>
                                        <div style="color: {color}; font-size: 0.9rem; margin-bottom: 0.5rem;">{team}</div>
                                    </div>
                                    <div style="text-align: right;">
                                        <div style="font-size: 0.9rem; color: #888;">Momentum Score</div>
                                        <div style="font-size: 1.2rem; font-weight: 700; color: {momentum_color};">
                                            {momentum_score:+.3f}s
                                        </div>
                                    </div>
                                </div>
                                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 0.5rem; margin-top: 1rem; font-size: 0.85rem;">
                                    <div><strong>Recent Pace:</strong> {format_lap_time(row['Recent_Pace'])}</div>
                                    <div><strong>Early Pace:</strong> {format_lap_time(row['Early_Pace'])}</div>
                                    <div><strong>Volatility:</strong> ±{row['Volatility']:.3f}s</div>
                                    <div><strong>Trend Strength:</strong> {row['Trend_Strength']:.2f}</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Comparative Analysis for selected drivers
                    if len(selected_drivers) >= 2:
                        st.subheader("🔄 Head-to-Head Comparison")
                        
                        # Initialize comparative analytics
                        comparative_analytics = ComparativeF1Analytics(st.session_state.data_loader.session, laps_data)
                        
                        # Driver selection for comparison
                        comp_col1, comp_col2 = st.columns(2)
                        with comp_col1:
                            driver1 = st.selectbox("Driver 1:", selected_drivers, key="comp_driver1")
                        with comp_col2:
                            driver2 = st.selectbox("Driver 2:", [d for d in selected_drivers if d != driver1], key="comp_driver2")
                        
                        if driver1 and driver2:
                            comparison_data = comparative_analytics.head_to_head_analysis(driver1, driver2)
                            
                            if comparison_data:
                                d1_stats = comparison_data['driver1_stats']
                                d2_stats = comparison_data['driver2_stats']
                                
                                # Comparison visualization
                                comp_cols = st.columns(2)
                                
                                with comp_cols[0]:
                                    team1 = DRIVER_TEAMS.get(driver1, 'Unknown')
                                    color1 = TEAM_COLORS.get(team1, '#FFFFFF')
                                    
                                    st.markdown(f"""
                                    <div class="metric-card" style="border-left: 4px solid {color1};">
                                        <div class="team-badge-enhanced" style="background-color: {color1}; margin-bottom: 1rem;">{driver1}</div>
                                        <div style="display: grid; gap: 0.5rem;">
                                            <div><strong>Best Lap:</strong> {format_lap_time(d1_stats['best_lap'])}</div>
                                            <div><strong>Average:</strong> {format_lap_time(d1_stats['average_lap'])}</div>
                                            <div><strong>Consistency:</strong> ±{d1_stats['consistency']:.3f}s</div>
                                            <div><strong>Total Laps:</strong> {d1_stats['total_laps']}</div>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                with comp_cols[1]:
                                    team2 = DRIVER_TEAMS.get(driver2, 'Unknown')
                                    color2 = TEAM_COLORS.get(team2, '#FFFFFF')
                                    
                                    st.markdown(f"""
                                    <div class="metric-card" style="border-left: 4px solid {color2};">
                                        <div class="team-badge-enhanced" style="background-color: {color2}; margin-bottom: 1rem;">{driver2}</div>
                                        <div style="display: grid; gap: 0.5rem;">
                                            <div><strong>Best Lap:</strong> {format_lap_time(d2_stats['best_lap'])}</div>
                                            <div><strong>Average:</strong> {format_lap_time(d2_stats['average_lap'])}</div>
                                            <div><strong>Consistency:</strong> ±{d2_stats['consistency']:.3f}s</div>
                                            <div><strong>Total Laps:</strong> {d2_stats['total_laps']}</div>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                # Statistical significance
                                if 'statistical_test' in comparison_data:
                                    test_result = comparison_data['statistical_test']
                                    significance = "Statistically Significant" if test_result['significant'] else "Not Statistically Significant"
                                    significance_color = "#00FF00" if test_result['significant'] else "#FF8800"
                                    
                                    st.markdown(f"""
                                    <div style="text-align: center; margin: 1rem 0; padding: 1rem; 
                                                background: rgba(35, 39, 47, 0.8); border-radius: 8px; 
                                                border: 1px solid {significance_color};">
                                        <div style="color: {significance_color}; font-weight: 700; font-size: 1.1rem;">
                                            {significance}
                                        </div>
                                        <div style="color: #888; font-size: 0.9rem; margin-top: 0.3rem;">
                                            p-value: {test_result['p_value']:.4f}
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                
                else:
                    st.info("Loading session data for real-time analysis...")
            
            except Exception as e:
                st.error(f"Error in real-time analysis: {str(e)}")
        else:
            st.info("Select drivers to enable real-time analysis.")

if __name__ == "__main__":
    main()
