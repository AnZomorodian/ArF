"""
Real-time F1 Insights and Live Analysis
Dynamic performance tracking and instant race insights
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from datetime import datetime, timedelta
from .constants import TEAM_COLORS

class RealTimeF1Insights:
    def __init__(self, session, laps_data):
        self.session = session
        self.laps_data = laps_data
        
    def live_performance_dashboard(self):
        """Create a live performance dashboard with key metrics"""
        if self.laps_data is None:
            return None
            
        try:
            # Current session statistics
            total_laps = len(self.laps_data)
            active_drivers = len(self.laps_data['Driver'].unique())
            session_duration = self._calculate_session_duration()
            
            # Performance leaders
            fastest_lap_info = self._get_fastest_lap_info()
            most_consistent = self._get_most_consistent_driver()
            pace_setter = self._get_current_pace_leader()
            
            dashboard_data = {
                'session_stats': {
                    'total_laps': total_laps,
                    'active_drivers': active_drivers,
                    'session_duration': session_duration,
                    'avg_lap_time': self._get_average_lap_time()
                },
                'performance_leaders': {
                    'fastest_lap': fastest_lap_info,
                    'most_consistent': most_consistent,
                    'pace_setter': pace_setter
                },
                'live_trends': self._get_live_performance_trends()
            }
            
            return dashboard_data
            
        except Exception as e:
            st.error(f"Error creating live dashboard: {str(e)}")
            return None
    
    def momentum_analysis(self):
        """Analyze driver momentum and performance trends"""
        if self.laps_data is None:
            return None
            
        try:
            momentum_data = []
            
            for driver in self.laps_data['Driver'].unique():
                driver_laps = self.laps_data[
                    (self.laps_data['Driver'] == driver) & 
                    (self.laps_data['LapTime'].notna())
                ].sort_values('LapNumber')
                
                if len(driver_laps) < 5:
                    continue
                
                lap_times = driver_laps['LapTime'].dt.total_seconds()
                
                # Calculate momentum indicators
                recent_laps = min(5, len(lap_times))
                if recent_laps < 3:
                    continue
                    
                recent_performance = lap_times.tail(recent_laps).mean()
                early_performance = lap_times.head(recent_laps).mean()
                
                # Momentum score (negative = improving, positive = declining)
                momentum_score = recent_performance - early_performance
                
                # Performance volatility (lower = more consistent)
                volatility = lap_times.std()
                
                # Trend strength
                lap_numbers = range(len(lap_times))
                correlation = np.corrcoef(lap_numbers, lap_times)[0, 1] if len(lap_times) > 2 else 0
                
                momentum_data.append({
                    'Driver': driver,
                    'Momentum_Score': momentum_score,
                    'Recent_Pace': recent_performance,
                    'Early_Pace': early_performance,
                    'Volatility': volatility,
                    'Trend_Strength': abs(correlation),
                    'Trend_Direction': 'Improving' if momentum_score < -0.1 else 'Declining' if momentum_score > 0.1 else 'Stable',
                    'Total_Laps': len(driver_laps)
                })
            
            if not momentum_data:
                return None
                
            return pd.DataFrame(momentum_data).sort_values('Momentum_Score')
            
        except Exception as e:
            st.error(f"Error in momentum analysis: {str(e)}")
            return None
    
    def sector_dominance_heatmap(self):
        """Create real-time sector dominance analysis"""
        if self.laps_data is None or 'Sector1Time' not in self.laps_data.columns:
            return None
            
        try:
            sector_data = []
            
            for driver in self.laps_data['Driver'].unique():
                driver_laps = self.laps_data[
                    (self.laps_data['Driver'] == driver) & 
                    (self.laps_data['Sector1Time'].notna()) &
                    (self.laps_data['Sector2Time'].notna()) &
                    (self.laps_data['Sector3Time'].notna())
                ]
                
                if len(driver_laps) == 0:
                    continue
                
                # Calculate average sector times
                sector1_avg = driver_laps['Sector1Time'].dt.total_seconds().mean()
                sector2_avg = driver_laps['Sector2Time'].dt.total_seconds().mean()
                sector3_avg = driver_laps['Sector3Time'].dt.total_seconds().mean()
                
                # Best sector times
                sector1_best = driver_laps['Sector1Time'].dt.total_seconds().min()
                sector2_best = driver_laps['Sector2Time'].dt.total_seconds().min()
                sector3_best = driver_laps['Sector3Time'].dt.total_seconds().min()
                
                sector_data.append({
                    'Driver': driver,
                    'Sector1_Avg': sector1_avg,
                    'Sector2_Avg': sector2_avg,
                    'Sector3_Avg': sector3_avg,
                    'Sector1_Best': sector1_best,
                    'Sector2_Best': sector2_best,
                    'Sector3_Best': sector3_best
                })
            
            if not sector_data:
                return None
                
            sector_df = pd.DataFrame(sector_data)
            
            # Calculate relative performance (percentage off fastest)
            for sector in ['Sector1', 'Sector2', 'Sector3']:
                fastest_avg = sector_df[f'{sector}_Avg'].min()
                fastest_best = sector_df[f'{sector}_Best'].min()
                
                sector_df[f'{sector}_Avg_Delta'] = ((sector_df[f'{sector}_Avg'] - fastest_avg) / fastest_avg) * 100
                sector_df[f'{sector}_Best_Delta'] = ((sector_df[f'{sector}_Best'] - fastest_best) / fastest_best) * 100
            
            return sector_df
            
        except Exception as e:
            st.error(f"Error in sector dominance analysis: {str(e)}")
            return None
    
    def _calculate_session_duration(self):
        """Calculate current session duration"""
        if self.laps_data is None or len(self.laps_data) == 0:
            return "Unknown"
            
        try:
            if 'Time' in self.laps_data.columns:
                min_time = self.laps_data['Time'].min()
                max_time = self.laps_data['Time'].max()
                duration = max_time - min_time
                return str(duration).split('.')[0]  # Remove microseconds
            return "Unknown"
        except:
            return "Unknown"
    
    def _get_fastest_lap_info(self):
        """Get fastest lap information"""
        if self.laps_data is None:
            return None
            
        try:
            valid_laps = self.laps_data[self.laps_data['LapTime'].notna()]
            if len(valid_laps) == 0:
                return None
                
            fastest_lap = valid_laps.loc[valid_laps['LapTime'].idxmin()]
            return {
                'driver': fastest_lap['Driver'],
                'time': fastest_lap['LapTime'],
                'lap_number': fastest_lap.get('LapNumber', 'Unknown')
            }
        except:
            return None
    
    def _get_most_consistent_driver(self):
        """Get most consistent driver"""
        if self.laps_data is None:
            return None
            
        try:
            consistency_data = []
            
            for driver in self.laps_data['Driver'].unique():
                driver_laps = self.laps_data[
                    (self.laps_data['Driver'] == driver) & 
                    (self.laps_data['LapTime'].notna())
                ]
                
                if len(driver_laps) < 3:
                    continue
                
                lap_times = driver_laps['LapTime'].dt.total_seconds()
                consistency = lap_times.std()
                
                consistency_data.append({
                    'driver': driver,
                    'consistency': consistency,
                    'laps': len(driver_laps)
                })
            
            if not consistency_data:
                return None
                
            most_consistent = min(consistency_data, key=lambda x: x['consistency'])
            return most_consistent
            
        except:
            return None
    
    def _get_current_pace_leader(self):
        """Get current pace leader based on recent laps"""
        if self.laps_data is None:
            return None
            
        try:
            pace_data = []
            
            for driver in self.laps_data['Driver'].unique():
                driver_laps = self.laps_data[
                    (self.laps_data['Driver'] == driver) & 
                    (self.laps_data['LapTime'].notna())
                ].sort_values('LapNumber')
                
                if len(driver_laps) < 3:
                    continue
                
                # Get recent pace (last 5 laps or all if less)
                recent_laps = driver_laps.tail(min(5, len(driver_laps)))
                recent_pace = recent_laps['LapTime'].dt.total_seconds().mean()
                
                pace_data.append({
                    'driver': driver,
                    'recent_pace': recent_pace,
                    'recent_laps': len(recent_laps)
                })
            
            if not pace_data:
                return None
                
            pace_leader = min(pace_data, key=lambda x: x['recent_pace'])
            return pace_leader
            
        except:
            return None
    
    def _get_average_lap_time(self):
        """Get session average lap time"""
        if self.laps_data is None:
            return None
            
        try:
            valid_laps = self.laps_data[self.laps_data['LapTime'].notna()]
            if len(valid_laps) == 0:
                return None
                
            avg_seconds = valid_laps['LapTime'].dt.total_seconds().mean()
            return pd.Timedelta(seconds=avg_seconds)
            
        except:
            return None
    
    def _get_live_performance_trends(self):
        """Get live performance trends"""
        if self.laps_data is None:
            return None
            
        try:
            trends = {}
            
            for driver in self.laps_data['Driver'].unique():
                driver_laps = self.laps_data[
                    (self.laps_data['Driver'] == driver) & 
                    (self.laps_data['LapTime'].notna())
                ].sort_values('LapNumber')
                
                if len(driver_laps) < 5:
                    continue
                
                lap_times = driver_laps['LapTime'].dt.total_seconds()
                lap_numbers = driver_laps['LapNumber'].values
                
                # Calculate trend
                if len(lap_times) > 1:
                    correlation = np.corrcoef(lap_numbers, lap_times)[0, 1]
                    trends[driver] = {
                        'trend': correlation,
                        'direction': 'Improving' if correlation < -0.1 else 'Declining' if correlation > 0.1 else 'Stable',
                        'latest_lap': lap_times.iloc[-1],
                        'best_lap': lap_times.min()
                    }
            
            return trends
            
        except:
            return None
    
    def create_live_dashboard_viz(self, dashboard_data):
        """Create live dashboard visualization"""
        if dashboard_data is None:
            return None
            
        try:
            fig = make_subplots(
                rows=3, cols=2,
                subplot_titles=['Session Overview', 'Performance Leaders',
                              'Live Trends', 'Driver Momentum',
                              'Recent Performance', 'Session Progress'],
                specs=[[{"type": "indicator"}, {"type": "bar"}],
                       [{"type": "scatter"}, {"type": "bar"}],
                       [{"type": "scatter"}, {"type": "indicator"}]]
            )
            
            # Session stats indicator
            session_stats = dashboard_data.get('session_stats', {})
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=session_stats.get('total_laps', 0),
                    title={'text': "Total Laps"},
                    gauge={'axis': {'range': [0, 100]},
                          'bar': {'color': "#DC0000"},
                          'steps': [{'range': [0, 50], 'color': "lightgray"},
                                   {'range': [50, 100], 'color': "gray"}],
                          'threshold': {'line': {'color': "red", 'width': 4},
                                      'thickness': 0.75, 'value': 90}}
                ),
                row=1, col=1
            )
            
            fig.update_layout(
                title="F1 Live Performance Dashboard",
                height=900,
                showlegend=True,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating live dashboard: {str(e)}")
            return None