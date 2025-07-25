"""
Track dominance map visualization for F1 analysis
"""

import plotly.graph_objects as go
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import streamlit as st
from .constants import TEAM_COLORS, DRIVER_TEAMS

def interpolate_track_coordinates(X, Y, num_points=2000):
    """Interpolate track coordinates for smooth visualization"""
    try:
        # Remove NaN values
        mask = ~(np.isnan(X) | np.isnan(Y))
        X_clean = X[mask]
        Y_clean = Y[mask]
        
        if len(X_clean) < 4:  # Need at least 4 points for cubic interpolation
            return X_clean, Y_clean, np.linspace(0, 1, len(X_clean))
        
        # Calculate cumulative distance
        dist = np.sqrt(np.diff(X_clean)**2 + np.diff(Y_clean)**2)
        cumdist = np.insert(np.cumsum(dist), 0, 0)
        
        # Create interpolation functions
        fx = interp1d(cumdist, X_clean, kind='cubic', fill_value='extrapolate')
        fy = interp1d(cumdist, Y_clean, kind='cubic', fill_value='extrapolate')
        
        # Create uniform distance array
        uniform_dist = np.linspace(cumdist[0], cumdist[-1], num_points)
        
        # Interpolate coordinates
        X_new = fx(uniform_dist)
        Y_new = fy(uniform_dist)
        
        return X_new, Y_new, uniform_dist
    
    except Exception as e:
        st.error(f"Error interpolating track coordinates: {str(e)}")
        return X, Y, np.linspace(0, 1, len(X))

def create_track_dominance_map(data_loader, drivers, num_minisectors=200, show_track_outline=True):
    """Create track dominance map showing fastest mini-sectors"""
    try:
        telemetry_data = data_loader.get_fastest_lap_telemetry(drivers)
        
        if not telemetry_data:
            return None
        
        # Prepare interpolated telemetry for each driver
        driver_telemetry = {}
        
        for driver in drivers:
            if driver not in telemetry_data:
                continue
                
            telemetry = telemetry_data[driver]
            
            if 'X' not in telemetry.columns or 'Y' not in telemetry.columns or 'Speed' not in telemetry.columns:
                continue
            
            # Interpolate track coordinates and speed
            X_interp, Y_interp, dist = interpolate_track_coordinates(
                telemetry['X'].values, 
                telemetry['Y'].values, 
                num_minisectors
            )
            
            # Interpolate speed data
            if len(telemetry['Speed']) > 1:
                speed_interp_func = interp1d(
                    np.linspace(0, 1, len(telemetry)), 
                    telemetry['Speed'].values, 
                    kind='linear', 
                    fill_value='extrapolate'
                )
                speed_interp = speed_interp_func(np.linspace(0, 1, len(X_interp)))
            else:
                speed_interp = np.full(len(X_interp), telemetry['Speed'].iloc[0])
            
            driver_telemetry[driver] = {
                'X': X_interp,
                'Y': Y_interp,
                'Speed': speed_interp,
                'Distance': np.linspace(0, 1, len(X_interp))
            }
        
        if not driver_telemetry:
            return None
        
        fig = go.Figure()
        
        # Create mini-sectors and find fastest driver for each
        mini_sectors = np.linspace(0, 1, num_minisectors)
        
        for i in range(num_minisectors - 1):
            fastest_driver = None
            fastest_speed = -1
            fastest_sector_data = None
            
            # Find fastest driver in this mini-sector
            for driver, tel in driver_telemetry.items():
                mask = (tel['Distance'] >= mini_sectors[i]) & (tel['Distance'] < mini_sectors[i+1])
                
                if not np.any(mask):
                    continue
                
                mean_speed = np.mean(tel['Speed'][mask])
                
                if mean_speed > fastest_speed:
                    fastest_speed = mean_speed
                    fastest_driver = driver
                    fastest_sector_data = {
                        'X': tel['X'][mask],
                        'Y': tel['Y'][mask]
                    }
            
            # Plot the fastest sector
            if fastest_sector_data is not None and fastest_driver is not None:
                team = DRIVER_TEAMS.get(fastest_driver, 'Unknown')
                color = TEAM_COLORS.get(team, '#FFFFFF')
                
                fig.add_trace(go.Scatter(
                    x=fastest_sector_data['X'],
                    y=fastest_sector_data['Y'],
                    mode='lines',
                    line=dict(color=color, width=6),
                    name=fastest_driver,
                    showlegend=False,
                    hovertemplate=f"<b>{fastest_driver}</b><br>Speed: {fastest_speed:.1f} km/h<extra></extra>"
                ))
        
        # Show track outline if requested
        if show_track_outline:
            # Use first driver's track coordinates for outline
            first_driver = list(driver_telemetry.keys())[0]
            outline_data = driver_telemetry[first_driver]
            
            fig.add_trace(go.Scatter(
                x=outline_data['X'],
                y=outline_data['Y'],
                mode='lines',
                line=dict(color='rgba(255,255,255,0.3)', width=1),
                name='Track Outline',
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Add legend for drivers
        for driver in drivers:
            if driver in driver_telemetry:
                team = DRIVER_TEAMS.get(driver, 'Unknown')
                color = TEAM_COLORS.get(team, '#FFFFFF')
                
                fig.add_trace(go.Scatter(
                    x=[None], y=[None],
                    mode='lines',
                    line=dict(color=color, width=6),
                    name=f"{driver} ({team})",
                    showlegend=True
                ))
        
        fig.update_layout(
            title=f"Track Dominance Map - Fastest Mini-Sectors ({num_minisectors} sectors)",
            xaxis=dict(
                showgrid=False,
                showticklabels=False,
                zeroline=False,
                scaleanchor="y",
                scaleratio=1
            ),
            yaxis=dict(
                showgrid=False,
                showticklabels=False,
                zeroline=False
            ),
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
            showlegend=True,
            hovermode='closest'
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating track dominance map: {str(e)}")
        return None

def create_speed_heatmap(data_loader, driver):
    """Create speed heatmap for a single driver"""
    try:
        telemetry = data_loader.get_driver_telemetry(driver)
        
        if telemetry is None or telemetry.empty:
            return None
        
        if 'X' not in telemetry.columns or 'Y' not in telemetry.columns or 'Speed' not in telemetry.columns:
            return None
        
        fig = go.Figure()
        
        # Create speed-colored track
        fig.add_trace(go.Scatter(
            x=telemetry['X'],
            y=telemetry['Y'],
            mode='markers',
            marker=dict(
                size=4,
                color=telemetry['Speed'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Speed (km/h)")
            ),
            name=f"{driver} Speed",
            hovertemplate=f"<b>{driver}</b><br>Speed: %{{marker.color:.1f}} km/h<extra></extra>"
        ))
        
        team = DRIVER_TEAMS.get(driver, 'Unknown')
        
        fig.update_layout(
            title=f"Speed Heatmap - {driver} ({team})",
            xaxis=dict(
                showgrid=False,
                showticklabels=False,
                zeroline=False,
                scaleanchor="y",
                scaleratio=1
            ),
            yaxis=dict(
                showgrid=False,
                showticklabels=False,
                zeroline=False
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating speed heatmap: {str(e)}")
        return None
