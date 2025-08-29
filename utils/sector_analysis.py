"""
Sector-by-sector analysis utilities for F1 data
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .constants import TEAM_COLORS, DRIVER_TEAMS
from .formatters import format_lap_time

class SectorAnalyzer:
    """Advanced sector-by-sector performance analysis"""
    
    def __init__(self, session):
        self.session = session
        
    def analyze_sector_performance(self, drivers):
        """Analyze detailed sector performance for drivers"""
        sector_data = []
        
        for driver in drivers:
            try:
                driver_laps = self.session.laps.pick_drivers([driver]).pick_quicklaps()
                if driver_laps.empty:
                    continue
                
                # Get fastest sector times
                best_s1 = driver_laps['Sector1Time'].min()
                best_s2 = driver_laps['Sector2Time'].min() 
                best_s3 = driver_laps['Sector3Time'].min()
                
                # Calculate sector consistency
                s1_std = driver_laps['Sector1Time'].std().total_seconds() if not pd.isna(driver_laps['Sector1Time'].std()) else 0
                s2_std = driver_laps['Sector2Time'].std().total_seconds() if not pd.isna(driver_laps['Sector2Time'].std()) else 0
                s3_std = driver_laps['Sector3Time'].std().total_seconds() if not pd.isna(driver_laps['Sector3Time'].std()) else 0
                
                sector_data.append({
                    'driver': driver,
                    'sector_1_best': best_s1.total_seconds() if not pd.isna(best_s1) else None,
                    'sector_2_best': best_s2.total_seconds() if not pd.isna(best_s2) else None,
                    'sector_3_best': best_s3.total_seconds() if not pd.isna(best_s3) else None,
                    'sector_1_consistency': s1_std,
                    'sector_2_consistency': s2_std,
                    'sector_3_consistency': s3_std,
                    'total_laps': len(driver_laps)
                })
                
            except Exception as e:
                print(f"Error analyzing sectors for {driver}: {e}")
                continue
                
        return sector_data
    
    def create_sector_comparison_chart(self, drivers):
        """Create detailed sector comparison visualization"""
        try:
            sector_data = self.analyze_sector_performance(drivers)
            if not sector_data:
                return None
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Sector 1 Performance', 'Sector 2 Performance', 
                               'Sector 3 Performance', 'Sector Consistency'),
                specs=[[{"type": "bar"}, {"type": "bar"}],
                       [{"type": "bar"}, {"type": "bar"}]]
            )
            
            drivers_list = [d['driver'] for d in sector_data]
            colors = [TEAM_COLORS.get(DRIVER_TEAMS.get(d, 'Unknown'), '#808080') for d in drivers_list]
            
            # Sector best times
            for i, sector in enumerate(['sector_1_best', 'sector_2_best', 'sector_3_best'], 1):
                times = [d[sector] for d in sector_data]
                row = 1 if i <= 2 else 2
                col = i if i <= 2 else i - 2
                
                fig.add_trace(
                    go.Bar(
                        x=drivers_list,
                        y=times,
                        name=f'Sector {i}',
                        marker_color=colors,
                        showlegend=False,
                        text=[format_lap_time(t) if t else 'N/A' for t in times],
                        textposition='auto'
                    ),
                    row=row, col=col
                )
            
            # Consistency chart
            consistency_data = [d['sector_1_consistency'] + d['sector_2_consistency'] + d['sector_3_consistency'] for d in sector_data]
            fig.add_trace(
                go.Bar(
                    x=drivers_list,
                    y=consistency_data,
                    name='Total Variance',
                    marker_color=colors,
                    showlegend=False,
                    text=[f'{c:.3f}s' for c in consistency_data],
                    textposition='auto'
                ),
                row=2, col=2
            )
            
            fig.update_layout(
                title='🏁 Detailed Sector Analysis',
                height=600,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating sector comparison: {e}")
            return None

def create_sector_evolution_chart(session, driver):
    """Track sector time evolution throughout the session"""
    try:
        driver_laps = session.laps.pick_drivers([driver]).pick_quicklaps()
        if driver_laps.empty:
            return None
        
        fig = go.Figure()
        
        lap_numbers = driver_laps['LapNumber'].values
        
        # Add sector traces
        sectors = ['Sector1Time', 'Sector2Time', 'Sector3Time']
        sector_names = ['Sector 1', 'Sector 2', 'Sector 3']
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1']
        
        for sector, name, color in zip(sectors, sector_names, colors):
            if sector in driver_laps.columns:
                times = [t.total_seconds() if not pd.isna(t) else None for t in driver_laps[sector]]
                
                fig.add_trace(go.Scatter(
                    x=lap_numbers,
                    y=times,
                    mode='lines+markers',
                    name=name,
                    line=dict(color=color, width=3),
                    marker=dict(size=6)
                ))
        
        fig.update_layout(
            title=f'Sector Time Evolution - {driver}',
            xaxis_title='Lap Number',
            yaxis_title='Sector Time (seconds)',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            hovermode='x unified'
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating sector evolution chart: {e}")
        return None