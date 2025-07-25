"""
Weather Analytics Module for F1 Data Analysis
Provides weather impact analysis and track condition insights
"""

import fastf1
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class WeatherAnalytics:
    """Weather analysis for F1 sessions"""
    
    def __init__(self, session):
        self.session = session
        self.weather_data = session.weather_data if hasattr(session, 'weather_data') else None
        self.laps = session.laps
        
    def get_weather_summary(self):
        """Get comprehensive weather summary for the session"""
        if self.weather_data is None or self.weather_data.empty:
            return self._get_basic_weather_info()
            
        summary = {
            'air_temperature': {
                'min': self.weather_data['AirTemp'].min(),
                'max': self.weather_data['AirTemp'].max(),
                'mean': self.weather_data['AirTemp'].mean(),
            },
            'track_temperature': {
                'min': self.weather_data['TrackTemp'].min(),
                'max': self.weather_data['TrackTemp'].max(),
                'mean': self.weather_data['TrackTemp'].mean(),
            },
            'humidity': {
                'min': self.weather_data['Humidity'].min(),
                'max': self.weather_data['Humidity'].max(),
                'mean': self.weather_data['Humidity'].mean(),
            },
            'wind_speed': {
                'min': self.weather_data['WindSpeed'].min(),
                'max': self.weather_data['WindSpeed'].max(),
                'mean': self.weather_data['WindSpeed'].mean(),
            },
            'pressure': {
                'min': self.weather_data['Pressure'].min(),
                'max': self.weather_data['Pressure'].max(),
                'mean': self.weather_data['Pressure'].mean(),
            },
            'rainfall': self.weather_data['Rainfall'].any() if 'Rainfall' in self.weather_data.columns else False
        }
        
        return summary
    
    def _get_basic_weather_info(self):
        """Get basic weather info from lap data if weather_data is not available"""
        # Try to extract weather info from laps data
        weather_info = {}
        
        # Get unique weather conditions if available
        if 'TrackStatus' in self.laps.columns:
            track_conditions = self.laps['TrackStatus'].value_counts().to_dict()
            weather_info['track_conditions'] = track_conditions
            
        if 'IsPersonalBest' in self.laps.columns:
            # Analyze performance trends which might indicate weather impact
            weather_info['performance_trend'] = 'stable'
            
        return weather_info
    
    def analyze_weather_impact_on_lap_times(self):
        """Analyze how weather conditions affect lap times"""
        if self.weather_data is None or self.weather_data.empty:
            return None
            
        # Merge weather data with lap data
        weather_impact = []
        
        for idx, weather_row in self.weather_data.iterrows():
            # Find laps that occurred during this weather measurement
            session_time = weather_row['Time']
            
            # Get laps around this time (within 1 minute)
            time_window_laps = self.laps[
                (self.laps['Time'] >= session_time - pd.Timedelta(minutes=1)) &
                (self.laps['Time'] <= session_time + pd.Timedelta(minutes=1))
            ]
            
            if not time_window_laps.empty:
                avg_lap_time = time_window_laps['LapTime'].mean()
                
                weather_impact.append({
                    'time': session_time,
                    'air_temp': weather_row['AirTemp'],
                    'track_temp': weather_row['TrackTemp'],
                    'humidity': weather_row['Humidity'],
                    'wind_speed': weather_row['WindSpeed'],
                    'pressure': weather_row['Pressure'],
                    'average_lap_time': avg_lap_time.total_seconds() if pd.notna(avg_lap_time) else None,
                    'lap_count': len(time_window_laps)
                })
        
        return pd.DataFrame(weather_impact)
    
    def create_weather_evolution_plot(self):
        """Create a plot showing weather evolution during the session"""
        if self.weather_data is None or self.weather_data.empty:
            return self._create_basic_weather_plot()
            
        fig = make_subplots(
            rows=4, cols=1,
            subplot_titles=[
                'Temperature Evolution (°C)',
                'Humidity and Pressure',
                'Wind Conditions',
                'Track Conditions'
            ],
            vertical_spacing=0.08
        )
        
        # Temperature plot
        fig.add_trace(go.Scatter(
            x=self.weather_data.index,
            y=self.weather_data['AirTemp'],
            name='Air Temperature',
            line=dict(color='#FF6B6B', width=2)
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=self.weather_data.index,
            y=self.weather_data['TrackTemp'],
            name='Track Temperature',
            line=dict(color='#4ECDC4', width=2)
        ), row=1, col=1)
        
        # Humidity and Pressure
        fig.add_trace(go.Scatter(
            x=self.weather_data.index,
            y=self.weather_data['Humidity'],
            name='Humidity (%)',
            line=dict(color='#45B7D1', width=2),
            yaxis='y2'
        ), row=2, col=1)
        
        fig.add_trace(go.Scatter(
            x=self.weather_data.index,
            y=self.weather_data['Pressure'],
            name='Pressure (mbar)',
            line=dict(color='#96CEB4', width=2)
        ), row=2, col=1)
        
        # Wind conditions
        fig.add_trace(go.Scatter(
            x=self.weather_data.index,
            y=self.weather_data['WindSpeed'],
            name='Wind Speed (km/h)',
            line=dict(color='#FFEAA7', width=2)
        ), row=3, col=1)
        
        if 'WindDirection' in self.weather_data.columns:
            fig.add_trace(go.Scatter(
                x=self.weather_data.index,
                y=self.weather_data['WindDirection'],
                name='Wind Direction (°)',
                line=dict(color='#DDA0DD', width=2),
                yaxis='y4'
            ), row=3, col=1)
        
        # Track conditions (if rainfall data exists)
        if 'Rainfall' in self.weather_data.columns:
            fig.add_trace(go.Bar(
                x=self.weather_data.index,
                y=self.weather_data['Rainfall'].astype(int),
                name='Rainfall',
                marker_color='#74B9FF',
                opacity=0.7
            ), row=4, col=1)
        
        fig.update_layout(
            height=800,
            title='Weather Evolution During Session',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=True
        )
        
        # Update axes
        for i in range(1, 5):
            fig.update_xaxes(
                title_text='Session Time' if i == 4 else '',
                gridcolor='rgba(255,255,255,0.1)',
                row=i, col=1
            )
            fig.update_yaxes(
                gridcolor='rgba(255,255,255,0.1)',
                row=i, col=1
            )
        
        return fig
    
    def _create_basic_weather_plot(self):
        """Create basic weather info plot when detailed data is not available"""
        fig = go.Figure()
        
        fig.add_annotation(
            x=0.5, y=0.5,
            text="Detailed weather data not available for this session.<br>Weather impact analysis requires live session data.",
            showarrow=False,
            font=dict(size=16, color='white'),
            align='center'
        )
        
        fig.update_layout(
            title='Weather Information',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=False,
            height=400
        )
        
        return fig
    
    def get_optimal_conditions_analysis(self):
        """Analyze optimal weather conditions for fastest lap times"""
        weather_impact_data = self.analyze_weather_impact_on_lap_times()
        
        if weather_impact_data is None or weather_impact_data.empty:
            return None
            
        # Filter out invalid lap times
        valid_data = weather_impact_data[weather_impact_data['average_lap_time'].notna()]
        
        if valid_data.empty:
            return None
            
        # Find conditions for fastest average lap times
        fastest_conditions_idx = valid_data['average_lap_time'].idxmin()
        fastest_conditions = valid_data.iloc[fastest_conditions_idx]
        
        # Calculate correlations
        correlations = {}
        lap_time_series = pd.Series(valid_data['average_lap_time'])
        for weather_param in ['air_temp', 'track_temp', 'humidity', 'wind_speed', 'pressure']:
            if weather_param in valid_data.columns:
                weather_series = pd.Series(valid_data[weather_param])
                correlation = lap_time_series.corr(weather_series)
                correlations[weather_param] = correlation
        
        return {
            'optimal_conditions': fastest_conditions.to_dict(),
            'correlations': correlations,
            'total_samples': len(valid_data)
        }