"""
Power Unit Analysis for F1 Data
Analyzes engine performance, energy recovery, and power delivery
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .constants import TEAM_COLORS, DRIVER_TEAMS
from .formatters import format_lap_time

class PowerAnalyzer:
    """Advanced power unit and energy analysis"""
    
    def __init__(self, session):
        self.session = session
        
    def analyze_power_delivery(self, drivers):
        """Analyze power unit performance metrics"""
        power_data = []
        
        for driver in drivers:
            try:
                driver_laps = self.session.laps.pick_drivers([driver])
                if driver_laps.empty:
                    continue
                
                fastest_lap = driver_laps.pick_fastest()
                telemetry = fastest_lap.get_telemetry()
                
                if 'Speed' in telemetry.columns and 'Throttle' in telemetry.columns:
                    # Calculate power-related metrics
                    max_speed = telemetry['Speed'].max()
                    avg_speed = telemetry['Speed'].mean()
                    
                    # Throttle application analysis
                    full_throttle_pct = (telemetry['Throttle'] == 100).sum() / len(telemetry) * 100
                    avg_throttle = telemetry['Throttle'].mean()
                    
                    # Power efficiency estimate
                    power_efficiency = (avg_speed / max_speed) * (avg_throttle / 100) * 100
                    
                    # Acceleration zones (throttle > 80% and increasing speed)
                    speed_diff = telemetry['Speed'].diff()
                    accel_zones = ((telemetry['Throttle'] > 80) & (speed_diff > 0)).sum()
                    
                    power_data.append({
                        'driver': driver,
                        'max_speed': f"{max_speed:.1f} km/h",
                        'avg_speed': f"{avg_speed:.1f} km/h",
                        'full_throttle_pct': f"{full_throttle_pct:.1f}%",
                        'avg_throttle': f"{avg_throttle:.1f}%",
                        'power_efficiency': f"{power_efficiency:.1f}%",
                        'acceleration_zones': int(accel_zones),
                        'power_score': power_efficiency
                    })
                    
            except Exception as e:
                print(f"Error analyzing power for {driver}: {e}")
                continue
                
        return power_data
    
    def create_power_comparison_chart(self, drivers):
        """Create power unit comparison visualization"""
        try:
            power_data = self.analyze_power_delivery(drivers)
            if not power_data:
                return None
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Maximum Speed', 'Power Efficiency', 
                               'Throttle Application', 'Acceleration Zones'),
                specs=[[{"type": "bar"}, {"type": "bar"}],
                       [{"type": "bar"}, {"type": "bar"}]]
            )
            
            drivers_list = [d['driver'] for d in power_data]
            colors = [TEAM_COLORS.get(DRIVER_TEAMS.get(d, 'Unknown'), '#808080') for d in drivers_list]
            
            # Max speed
            max_speeds = [float(d['max_speed'].replace(' km/h', '')) for d in power_data]
            fig.add_trace(
                go.Bar(x=drivers_list, y=max_speeds, name='Max Speed', 
                       marker_color=colors, showlegend=False),
                row=1, col=1
            )
            
            # Power efficiency
            efficiencies = [float(d['power_efficiency'].replace('%', '')) for d in power_data]
            fig.add_trace(
                go.Bar(x=drivers_list, y=efficiencies, name='Efficiency', 
                       marker_color=colors, showlegend=False),
                row=1, col=2
            )
            
            # Throttle application
            throttle_pcts = [float(d['full_throttle_pct'].replace('%', '')) for d in power_data]
            fig.add_trace(
                go.Bar(x=drivers_list, y=throttle_pcts, name='Full Throttle %', 
                       marker_color=colors, showlegend=False),
                row=2, col=1
            )
            
            # Acceleration zones
            accel_zones = [d['acceleration_zones'] for d in power_data]
            fig.add_trace(
                go.Bar(x=drivers_list, y=accel_zones, name='Acceleration Zones', 
                       marker_color=colors, showlegend=False),
                row=2, col=2
            )
            
            fig.update_layout(
                title='⚡ Power Unit Analysis',
                height=600,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating power comparison: {e}")
            return None

def analyze_energy_recovery(session, driver):
    """Analyze ERS deployment and energy recovery patterns"""
    try:
        driver_laps = session.laps.pick_drivers([driver])
        if driver_laps.empty:
            return None
        
        fastest_lap = driver_laps.pick_fastest()
        telemetry = fastest_lap.get_telemetry().add_distance()
        
        if 'Throttle' not in telemetry.columns or 'Brake' not in telemetry.columns:
            return None
        
        fig = go.Figure()
        
        # Throttle trace (power deployment)
        fig.add_trace(go.Scatter(
            x=telemetry['Distance'],
            y=telemetry['Throttle'],
            mode='lines',
            name='Throttle %',
            line=dict(color='#00ff00', width=2),
            yaxis='y'
        ))
        
        # Brake trace (energy recovery)
        fig.add_trace(go.Scatter(
            x=telemetry['Distance'],
            y=telemetry['Brake'],
            mode='lines',
            name='Brake %',
            line=dict(color='#ff0000', width=2),
            yaxis='y'
        ))
        
        # Speed trace
        fig.add_trace(go.Scatter(
            x=telemetry['Distance'],
            y=telemetry['Speed'],
            mode='lines',
            name='Speed (km/h)',
            line=dict(color='#0080ff', width=2),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title=f'Energy Management - {driver}',
            xaxis_title='Distance (m)',
            yaxis=dict(title='Throttle/Brake %', side='left'),
            yaxis2=dict(title='Speed (km/h)', overlaying='y', side='right'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            hovermode='x unified'
        )
        
        return fig
        
    except Exception as e:
        print(f"Error analyzing energy recovery: {e}")
        return None