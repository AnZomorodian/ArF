"""
Downforce Configuration Analysis Module
Advanced aerodynamic performance analysis for F1 data
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from utils.constants import TEAM_COLORS


class DownforceAnalyzer:
    """Advanced downforce and aerodynamic analysis for F1 performance"""
    
    def __init__(self, session):
        self.session = session
        
    def calculate_downforce_metrics(self):
        """Calculate comprehensive downforce and aerodynamic metrics"""
        drivers = self.session.drivers
        results = []

        for driver in drivers:
            try:
                driver_laps = self.session.laps.pick_drivers(driver)
                fastest_lap = driver_laps.pick_fastest()
                
                if fastest_lap.empty or pd.isna(fastest_lap['DriverNumber']):
                    continue
                
                telemetry = fastest_lap.get_car_data().add_distance()
                
                speed_data = telemetry['Speed']
                average_speed = speed_data.mean()
                top_speed = speed_data.max()
                
                # Downforce efficiency ratio
                downforce_efficiency = 100 * (average_speed / top_speed)
                
                # Speed variance for cornering analysis
                speed_variance = speed_data.std()
                
                # Corner speed analysis (speeds below 80% of max)
                corner_threshold = top_speed * 0.8
                corner_speeds = speed_data[speed_data < corner_threshold]
                avg_corner_speed = corner_speeds.mean() if len(corner_speeds) > 0 else 0
                
                # Straight line speed analysis (speeds above 90% of max)
                straight_threshold = top_speed * 0.9
                straight_speeds = speed_data[speed_data > straight_threshold]
                avg_straight_speed = straight_speeds.mean() if len(straight_speeds) > 0 else top_speed
                
                # Aerodynamic balance indicator
                aero_balance = (avg_corner_speed / avg_straight_speed) * 100 if avg_straight_speed > 0 else 0
                
                driver_info = self.session.get_driver(driver)
                driver_name = driver_info['LastName'][:3].upper()
                team_name = driver_info.get('TeamName', 'Unknown')
                
                results.append({
                    'Driver': driver_name,
                    'Team': team_name,
                    'Average_Speed': average_speed,
                    'Top_Speed': top_speed,
                    'Downforce_Efficiency': downforce_efficiency,
                    'Speed_Variance': speed_variance,
                    'Corner_Speed_Avg': avg_corner_speed,
                    'Straight_Speed_Avg': avg_straight_speed,
                    'Aero_Balance': aero_balance,
                    'Speed_Range': top_speed - speed_data.min()
                })
                
            except Exception as e:
                continue
                
        return pd.DataFrame(results)

    def create_downforce_visualizations(self, df_downforce, session_info):
        """Create comprehensive downforce analysis visualizations"""
        
        if df_downforce.empty:
            return None
            
        # Create subplot layout
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                'Downforce Efficiency by Driver',
                'Aerodynamic Balance Analysis',
                'Speed Profile Comparison',
                'Corner vs Straight Speed Performance'
            ],
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )

        # Sort by downforce efficiency
        df_sorted = df_downforce.sort_values('Downforce_Efficiency', ascending=False)
        
        # Get team colors
        colors = [TEAM_COLORS.get(team, '#888888') for team in df_sorted['Team']]

        # 1. Downforce Efficiency Bar Chart
        fig.add_trace(
            go.Bar(
                x=df_sorted['Driver'],
                y=df_sorted['Downforce_Efficiency'],
                name='Downforce Efficiency',
                marker_color=colors,
                text=[f"{val:.2f}%" for val in df_sorted['Downforce_Efficiency']],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Efficiency: %{y:.2f}%<br>' +
                             'Avg Speed: %{customdata[0]:.1f} km/h<br>' +
                             'Top Speed: %{customdata[1]:.1f} km/h<extra></extra>',
                customdata=list(zip(df_sorted['Average_Speed'], df_sorted['Top_Speed']))
            ),
            row=1, col=1
        )

        # Add mean line for downforce efficiency
        mean_efficiency = df_sorted['Downforce_Efficiency'].mean()
        fig.add_hline(
            y=mean_efficiency,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {mean_efficiency:.2f}%",
            row=1, col=1
        )

        # 2. Aerodynamic Balance Scatter Plot
        fig.add_trace(
            go.Scatter(
                x=df_downforce['Corner_Speed_Avg'],
                y=df_downforce['Straight_Speed_Avg'],
                mode='markers+text',
                text=df_downforce['Driver'],
                textposition='top center',
                marker=dict(
                    size=df_downforce['Aero_Balance'] * 0.5,
                    color=[TEAM_COLORS.get(team, '#888888') for team in df_downforce['Team']],
                    line=dict(width=2, color='white'),
                    opacity=0.8
                ),
                name='Aero Balance',
                hovertemplate='<b>%{text}</b><br>' +
                             'Corner Speed: %{x:.1f} km/h<br>' +
                             'Straight Speed: %{y:.1f} km/h<br>' +
                             'Aero Balance: %{marker.size:.1f}%<extra></extra>'
            ),
            row=1, col=2
        )

        # 3. Speed Profile Comparison
        fig.add_trace(
            go.Bar(
                x=df_downforce['Driver'],
                y=df_downforce['Speed_Variance'],
                name='Speed Variance',
                marker=dict(
                    color=df_downforce['Speed_Variance'],
                    colorscale='Viridis',
                    showscale=False,
                    line=dict(width=1, color='white')
                ),
                text=[f"{val:.1f}" for val in df_downforce['Speed_Variance']],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Speed Variance: %{y:.2f} km/h<extra></extra>'
            ),
            row=2, col=1
        )

        # 4. Corner vs Straight Speed Analysis
        fig.add_trace(
            go.Scatter(
                x=df_downforce['Driver'],
                y=df_downforce['Corner_Speed_Avg'],
                mode='markers+lines',
                name='Corner Speed',
                marker=dict(size=10, color='#FF6B6B'),
                line=dict(color='#FF6B6B', width=3),
                yaxis='y4'
            ),
            row=2, col=2
        )
        
        fig.add_trace(
            go.Scatter(
                x=df_downforce['Driver'],
                y=df_downforce['Straight_Speed_Avg'],
                mode='markers+lines',
                name='Straight Speed',
                marker=dict(size=10, color='#4ECDC4'),
                line=dict(color='#4ECDC4', width=3),
                yaxis='y4'
            ),
            row=2, col=2
        )

        # Update layout
        fig.update_layout(
            title=dict(
                text=f"<b>Downforce & Aerodynamic Analysis - {session_info}</b>",
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

    def create_downforce_ranking_chart(self, df_downforce):
        """Create professional downforce efficiency ranking"""
        
        if df_downforce.empty:
            return None
            
        df_sorted = df_downforce.sort_values('Downforce_Efficiency', ascending=False)
        
        fig = go.Figure()

        # Add bars with team colors
        colors = [TEAM_COLORS.get(team, '#888888') for team in df_sorted['Team']]
        
        fig.add_trace(go.Bar(
            x=df_sorted['Driver'],
            y=df_sorted['Downforce_Efficiency'],
            marker_color=colors,
            text=[f"{val:.2f}%" for val in df_sorted['Downforce_Efficiency']],
            textposition='outside',
            textfont=dict(color='white', size=12),
            hovertemplate='<b>%{x}</b><br>' +
                         'Downforce Efficiency: %{y:.2f}%<br>' +
                         'Team: %{customdata}<extra></extra>',
            customdata=df_sorted['Team']
        ))

        # Add mean line
        mean_efficiency = df_sorted['Downforce_Efficiency'].mean()
        fig.add_hline(
            y=mean_efficiency,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {mean_efficiency:.2f}%",
            annotation_position="top right",
            annotation_font_color="white"
        )

        fig.update_layout(
            title=dict(
                text="<b>Downforce Efficiency Ranking</b>",
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
                title='Downforce Efficiency (%)',
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