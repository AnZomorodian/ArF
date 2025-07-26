"""
Driver Stress Index Analysis Module
Advanced driver stress calculation and visualization for F1 data
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from utils.constants import TEAM_COLORS


class DriverStressAnalyzer:
    """Advanced driver stress index analysis for F1 performance"""
    
    def __init__(self, session):
        self.session = session
        
    def calculate_driver_stress_index(self):
        """Calculate comprehensive Driver Stress Index (DSI) for all drivers"""
        drivers = self.session.drivers
        results = []

        for driver in drivers:
            driver_laps = self.session.laps.pick_driver(driver)
            fastest_lap = driver_laps.pick_fastest()

            if fastest_lap.empty or pd.isna(fastest_lap['DriverNumber']):
                continue

            try:
                telemetry = fastest_lap.get_car_data().add_distance()
            except (KeyError, AttributeError):
                continue

            # Enhanced telemetry analysis
            speed_data = telemetry['Speed']
            brake_data = telemetry['Brake']
            throttle_data = telemetry['Throttle']
            distance_data = telemetry['Distance']

            # Advanced calculations
            total_distance = distance_data.max() - distance_data.min()
            
            # Weighted metrics based on distance and intensity
            braking_weighted = (brake_data.sum() * (distance_data.diff().mean())) / total_distance * 100
            high_throttle_weighted = (len(throttle_data[throttle_data > 90]) * 
                                    distance_data.diff().mean()) / total_distance * 100
            
            # Critical speed analysis
            critical_speed_median = speed_data[(brake_data > 0) | (throttle_data > 90)].median()
            
            # Enhanced stress calculations
            speed_variance = speed_data.var()
            gear_changes = len(telemetry['nGear'].diff()[telemetry['nGear'].diff() != 0])
            
            # Comprehensive Driver Stress Index
            base_stress = (braking_weighted + (100 - high_throttle_weighted)) / max(critical_speed_median, 1)
            variance_factor = speed_variance / 1000  # Normalize speed variance
            gear_stress = gear_changes / total_distance * 1000  # Gear changes per km
            
            driver_stress_index = base_stress + variance_factor + gear_stress
            
            # Additional performance metrics
            consistency_index = 100 - (speed_data.std() / speed_data.mean() * 100)
            aggression_index = (braking_weighted + gear_stress) / 2
            smoothness_index = 100 - variance_factor
            
            driver_info = self.session.get_driver(driver)
            driver_name = driver_info['LastName'][:3].upper()
            team_name = driver_info.get('TeamName', 'Unknown')

            results.append({
                'Driver': driver_name,
                'Team': team_name,
                'Braking_Percentage': braking_weighted,
                'High_Throttle_Percentage': high_throttle_weighted,
                'Critical_Speed_Median': critical_speed_median,
                'Driver_Stress_Index': driver_stress_index,
                'Consistency_Index': consistency_index,
                'Aggression_Index': aggression_index,
                'Smoothness_Index': smoothness_index,
                'Gear_Changes_Per_Km': gear_stress,
                'Speed_Variance': speed_variance
            })

        return pd.DataFrame(results)

    def create_stress_analysis_visualizations(self, df_stress, session_info):
        """Create comprehensive stress analysis visualizations"""
        
        # Create subplot layout
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                'Driver Stress Index Ranking',
                'Stress Components Analysis',
                'Driving Style Comparison', 
                'Performance Correlation Matrix'
            ],
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"type": "heatmap"}]]
        )

        # Sort by stress index for better visualization
        df_sorted = df_stress.sort_values('Driver_Stress_Index', ascending=True)
        
        # Get team colors
        colors = [TEAM_COLORS.get(team, '#888888') for team in df_sorted['Team']]

        # 1. Driver Stress Index Bar Chart
        fig.add_trace(
            go.Bar(
                y=df_sorted['Driver'],
                x=df_sorted['Driver_Stress_Index'],
                orientation='h',
                name='Stress Index',
                marker_color=colors,
                text=[f"{val:.2f}" for val in df_sorted['Driver_Stress_Index']],
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Stress Index: %{x:.3f}<br>' +
                             'Critical Speed: %{customdata:.1f} km/h<extra></extra>',
                customdata=df_sorted['Critical_Speed_Median']
            ),
            row=1, col=1
        )

        # 2. Stress Components Stacked Bar
        fig.add_trace(
            go.Bar(
                x=df_stress['Driver'],
                y=df_stress['Braking_Percentage'],
                name='Braking %',
                marker_color='#FF6B6B',
                offsetgroup=1
            ),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Bar(
                x=df_stress['Driver'],
                y=df_stress['Aggression_Index'],
                name='Aggression',
                marker_color='#4ECDC4',
                offsetgroup=2
            ),
            row=1, col=2
        )

        # 3. Driving Style Scatter Plot
        fig.add_trace(
            go.Scatter(
                x=df_stress['Consistency_Index'],
                y=df_stress['Smoothness_Index'],
                mode='markers+text',
                text=df_stress['Driver'],
                textposition='top center',
                marker=dict(
                    size=df_stress['Driver_Stress_Index'] * 3,
                    color=[TEAM_COLORS.get(team, '#888888') for team in df_stress['Team']],
                    line=dict(width=2, color='white'),
                    opacity=0.8
                ),
                name='Driving Style',
                hovertemplate='<b>%{text}</b><br>' +
                             'Consistency: %{x:.1f}<br>' +
                             'Smoothness: %{y:.1f}<br>' +
                             'Stress Index: %{marker.size:.1f}<extra></extra>'
            ),
            row=2, col=1
        )

        # 4. Correlation Heatmap
        correlation_metrics = ['Driver_Stress_Index', 'Consistency_Index', 
                             'Aggression_Index', 'Smoothness_Index']
        corr_matrix = df_stress[correlation_metrics].corr()
        
        fig.add_trace(
            go.Heatmap(
                z=corr_matrix.values,
                x=['Stress', 'Consistency', 'Aggression', 'Smoothness'],
                y=['Stress', 'Consistency', 'Aggression', 'Smoothness'],
                colorscale='RdBu',
                zmid=0,
                text=np.round(corr_matrix.values, 3),
                texttemplate="%{text}",
                textfont={"size": 12, "color": "white"},
                hoverongaps=False
            ),
            row=2, col=2
        )

        # Update layout
        fig.update_layout(
            title=dict(
                text=f"<b>Driver Stress Analysis - {session_info}</b>",
                x=0.5,
                font=dict(size=24, color='white', family='Inter')
            ),
            font=dict(family='Inter', color='white'),
            paper_bgcolor='#0E1117',
            plot_bgcolor='#0E1117',
            showlegend=True,
            height=900,
            margin=dict(t=100, b=50, l=50, r=50)
        )

        # Update axes styling
        for i in range(1, 3):
            for j in range(1, 3):
                fig.update_xaxes(
                    gridcolor='rgba(128, 128, 128, 0.2)',
                    showgrid=True,
                    zeroline=False,
                    color='white',
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

    def create_stress_ranking_chart(self, df_stress):
        """Create a professional stress ranking visualization"""
        
        df_sorted = df_stress.sort_values('Driver_Stress_Index', ascending=False)
        
        # Create color gradient based on stress level
        colors = px.colors.sequential.Plasma
        normalized_stress = (df_sorted['Driver_Stress_Index'] - df_sorted['Driver_Stress_Index'].min()) / \
                          (df_sorted['Driver_Stress_Index'].max() - df_sorted['Driver_Stress_Index'].min())
        
        fig = go.Figure()

        # Add bars with gradient colors
        fig.add_trace(go.Bar(
            x=df_sorted['Driver'],
            y=df_sorted['Driver_Stress_Index'],
            marker=dict(
                color=normalized_stress,
                colorscale='Plasma',
                showscale=True,
                colorbar=dict(
                    title="Stress Level",
                    titlefont=dict(color='white'),
                    tickfont=dict(color='white')
                ),
                line=dict(width=1, color='white')
            ),
            text=[f"{val:.3f}" for val in df_sorted['Driver_Stress_Index']],
            textposition='outside',
            textfont=dict(color='white', size=12),
            hovertemplate='<b>%{x}</b><br>' +
                         'Stress Index: %{y:.3f}<br>' +
                         'Team: %{customdata}<extra></extra>',
            customdata=df_sorted['Team']
        ))

        # Add mean line
        mean_stress = df_sorted['Driver_Stress_Index'].mean()
        fig.add_hline(
            y=mean_stress,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {mean_stress:.3f}",
            annotation_position="top right",
            annotation_font_color="white"
        )

        fig.update_layout(
            title=dict(
                text="<b>Driver Stress Index Ranking</b>",
                x=0.5,
                font=dict(size=22, color='white', family='Inter')
            ),
            xaxis=dict(
                title='Driver',
                color='white',
                tickangle=45,
                gridcolor='rgba(128, 128, 128, 0.2)'
            ),
            yaxis=dict(
                title='Stress Index',
                color='white',
                gridcolor='rgba(128, 128, 128, 0.2)'
            ),
            font=dict(family='Inter', color='white'),
            paper_bgcolor='#0E1117',
            plot_bgcolor='#0E1117',
            height=600,
            margin=dict(t=80, b=100, l=50, r=50)
        )

        return fig