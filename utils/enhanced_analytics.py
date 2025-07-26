"""
Enhanced Advanced Analytics Module
Provides cutting-edge F1 performance analysis with machine learning insights
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from utils.constants import TEAM_COLORS


class EnhancedF1Analytics:
    """Advanced F1 analytics with machine learning and statistical analysis"""
    
    def __init__(self, session):
        self.session = session
        self.laps = session.laps
        self.results = session.results
        
    def calculate_driver_performance_index(self, drivers):
        """Calculate comprehensive performance index using multiple metrics"""
        performance_data = []
        
        for driver in drivers:
            try:
                driver_laps = self.laps.pick_drivers(driver)
                valid_laps = driver_laps[driver_laps['LapTime'].notna()]
                
                if len(valid_laps) < 3:
                    continue
                
                lap_times = valid_laps['LapTime'].dt.total_seconds()
                
                # Performance metrics
                consistency_score = 1 / (1 + lap_times.std())
                speed_consistency = 1 / (1 + valid_laps['SpeedI1'].std() / valid_laps['SpeedI1'].mean())
                pace_quality = 1 / lap_times.mean() * 100
                
                # Racecraft analysis
                overtakes = self._analyze_overtakes(valid_laps)
                sector_dominance = self._calculate_sector_dominance(valid_laps)
                
                # Tire management
                tire_efficiency = self._calculate_tire_efficiency(valid_laps)
                
                # Overall performance index (weighted combination)
                performance_index = (
                    consistency_score * 0.25 +
                    speed_consistency * 0.20 +
                    pace_quality * 0.25 +
                    overtakes * 0.10 +
                    sector_dominance * 0.10 +
                    tire_efficiency * 0.10
                )
                
                driver_info = self.session.get_driver(driver)
                
                performance_data.append({
                    'Driver': driver_info.get('Abbreviation', driver),
                    'Team': driver_info.get('TeamName', 'Unknown'),
                    'Performance_Index': performance_index,
                    'Consistency_Score': consistency_score,
                    'Speed_Consistency': speed_consistency,
                    'Pace_Quality': pace_quality,
                    'Overtake_Score': overtakes,
                    'Sector_Dominance': sector_dominance,
                    'Tire_Efficiency': tire_efficiency,
                    'Total_Laps': len(valid_laps),
                    'Best_Lap': lap_times.min(),
                    'Average_Lap': lap_times.mean()
                })
                
            except Exception as e:
                continue
                
        return pd.DataFrame(performance_data)
    
    def _analyze_overtakes(self, laps):
        """Analyze overtaking performance"""
        try:
            positions = laps['Position'].dropna()
            if len(positions) < 2:
                return 0
            
            position_changes = positions.diff()
            overtakes = len(position_changes[position_changes < 0])  # Negative = gained positions
            return min(1.0, overtakes / len(positions))
        except:
            return 0
    
    def _calculate_sector_dominance(self, laps):
        """Calculate how often driver has fastest sectors"""
        try:
            sector_times = []
            for col in ['Sector1Time', 'Sector2Time', 'Sector3Time']:
                if col in laps.columns:
                    sector_times.extend(laps[col].dropna().dt.total_seconds().tolist())
            
            if not sector_times:
                return 0
            
            # Simple dominance score based on percentile performance
            return np.percentile(sector_times, 25) / np.mean(sector_times)
        except:
            return 0
    
    def _calculate_tire_efficiency(self, laps):
        """Calculate tire management efficiency"""
        try:
            if 'Compound' not in laps.columns:
                return 0.5
            
            # Analyze lap time degradation by compound
            compounds = laps['Compound'].unique()
            efficiency_scores = []
            
            for compound in compounds:
                if pd.isna(compound):
                    continue
                    
                compound_laps = laps[laps['Compound'] == compound]
                if len(compound_laps) < 3:
                    continue
                
                lap_times = compound_laps['LapTime'].dt.total_seconds()
                lap_numbers = range(len(lap_times))
                
                # Calculate degradation rate
                if len(lap_times) > 1:
                    slope, _, r_value, _, _ = stats.linregress(lap_numbers, lap_times)
                    efficiency = max(0, 1 - abs(slope))  # Lower degradation = higher efficiency
                    efficiency_scores.append(efficiency)
            
            return np.mean(efficiency_scores) if efficiency_scores else 0.5
        except:
            return 0.5
    
    def create_performance_clustering(self, performance_df):
        """Create driver performance clusters using machine learning"""
        if performance_df.empty or len(performance_df) < 3:
            return None
        
        # Prepare data for clustering
        features = ['Consistency_Score', 'Speed_Consistency', 'Pace_Quality', 
                   'Overtake_Score', 'Sector_Dominance', 'Tire_Efficiency']
        
        X = performance_df[features].fillna(0)
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Perform clustering
        n_clusters = min(4, len(performance_df))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(X_scaled)
        
        performance_df['Cluster'] = clusters
        
        # Create visualization
        fig = go.Figure()
        
        cluster_names = ['Elite Performers', 'Consistent Drivers', 'Aggressive Racers', 'Developing Talent']
        colors = ['#FFD700', '#00D2BE', '#FF6B6B', '#4ECDC4']
        
        for i in range(n_clusters):
            cluster_data = performance_df[performance_df['Cluster'] == i]
            
            fig.add_trace(go.Scatter(
                x=cluster_data['Consistency_Score'],
                y=cluster_data['Pace_Quality'],
                mode='markers+text',
                text=cluster_data['Driver'],
                textposition='top center',
                marker=dict(
                    size=cluster_data['Performance_Index'] * 20,
                    color=colors[i],
                    line=dict(width=2, color='white'),
                    opacity=0.8
                ),
                name=cluster_names[i] if i < len(cluster_names) else f'Cluster {i+1}',
                hovertemplate='<b>%{text}</b><br>' +
                             'Consistency: %{x:.3f}<br>' +
                             'Pace Quality: %{y:.3f}<br>' +
                             'Performance Index: %{marker.size:.3f}<br>' +
                             '<extra></extra>'
            ))
        
        fig.update_layout(
            title='Driver Performance Clustering Analysis',
            xaxis_title='Consistency Score',
            yaxis_title='Pace Quality',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=600
        )
        
        return fig
    
    def create_performance_radar(self, performance_df):
        """Create radar chart for driver performance comparison"""
        if performance_df.empty:
            return None
        
        categories = ['Consistency', 'Speed Consistency', 'Pace Quality', 
                     'Overtaking', 'Sector Dominance', 'Tire Management']
        
        fig = go.Figure()
        
        for _, driver_data in performance_df.iterrows():
            team_color = TEAM_COLORS.get(driver_data['Team'], '#808080')
            
            values = [
                driver_data['Consistency_Score'],
                driver_data['Speed_Consistency'],
                driver_data['Pace_Quality'],
                driver_data['Overtake_Score'],
                driver_data['Sector_Dominance'],
                driver_data['Tire_Efficiency']
            ]
            
            fig.add_trace(go.Scatterpolar(
                r=values + [values[0]],  # Close the polygon
                theta=categories + [categories[0]],
                fill='toself',
                name=driver_data['Driver'],
                line=dict(color=team_color, width=3),
                fillcolor=team_color,
                opacity=0.3
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    gridcolor='rgba(255,255,255,0.2)'
                ),
                angularaxis=dict(
                    gridcolor='rgba(255,255,255,0.2)'
                )
            ),
            showlegend=True,
            title='Driver Performance Radar Comparison',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=600
        )
        
        return fig
    
    def analyze_race_pace_evolution(self, drivers):
        """Analyze how race pace evolves throughout the session"""
        pace_data = []
        
        for driver in drivers:
            try:
                driver_laps = self.laps.pick_drivers(driver)
                valid_laps = driver_laps[driver_laps['LapTime'].notna()]
                
                if len(valid_laps) < 5:
                    continue
                
                # Calculate rolling average pace (5-lap window)
                lap_times = valid_laps['LapTime'].dt.total_seconds()
                rolling_pace = lap_times.rolling(window=5, center=True).mean()
                
                for i, (_, lap) in enumerate(valid_laps.iterrows()):
                    if not pd.isna(rolling_pace.iloc[i]):
                        pace_data.append({
                            'Driver': driver,
                            'Lap': lap['LapNumber'],
                            'Pace': rolling_pace.iloc[i],
                            'Fuel_Load': 1 - (i / len(valid_laps)),  # Estimated fuel load
                            'Stint': self._get_stint_number(lap, valid_laps)
                        })
                        
            except Exception as e:
                continue
        
        return pd.DataFrame(pace_data)
    
    def _get_stint_number(self, lap, all_laps):
        """Determine stint number based on tire compound changes"""
        try:
            current_compound = lap['Compound']
            stint = 1
            
            for _, prev_lap in all_laps.iterrows():
                if prev_lap['LapNumber'] >= lap['LapNumber']:
                    break
                if prev_lap['Compound'] != current_compound:
                    stint += 1
                    current_compound = prev_lap['Compound']
            
            return stint
        except:
            return 1