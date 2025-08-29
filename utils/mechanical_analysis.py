"""
Mechanical Performance and Reliability Analysis for F1 Data
Analyzes car setup, mechanical grip, and component performance
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .constants import TEAM_COLORS, DRIVER_TEAMS
from .formatters import format_lap_time

class MechanicalAnalyzer:
    """Advanced mechanical performance analysis"""
    
    def __init__(self, session):
        self.session = session
        
    def analyze_mechanical_grip(self, drivers):
        """Analyze mechanical grip and setup effectiveness"""
        grip_data = []
        
        for driver in drivers:
            try:
                driver_laps = self.session.laps.pick_drivers([driver])
                if driver_laps.empty:
                    continue
                
                fastest_lap = driver_laps.pick_fastest()
                telemetry = fastest_lap.get_telemetry()
                
                if 'Speed' not in telemetry.columns:
                    continue
                
                # Analyze cornering performance (mechanical grip indicator)
                # Low speed corners indicate mechanical grip
                low_speed_sections = telemetry[telemetry['Speed'] < 100]
                if len(low_speed_sections) > 0:
                    low_speed_consistency = 100 - (low_speed_sections['Speed'].std() / low_speed_sections['Speed'].mean() * 100)
                else:
                    low_speed_consistency = 50
                
                # Medium speed corners (setup balance)
                medium_speed_sections = telemetry[(telemetry['Speed'] >= 100) & (telemetry['Speed'] < 200)]
                if len(medium_speed_sections) > 0:
                    medium_speed_efficiency = medium_speed_sections['Speed'].mean() / 150 * 100
                else:
                    medium_speed_efficiency = 50
                
                # High speed stability (aero efficiency)
                high_speed_sections = telemetry[telemetry['Speed'] >= 200]
                if len(high_speed_sections) > 0:
                    high_speed_stability = 100 - (high_speed_sections['Speed'].std() / high_speed_sections['Speed'].mean() * 100)
                else:
                    high_speed_stability = 50
                
                # Overall mechanical score
                mechanical_score = (low_speed_consistency + medium_speed_efficiency + high_speed_stability) / 3
                
                # Tire degradation analysis
                lap_times = []
                for _, lap in driver_laps.iterrows():
                    if pd.notna(lap['LapTime']):
                        lap_times.append(lap['LapTime'].total_seconds())
                
                degradation_rate = 0
                if len(lap_times) >= 10:
                    # Calculate degradation over stint
                    first_half = np.mean(lap_times[:len(lap_times)//2])
                    second_half = np.mean(lap_times[len(lap_times)//2:])
                    degradation_rate = (second_half - first_half) / first_half * 100
                
                grip_data.append({
                    'driver': driver,
                    'low_speed_grip': f"{low_speed_consistency:.1f}%",
                    'medium_speed_balance': f"{medium_speed_efficiency:.1f}%",
                    'high_speed_stability': f"{high_speed_stability:.1f}%",
                    'mechanical_score': f"{mechanical_score:.1f}%",
                    'tire_degradation': f"{degradation_rate:.2f}%",
                    'setup_effectiveness': mechanical_score
                })
                
            except Exception as e:
                print(f"Error analyzing mechanical grip for {driver}: {e}")
                continue
                
        return grip_data
    
    def analyze_component_stress(self, drivers):
        """Analyze component stress and reliability indicators"""
        stress_data = []
        
        for driver in drivers:
            try:
                driver_laps = self.session.laps.pick_drivers([driver])
                if driver_laps.empty:
                    continue
                
                fastest_lap = driver_laps.pick_fastest()
                telemetry = fastest_lap.get_telemetry()
                
                stress_metrics = {}
                
                # Engine stress (RPM analysis)
                if 'RPM' in telemetry.columns:
                    rpm_data = telemetry['RPM'].dropna()
                    if not rpm_data.empty:
                        high_rpm_time = (rpm_data > rpm_data.quantile(0.9)).sum() / len(rpm_data) * 100
                        stress_metrics['engine_stress'] = high_rpm_time
                    else:
                        stress_metrics['engine_stress'] = 50
                else:
                    stress_metrics['engine_stress'] = 50
                
                # Brake stress
                if 'Brake' in telemetry.columns:
                    brake_data = telemetry['Brake'].dropna()
                    if not brake_data.empty:
                        heavy_braking_time = (brake_data > 80).sum() / len(brake_data) * 100
                        stress_metrics['brake_stress'] = heavy_braking_time
                    else:
                        stress_metrics['brake_stress'] = 50
                else:
                    stress_metrics['brake_stress'] = 50
                
                # Throttle stress
                if 'Throttle' in telemetry.columns:
                    throttle_data = telemetry['Throttle'].dropna()
                    if not throttle_data.empty:
                        full_throttle_time = (throttle_data == 100).sum() / len(throttle_data) * 100
                        stress_metrics['throttle_stress'] = full_throttle_time
                    else:
                        stress_metrics['throttle_stress'] = 50
                else:
                    stress_metrics['throttle_stress'] = 50
                
                # Calculate reliability score (inverse of stress)
                avg_stress = np.mean(list(stress_metrics.values()))
                reliability_score = max(0, 100 - avg_stress)
                
                stress_data.append({
                    'driver': driver,
                    'engine_stress': f"{stress_metrics['engine_stress']:.1f}%",
                    'brake_stress': f"{stress_metrics['brake_stress']:.1f}%",
                    'throttle_stress': f"{stress_metrics['throttle_stress']:.1f}%",
                    'reliability_score': f"{reliability_score:.1f}%",
                    'overall_stress': avg_stress
                })
                
            except Exception as e:
                print(f"Error analyzing component stress for {driver}: {e}")
                continue
                
        return stress_data
    
    def create_mechanical_analysis_chart(self, drivers):
        """Create comprehensive mechanical analysis visualization"""
        try:
            grip_data = self.analyze_mechanical_grip(drivers)
            stress_data = self.analyze_component_stress(drivers)
            
            if not grip_data or not stress_data:
                return None
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Mechanical Grip Analysis', 'Component Stress Levels', 
                               'Setup Effectiveness', 'Reliability vs Performance'),
                specs=[[{"type": "bar"}, {"type": "bar"}],
                       [{"type": "bar"}, {"type": "scatter"}]]
            )
            
            drivers_list = [d['driver'] for d in grip_data]
            colors = [TEAM_COLORS.get(DRIVER_TEAMS.get(d, 'Unknown'), '#808080') for d in drivers_list]
            
            # Mechanical grip - stacked bar
            low_speed = [float(d['low_speed_grip'].replace('%', '')) for d in grip_data]
            medium_speed = [float(d['medium_speed_balance'].replace('%', '')) for d in grip_data]
            high_speed = [float(d['high_speed_stability'].replace('%', '')) for d in grip_data]
            
            fig.add_trace(go.Bar(x=drivers_list, y=low_speed, name='Low Speed', 
                               marker_color='#ff6b6b', showlegend=True), row=1, col=1)
            fig.add_trace(go.Bar(x=drivers_list, y=medium_speed, name='Medium Speed', 
                               marker_color='#4ecdc4', showlegend=True), row=1, col=1)
            fig.add_trace(go.Bar(x=drivers_list, y=high_speed, name='High Speed', 
                               marker_color='#45b7d1', showlegend=True), row=1, col=1)
            
            # Component stress
            engine_stress = [float(d['engine_stress'].replace('%', '')) for d in stress_data]
            brake_stress = [float(d['brake_stress'].replace('%', '')) for d in stress_data]
            throttle_stress = [float(d['throttle_stress'].replace('%', '')) for d in stress_data]
            
            fig.add_trace(go.Bar(x=drivers_list, y=engine_stress, name='Engine', 
                               marker_color='#ff9999', showlegend=True), row=1, col=2)
            fig.add_trace(go.Bar(x=drivers_list, y=brake_stress, name='Brake', 
                               marker_color='#ffcc99', showlegend=True), row=1, col=2)
            fig.add_trace(go.Bar(x=drivers_list, y=throttle_stress, name='Throttle', 
                               marker_color='#99ccff', showlegend=True), row=1, col=2)
            
            # Setup effectiveness
            setup_scores = [d['setup_effectiveness'] for d in grip_data]
            fig.add_trace(go.Bar(x=drivers_list, y=setup_scores, name='Setup', 
                               marker_color=colors, showlegend=False), row=2, col=1)
            
            # Reliability vs Performance scatter
            reliability_scores = [float(d['reliability_score'].replace('%', '')) for d in stress_data]
            fig.add_trace(go.Scatter(
                x=setup_scores, y=reliability_scores, mode='markers+text',
                text=drivers_list, textposition='top center',
                marker=dict(size=15, color=colors),
                name='Drivers', showlegend=False
            ), row=2, col=2)
            
            fig.update_layout(
                title='🔧 Mechanical Performance Analysis',
                height=800,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating mechanical analysis chart: {e}")
            return None

def analyze_suspension_performance(session, driver):
    """Analyze suspension performance through telemetry patterns"""
    try:
        driver_laps = session.laps.pick_drivers([driver])
        if driver_laps.empty:
            return None
        
        fastest_lap = driver_laps.pick_fastest()
        telemetry = fastest_lap.get_telemetry().add_distance()
        
        if 'Speed' not in telemetry.columns:
            return None
        
        # Analyze speed variations in corners (suspension effectiveness indicator)
        fig = go.Figure()
        
        # Speed trace
        fig.add_trace(go.Scatter(
            x=telemetry['Distance'],
            y=telemetry['Speed'],
            mode='lines',
            name='Speed',
            line=dict(color='#00ff00', width=2)
        ))
        
        # Identify corner entry and exit (speed changes)
        speed_diff = telemetry['Speed'].diff()
        corner_entries = telemetry[speed_diff < -5]  # Significant deceleration
        corner_exits = telemetry[speed_diff > 5]     # Significant acceleration
        
        if not corner_entries.empty:
            fig.add_trace(go.Scatter(
                x=corner_entries['Distance'],
                y=corner_entries['Speed'],
                mode='markers',
                name='Corner Entry',
                marker=dict(color='#ff0000', size=8, symbol='triangle-down')
            ))
        
        if not corner_exits.empty:
            fig.add_trace(go.Scatter(
                x=corner_exits['Distance'],
                y=corner_exits['Speed'],
                mode='markers',
                name='Corner Exit',
                marker=dict(color='#0080ff', size=8, symbol='triangle-up')
            ))
        
        fig.update_layout(
            title=f'Suspension Performance Analysis - {driver}',
            xaxis_title='Distance (m)',
            yaxis_title='Speed (km/h)',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            hovermode='x unified'
        )
        
        return fig
        
    except Exception as e:
        print(f"Error analyzing suspension performance: {e}")
        return None