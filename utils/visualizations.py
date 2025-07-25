"""
Visualization utilities for F1 data analysis
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import streamlit as st
from .constants import TEAM_COLORS, DRIVER_TEAMS, TIRE_COLORS

def create_telemetry_plot(data_loader, drivers, telemetry_type='speed'):
    """Create telemetry comparison plot"""
    if not drivers:
        return None
    
    try:
        telemetry_data = data_loader.get_fastest_lap_telemetry(drivers)
        
        if not telemetry_data:
            return None
        
        fig = go.Figure()
        
        for driver in drivers:
            if driver not in telemetry_data:
                continue
                
            telemetry = telemetry_data[driver]
            
            if telemetry_type.lower() == 'speed' and 'Speed' in telemetry.columns:
                y_data = telemetry['Speed']
                y_title = 'Speed (km/h)'
            elif telemetry_type.lower() == 'throttle' and 'Throttle' in telemetry.columns:
                y_data = telemetry['Throttle']
                y_title = 'Throttle (%)'
            elif telemetry_type.lower() == 'brake' and 'Brake' in telemetry.columns:
                y_data = telemetry['Brake']
                y_title = 'Brake Pressure'
            elif telemetry_type.lower() == 'rpm' and 'RPM' in telemetry.columns:
                y_data = telemetry['RPM']
                y_title = 'Engine RPM'
            elif telemetry_type.lower() == 'gear' and 'nGear' in telemetry.columns:
                y_data = telemetry['nGear']
                y_title = 'Gear'
            else:
                continue
            
            team = DRIVER_TEAMS.get(driver, 'Unknown')
            color = TEAM_COLORS.get(team, '#FFFFFF')
            
            fig.add_trace(go.Scatter(
                x=telemetry['Distance'] if 'Distance' in telemetry.columns else range(len(y_data)),
                y=y_data,
                mode='lines',
                name=f"{driver} ({team})",
                line=dict(color=color, width=3),
                hovertemplate=f"<b>{driver}</b><br>Distance: %{{x:.0f}}m<br>{y_title}: %{{y:.1f}}<extra></extra>"
            ))
        
        # Set default y_title if not defined
        if 'y_title' not in locals():
            y_title = telemetry_type.title()
            
        fig.update_layout(
            title=f"{telemetry_type.title()} Comparison - Fastest Laps",
            xaxis_title="Distance (m)" if any('Distance' in telemetry_data[d].columns for d in telemetry_data) else "Data Points",
            yaxis_title=y_title,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode='x unified'
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating telemetry plot: {str(e)}")
        return None

def create_tire_strategy_plot(data_loader, drivers):
    """Create tire strategy visualization"""
    try:
        tire_data = data_loader.get_tire_data(drivers)
        
        if tire_data is None or tire_data.empty:
            return None
        
        fig = go.Figure()
        
        y_pos = 0
        for driver in drivers:
            driver_data = tire_data[tire_data['Driver'] == driver]
            if driver_data.empty:
                continue
            
            # Group consecutive laps with same compound
            stints = []
            current_compound = None
            stint_start = None
            prev_lap_num = None
            
            for _, lap in driver_data.iterrows():
                if current_compound != lap['Compound']:
                    if current_compound is not None and prev_lap_num is not None:
                        stints.append({
                            'compound': current_compound,
                            'start_lap': stint_start,
                            'end_lap': prev_lap_num,
                            'laps': prev_lap_num - stint_start + 1
                        })
                    current_compound = lap['Compound']
                    stint_start = lap['LapNumber']
                prev_lap_num = lap['LapNumber']
            
            # Add final stint
            if current_compound is not None and prev_lap_num is not None:
                stints.append({
                    'compound': current_compound,
                    'start_lap': stint_start,
                    'end_lap': prev_lap_num,
                    'laps': prev_lap_num - stint_start + 1
                })
            
            # Plot stints
            for stint in stints:
                color = TIRE_COLORS.get(stint['compound'], '#808080')
                
                fig.add_trace(go.Bar(
                    x=[stint['laps']],
                    y=[driver],
                    orientation='h',
                    name=f"{driver} - {stint['compound']}",
                    marker_color=color,
                    base=stint['start_lap'] - 1,
                    hovertemplate=f"<b>{driver}</b><br>Compound: {stint['compound']}<br>Laps: {stint['start_lap']}-{stint['end_lap']}<br>Stint Length: {stint['laps']} laps<extra></extra>",
                    showlegend=False
                ))
            
            y_pos += 1
        
        # Add compound legend
        compounds_used = tire_data['Compound'].unique()
        for compound in compounds_used:
            if compound in TIRE_COLORS:
                fig.add_trace(go.Scatter(
                    x=[None], y=[None],
                    mode='markers',
                    marker=dict(size=15, color=TIRE_COLORS[compound], symbol='square'),
                    name=compound,
                    showlegend=True
                ))
        
        fig.update_layout(
            title="Tire Strategy Analysis",
            xaxis_title="Lap Number",
            yaxis_title="Driver",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            barmode='overlay',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating tire strategy plot: {str(e)}")
        return None

def create_race_progression_plot(data_loader, drivers):
    """Create race progression visualization"""
    try:
        position_data = data_loader.get_position_data(drivers)
        
        if position_data is None or position_data.empty:
            return None
        
        fig = go.Figure()
        
        for driver in drivers:
            driver_data = position_data[position_data['Driver'] == driver]
            if driver_data.empty:
                continue
            
            team = DRIVER_TEAMS.get(driver, 'Unknown')
            color = TEAM_COLORS.get(team, '#FFFFFF')
            
            fig.add_trace(go.Scatter(
                x=driver_data['LapNumber'],
                y=driver_data['Position'],
                mode='lines+markers',
                name=f"{driver} ({team})",
                line=dict(color=color, width=3),
                marker=dict(size=6, color=color),
                hovertemplate=f"<b>{driver}</b><br>Lap: %{{x}}<br>Position: P%{{y}}<extra></extra>"
            ))
        
        fig.update_layout(
            title="Race Progression - Position Changes",
            xaxis_title="Lap Number",
            yaxis_title="Position",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            yaxis=dict(autorange='reversed'),  # Reverse Y-axis so P1 is at top
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode='x unified'
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating race progression plot: {str(e)}")
        return None

def create_sector_comparison_plot(data_loader, drivers):
    """Create sector time comparison plot"""
    try:
        lap_data = data_loader.get_lap_comparison(drivers)
        
        if lap_data is None or lap_data.empty:
            return None
        
        # Get fastest lap for each driver
        fastest_laps = lap_data.loc[lap_data.groupby('Driver')['LapTime_seconds'].idxmin()]
        
        sectors = ['Sector1Time', 'Sector2Time', 'Sector3Time']
        sector_data = []
        
        for _, lap in fastest_laps.iterrows():
            driver = lap['Driver']
            team = DRIVER_TEAMS.get(driver, 'Unknown')
            
            for i, sector in enumerate(sectors, 1):
                if pd.notna(lap[sector]) and hasattr(lap[sector], 'total_seconds'):
                    sector_data.append({
                        'Driver': driver,
                        'Team': team,
                        'Sector': f'S{i}',
                        'Time': lap[sector].total_seconds()
                    })
        
        if not sector_data:
            return None
        
        sector_df = pd.DataFrame(sector_data)
        
        fig = px.bar(
            sector_df,
            x='Sector',
            y='Time',
            color='Driver',
            color_discrete_map={
                driver: TEAM_COLORS.get(DRIVER_TEAMS.get(driver, 'Unknown'), '#FFFFFF')
                for driver in drivers
            },
            title="Sector Time Comparison - Fastest Laps",
            labels={'Time': 'Sector Time (seconds)'},
            barmode='group'
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating sector comparison plot: {str(e)}")
        return None
