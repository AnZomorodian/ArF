"""
Advanced Pit Strategy Analysis for F1 Data
Analyzes pit stop timing, strategy effectiveness, and competitive impact
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .constants import TEAM_COLORS, DRIVER_TEAMS, TIRE_COLORS

class PitStrategyAnalyzer:
    """Advanced pit stop strategy analysis"""
    
    def __init__(self, session):
        self.session = session
        
    def analyze_pit_windows(self, drivers):
        """Analyze optimal pit stop windows and strategy effectiveness"""
        pit_data = []
        
        for driver in drivers:
            try:
                driver_laps = self.session.laps.pick_drivers([driver])
                if driver_laps.empty:
                    continue
                
                # Detect pit stops (compound changes)
                compounds = driver_laps['Compound'].dropna()
                pit_stops = []
                current_compound = None
                
                for idx, (_, lap) in enumerate(driver_laps.iterrows()):
                    if pd.notna(lap['Compound']) and lap['Compound'] != current_compound:
                        if current_compound is not None:
                            pit_stops.append({
                                'lap': lap['LapNumber'],
                                'from_compound': current_compound,
                                'to_compound': lap['Compound']
                            })
                        current_compound = lap['Compound']
                
                # Strategy analysis
                total_pit_stops = len(pit_stops)
                strategy_type = self._classify_strategy(total_pit_stops)
                
                # Calculate stint lengths
                stint_lengths = []
                if len(compounds) > 0:
                    current_stint = 1
                    for i in range(1, len(driver_laps)):
                        if (driver_laps.iloc[i]['Compound'] != driver_laps.iloc[i-1]['Compound'] and 
                            pd.notna(driver_laps.iloc[i]['Compound'])):
                            stint_lengths.append(current_stint)
                            current_stint = 1
                        else:
                            current_stint += 1
                    stint_lengths.append(current_stint)
                
                avg_stint_length = np.mean(stint_lengths) if stint_lengths else 0
                
                # Strategy effectiveness score
                effectiveness_score = self._calculate_strategy_effectiveness(
                    driver_laps, pit_stops, stint_lengths
                )
                
                pit_data.append({
                    'driver': driver,
                    'total_pit_stops': total_pit_stops,
                    'strategy_type': strategy_type,
                    'avg_stint_length': f"{avg_stint_length:.1f}",
                    'pit_windows': pit_stops,
                    'effectiveness_score': f"{effectiveness_score:.1f}%",
                    'compounds_used': list(compounds.unique())
                })
                
            except Exception as e:
                print(f"Error analyzing pit strategy for {driver}: {e}")
                continue
                
        return pit_data
    
    def _classify_strategy(self, pit_stops):
        """Classify pit stop strategy"""
        if pit_stops == 0:
            return "No-stop"
        elif pit_stops == 1:
            return "One-stop"
        elif pit_stops == 2:
            return "Two-stop"
        elif pit_stops >= 3:
            return "Multi-stop"
        else:
            return "Unknown"
    
    def _calculate_strategy_effectiveness(self, laps, pit_stops, stint_lengths):
        """Calculate strategy effectiveness based on lap times and positions"""
        try:
            if laps.empty:
                return 50.0
            
            # Position improvement factor
            start_pos = laps.iloc[0]['Position'] if pd.notna(laps.iloc[0]['Position']) else 10
            end_pos = laps.iloc[-1]['Position'] if pd.notna(laps.iloc[-1]['Position']) else 10
            position_factor = max(0, start_pos - end_pos) * 10
            
            # Stint length consistency factor
            stint_consistency = 100 - (np.std(stint_lengths) * 5) if stint_lengths else 50
            
            # Overall effectiveness
            effectiveness = min(100, (position_factor + stint_consistency) / 2 + 25)
            return effectiveness
            
        except Exception:
            return 50.0
    
    def create_pit_strategy_visualization(self, drivers):
        """Create comprehensive pit strategy visualization"""
        try:
            pit_data = self.analyze_pit_windows(drivers)
            if not pit_data:
                return None
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Strategy Distribution', 'Pit Stop Timing', 
                               'Strategy Effectiveness', 'Stint Lengths'),
                specs=[[{"type": "pie"}, {"type": "scatter"}],
                       [{"type": "bar"}, {"type": "bar"}]]
            )
            
            # Strategy distribution pie chart
            strategies = [d['strategy_type'] for d in pit_data]
            strategy_counts = pd.Series(strategies).value_counts()
            
            fig.add_trace(
                go.Pie(
                    labels=strategy_counts.index,
                    values=strategy_counts.values,
                    name="Strategy Distribution",
                    marker_colors=['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4']
                ),
                row=1, col=1
            )
            
            # Pit stop timing
            for i, data in enumerate(pit_data):
                pit_laps = [stop['lap'] for stop in data['pit_windows']]
                if pit_laps:
                    fig.add_trace(
                        go.Scatter(
                            x=pit_laps,
                            y=[i] * len(pit_laps),
                            mode='markers',
                            name=data['driver'],
                            marker=dict(
                                size=15,
                                color=TEAM_COLORS.get(DRIVER_TEAMS.get(data['driver'], 'Unknown'), '#808080')
                            ),
                            showlegend=False
                        ),
                        row=1, col=2
                    )
            
            # Strategy effectiveness
            drivers_list = [d['driver'] for d in pit_data]
            colors = [TEAM_COLORS.get(DRIVER_TEAMS.get(d, 'Unknown'), '#808080') for d in drivers_list]
            effectiveness = [float(d['effectiveness_score'].replace('%', '')) for d in pit_data]
            
            fig.add_trace(
                go.Bar(
                    x=drivers_list,
                    y=effectiveness,
                    name='Effectiveness',
                    marker_color=colors,
                    showlegend=False
                ),
                row=2, col=1
            )
            
            # Average stint lengths
            stint_lengths = [float(d['avg_stint_length']) for d in pit_data]
            fig.add_trace(
                go.Bar(
                    x=drivers_list,
                    y=stint_lengths,
                    name='Avg Stint Length',
                    marker_color=colors,
                    showlegend=False
                ),
                row=2, col=2
            )
            
            fig.update_layout(
                title='🔧 Advanced Pit Strategy Analysis',
                height=800,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating pit strategy visualization: {e}")
            return None

def analyze_undercut_overcut_opportunities(session, reference_driver):
    """Analyze undercut and overcut opportunities relative to a reference driver"""
    try:
        reference_laps = session.laps.pick_drivers([reference_driver])
        if reference_laps.empty:
            return None
        
        # Get all drivers for comparison
        all_drivers = session.laps['Driver'].unique()
        opportunity_data = []
        
        for driver in all_drivers:
            if driver == reference_driver:
                continue
                
            driver_laps = session.laps.pick_drivers([driver])
            if driver_laps.empty:
                continue
            
            # Find potential undercut/overcut opportunities
            opportunities = 0
            for _, ref_lap in reference_laps.iterrows():
                # Look for laps where strategies diverged
                corresponding_lap = driver_laps[driver_laps['LapNumber'] == ref_lap['LapNumber']]
                if not corresponding_lap.empty and pd.notna(ref_lap['Compound']) and pd.notna(corresponding_lap.iloc[0]['Compound']):
                    if ref_lap['Compound'] != corresponding_lap.iloc[0]['Compound']:
                        opportunities += 1
            
            opportunity_data.append({
                'driver': driver,
                'opportunities': opportunities,
                'strategic_variance': opportunities / len(driver_laps) * 100 if len(driver_laps) > 0 else 0
            })
        
        return opportunity_data
        
    except Exception as e:
        print(f"Error analyzing undercut/overcut opportunities: {e}")
        return None