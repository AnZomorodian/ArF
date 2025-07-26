"""
Comparative Analytics for F1 Performance
Advanced driver and team comparison with statistical insights
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from scipy import stats
from .constants import TEAM_COLORS

class ComparativeF1Analytics:
    def __init__(self, session, laps_data):
        self.session = session
        self.laps_data = laps_data
        
    def head_to_head_analysis(self, driver1, driver2):
        """Detailed head-to-head comparison between two drivers"""
        if self.laps_data is None:
            return None
            
        try:
            driver1_laps = self.laps_data[
                (self.laps_data['Driver'] == driver1) & 
                (self.laps_data['LapTime'].notna())
            ]
            driver2_laps = self.laps_data[
                (self.laps_data['Driver'] == driver2) & 
                (self.laps_data['LapTime'].notna())
            ]
            
            if len(driver1_laps) == 0 or len(driver2_laps) == 0:
                return None
            
            # Convert lap times to seconds
            d1_times = driver1_laps['LapTime'].dt.total_seconds()
            d2_times = driver2_laps['LapTime'].dt.total_seconds()
            
            # Statistical comparison
            comparison_data = {
                'driver1': driver1,
                'driver2': driver2,
                'driver1_stats': {
                    'best_lap': d1_times.min(),
                    'average_lap': d1_times.mean(),
                    'consistency': d1_times.std(),
                    'total_laps': len(d1_times),
                    'median_lap': d1_times.median(),
                    'q75_lap': d1_times.quantile(0.75),
                    'q25_lap': d1_times.quantile(0.25)
                },
                'driver2_stats': {
                    'best_lap': d2_times.min(),
                    'average_lap': d2_times.mean(),
                    'consistency': d2_times.std(),
                    'total_laps': len(d2_times),
                    'median_lap': d2_times.median(),
                    'q75_lap': d2_times.quantile(0.75),
                    'q25_lap': d2_times.quantile(0.25)
                }
            }
            
            # Statistical significance test
            if len(d1_times) > 2 and len(d2_times) > 2:
                t_stat, p_value = stats.ttest_ind(d1_times, d2_times)
                comparison_data['statistical_test'] = {
                    't_statistic': t_stat,
                    'p_value': p_value,
                    'significant': p_value < 0.05
                }
            
            # Sector comparison if available
            if 'Sector1Time' in self.laps_data.columns:
                comparison_data['sector_comparison'] = self._compare_sectors(driver1, driver2)
            
            return comparison_data
            
        except Exception as e:
            st.error(f"Error in head-to-head analysis: {str(e)}")
            return None
    
    def performance_percentiles(self):
        """Calculate performance percentiles for all drivers"""
        if self.laps_data is None:
            return None
            
        try:
            percentile_data = []
            
            for driver in self.laps_data['Driver'].unique():
                driver_laps = self.laps_data[
                    (self.laps_data['Driver'] == driver) & 
                    (self.laps_data['LapTime'].notna())
                ]
                
                if len(driver_laps) < 3:
                    continue
                
                lap_times = driver_laps['LapTime'].dt.total_seconds()
                
                percentile_data.append({
                    'Driver': driver,
                    'P10': np.percentile(lap_times, 10),
                    'P25': np.percentile(lap_times, 25),
                    'P50': np.percentile(lap_times, 50),
                    'P75': np.percentile(lap_times, 75),
                    'P90': np.percentile(lap_times, 90),
                    'Best': lap_times.min(),
                    'Worst': lap_times.max(),
                    'Mean': lap_times.mean(),
                    'Std': lap_times.std(),
                    'Range': lap_times.max() - lap_times.min(),
                    'Laps': len(lap_times)
                })
            
            if not percentile_data:
                return None
                
            return pd.DataFrame(percentile_data)
            
        except Exception as e:
            st.error(f"Error calculating percentiles: {str(e)}")
            return None
    
    def consistency_ranking(self):
        """Rank drivers by consistency metrics"""
        if self.laps_data is None:
            return None
            
        try:
            consistency_data = []
            
            for driver in self.laps_data['Driver'].unique():
                driver_laps = self.laps_data[
                    (self.laps_data['Driver'] == driver) & 
                    (self.laps_data['LapTime'].notna())
                ]
                
                if len(driver_laps) < 5:
                    continue
                
                lap_times = driver_laps['LapTime'].dt.total_seconds()
                
                # Multiple consistency metrics
                std_dev = lap_times.std()
                coefficient_of_variation = (std_dev / lap_times.mean()) * 100
                iqr = lap_times.quantile(0.75) - lap_times.quantile(0.25)
                
                # Outlier analysis
                q1 = lap_times.quantile(0.25)
                q3 = lap_times.quantile(0.75)
                iqr_range = q3 - q1
                outliers = lap_times[(lap_times < q1 - 1.5 * iqr_range) | 
                                   (lap_times > q3 + 1.5 * iqr_range)]
                outlier_percentage = (len(outliers) / len(lap_times)) * 100
                
                consistency_data.append({
                    'Driver': driver,
                    'Standard_Deviation': std_dev,
                    'Coefficient_of_Variation': coefficient_of_variation,
                    'IQR': iqr,
                    'Outlier_Percentage': outlier_percentage,
                    'Best_Lap': lap_times.min(),
                    'Average_Lap': lap_times.mean(),
                    'Consistency_Score': (std_dev * 0.4) + (coefficient_of_variation * 0.3) + (outlier_percentage * 0.3),
                    'Total_Laps': len(lap_times)
                })
            
            if not consistency_data:
                return None
                
            df = pd.DataFrame(consistency_data)
            return df.sort_values('Consistency_Score')
            
        except Exception as e:
            st.error(f"Error in consistency ranking: {str(e)}")
            return None
    
    def _compare_sectors(self, driver1, driver2):
        """Compare sector performance between two drivers"""
        try:
            d1_laps = self.laps_data[
                (self.laps_data['Driver'] == driver1) & 
                (self.laps_data['Sector1Time'].notna()) &
                (self.laps_data['Sector2Time'].notna()) &
                (self.laps_data['Sector3Time'].notna())
            ]
            d2_laps = self.laps_data[
                (self.laps_data['Driver'] == driver2) & 
                (self.laps_data['Sector1Time'].notna()) &
                (self.laps_data['Sector2Time'].notna()) &
                (self.laps_data['Sector3Time'].notna())
            ]
            
            if len(d1_laps) == 0 or len(d2_laps) == 0:
                return None
            
            sector_comparison = {}
            
            for sector in ['Sector1Time', 'Sector2Time', 'Sector3Time']:
                d1_sector = d1_laps[sector].dt.total_seconds()
                d2_sector = d2_laps[sector].dt.total_seconds()
                
                sector_comparison[sector] = {
                    'driver1_avg': d1_sector.mean(),
                    'driver2_avg': d2_sector.mean(),
                    'driver1_best': d1_sector.min(),
                    'driver2_best': d2_sector.min(),
                    'difference_avg': d1_sector.mean() - d2_sector.mean(),
                    'difference_best': d1_sector.min() - d2_sector.min()
                }
            
            return sector_comparison
            
        except:
            return None
    
    def create_head_to_head_viz(self, comparison_data):
        """Create head-to-head visualization"""
        if comparison_data is None:
            return None
            
        try:
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=['Lap Time Distribution', 'Performance Metrics',
                              'Statistical Comparison', 'Sector Analysis'],
                specs=[[{"type": "violin"}, {"type": "bar"}],
                       [{"type": "bar"}, {"type": "radar"}]]
            )
            
            driver1 = comparison_data['driver1']
            driver2 = comparison_data['driver2']
            d1_stats = comparison_data['driver1_stats']
            d2_stats = comparison_data['driver2_stats']
            
            # Performance metrics comparison
            metrics = ['best_lap', 'average_lap', 'consistency']
            d1_values = [d1_stats[metric] for metric in metrics]
            d2_values = [d2_stats[metric] for metric in metrics]
            
            fig.add_trace(
                go.Bar(
                    x=metrics,
                    y=d1_values,
                    name=driver1,
                    marker_color='#DC0000'
                ),
                row=1, col=2
            )
            
            fig.add_trace(
                go.Bar(
                    x=metrics,
                    y=d2_values,
                    name=driver2,
                    marker_color='#00D2BE'
                ),
                row=1, col=2
            )
            
            fig.update_layout(
                title=f"Head-to-Head: {driver1} vs {driver2}",
                height=800,
                showlegend=True,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating head-to-head visualization: {str(e)}")
            return None
    
    def create_percentile_visualization(self, percentile_data):
        """Create performance percentiles visualization"""
        if percentile_data is None or len(percentile_data) == 0:
            return None
            
        try:
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=['Performance Distribution', 'Consistency Analysis',
                              'Percentile Ranges', 'Statistical Summary'],
                specs=[[{"type": "box"}, {"type": "scatter"}],
                       [{"type": "bar"}, {"type": "table"}]]
            )
            
            # Box plot for performance distribution
            for _, driver_data in percentile_data.iterrows():
                driver = driver_data['Driver']
                y_values = [
                    driver_data['Best'], driver_data['P10'], driver_data['P25'],
                    driver_data['P50'], driver_data['P75'], driver_data['P90'],
                    driver_data['Worst']
                ]
                
                fig.add_trace(
                    go.Box(
                        y=y_values,
                        name=driver,
                        boxpoints='all',
                        jitter=0.3
                    ),
                    row=1, col=1
                )
            
            # Consistency scatter plot
            fig.add_trace(
                go.Scatter(
                    x=percentile_data['Mean'],
                    y=percentile_data['Std'],
                    mode='markers+text',
                    text=percentile_data['Driver'],
                    textposition='top center',
                    marker=dict(
                        size=12,
                        color=percentile_data['Range'],
                        colorscale='Viridis',
                        showscale=True
                    ),
                    name='Consistency vs Performance'
                ),
                row=1, col=2
            )
            
            fig.update_layout(
                title="Driver Performance Percentiles Analysis",
                height=800,
                showlegend=True,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating percentile visualization: {str(e)}")
            return None