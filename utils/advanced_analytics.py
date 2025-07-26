"""
Advanced F1 Analytics Module
Provides comprehensive driver performance metrics, weather analysis, and race statistics
"""

import fastf1
import pandas as pd
import numpy as np
from scipy.stats import zscore
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class AdvancedF1Analytics:
    """Advanced analytics for F1 data with comprehensive performance metrics"""
    
    def __init__(self, session):
        self.session = session
        self.laps = session.laps
        self.results = session.results
        
    def calculate_driver_consistency(self, driver_code):
        """Calculate driver consistency metrics across all laps"""
        driver_laps = self.laps.pick_drivers(driver_code)
        valid_laps = driver_laps[driver_laps['LapTime'].notna()]
        
        if len(valid_laps) < 3:
            return None
            
        lap_times = valid_laps['LapTime'].dt.total_seconds()
        
        return {
            'mean_lap_time': lap_times.mean(),
            'std_deviation': lap_times.std(),
            'coefficient_variation': lap_times.std() / lap_times.mean(),
            'fastest_lap': lap_times.min(),
            'slowest_lap': lap_times.max(),
            'consistency_score': 1 / (1 + lap_times.std()),
            'total_laps': len(valid_laps)
        }
    
    def analyze_tire_degradation(self, driver_code):
        """Analyze tire degradation patterns for a driver"""
        driver_laps = self.laps.pick_drivers(driver_code)
        
        degradation_data = []
        
        for compound in driver_laps['Compound'].unique():
            if pd.isna(compound):
                continue
                
            compound_laps = driver_laps[driver_laps['Compound'] == compound]
            if len(compound_laps) < 2:
                continue
                
            # Calculate degradation rate
            lap_times = compound_laps['LapTime'].dt.total_seconds()
            lap_numbers = range(len(lap_times))
            
            if len(lap_times) > 1:
                degradation_rate = np.polyfit(lap_numbers, lap_times, 1)[0]
                
                degradation_data.append({
                    'compound': compound,
                    'stint_length': len(compound_laps),
                    'degradation_rate': degradation_rate,
                    'initial_pace': lap_times.iloc[0] if len(lap_times) > 0 else None,
                    'final_pace': lap_times.iloc[-1] if len(lap_times) > 0 else None,
                    'total_degradation': lap_times.iloc[-1] - lap_times.iloc[0] if len(lap_times) > 1 else 0
                })
        
        return degradation_data
    
    def calculate_sector_dominance(self):
        """Calculate which drivers dominate each sector"""
        sector_data = {
            'Sector1': {},
            'Sector2': {},
            'Sector3': {}
        }
        
        for driver in self.laps['Driver'].unique():
            if pd.isna(driver):
                continue
                
            driver_laps = self.laps.pick_driver(driver)
            
            for sector in ['Sector1Time', 'Sector2Time', 'Sector3Time']:
                valid_times = driver_laps[sector].dropna()
                if len(valid_times) > 0:
                    sector_name = sector.replace('Time', '')
                    sector_data[sector_name][driver] = {
                        'best_time': valid_times.min().total_seconds(),
                        'average_time': valid_times.mean().total_seconds(),
                        'consistency': valid_times.std().total_seconds()
                    }
        
        return sector_data
    
    def analyze_overtaking_patterns(self):
        """Analyze overtaking and position changes during the race"""
        if not hasattr(self.session, 'laps') or self.session.laps.empty:
            return {}
            
        overtaking_data = {}
        
        for lap_num in range(1, self.laps['LapNumber'].max() + 1):
            lap_data = self.laps[self.laps['LapNumber'] == lap_num]
            
            if len(lap_data) > 1:
                # Calculate position changes
                if lap_num > 1:
                    prev_lap = self.laps[self.laps['LapNumber'] == lap_num - 1]
                    
                    for driver in lap_data['Driver'].unique():
                        if pd.isna(driver):
                            continue
                            
                        current_pos = lap_data[lap_data['Driver'] == driver]['Position'].iloc[0] if len(lap_data[lap_data['Driver'] == driver]) > 0 else None
                        prev_pos = prev_lap[prev_lap['Driver'] == driver]['Position'].iloc[0] if len(prev_lap[prev_lap['Driver'] == driver]) > 0 else None
                        
                        if current_pos is not None and prev_pos is not None:
                            position_change = prev_pos - current_pos
                            
                            if driver not in overtaking_data:
                                overtaking_data[driver] = {
                                    'positions_gained': 0,
                                    'positions_lost': 0,
                                    'overtakes': [],
                                    'net_position_change': 0
                                }
                            
                            if position_change > 0:
                                overtaking_data[driver]['positions_gained'] += position_change
                                overtaking_data[driver]['overtakes'].append({
                                    'lap': lap_num,
                                    'positions': position_change,
                                    'type': 'gained'
                                })
                            elif position_change < 0:
                                overtaking_data[driver]['positions_lost'] += abs(position_change)
                                overtaking_data[driver]['overtakes'].append({
                                    'lap': lap_num,
                                    'positions': abs(position_change),
                                    'type': 'lost'
                                })
        
        # Calculate net position changes
        for driver in overtaking_data:
            overtaking_data[driver]['net_position_change'] = (
                overtaking_data[driver]['positions_gained'] - 
                overtaking_data[driver]['positions_lost']
            )
        
        return overtaking_data
    
    def create_advanced_telemetry_comparison(self, driver1, driver2, lap_number=None):
        """Create advanced telemetry comparison with multiple metrics"""
        
        if lap_number is None:
            # Use fastest laps
            lap1 = self.laps.pick_driver(driver1).pick_fastest()
            lap2 = self.laps.pick_driver(driver2).pick_fastest()
        else:
            lap1 = self.laps.pick_driver(driver1).pick_lap(lap_number)
            lap2 = self.laps.pick_driver(driver2).pick_lap(lap_number)
        
        try:
            telemetry1 = lap1.get_telemetry()
            telemetry2 = lap2.get_telemetry()
        except:
            return None
        
        # Create comprehensive telemetry comparison
        fig = make_subplots(
            rows=6, cols=1,
            subplot_titles=[
                'Speed Comparison (km/h)',
                'Throttle Position (%)',
                'Brake Pressure',
                'RPM',
                'Gear',
                'DRS Status'
            ],
            vertical_spacing=0.08
        )
        
        # Speed comparison
        fig.add_trace(go.Scatter(
            x=telemetry1['Distance'],
            y=telemetry1['Speed'],
            name=f'{driver1} Speed',
            line=dict(color='#DC0000', width=2)
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=telemetry2['Distance'],
            y=telemetry2['Speed'],
            name=f'{driver2} Speed',
            line=dict(color='#00D2BE', width=2)
        ), row=1, col=1)
        
        # Throttle comparison
        fig.add_trace(go.Scatter(
            x=telemetry1['Distance'],
            y=telemetry1['Throttle'],
            name=f'{driver1} Throttle',
            line=dict(color='#DC0000', width=2),
            showlegend=False
        ), row=2, col=1)
        
        fig.add_trace(go.Scatter(
            x=telemetry2['Distance'],
            y=telemetry2['Throttle'],
            name=f'{driver2} Throttle',
            line=dict(color='#00D2BE', width=2),
            showlegend=False
        ), row=2, col=1)
        
        # Brake comparison
        fig.add_trace(go.Scatter(
            x=telemetry1['Distance'],
            y=telemetry1['Brake'],
            name=f'{driver1} Brake',
            line=dict(color='#DC0000', width=2),
            showlegend=False
        ), row=3, col=1)
        
        fig.add_trace(go.Scatter(
            x=telemetry2['Distance'],
            y=telemetry2['Brake'],
            name=f'{driver2} Brake',
            line=dict(color='#00D2BE', width=2),
            showlegend=False
        ), row=3, col=1)
        
        # RPM comparison
        fig.add_trace(go.Scatter(
            x=telemetry1['Distance'],
            y=telemetry1['RPM'],
            name=f'{driver1} RPM',
            line=dict(color='#DC0000', width=2),
            showlegend=False
        ), row=4, col=1)
        
        fig.add_trace(go.Scatter(
            x=telemetry2['Distance'],
            y=telemetry2['RPM'],
            name=f'{driver2} RPM',
            line=dict(color='#00D2BE', width=2),
            showlegend=False
        ), row=4, col=1)
        
        # Gear comparison
        fig.add_trace(go.Scatter(
            x=telemetry1['Distance'],
            y=telemetry1['nGear'],
            name=f'{driver1} Gear',
            line=dict(color='#DC0000', width=2),
            showlegend=False,
            mode='lines+markers',
            marker=dict(size=3)
        ), row=5, col=1)
        
        fig.add_trace(go.Scatter(
            x=telemetry2['Distance'],
            y=telemetry2['nGear'],
            name=f'{driver2} Gear',
            line=dict(color='#00D2BE', width=2),
            showlegend=False,
            mode='lines+markers',
            marker=dict(size=3)
        ), row=5, col=1)
        
        # DRS comparison
        fig.add_trace(go.Scatter(
            x=telemetry1['Distance'],
            y=telemetry1['DRS'],
            name=f'{driver1} DRS',
            line=dict(color='#DC0000', width=2),
            showlegend=False
        ), row=6, col=1)
        
        fig.add_trace(go.Scatter(
            x=telemetry2['Distance'],
            y=telemetry2['DRS'],
            name=f'{driver2} DRS',
            line=dict(color='#00D2BE', width=2),
            showlegend=False
        ), row=6, col=1)
        
        fig.update_layout(
            height=1200,
            title=f'Advanced Telemetry Comparison: {driver1} vs {driver2}',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=True
        )
        
        # Update x-axis labels
        for i in range(1, 7):
            fig.update_xaxes(
                title_text='Distance (m)' if i == 6 else '',
                gridcolor='rgba(255,255,255,0.1)',
                row=i, col=1
            )
            fig.update_yaxes(
                gridcolor='rgba(255,255,255,0.1)',
                row=i, col=1
            )
        
        return fig