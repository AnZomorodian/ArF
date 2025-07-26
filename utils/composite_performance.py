"""
Composite Performance Index Module for F1 Data Platform
Calculates comprehensive performance metrics combining multiple factors
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from utils.constants import TEAM_COLORS


class CompositePerformanceAnalyzer:
    def __init__(self, session):
        self.session = session
        
    def calculate_composite_performance(self, drivers):
        """Calculate composite performance index for selected drivers"""
        results = []
        
        for driver in drivers:
            try:
                driver_laps = self.session.laps.pick_drivers(driver)
                if driver_laps.empty:
                    continue
                    
                fastest_lap = driver_laps.pick_fastest()
                if fastest_lap.empty or pd.isna(fastest_lap['DriverNumber']):
                    continue
                
                telemetry = fastest_lap.get_car_data().add_distance()
                if telemetry.empty:
                    continue
                
                # Speed, acceleration and brake data
                brake_data = telemetry['Brake']
                speed_data = telemetry['Speed']
                
                # Calculate acceleration (change in speed over distance)
                speed_diff = speed_data.diff()
                distance_diff = telemetry['Distance'].diff()
                acceleration_data = speed_diff / distance_diff
                acceleration_data = acceleration_data.replace([np.inf, -np.inf], 0).fillna(0)
                
                # Calculate time spent braking
                time_diff = telemetry['Time'].diff().dt.total_seconds()
                braking_duration = (brake_data * time_diff).sum()
                
                # Total lap time in seconds
                lap_time_seconds = fastest_lap['LapTime'].total_seconds()
                
                # Performance factors
                brake_efficiency = (braking_duration / lap_time_seconds) * 100
                speed_factor = speed_data.mean()
                acceleration_factor = acceleration_data[acceleration_data > 0].mean()
                
                # Handle NaN acceleration factor
                if pd.isna(acceleration_factor):
                    acceleration_factor = 0.1
                
                # Handling time (time spent at low speeds, indicating cornering)
                handling_threshold = speed_data.mean() * 0.7
                low_speed_mask = speed_data < handling_threshold
                handling_time = (low_speed_mask * time_diff).sum()
                
                # Composite Performance Index with safety checks
                denominator = max(brake_efficiency + handling_time, 1)  # Avoid division by zero
                composite_performance_index = (speed_factor * acceleration_factor) / denominator
                
                # Additional metrics
                top_speed = speed_data.max()
                speed_consistency = 1 - (speed_data.std() / speed_data.mean())
                throttle_efficiency = telemetry['Throttle'].mean()
                
                # Get driver info
                driver_info = self.session.get_driver(driver)
                driver_name = driver_info['Abbreviation']
                team_name = driver_info['TeamName']
                
                results.append({
                    'Driver': driver_name,
                    'Team': team_name,
                    'Composite_Performance_Index': composite_performance_index,
                    'Speed_Factor': speed_factor,
                    'Acceleration_Factor': acceleration_factor,
                    'Brake_Efficiency': brake_efficiency,
                    'Handling_Time': handling_time,
                    'Top_Speed': top_speed,
                    'Speed_Consistency': speed_consistency,
                    'Throttle_Efficiency': throttle_efficiency,
                    'Lap_Time': lap_time_seconds
                })
                
            except Exception as e:
                print(f"Error calculating composite performance for driver {driver}: {e}")
                continue
        
        return pd.DataFrame(results)
    
    def create_composite_performance_visualization(self, performance_data, session_info):
        """Create comprehensive composite performance visualization"""
        if performance_data.empty:
            return None
            
        # Sort by composite performance index
        perf_data_sorted = performance_data.sort_values('Composite_Performance_Index', ascending=False)
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Composite Performance Index', 'Performance Factors Breakdown', 
                          'Speed vs Acceleration Analysis', 'Efficiency Metrics'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # 1. Composite Performance Index Bar Chart
        colors = [TEAM_COLORS.get(team, '#808080') for team in perf_data_sorted['Team']]
        
        fig.add_trace(
            go.Bar(
                x=perf_data_sorted['Driver'],
                y=perf_data_sorted['Composite_Performance_Index'],
                name='Composite Performance Index',
                marker_color=colors,
                text=[f"{cpi:.2f}" for cpi in perf_data_sorted['Composite_Performance_Index']],
                textposition='outside'
            ),
            row=1, col=1
        )
        
        # Add average line
        mean_performance = perf_data_sorted['Composite_Performance_Index'].mean()
        fig.add_hline(
            y=mean_performance,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Average: {mean_performance:.2f}",
            row=1, col=1
        )
        
        # 2. Performance Factors Breakdown (Stacked Bar)
        fig.add_trace(
            go.Bar(
                x=perf_data_sorted['Driver'],
                y=perf_data_sorted['Speed_Factor'],
                name='Speed Factor',
                marker_color='#FF6B6B'
            ),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Bar(
                x=perf_data_sorted['Driver'],
                y=perf_data_sorted['Acceleration_Factor'] * 100,  # Scale for visibility
                name='Acceleration Factor (x100)',
                marker_color='#4ECDC4'
            ),
            row=1, col=2
        )
        
        # 3. Speed vs Acceleration Scatter
        fig.add_trace(
            go.Scatter(
                x=perf_data_sorted['Speed_Factor'],
                y=perf_data_sorted['Acceleration_Factor'],
                mode='markers+text',
                name='Speed vs Acceleration',
                marker=dict(
                    size=15,
                    color=[TEAM_COLORS.get(team, '#808080') for team in perf_data_sorted['Team']],
                    line=dict(width=2, color='white')
                ),
                text=perf_data_sorted['Driver'],
                textposition="top center",
                textfont=dict(color='white', size=10)
            ),
            row=2, col=1
        )
        
        # 4. Efficiency Metrics
        fig.add_trace(
            go.Scatter(
                x=perf_data_sorted['Driver'],
                y=perf_data_sorted['Speed_Consistency'] * 100,
                mode='lines+markers',
                name='Speed Consistency (%)',
                line=dict(color='#FFD93D', width=3),
                marker=dict(size=8)
            ),
            row=2, col=2
        )
        
        fig.add_trace(
            go.Scatter(
                x=perf_data_sorted['Driver'],
                y=perf_data_sorted['Throttle_Efficiency'],
                mode='lines+markers',
                name='Throttle Efficiency (%)',
                line=dict(color='#FF8A80', width=3),
                marker=dict(size=8)
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            title=f'Composite Performance Analysis - {session_info}',
            title_font=dict(size=20, color='white'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            height=800
        )
        
        # Update axes
        fig.update_xaxes(
            gridcolor='rgba(128,128,128,0.3)',
            title_font=dict(color='white'),
            tickfont=dict(color='white')
        )
        fig.update_yaxes(
            gridcolor='rgba(128,128,128,0.3)',
            title_font=dict(color='white'),
            tickfont=dict(color='white')
        )
        
        # Update subplot titles
        for annotation in fig['layout']['annotations']:
            annotation['font'] = dict(color='white', size=14)
        
        return fig
    
    def create_performance_radar(self, performance_data):
        """Create radar chart for performance comparison"""
        if performance_data.empty or len(performance_data) == 0:
            return None
        
        # Normalize metrics for radar chart
        metrics = ['Speed_Factor', 'Acceleration_Factor', 'Speed_Consistency', 
                  'Throttle_Efficiency', 'Composite_Performance_Index']
        
        normalized_data = performance_data.copy()
        for metric in metrics:
            if metric in normalized_data.columns:
                min_val = normalized_data[metric].min()
                max_val = normalized_data[metric].max()
                if max_val != min_val:
                    normalized_data[metric] = (normalized_data[metric] - min_val) / (max_val - min_val)
                else:
                    normalized_data[metric] = 0.5
        
        fig = go.Figure()
        
        # Add trace for each driver (limit to top 5 for readability)
        top_drivers = performance_data.nlargest(5, 'Composite_Performance_Index')
        
        for _, driver_data in top_drivers.iterrows():
            values = []
            for metric in metrics:
                norm_val = normalized_data[normalized_data['Driver'] == driver_data['Driver']][metric].iloc[0]
                values.append(norm_val)
            
            values.append(values[0])  # Close the radar chart
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=metrics + [metrics[0]],
                fill='toself',
                name=driver_data['Driver'],
                line_color=TEAM_COLORS.get(driver_data['Team'], '#808080')
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    gridcolor='rgba(128,128,128,0.3)',
                    tickfont=dict(color='white')
                ),
                angularaxis=dict(
                    gridcolor='rgba(128,128,128,0.3)',
                    tickfont=dict(color='white')
                )
            ),
            title='Performance Radar Comparison (Top 5 Drivers)',
            title_font=dict(size=18, color='white'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=500
        )
        
        return fig