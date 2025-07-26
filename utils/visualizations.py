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
        
        # Initialize y_title based on telemetry_type
        y_title_map = {
            'speed': 'Speed (km/h)',
            'throttle': 'Throttle (%)',
            'brake': 'Brake Pressure',
            'rpm': 'Engine RPM',
            'gear': 'Gear'
        }
        y_title = y_title_map.get(telemetry_type.lower(), telemetry_type.title())
        
        for driver in drivers:
            if driver not in telemetry_data:
                continue
                
            telemetry = telemetry_data[driver]
            
            if telemetry_type.lower() == 'speed' and 'Speed' in telemetry.columns:
                y_data = telemetry['Speed']
            elif telemetry_type.lower() == 'throttle' and 'Throttle' in telemetry.columns:
                y_data = telemetry['Throttle']
            elif telemetry_type.lower() == 'brake' and 'Brake' in telemetry.columns:
                y_data = telemetry['Brake']
            elif telemetry_type.lower() == 'rpm' and 'RPM' in telemetry.columns:
                y_data = telemetry['RPM']
            elif telemetry_type.lower() == 'gear' and 'nGear' in telemetry.columns:
                y_data = telemetry['nGear']
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
        
        # y_title is already defined above
            
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
            
            # Plot stints with enhanced styling
            team = DRIVER_TEAMS.get(driver, 'Unknown')
            team_color = TEAM_COLORS.get(team, '#FFFFFF')
            
            for i, stint in enumerate(stints):
                tire_color = TIRE_COLORS.get(stint['compound'], '#808080')
                
                # Create gradient effect by varying opacity
                opacity = 0.8 if i % 2 == 0 else 0.9
                
                fig.add_trace(go.Bar(
                    x=[stint['laps']],
                    y=[driver],
                    orientation='h',
                    name=f"{driver} - {stint['compound']}",
                    marker=dict(
                        color=tire_color,
                        opacity=opacity,
                        line=dict(color=team_color, width=2)
                    ),
                    base=stint['start_lap'] - 1,
                    hovertemplate=(
                        f"<b>{driver}</b> ({team})<br>"
                        f"Compound: {stint['compound']}<br>"
                        f"Laps: {stint['start_lap']}-{stint['end_lap']}<br>"
                        f"Stint Length: {stint['laps']} laps"
                        "<extra></extra>"
                    ),
                    showlegend=False
                ))
                
                # Add stint length annotation
                fig.add_annotation(
                    x=stint['start_lap'] + stint['laps']/2 - 1,
                    y=y_pos,
                    text=str(stint['laps']),
                    showarrow=False,
                    font=dict(color="white", size=10, family="monospace")
                )
            
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
            title="Enhanced Tire Strategy Analysis",
            xaxis_title="Lap Number",
            yaxis_title="Driver",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            barmode='overlay',
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(0,0,0,0.5)",
                bordercolor="rgba(255,255,255,0.2)",
                borderwidth=1
            ),
            hovermode='closest'
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating tire strategy plot: {str(e)}")
        return None

def create_race_progression_plot(data_loader, drivers):
    """Create professional race progression visualization with enhanced features"""
    try:
        position_data = data_loader.get_position_data(drivers)
        
        if position_data is None or position_data.empty:
            return None
        
        fig = go.Figure()
        
        # Add background grid for better readability
        max_laps = position_data['LapNumber'].max()
        max_pos = position_data['Position'].max()
        
        # Create enhanced traces for each driver
        for driver in drivers:
            driver_data = position_data[position_data['Driver'] == driver].sort_values('LapNumber')
            if driver_data.empty:
                continue
            
            team = DRIVER_TEAMS.get(driver, 'Unknown')
            color = TEAM_COLORS.get(team, '#FFFFFF')
            
            # Get position changes for annotations
            start_pos = driver_data['Position'].iloc[0]
            end_pos = driver_data['Position'].iloc[-1]
            position_change = start_pos - end_pos
            
            # Create smooth line with markers
            fig.add_trace(go.Scatter(
                x=driver_data['LapNumber'],
                y=driver_data['Position'],
                mode='lines+markers',
                name=f"{driver} (P{start_pos}→P{end_pos})",
                line=dict(
                    color=color, 
                    width=4,
                    shape='spline',
                    smoothing=1.0
                ),
                marker=dict(
                    size=8, 
                    color=color,
                    line=dict(width=2, color='white')
                ),
                fill=None,
                connectgaps=True,
                hovertemplate=f"""
                <b>{driver} ({team})</b><br>
                Lap: %{{x}}<br>
                Position: P%{{y}}<br>
                <extra></extra>
                """
            ))
            
            # Add start/finish position annotations
            fig.add_annotation(
                x=driver_data['LapNumber'].iloc[0],
                y=start_pos,
                text=f"P{start_pos}",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor=color,
                font=dict(size=10, color=color),
                bgcolor="rgba(0,0,0,0.7)",
                bordercolor=color,
                borderwidth=1
            )
            
            fig.add_annotation(
                x=driver_data['LapNumber'].iloc[-1],
                y=end_pos,
                text=f"P{end_pos}",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor=color,
                font=dict(size=10, color=color),
                bgcolor="rgba(0,0,0,0.7)",
                bordercolor=color,
                borderwidth=1
            )
        
        # Enhanced layout with professional styling
        fig.update_layout(
            title={
                'text': "📊 Race Progression Analysis<br><sub>Position Changes Throughout the Race</sub>",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24, 'color': 'white'}
            },
            xaxis=dict(
                title="Lap Number",
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(255,255,255,0.1)',
                range=[0, max_laps + 2],
                dtick=5,
                title_font=dict(size=14, color='white'),
                tickfont=dict(size=12, color='white')
            ),
            yaxis=dict(
                title="Track Position",
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(255,255,255,0.1)',
                autorange='reversed',  # Reverse so P1 is at top
                dtick=1,
                range=[max_pos + 0.5, 0.5],
                title_font=dict(size=14, color='white'),
                tickfont=dict(size=12, color='white')
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            legend=dict(
                orientation="v",
                yanchor="top",
                y=0.98,
                xanchor="left",
                x=0.02,
                bgcolor='rgba(24, 25, 26, 0.8)',
                bordercolor='rgba(0, 210, 190, 0.3)',
                borderwidth=1,
                font=dict(size=11)
            ),
            hovermode='x unified',
            margin=dict(l=60, r=20, t=80, b=60)
        )
        
        # Add position lines for reference
        for pos in range(1, min(max_pos + 1, 21)):  # Only show up to P20
            fig.add_shape(
                type="line",
                x0=0, y0=pos, x1=max_laps, y1=pos,
                line=dict(
                    color="rgba(255,255,255,0.05)",
                    width=1,
                    dash="dot"
                )
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
