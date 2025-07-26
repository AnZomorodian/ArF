"""
Tire Performance Analysis Module
Professional F1 tire performance analytics and visualization
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from utils.constants import TEAM_COLORS


class TirePerformanceAnalyzer:
    """Advanced tire performance analysis for F1 data"""
    
    def __init__(self, session):
        self.session = session
        
    def calculate_tire_performance(self):
        """Calculate comprehensive tire performance metrics for all drivers"""
        drivers = self.session.drivers
        results = []

        for driver in drivers:
            driver_laps = self.session.laps.pick_drivers(driver)
            fastest_lap = driver_laps.pick_fastest()
            
            if fastest_lap is None or fastest_lap.empty or pd.isna(fastest_lap['DriverNumber']):
                continue
            
            try:
                telemetry = fastest_lap.get_car_data().add_distance()
            except (KeyError, AttributeError):
                continue

            # Enhanced metrics calculation
            speed_data = telemetry['Speed']
            acceleration_data = speed_data.diff() / telemetry['Distance'].diff()
            braking_data = telemetry['Brake']
            throttle_data = telemetry['Throttle']

            # Advanced Tire Stress Index
            braking_factor = braking_data.mean() / 100.0  # Normalize to 0-1
            acceleration_stress = acceleration_data.abs().mean()
            tire_stress_index = (speed_data.mean() * acceleration_stress) * (1 + braking_factor)

            # Tire Temperature Simulation (based on speed, braking, and throttle)
            thermal_load = (speed_data.mean() * 0.4 + 
                           braking_data.mean() * 0.4 + 
                           throttle_data.mean() * 0.2)
            tire_temperature = 80 + thermal_load * 0.8  # Base temp + thermal load

            # Tire Efficiency (speed per unit stress)
            tire_efficiency = speed_data.mean() / (1 + tire_stress_index) if tire_stress_index > 0 else 0

            # Tire Wear Index (comprehensive wear calculation)
            distance_factor = telemetry['Distance'].max() / 1000  # Convert to km
            tire_wear_index = (tire_stress_index * 0.6 + 
                              braking_factor * 100 * 0.3 + 
                              distance_factor * 0.1)

            # Grip Level Estimation
            max_lateral_g = acceleration_data.abs().quantile(0.95)
            grip_level = min(100, max_lateral_g * 50)  # Scaled grip estimation

            driver_info = self.session.get_driver(driver)
            driver_name = driver_info['LastName'][:3].upper()
            team_name = driver_info.get('TeamName', 'Unknown')
            
            results.append({
                'Driver': driver_name,
                'Team': team_name,
                'Tire_Stress_Index': tire_stress_index,
                'Tire_Temperature': tire_temperature,
                'Tire_Efficiency': tire_efficiency,
                'Tire_Wear_Index': tire_wear_index,
                'Grip_Level': grip_level,
                'Avg_Speed': speed_data.mean(),
                'Peak_Acceleration': acceleration_data.abs().max(),
                'Braking_Intensity': braking_factor * 100
            })

        return pd.DataFrame(results)

    def create_enhanced_tire_performance_visualizations(self, df_tires, session_info):
        """Create comprehensive tire performance visualizations"""
        
        # Create subplot layout
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                'Tire Stress Index by Driver',
                'Tire Temperature Analysis', 
                'Tire Efficiency Comparison',
                'Tire Wear Index'
            ],
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )

        # Get team colors for drivers
        colors = []
        for _, row in df_tires.iterrows():
            team = row['Team']
            color = TEAM_COLORS.get(team, '#888888')
            colors.append(color)

        # 1. Tire Stress Index
        fig.add_trace(
            go.Bar(
                x=df_tires['Driver'],
                y=df_tires['Tire_Stress_Index'],
                name='Stress Index',
                marker_color=colors,
                text=[f"{val:.1f}" for val in df_tires['Tire_Stress_Index']],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Stress Index: %{y:.2f}<extra></extra>'
            ),
            row=1, col=1
        )

        # 2. Tire Temperature
        fig.add_trace(
            go.Scatter(
                x=df_tires['Driver'],
                y=df_tires['Tire_Temperature'],
                mode='markers+lines',
                name='Temperature',
                marker=dict(
                    size=12,
                    color=df_tires['Tire_Temperature'],
                    colorscale='Thermal',
                    showscale=False,
                    line=dict(width=2, color='white')
                ),
                line=dict(color='#FF6B6B', width=3),
                text=[f"{val:.1f}°C" for val in df_tires['Tire_Temperature']],
                textposition='top center',
                hovertemplate='<b>%{x}</b><br>Temperature: %{y:.1f}°C<extra></extra>'
            ),
            row=1, col=2
        )

        # 3. Tire Efficiency
        efficiency_colors = px.colors.sequential.Viridis
        fig.add_trace(
            go.Bar(
                x=df_tires['Driver'],
                y=df_tires['Tire_Efficiency'],
                name='Efficiency',
                marker=dict(
                    color=df_tires['Tire_Efficiency'],
                    colorscale='Viridis',
                    showscale=False,
                    line=dict(width=1, color='white')
                ),
                text=[f"{val:.2f}" for val in df_tires['Tire_Efficiency']],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Efficiency: %{y:.3f}<extra></extra>'
            ),
            row=2, col=1
        )

        # 4. Tire Wear Index
        fig.add_trace(
            go.Bar(
                x=df_tires['Driver'],
                y=df_tires['Tire_Wear_Index'],
                name='Wear Index',
                marker=dict(
                    color=df_tires['Tire_Wear_Index'],
                    colorscale='Plasma',
                    showscale=False,
                    line=dict(width=1, color='white')
                ),
                text=[f"{val:.1f}" for val in df_tires['Tire_Wear_Index']],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Wear Index: %{y:.2f}<extra></extra>'
            ),
            row=2, col=2
        )

        # Update layout
        fig.update_layout(
            title=dict(
                text=f"<b>Tire Performance Analysis - {session_info}</b>",
                x=0.5,
                font=dict(size=24, color='white', family='Inter')
            ),
            font=dict(family='Inter', color='white'),
            paper_bgcolor='#0E1117',
            plot_bgcolor='#0E1117',
            showlegend=False,
            height=800,
            margin=dict(t=100, b=50, l=50, r=50)
        )

        # Update axes
        for i in range(1, 3):
            for j in range(1, 3):
                fig.update_xaxes(
                    gridcolor='rgba(128, 128, 128, 0.2)',
                    showgrid=True,
                    zeroline=False,
                    color='white',
                    tickangle=45,
                    row=i, col=j
                )
                fig.update_yaxes(
                    gridcolor='rgba(128, 128, 128, 0.2)',
                    showgrid=True,
                    zeroline=False,
                    color='white',
                    row=i, col=j
                )

        return fig

    def create_tire_comparison_heatmap(self, df_tires):
        """Create a heatmap comparing all tire metrics"""
        
        # Prepare data for heatmap
        metrics = ['Tire_Stress_Index', 'Tire_Temperature', 'Tire_Efficiency', 
                  'Tire_Wear_Index', 'Grip_Level']
        
        # Normalize data for better visualization
        heatmap_data = df_tires[metrics].copy()
        for col in metrics:
            heatmap_data[col] = (heatmap_data[col] - heatmap_data[col].min()) / \
                               (heatmap_data[col].max() - heatmap_data[col].min())

        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values.T,
            x=df_tires['Driver'],
            y=['Stress Index', 'Temperature', 'Efficiency', 'Wear Index', 'Grip Level'],
            colorscale='RdYlBu_r',
            text=np.round(heatmap_data.values.T, 3),
            texttemplate="%{text}",
            textfont={"size": 10, "color": "white"},
            hoverongaps=False,
            hovertemplate='<b>%{y}</b><br>Driver: %{x}<br>Normalized Value: %{z:.3f}<extra></extra>'
        ))

        fig.update_layout(
            title=dict(
                text="<b>Tire Performance Heatmap - Normalized Metrics</b>",
                x=0.5,
                font=dict(size=20, color='white', family='Inter')
            ),
            xaxis=dict(title='Driver', color='white'),
            yaxis=dict(title='Metrics', color='white'),
            font=dict(family='Inter', color='white'),
            paper_bgcolor='#0E1117',
            plot_bgcolor='#0E1117',
            height=500
        )

        return fig