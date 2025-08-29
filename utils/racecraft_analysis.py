"""
Racecraft and Driving Style Analysis for F1 Data
Analyzes overtaking, defending, and racing intelligence
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .constants import TEAM_COLORS, DRIVER_TEAMS

class RacecraftAnalyzer:
    """Advanced racecraft and driving style analysis"""
    
    def __init__(self, session):
        self.session = session
        
    def analyze_overtaking_patterns(self, drivers):
        """Analyze overtaking opportunities and success rates"""
        overtaking_data = []
        
        for driver in drivers:
            try:
                driver_laps = self.session.laps.pick_drivers([driver])
                if driver_laps.empty:
                    continue
                
                positions = driver_laps['Position'].dropna()
                if len(positions) < 2:
                    continue
                
                # Calculate position changes
                position_changes = []
                overtakes = 0
                positions_lost = 0
                
                for i in range(1, len(positions)):
                    change = positions.iloc[i-1] - positions.iloc[i]  # Negative = lost position
                    position_changes.append(change)
                    
                    if change > 0:
                        overtakes += change
                    elif change < 0:
                        positions_lost += abs(change)
                
                # Racing aggression (position changes per lap)
                aggression_score = (overtakes + positions_lost) / len(driver_laps) * 100
                
                # Net position change
                net_change = positions.iloc[0] - positions.iloc[-1]
                
                # Consistency in wheel-to-wheel combat
                position_volatility = np.std(position_changes) if position_changes else 0
                
                overtaking_data.append({
                    'driver': driver,
                    'overtakes_made': int(overtakes),
                    'positions_lost': int(positions_lost),
                    'net_position_change': int(net_change),
                    'racing_aggression': f"{aggression_score:.2f}",
                    'position_volatility': f"{position_volatility:.2f}",
                    'racecraft_score': max(0, 100 - position_volatility * 10) if overtakes > 0 else 50
                })
                
            except Exception as e:
                print(f"Error analyzing overtaking for {driver}: {e}")
                continue
                
        return overtaking_data
    
    def analyze_defensive_driving(self, drivers):
        """Analyze defensive driving capabilities"""
        defensive_data = []
        
        for driver in drivers:
            try:
                driver_laps = self.session.laps.pick_drivers([driver])
                if driver_laps.empty:
                    continue
                
                # Analyze lap time consistency under pressure
                lap_times = []
                for _, lap in driver_laps.iterrows():
                    if pd.notna(lap['LapTime']):
                        lap_times.append(lap['LapTime'].total_seconds())
                
                if len(lap_times) < 5:
                    continue
                
                # Calculate consistency metrics
                lap_time_std = np.std(lap_times)
                lap_time_mean = np.mean(lap_times)
                consistency_coeff = (lap_time_std / lap_time_mean) * 100
                
                # Pressure handling (consistency in middle stints)
                middle_third_start = len(lap_times) // 3
                middle_third_end = 2 * len(lap_times) // 3
                middle_stint_consistency = np.std(lap_times[middle_third_start:middle_third_end])
                
                # Defensive score
                defensive_score = max(0, 100 - consistency_coeff * 10)
                
                defensive_data.append({
                    'driver': driver,
                    'lap_time_consistency': f"{consistency_coeff:.3f}%",
                    'pressure_handling': f"{100 - (middle_stint_consistency * 100):.1f}%",
                    'defensive_score': f"{defensive_score:.1f}",
                    'total_race_laps': len(lap_times)
                })
                
            except Exception as e:
                print(f"Error analyzing defensive driving for {driver}: {e}")
                continue
                
        return defensive_data
    
    def create_racecraft_comparison(self, drivers):
        """Create comprehensive racecraft comparison chart"""
        try:
            overtaking_data = self.analyze_overtaking_patterns(drivers)
            defensive_data = self.analyze_defensive_driving(drivers)
            
            if not overtaking_data or not defensive_data:
                return None
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Overtaking Performance', 'Racing Aggression', 
                               'Defensive Capability', 'Overall Racecraft'),
                specs=[[{"type": "bar"}, {"type": "bar"}],
                       [{"type": "bar"}, {"type": "radar"}]]
            )
            
            drivers_list = [d['driver'] for d in overtaking_data]
            colors = [TEAM_COLORS.get(DRIVER_TEAMS.get(d, 'Unknown'), '#808080') for d in drivers_list]
            
            # Overtaking performance
            overtakes = [d['overtakes_made'] for d in overtaking_data]
            fig.add_trace(
                go.Bar(x=drivers_list, y=overtakes, name='Overtakes', 
                       marker_color=colors, showlegend=False),
                row=1, col=1
            )
            
            # Racing aggression
            aggression = [float(d['racing_aggression']) for d in overtaking_data]
            fig.add_trace(
                go.Bar(x=drivers_list, y=aggression, name='Aggression', 
                       marker_color=colors, showlegend=False),
                row=1, col=2
            )
            
            # Defensive capability
            defensive_scores = [float(d['defensive_score']) for d in defensive_data]
            fig.add_trace(
                go.Bar(x=drivers_list, y=defensive_scores, name='Defense', 
                       marker_color=colors, showlegend=False),
                row=2, col=1
            )
            
            # Radar chart for overall racecraft
            if len(drivers_list) <= 4:  # Only show radar for manageable number of drivers
                for i, driver in enumerate(drivers_list):
                    overtaking_score = overtaking_data[i]['racecraft_score']
                    defensive_score = float(defensive_data[i]['defensive_score'])
                    
                    fig.add_trace(
                        go.Scatterpolar(
                            r=[overtaking_score, defensive_score, 
                               float(overtaking_data[i]['racing_aggression']), overtaking_score],
                            theta=['Overtaking', 'Defense', 'Aggression', 'Overtaking'],
                            fill='toself',
                            name=driver,
                            line_color=colors[i]
                        ),
                        row=2, col=2
                    )
            
            fig.update_layout(
                title='🏁 Racecraft Analysis',
                height=800,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating racecraft comparison: {e}")
            return None

def analyze_driving_style(session, driver):
    """Analyze individual driving style characteristics"""
    try:
        driver_laps = session.laps.pick_drivers([driver])
        if driver_laps.empty:
            return None
        
        fastest_lap = driver_laps.pick_fastest()
        telemetry = fastest_lap.get_telemetry().add_distance()
        
        if 'Throttle' not in telemetry.columns or 'Brake' not in telemetry.columns:
            return None
        
        # Analyze driving characteristics
        throttle_aggression = (telemetry['Throttle'] > 90).sum() / len(telemetry) * 100
        brake_aggression = (telemetry['Brake'] > 80).sum() / len(telemetry) * 100
        
        # Smoothness analysis
        throttle_changes = telemetry['Throttle'].diff().abs().mean()
        brake_changes = telemetry['Brake'].diff().abs().mean()
        
        style_metrics = {
            'throttle_aggression': f"{throttle_aggression:.1f}%",
            'brake_aggression': f"{brake_aggression:.1f}%",
            'throttle_smoothness': f"{100 - throttle_changes:.1f}%",
            'brake_smoothness': f"{100 - brake_changes:.1f}%",
            'style_score': (throttle_aggression + brake_aggression) / 2
        }
        
        return style_metrics
        
    except Exception as e:
        print(f"Error analyzing driving style: {e}")
        return None