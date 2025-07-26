"""
Race Strategy Analysis Module
Provides comprehensive strategy analysis including pit stops, tire strategy, and race pace
"""

import fastf1
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .constants import TIRE_COLORS, TEAM_COLORS

class RaceStrategyAnalyzer:
    """Advanced race strategy analysis"""
    
    def __init__(self, session):
        self.session = session
        self.laps = session.laps
        self.results = session.results
        
    def analyze_pit_stop_strategies(self):
        """Analyze pit stop strategies for all drivers"""
        pit_strategies = {}
        
        for driver in self.laps['Driver'].unique():
            if pd.isna(driver):
                continue
                
            driver_laps = self.laps.pick_driverss(driver)
            pit_stops = []
            
            # Find pit stops by looking for compound changes
            prev_compound = None
            for idx, lap in driver_laps.iterrows():
                current_compound = lap['Compound']
                
                if prev_compound is not None and current_compound != prev_compound:
                    pit_stops.append({
                        'lap_number': lap['LapNumber'],
                        'old_compound': prev_compound,
                        'new_compound': current_compound,
                        'pit_time': lap['PitInTime'] if pd.notna(lap['PitInTime']) else None,
                        'pit_out_time': lap['PitOutTime'] if pd.notna(lap['PitOutTime']) else None
                    })
                
                prev_compound = current_compound
            
            # Calculate stint lengths
            stints = []
            stint_start = 1
            
            for pit_stop in pit_stops:
                stint_length = pit_stop['lap_number'] - stint_start
                stints.append({
                    'stint_number': len(stints) + 1,
                    'start_lap': stint_start,
                    'end_lap': pit_stop['lap_number'] - 1,
                    'length': stint_length,
                    'compound': pit_stop['old_compound']
                })
                stint_start = pit_stop['lap_number']
            
            # Add final stint
            final_lap = driver_laps['LapNumber'].max()
            if stint_start <= final_lap:
                stints.append({
                    'stint_number': len(stints) + 1,
                    'start_lap': stint_start,
                    'end_lap': final_lap,
                    'length': final_lap - stint_start + 1,
                    'compound': driver_laps.iloc[-1]['Compound']
                })
            
            pit_strategies[driver] = {
                'pit_stops': pit_stops,
                'stints': stints,
                'total_pit_stops': len(pit_stops),
                'strategy_type': self._classify_strategy(stints)
            }
        
        return pit_strategies
    
    def _classify_strategy(self, stints):
        """Classify pit strategy type"""
        num_stints = len(stints)
        
        if num_stints == 1:
            return "No-stop"
        elif num_stints == 2:
            return "One-stop"
        elif num_stints == 3:
            return "Two-stop"
        else:
            return f"{num_stints-1}-stop"
    
    def analyze_undercut_overcut_effectiveness(self):
        """Analyze undercut and overcut strategies"""
        strategies = {}
        pit_strategies = self.analyze_pit_stop_strategies()
        
        for driver, strategy_data in pit_strategies.items():
            if not strategy_data['pit_stops']:
                continue
                
            driver_analysis = []
            
            for pit_stop in strategy_data['pit_stops']:
                pit_lap = pit_stop['lap_number']
                
                # Analyze position changes around pit stop
                positions_before = []
                positions_after = []
                
                # Get positions 3 laps before and after pit stop
                for lap_offset in range(-3, 4):
                    target_lap = pit_lap + lap_offset
                    
                    lap_data = self.laps[
                        (self.laps['Driver'] == driver) & 
                        (self.laps['LapNumber'] == target_lap)
                    ]
                    
                    if not lap_data.empty:
                        position = lap_data.iloc[0]['Position']
                        if lap_offset < 0:
                            positions_before.append(position)
                        elif lap_offset > 0:
                            positions_after.append(position)
                
                # Calculate effectiveness
                if positions_before and positions_after:
                    avg_pos_before = np.mean(positions_before)
                    avg_pos_after = np.mean(positions_after)
                    position_change = avg_pos_before - avg_pos_after
                    
                    driver_analysis.append({
                        'pit_lap': pit_lap,
                        'position_change': position_change,
                        'effectiveness': 'positive' if position_change > 0 else 'negative',
                        'magnitude': abs(position_change)
                    })
            
            strategies[driver] = driver_analysis
        
        return strategies
    
    def create_strategy_timeline_plot(self):
        """Create comprehensive strategy timeline visualization"""
        pit_strategies = self.analyze_pit_stop_strategies()
        
        fig = go.Figure()
        
        y_position = 0
        driver_positions = {}
        
        for driver, strategy_data in pit_strategies.items():
            driver_positions[driver] = y_position
            
            # Plot stints as horizontal bars
            for stint in strategy_data['stints']:
                compound = stint['compound']
                color = TIRE_COLORS.get(compound, '#808080')
                
                fig.add_trace(go.Scatter(
                    x=[stint['start_lap'], stint['end_lap']],
                    y=[y_position, y_position],
                    mode='lines',
                    line=dict(color=color, width=8),
                    name=f"{driver} - {compound}",
                    showlegend=False,
                    hovertemplate=f"Driver: {driver}<br>Compound: {compound}<br>Stint: {stint['start_lap']}-{stint['end_lap']}<br>Length: {stint['length']} laps<extra></extra>"
                ))
            
            # Mark pit stops
            for pit_stop in strategy_data['pit_stops']:
                fig.add_trace(go.Scatter(
                    x=[pit_stop['lap_number']],
                    y=[y_position],
                    mode='markers',
                    marker=dict(
                        color='white',
                        size=10,
                        symbol='diamond',
                        line=dict(color='black', width=2)
                    ),
                    name=f"{driver} Pit Stop",
                    showlegend=False,
                    hovertemplate=f"Pit Stop<br>Driver: {driver}<br>Lap: {pit_stop['lap_number']}<br>Change: {pit_stop['old_compound']} → {pit_stop['new_compound']}<extra></extra>"
                ))
            
            y_position += 1
        
        # Add driver labels
        fig.update_layout(
            title='Race Strategy Timeline - Tire Compounds and Pit Stops',
            xaxis_title='Lap Number',
            yaxis=dict(
                tickvals=list(driver_positions.values()),
                ticktext=list(driver_positions.keys()),
                title='Drivers'
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=max(600, len(pit_strategies) * 40),
            showlegend=False,
            hovermode='closest'
        )
        
        fig.update_xaxes(gridcolor='rgba(255,255,255,0.1)')
        fig.update_yaxes(gridcolor='rgba(255,255,255,0.1)')
        
        return fig
    
    def analyze_fuel_effect_on_pace(self):
        """Analyze how fuel load affects lap times throughout the race"""
        fuel_analysis = {}
        
        for driver in self.laps['Driver'].unique():
            if pd.isna(driver):
                continue
                
            driver_laps = self.laps.pick_driverss(driver)
            valid_laps = driver_laps[driver_laps['LapTime'].notna()]
            
            if len(valid_laps) < 5:
                continue
            
            lap_numbers = valid_laps['LapNumber'].values
            lap_times = valid_laps['LapTime'].dt.total_seconds().values
            
            # Calculate theoretical fuel effect (assuming linear fuel consumption)
            race_distance = lap_numbers.max()
            
            # Estimate fuel load effect (rough approximation)
            fuel_loads = []
            for lap_num in lap_numbers:
                remaining_laps = race_distance - lap_num
                estimated_fuel_load = remaining_laps / race_distance
                fuel_loads.append(estimated_fuel_load)
            
            # Calculate pace improvement over the race
            if len(lap_times) > 1:
                pace_trend = np.polyfit(lap_numbers, lap_times, 1)[0]
                
                fuel_analysis[driver] = {
                    'pace_trend': pace_trend,  # seconds per lap improvement
                    'total_improvement': pace_trend * (lap_numbers.max() - lap_numbers.min()),
                    'average_pace': np.mean(lap_times),
                    'consistency': np.std(lap_times),
                    'laps_analyzed': len(valid_laps)
                }
        
        return fuel_analysis
    
    def create_pace_evolution_plot(self):
        """Create pace evolution plot showing fuel effect"""
        fuel_analysis = self.analyze_fuel_effect_on_pace()
        
        fig = go.Figure()
        
        colors = ['#DC0000', '#00D2BE', '#FF8700', '#1E41FF', '#0090FF', '#006F62', '#808080', '#1660AD', '#87CEEB', '#00E701']
        color_idx = 0
        
        for driver, analysis in fuel_analysis.items():
            driver_laps = self.laps.pick_driverss(driver)
            valid_laps = driver_laps[driver_laps['LapTime'].notna()]
            
            if len(valid_laps) < 5:
                continue
            
            lap_numbers = valid_laps['LapNumber'].values
            lap_times = valid_laps['LapTime'].dt.total_seconds().values
            
            # Create trend line
            trend_line = np.poly1d(np.polyfit(lap_numbers, lap_times, 1))
            trend_y = trend_line(lap_numbers)
            
            fig.add_trace(go.Scatter(
                x=lap_numbers,
                y=lap_times,
                mode='markers',
                marker=dict(color=colors[color_idx % len(colors)], size=6, opacity=0.6),
                name=f'{driver} (actual)',
                showlegend=True
            ))
            
            fig.add_trace(go.Scatter(
                x=lap_numbers,
                y=trend_y,
                mode='lines',
                line=dict(color=colors[color_idx % len(colors)], width=2, dash='dash'),
                name=f'{driver} (trend)',
                showlegend=False
            ))
            
            color_idx += 1
        
        fig.update_layout(
            title='Pace Evolution Throughout the Race (Fuel Effect Analysis)',
            xaxis_title='Lap Number',
            yaxis_title='Lap Time (seconds)',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=600,
            hovermode='closest'
        )
        
        fig.update_xaxes(gridcolor='rgba(255,255,255,0.1)')
        fig.update_yaxes(gridcolor='rgba(255,255,255,0.1)')
        
        return fig