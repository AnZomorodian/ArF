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

# Configure page
st.set_page_config(
    page_title="F1 Data Analysis Platform",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for F1 styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(135deg, #DC0000, #00D2BE);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #23272F, #18191A);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #00D2BE;
        margin: 0.5rem 0;
    }
    
    .driver-tag {
        display: inline-block;
        padding: 0.2rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
        margin: 0.2rem;
        color: white;
    }
    
    .stSelectbox > div > div {
        background-color: #23272F;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #23272F, #18191A);
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
                        # Fastest lap times
                        st.subheader("🏆 Fastest Lap Times")
                        fastest_laps = lap_data.groupby('Driver')['LapTime'].min().sort_values()
                        
                        for i, (driver, lap_time) in enumerate(fastest_laps.items()):
                            team = DRIVER_TEAMS.get(driver, 'Unknown')
                            color = TEAM_COLORS.get(team, '#FFFFFF')
                            
                            col1, col2, col3 = st.columns([1, 2, 1])
                            with col2:
                                if i == 0:
                                    st.success(f"🥇 {driver}: {lap_time}")
                                elif i == 1:
                                    st.info(f"🥈 {driver}: {lap_time}")
                                elif i == 2:
                                    st.warning(f"🥉 {driver}: {lap_time}")
                                else:
                                    st.text(f"{i+1}. {driver}: {lap_time}")
                        
                        # Lap time distribution
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
                            title="Lap Time Distribution by Driver"
                        )
                        fig.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font_color='white'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Detailed lap times table
                        st.subheader("📋 Detailed Lap Times")
                        display_data = lap_data[['Driver', 'LapNumber', 'LapTime', 'Compound']].copy()
                        st.dataframe(display_data, use_container_width=True)
                        
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
                        
                        # Position changes summary
                        st.subheader("📈 Position Changes")
                        position_data = st.session_state.data_loader.get_position_data(selected_drivers)
                        if position_data is not None and not position_data.empty:
                            start_positions = position_data.groupby('Driver')['Position'].first()
                            end_positions = position_data.groupby('Driver')['Position'].last()
                            position_changes = start_positions - end_positions
                            
                            for driver in selected_drivers:
                                if driver in position_changes:
                                    change = position_changes[driver]
                                    start_pos = start_positions[driver]
                                    end_pos = end_positions[driver]
                                    
                                    if change > 0:
                                        st.success(f"📈 {driver}: P{start_pos} → P{end_pos} (+{change} positions)")
                                    elif change < 0:
                                        st.error(f"📉 {driver}: P{start_pos} → P{end_pos} ({change} positions)")
                                    else:
                                        st.info(f"➡️ {driver}: P{start_pos} → P{end_pos} (no change)")
                        
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
