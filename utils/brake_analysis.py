"""
Brake Configurations Analysis Module for F1 Data Platform
Enhanced brake efficiency analysis based on your latest requirements
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
from utils.constants import TEAM_COLORS


class BrakeAnalyzer:
    def __init__(self, session):
        self.session = session
        
    def analyze_brake_efficiency(self, drivers):
        """Calculate enhanced brake efficiency for selected drivers"""
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
                
                # Brake and speed data
                brake_data = telemetry['Brake']  # 1 when braking, 0 when not
                speed_data = telemetry['Speed']
                
                # Enhanced brake calculation based on your requirements
                braking_duration = brake_data.sum() * (telemetry['Distance'].diff().mean() / speed_data.mean())
                
                # Total lap time in seconds
                lap_time_seconds = fastest_lap['LapTime'].total_seconds()
                
                # Brake efficiency: percentage of time spent braking
                brake_efficiency = (braking_duration / lap_time_seconds) * 100
                
                # Additional enhanced metrics
                max_brake_force = brake_data.max() * 100
                avg_brake_force = brake_data.mean() * 100
                brake_zones = len(brake_data[brake_data > 0.1])
                
                # Get driver info
                driver_info = self.session.get_driver(driver)
                driver_name = driver_info['LastName'][:3].upper()
                team_name = driver_info['TeamName']
                
                results.append({
                    'Driver': driver_name,
                    'Team': team_name,
                    'Brake_Efficiency': brake_efficiency,
                    'Max_Brake_Force': max_brake_force,
                    'Avg_Brake_Force': avg_brake_force,
                    'Brake_Zones': brake_zones,
                    'Lap_Time': lap_time_seconds,
                    'Braking_Duration': braking_duration
                })
                
            except Exception as e:
                print(f"Error analyzing brake data for driver {driver}: {e}")
                continue
        
        return pd.DataFrame(results)
    
    def create_brake_efficiency_chart(self, brake_data):
        """Create enhanced brake efficiency visualization"""
        if brake_data.empty:
            return None
        
        # Sort by brake efficiency
        brake_data = brake_data.sort_values('Brake_Efficiency', ascending=False)
        
        # Create bar chart with team colors
        fig = go.Figure()
        
        colors = [TEAM_COLORS.get(team, '#FFFFFF') for team in brake_data['Team']]
        
        fig.add_trace(go.Bar(
            x=brake_data['Driver'],
            y=brake_data['Brake_Efficiency'],
            marker_color=colors,
            text=[f'{val:.2f}%' for val in brake_data['Brake_Efficiency']],
            textposition='outside',
            name='Brake Efficiency'
        ))
        
        # Add mean line
        mean_efficiency = brake_data['Brake_Efficiency'].mean()
        fig.add_hline(y=mean_efficiency, line_dash="dash", line_color="red",
                     annotation_text=f"Mean: {mean_efficiency:.2f}%")
        
        fig.update_layout(
            title=f'Brake Efficiency Comparison - {self.session.event.year} {self.session.event["EventName"]}',
            xaxis_title='Driver',
            yaxis_title='Brake Efficiency (%)',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            title_font=dict(size=20, color='white'),
            showlegend=False
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)')
        
        return fig
    
    def create_brake_efficiency_visualization(self, brake_data, session_info):
        """Create comprehensive brake efficiency visualization"""
        if brake_data.empty:
            return None
            
        # Sort by brake efficiency
        brake_data_sorted = brake_data.sort_values('Brake_Efficiency', ascending=False)
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Brake Efficiency Comparison', 'Brake Force Analysis', 
                          'Braking Duration vs Lap Time', 'Brake Zones Distribution'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": True}, {"secondary_y": False}]]
        )
        
        # 1. Brake Efficiency Bar Chart
        colors = [TEAM_COLORS.get(team, '#808080') for team in brake_data_sorted['Team']]
        
        fig.add_trace(
            go.Bar(
                x=brake_data_sorted['Driver'],
                y=brake_data_sorted['Brake_Efficiency'],
                name='Brake Efficiency (%)',
                marker_color=colors,
                text=[f"{eff:.1f}%" for eff in brake_data_sorted['Brake_Efficiency']],
                textposition='outside'
            ),
            row=1, col=1
        )
        
        # 2. Max vs Avg Brake Force
        fig.add_trace(
            go.Scatter(
                x=brake_data_sorted['Driver'],
                y=brake_data_sorted['Max_Brake_Force'],
                mode='lines+markers',
                name='Max Brake Force (%)',
                line=dict(color='#FF6B6B', width=3),
                marker=dict(size=8)
            ),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Scatter(
                x=brake_data_sorted['Driver'],
                y=brake_data_sorted['Avg_Brake_Force'],
                mode='lines+markers',
                name='Avg Brake Force (%)',
                line=dict(color='#4ECDC4', width=3),
                marker=dict(size=8)
            ),
            row=1, col=2
        )
        
        # 3. Braking Duration vs Lap Time (with secondary y-axis)
        fig.add_trace(
            go.Scatter(
                x=brake_data_sorted['Driver'],
                y=brake_data_sorted['Braking_Duration'],
                mode='lines+markers',
                name='Braking Duration (s)',
                line=dict(color='#FFD93D', width=3),
                marker=dict(size=10)
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=brake_data_sorted['Driver'],
                y=brake_data_sorted['Lap_Time'],
                mode='lines+markers',
                name='Lap Time (s)',
                line=dict(color='#FF8A80', width=3),
                marker=dict(size=10),
                yaxis='y4'
            ),
            row=2, col=1, secondary_y=True
        )
        
        # 4. Brake Zones Distribution
        fig.add_trace(
            go.Bar(
                x=brake_data_sorted['Driver'],
                y=brake_data_sorted['Brake_Zones'],
                name='Brake Zones',
                marker_color='#A8E6CF',
                text=brake_data_sorted['Brake_Zones'],
                textposition='outside'
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            title=f'Brake Analysis - {session_info}',
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
    
    def create_brake_heatmap(self, brake_data):
        """Create brake performance heatmap"""
        if brake_data.empty:
            return None
            
        # Prepare data for heatmap
        metrics = ['Brake_Efficiency', 'Max_Brake_Force', 'Avg_Brake_Force', 'Brake_Zones']
        heatmap_data = brake_data[['Driver'] + metrics].set_index('Driver')
        
        # Normalize data for better visualization
        normalized_data = (heatmap_data - heatmap_data.min()) / (heatmap_data.max() - heatmap_data.min())
        
        fig = go.Figure(data=go.Heatmap(
            z=normalized_data.values.T,
            x=normalized_data.index,
            y=['Brake Efficiency', 'Max Brake Force', 'Avg Brake Force', 'Brake Zones'],
            colorscale='RdYlGn',
            colorbar=dict(title="Normalized Performance", titlefont=dict(color='white')),
            text=[[f"{heatmap_data.iloc[j, i]:.1f}" for j in range(len(heatmap_data))] 
                  for i in range(len(metrics))],
            texttemplate="%{text}",
            textfont={"size": 10, "color": "white"},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title='Brake Performance Heatmap (Normalized)',
            title_font=dict(size=18, color='white'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(title='Driver', titlefont=dict(color='white')),
            yaxis=dict(title='Metrics', titlefont=dict(color='white')),
            height=400
        )
        
        return fig