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
from utils.brake_analysis import BrakeAnalyzer
from utils.composite_performance import CompositePerformanceAnalyzer

# Configure page
st.set_page_config(
    page_title="Track.lytix - F1 Analytics",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional minimal styling
st.markdown("""
<style>
    /* Import professional fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global reset and base styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Root variables */
    :root {
        --primary-color: #1f2937;
        --secondary-color: #374151;
        --accent-color: #dc2626;
        --text-primary: #111827;
        --text-secondary: #6b7280;
        --bg-light: #f9fafb;
        --bg-white: #ffffff;
        --border-color: #e5e7eb;
        --success-color: #059669;
        --warning-color: #d97706;
        --radius: 8px;
        --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    /* Main container */
    .main .block-container {
        background-color: var(--bg-light);
        padding: 2rem 1rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Header styles */
    .header-container {
        background: var(--bg-white);
        padding: 2rem;
        border-radius: var(--radius);
        box-shadow: var(--shadow);
        margin-bottom: 2rem;
        text-align: center;
        border-left: 4px solid var(--accent-color);
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        font-size: 1.1rem;
        color: var(--text-secondary);
        font-weight: 400;
        margin: 0;
    }
    
    /* Card styles */
    .card {
        background: var(--bg-white);
        border-radius: var(--radius);
        padding: 1.5rem;
        box-shadow: var(--shadow);
        margin-bottom: 1.5rem;
        border: 1px solid var(--border-color);
    }
    
    .card-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--border-color);
    }
    
    /* Driver card */
    .driver-card {
        background: var(--bg-white);
        border: 1px solid var(--border-color);
        border-radius: var(--radius);
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.2s ease;
        text-align: center;
    }
    
    .driver-card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-1px);
    }
    
    .driver-name {
        font-weight: 600;
        font-size: 1.1rem;
        color: var(--text-primary);
    }
    
    .driver-team {
        font-size: 0.9rem;
        color: var(--text-secondary);
        margin-top: 0.25rem;
    }
    
    .driver-number {
        font-size: 0.8rem;
        color: var(--text-secondary);
        margin-top: 0.25rem;
    }
    
    /* Session controls */
    .session-controls {
        background: var(--bg-white);
        border-radius: var(--radius);
        padding: 1.5rem;
        box-shadow: var(--shadow);
        margin-bottom: 2rem;
        border: 1px solid var(--border-color);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: var(--bg-white);
        padding: 0.5rem;
        border-radius: var(--radius);
        border: 1px solid var(--border-color);
        margin-bottom: 1.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background: transparent;
        border-radius: calc(var(--radius) - 2px);
        color: var(--text-secondary);
        font-weight: 500;
        font-size: 0.9rem;
        border: none;
        padding: 0 1.5rem;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: var(--bg-light);
        color: var(--text-primary);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--accent-color);
        color: white;
        font-weight: 600;
    }
    
    /* Button styling */
    .stButton > button {
        background: var(--accent-color);
        color: white;
        border: none;
        border-radius: var(--radius);
        padding: 0.6rem 1.5rem;
        font-weight: 500;
        font-size: 0.9rem;
        transition: all 0.2s ease;
        box-shadow: var(--shadow);
    }
    
    .stButton > button:hover {
        background: #b91c1c;
        box-shadow: var(--shadow-lg);
        transform: translateY(-1px);
    }
    
    /* Select box styling */
    .stSelectbox > div > div {
        background-color: var(--bg-white);
        border: 1px solid var(--border-color);
        border-radius: var(--radius);
        font-size: 0.9rem;
    }
    
    .stMultiSelect > div > div {
        background-color: var(--bg-white);
        border: 1px solid var(--border-color);
        border-radius: var(--radius);
        font-size: 0.9rem;
    }
    
    /* Data table styling */
    .stDataFrame {
        background: var(--bg-white);
        border: 1px solid var(--border-color);
        border-radius: var(--radius);
        overflow: hidden;
        box-shadow: var(--shadow);
    }
    
    .stDataFrame thead tr th {
        background: var(--primary-color);
        color: white;
        font-weight: 600;
        text-align: center;
        padding: 1rem 0.5rem;
        border: none;
        font-size: 0.9rem;
    }
    
    .stDataFrame tbody tr td {
        text-align: center;
        padding: 0.75rem 0.5rem;
        border-bottom: 1px solid var(--border-color);
        color: var(--text-primary);
        font-size: 0.85rem;
    }
    
    .stDataFrame tbody tr:hover td {
        background: var(--bg-light);
    }
    
    /* Metrics styling */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: var(--bg-white);
        border: 1px solid var(--border-color);
        border-radius: var(--radius);
        padding: 1.25rem;
        text-align: center;
        box-shadow: var(--shadow);
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--accent-color);
        margin-bottom: 0.25rem;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: var(--text-secondary);
        font-weight: 500;
    }
    
    /* Status indicators */
    .status-success {
        color: var(--success-color);
    }
    
    .status-warning {
        color: var(--warning-color);
    }
    
    .status-error {
        color: var(--accent-color);
    }
    
    /* Loading states */
    .stSpinner > div {
        border-color: var(--accent-color);
    }
    
    /* Info messages */
    .stAlert {
        border-radius: var(--radius);
        border: 1px solid var(--border-color);
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem 0.5rem;
        }
        
        .header-title {
            font-size: 2rem;
        }
        
        .card {
            padding: 1rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0 1rem;
            font-size: 0.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_loader' not in st.session_state:
    st.session_state.data_loader = DataLoader()

def main():
    """Main application function"""
    
    # Header
    st.markdown("""
    <div class="header-container">
        <h1 class="header-title">🏎️ Track.lytix</h1>
        <p class="header-subtitle">Professional Formula 1 Data Analysis Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Session controls
    st.markdown('<div class="session-controls">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">📊 Session Configuration</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        year = st.selectbox(
            "Season",
            options=list(range(2024, 2017, -1)),
            index=0,
            help="Select F1 season year"
        )
    
    with col2:
        selected_gp = st.selectbox(
            "Grand Prix",
            options=GRANDS_PRIX,
            index=0,
            help="Select Grand Prix event"
        )
    
    with col3:
        session_type = st.selectbox(
            "Session",
            options=list(SESSIONS.keys()),
            index=2,  # Default to Qualifying
            help="Select session type"
        )
    
    # Load session button
    if st.button("🔄 Load Session Data", type="primary"):
        with st.spinner("Loading F1 session data..."):
            try:
                success = st.session_state.data_loader.load_session(
                    year, selected_gp, SESSIONS[session_type]
                )
                if success:
                    st.success(f"✅ Successfully loaded {year} {selected_gp} {session_type}")
                else:
                    st.error("❌ Failed to load session data")
            except Exception as e:
                st.error(f"❌ Error loading session: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Driver selection
    selected_drivers = []
    if hasattr(st.session_state.data_loader, 'session') and st.session_state.data_loader.session is not None:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">🏁 Driver Selection</div>', unsafe_allow_html=True)
        
        # Get driver information
        driver_manager = DynamicDriverManager(st.session_state.data_loader.session)
        driver_info = driver_manager.get_driver_info()
        team_mappings = driver_manager.get_team_mappings()
        team_colors = driver_manager.get_team_colors()
        
        available_drivers = list(driver_info.keys())
        
        if available_drivers:
            selected_drivers = st.multiselect(
                "Select drivers for analysis",
                available_drivers,
                default=[],
                format_func=lambda x: f"{driver_info[x]['abbreviation']} - {driver_info[x]['team_name']}",
                help="Choose 2-4 drivers for optimal comparison"
            )
            
            # Display selected drivers
            if selected_drivers:
                st.markdown("**Selected Drivers:**")
                driver_cols = st.columns(min(len(selected_drivers), 4))
                
                for idx, driver in enumerate(selected_drivers):
                    with driver_cols[idx % 4]:
                        driver_data = driver_info[driver]
                        team_name = driver_data['team_name']
                        team_color = team_colors.get(team_name, '#6b7280')
                        
                        st.markdown(f"""
                        <div class="driver-card" style="border-left: 3px solid {team_color};">
                            <div class="driver-name">{driver_data['abbreviation']}</div>
                            <div class="driver-team">{team_name}</div>
                            <div class="driver-number">#{driver_data.get('driver_number', 'N/A')}</div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("👆 Select drivers above to begin analysis")
        else:
            st.warning("No drivers available in this session")
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("⬆️ Load session data first to select drivers")
    
    # Analysis tabs
    if selected_drivers and hasattr(st.session_state.data_loader, 'session'):
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📈 Telemetry",
            "🗺️ Track Map", 
            "⏱️ Lap Times",
            "🔧 Tire Strategy",
            "📊 Race Progress",
            "🧠 Advanced Analytics"
        ])
        
        with tab1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">📈 Telemetry Analysis</div>', unsafe_allow_html=True)
            
            telemetry_type = st.selectbox(
                "Telemetry Parameter",
                ["Speed", "Throttle", "Brake", "RPM", "Gear"],
                help="Select telemetry data to analyze"
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
                    else:
                        st.error("Unable to generate telemetry plot")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">🗺️ Track Dominance Map</div>', unsafe_allow_html=True)
            
            with st.spinner("Creating track dominance map..."):
                try:
                    fig = create_track_dominance_map(
                        st.session_state.data_loader,
                        selected_drivers
                    )
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("Unable to generate track map")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab3:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">⏱️ Lap Time Comparison</div>', unsafe_allow_html=True)
            
            try:
                session = st.session_state.data_loader.session
                laps_data = []
                
                for driver in selected_drivers:
                    driver_laps = session.laps.pick_drivers([driver]).pick_quicklaps()
                    if not driver_laps.empty:
                        best_lap = driver_laps.pick_fastest()
                        lap_time = best_lap['LapTime'].total_seconds()
                        laps_data.append({
                            'Driver': driver,
                            'Best Lap Time': format_lap_time(lap_time),
                            'Lap Number': best_lap['LapNumber'],
                            'Compound': best_lap['Compound']
                        })
                
                if laps_data:
                    df = pd.DataFrame(laps_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("No lap data available")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab4:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">🔧 Tire Strategy Analysis</div>', unsafe_allow_html=True)
            
            with st.spinner("Analyzing tire strategy..."):
                try:
                    fig = create_tire_strategy_plot(
                        st.session_state.data_loader,
                        selected_drivers
                    )
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("Unable to generate tire strategy plot")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab5:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">📊 Race Progression</div>', unsafe_allow_html=True)
            
            with st.spinner("Creating race progression chart..."):
                try:
                    fig = create_race_progression_plot(
                        st.session_state.data_loader,
                        selected_drivers
                    )
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("Unable to generate race progression plot")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab6:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">🧠 Advanced Analytics</div>', unsafe_allow_html=True)
            
            try:
                analytics = AdvancedF1Analytics(st.session_state.data_loader.session)
                
                # Display driver consistency metrics
                st.markdown("**Driver Consistency Analysis:**")
                
                consistency_data = []
                for driver in selected_drivers:
                    consistency = analytics.calculate_driver_consistency(driver)
                    if consistency:
                        consistency_data.append({
                            'Driver': driver,
                            'Consistency Score': f"{consistency['consistency_score']:.3f}",
                            'Fastest Lap': format_lap_time(consistency['fastest_lap']),
                            'Mean Lap Time': format_lap_time(consistency['mean_lap_time']),
                            'Total Laps': consistency['total_laps']
                        })
                
                if consistency_data:
                    # Display metrics grid
                    for data in consistency_data:
                        st.markdown(f"""
                        <div class="metric-grid">
                            <div class="metric-card">
                                <div class="metric-value">{data['Driver']}</div>
                                <div class="metric-label">Driver</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{data['Consistency Score']}</div>
                                <div class="metric-label">Consistency</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{data['Fastest Lap']}</div>
                                <div class="metric-label">Fastest Lap</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">{data['Total Laps']}</div>
                                <div class="metric-label">Laps Completed</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Full data table
                    st.markdown("**Detailed Analytics:**")
                    df = pd.DataFrame(consistency_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("No analytics data available for selected drivers")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    elif not selected_drivers and hasattr(st.session_state.data_loader, 'session'):
        st.info("👆 Select drivers to view analysis tabs")
    else:
        st.info("⬆️ Load session data and select drivers to begin analysis")

if __name__ == "__main__":
    main()