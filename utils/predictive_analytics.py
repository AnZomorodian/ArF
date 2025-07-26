"""
Predictive Analytics for F1 Performance
Advanced machine learning insights for race predictions and driver performance
"""

import pandas as pd
import numpy as np
from scipy import stats
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from .constants import TEAM_COLORS

class PredictiveF1Analytics:
    def __init__(self, session, laps_data):
        self.session = session
        self.laps_data = laps_data
        
    def predict_qualifying_performance(self):
        """Predict qualifying performance based on practice sessions"""
        if self.laps_data is None or len(self.laps_data) == 0:
            return None
            
        try:
            # Calculate performance metrics per driver
            driver_stats = []
            
            for driver in self.laps_data['Driver'].unique():
                driver_laps = self.laps_data[self.laps_data['Driver'] == driver]
                
                # Filter valid laps (no deletions, reasonable times)
                valid_laps = driver_laps[
                    (driver_laps['LapTime'].notna()) & 
                    (driver_laps['LapTime'] < pd.Timedelta(seconds=200))
                ]
                
                if len(valid_laps) < 3:
                    continue
                    
                # Convert lap times to seconds for analysis
                lap_times_seconds = valid_laps['LapTime'].dt.total_seconds()
                
                # Calculate performance indicators
                best_time = lap_times_seconds.min()
                avg_time = lap_times_seconds.mean()
                consistency = lap_times_seconds.std()
                
                # Pace improvement trend (linear regression on lap times)
                lap_numbers = valid_laps['LapNumber'].values
                if len(lap_numbers) > 1:
                    slope, intercept, r_value, p_value, std_err = stats.linregress(lap_numbers, lap_times_seconds)
                    pace_trend = slope * 1000  # Convert to milliseconds per lap
                else:
                    pace_trend = 0
                    r_value = 0
                
                # Qualifying prediction score (lower is better)
                prediction_score = best_time + (consistency * 0.5) + (pace_trend * 0.3)
                
                driver_stats.append({
                    'Driver': driver,
                    'Best_Time': best_time,
                    'Average_Time': avg_time,
                    'Consistency': consistency,
                    'Pace_Trend': pace_trend,
                    'Trend_Correlation': r_value,
                    'Prediction_Score': prediction_score,
                    'Valid_Laps': len(valid_laps)
                })
            
            if not driver_stats:
                return None
                
            df_stats = pd.DataFrame(driver_stats)
            df_stats = df_stats.sort_values('Prediction_Score').reset_index(drop=True)
            df_stats['Predicted_Position'] = range(1, len(df_stats) + 1)
            
            return df_stats
            
        except Exception as e:
            st.error(f"Error in qualifying prediction: {str(e)}")
            return None
    
    def analyze_tire_degradation_patterns(self):
        """Advanced tire degradation analysis with predictive modeling"""
        if self.laps_data is None:
            return None
            
        try:
            degradation_data = []
            
            for driver in self.laps_data['Driver'].unique():
                driver_laps = self.laps_data[
                    (self.laps_data['Driver'] == driver) & 
                    (self.laps_data['LapTime'].notna()) &
                    (self.laps_data['Compound'].notna())
                ]
                
                if len(driver_laps) < 5:
                    continue
                
                # Group by tire stint
                stints = []
                current_compound = None
                stint_start = 0
                
                for i, (_, lap) in enumerate(driver_laps.iterrows()):
                    if lap['Compound'] != current_compound:
                        if current_compound is not None and i > stint_start + 2:
                            stint_laps = driver_laps.iloc[stint_start:i]
                            stints.append({
                                'driver': driver,
                                'compound': current_compound,
                                'laps': stint_laps,
                                'stint_length': len(stint_laps)
                            })
                        current_compound = lap['Compound']
                        stint_start = i
                
                # Add final stint
                if stint_start < len(driver_laps) - 2:
                    stint_laps = driver_laps.iloc[stint_start:]
                    stints.append({
                        'driver': driver,
                        'compound': current_compound,
                        'laps': stint_laps,
                        'stint_length': len(stint_laps)
                    })
                
                # Analyze each stint
                for stint in stints:
                    stint_laps = stint['laps']
                    lap_times = stint_laps['LapTime'].dt.total_seconds()
                    
                    if len(lap_times) < 3:
                        continue
                    
                    # Calculate degradation rate
                    lap_positions = range(len(lap_times))
                    slope, intercept, r_value, p_value, std_err = stats.linregress(lap_positions, lap_times)
                    
                    degradation_data.append({
                        'Driver': driver,
                        'Compound': stint['compound'],
                        'Stint_Length': stint['stint_length'],
                        'Initial_Pace': intercept,
                        'Degradation_Rate': slope,
                        'Correlation': r_value,
                        'Total_Degradation': slope * (stint['stint_length'] - 1),
                        'Avg_Lap_Time': lap_times.mean(),
                        'Best_Lap_Time': lap_times.min()
                    })
            
            if not degradation_data:
                return None
                
            return pd.DataFrame(degradation_data)
            
        except Exception as e:
            st.error(f"Error in tire degradation analysis: {str(e)}")
            return None
    
    def performance_evolution_tracking(self):
        """Track performance evolution throughout the session"""
        if self.laps_data is None:
            return None
            
        try:
            evolution_data = []
            
            for driver in self.laps_data['Driver'].unique():
                driver_laps = self.laps_data[
                    (self.laps_data['Driver'] == driver) & 
                    (self.laps_data['LapTime'].notna())
                ]
                
                if len(driver_laps) < 5:
                    continue
                
                lap_times = driver_laps['LapTime'].dt.total_seconds()
                lap_numbers = driver_laps['LapNumber'].values
                
                # Calculate rolling performance metrics
                window_size = min(5, len(lap_times) // 3)
                if window_size < 2:
                    continue
                
                rolling_mean = pd.Series(lap_times).rolling(window=window_size, center=True).mean()
                rolling_std = pd.Series(lap_times).rolling(window=window_size, center=True).std()
                
                for i in range(len(lap_times)):
                    if pd.notna(rolling_mean.iloc[i]) and pd.notna(rolling_std.iloc[i]):
                        evolution_data.append({
                            'Driver': driver,
                            'Lap_Number': lap_numbers[i],
                            'Lap_Time': lap_times.iloc[i],
                            'Rolling_Average': rolling_mean.iloc[i],
                            'Rolling_Consistency': rolling_std.iloc[i],
                            'Performance_Index': (lap_times.iloc[i] - rolling_mean.iloc[i]) / rolling_std.iloc[i] if rolling_std.iloc[i] > 0 else 0
                        })
            
            if not evolution_data:
                return None
                
            return pd.DataFrame(evolution_data)
            
        except Exception as e:
            st.error(f"Error in performance evolution tracking: {str(e)}")
            return None
    
    def create_prediction_visualization(self, prediction_data):
        """Create visualization for qualifying predictions"""
        if prediction_data is None or len(prediction_data) == 0:
            return None
            
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=['Predicted Qualifying Order', 'Consistency vs Performance', 
                          'Pace Improvement Trend', 'Performance Metrics'],
            specs=[[{"type": "bar"}, {"type": "scatter"}],
                   [{"type": "bar"}, {"type": "radar"}]]
        )
        
        # Predicted qualifying order
        fig.add_trace(
            go.Bar(
                x=prediction_data['Driver'],
                y=prediction_data['Best_Time'],
                name='Best Lap Time',
                marker_color='#DC0000',
                text=[f"P{pos}" for pos in prediction_data['Predicted_Position']],
                textposition='outside'
            ),
            row=1, col=1
        )
        
        # Consistency vs Performance scatter
        fig.add_trace(
            go.Scatter(
                x=prediction_data['Best_Time'],
                y=prediction_data['Consistency'],
                mode='markers+text',
                text=prediction_data['Driver'],
                textposition='top center',
                marker=dict(
                    size=12,
                    color=prediction_data['Pace_Trend'],
                    colorscale='RdYlGn_r',
                    showscale=True,
                    colorbar=dict(title="Pace Trend (ms/lap)")
                ),
                name='Driver Performance'
            ),
            row=1, col=2
        )
        
        # Pace improvement trend
        colors = ['#00FF00' if trend < 0 else '#FF0000' for trend in prediction_data['Pace_Trend']]
        fig.add_trace(
            go.Bar(
                x=prediction_data['Driver'],
                y=prediction_data['Pace_Trend'],
                name='Pace Trend',
                marker_color=colors,
                text=[f"{trend:.2f}ms" for trend in prediction_data['Pace_Trend']],
                textposition='outside'
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title="F1 Qualifying Performance Predictions",
            height=800,
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        
        return fig
    
    def create_degradation_visualization(self, degradation_data):
        """Create tire degradation visualization"""
        if degradation_data is None or len(degradation_data) == 0:
            return None
            
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=['Degradation Rate by Compound', 'Stint Performance Analysis',
                          'Total Degradation Impact', 'Compound Efficiency'],
            specs=[[{"type": "box"}, {"type": "scatter"}],
                   [{"type": "bar"}, {"type": "violin"}]]
        )
        
        # Box plot of degradation rates by compound
        compounds = degradation_data['Compound'].unique()
        for compound in compounds:
            compound_data = degradation_data[degradation_data['Compound'] == compound]
            fig.add_trace(
                go.Box(
                    y=compound_data['Degradation_Rate'],
                    name=compound,
                    boxpoints='all',
                    jitter=0.3,
                    pointpos=-1.8
                ),
                row=1, col=1
            )
        
        # Scatter: Stint length vs degradation
        fig.add_trace(
            go.Scatter(
                x=degradation_data['Stint_Length'],
                y=degradation_data['Total_Degradation'],
                mode='markers+text',
                text=degradation_data['Driver'],
                textposition='top center',
                marker=dict(
                    size=10,
                    color=degradation_data['Avg_Lap_Time'],
                    colorscale='Viridis',
                    showscale=True
                ),
                name='Stint Analysis'
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title="Advanced Tire Degradation Analysis",
            height=800,
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        
        return fig