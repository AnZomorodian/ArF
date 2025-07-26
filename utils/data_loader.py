"""
Data loading utilities for F1 analysis platform
"""

import fastf1
import pandas as pd
import numpy as np
import os
import tempfile
from datetime import datetime
import streamlit as st
from .constants import DRIVER_TEAMS, CIRCUIT_ALIASES

class DataLoader:
    def __init__(self):
        self.session = None
        self.session_info = {}
        self._setup_cache()
        
    def _setup_cache(self):
        """Setup FastF1 caching"""
        try:
            # Use system temp directory for cache
            cache_dir = os.path.join(tempfile.gettempdir(), 'fastf1_cache')
            os.makedirs(cache_dir, exist_ok=True)
            fastf1.Cache.enable_cache(cache_dir)
        except Exception as e:
            st.warning(f"Could not setup cache: {e}")
    
    def load_session(self, year, grand_prix, session_type):
        """Load F1 session data"""
        try:
            self.session = fastf1.get_session(year, grand_prix, session_type)
            self.session.load()
            
            # Store session info
            self.session_info = {
                'year': year,
                'event_name': grand_prix,
                'session_name': session_type,
                'date': self.session.date.strftime('%Y-%m-%d') if hasattr(self.session, 'date') and self.session.date else 'Unknown',
                'circuit': CIRCUIT_ALIASES.get(self.session.event['EventName'], self.session.event['EventName']) if hasattr(self.session, 'event') else 'Unknown'
            }
            
            return True
            
        except Exception as e:
            st.error(f"Failed to load session: {str(e)}")
            return False
    
    def get_session_info(self):
        """Get current session information"""
        return self.session_info if hasattr(self, 'session_info') else None
    
    def get_available_drivers(self):
        """Get list of available drivers in current session"""
        if self.session is None:
            return []
        
        try:
            if hasattr(self.session, 'results') and not self.session.results.empty:
                return sorted(self.session.results['Abbreviation'].tolist())
            elif hasattr(self.session, 'laps') and not self.session.laps.empty:
                return sorted(self.session.laps['Driver'].unique().tolist())
            else:
                return []
        except Exception as e:
            st.error(f"Error getting drivers: {str(e)}")
            return []
    
    def get_driver_telemetry(self, driver, lap_type='fastest'):
        """Get telemetry data for a specific driver"""
        if self.session is None:
            return None
        
        try:
            driver_laps = self.session.laps.pick_drivers(driver)
            if driver_laps.empty:
                return None
            
            if lap_type == 'fastest':
                lap = driver_laps.pick_fastest()
            else:
                lap = driver_laps.iloc[0]  # First lap as default
            
            if lap is None or pd.isna(lap.name):
                return None
                
            telemetry = lap.get_telemetry()
            return telemetry
            
        except Exception as e:
            st.error(f"Error getting telemetry for {driver}: {str(e)}")
            return None
    
    def get_lap_comparison(self, drivers):
        """Get lap time comparison data for selected drivers"""
        if self.session is None:
            return None
        
        try:
            lap_data = []
            
            for driver in drivers:
                driver_laps = self.session.laps.pick_drivers(driver)
                if driver_laps.empty:
                    continue
                    
                for _, lap in driver_laps.iterrows():
                    if pd.notna(lap['LapTime']) and lap['LapTime'].total_seconds() > 0:
                        lap_data.append({
                            'Driver': driver,
                            'LapNumber': lap['LapNumber'],
                            'LapTime': str(lap['LapTime']).split('.')[0],  # Remove microseconds
                            'LapTime_seconds': lap['LapTime'].total_seconds(),
                            'Compound': lap.get('Compound', 'Unknown'),
                            'TyreLife': lap.get('TyreLife', 0),
                            'Sector1Time': lap.get('Sector1Time', pd.NaT),
                            'Sector2Time': lap.get('Sector2Time', pd.NaT),
                            'Sector3Time': lap.get('Sector3Time', pd.NaT)
                        })
            
            if lap_data:
                return pd.DataFrame(lap_data)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            st.error(f"Error getting lap comparison: {str(e)}")
            return None
    
    def get_tire_data(self, drivers):
        """Get tire strategy data for selected drivers"""
        if self.session is None:
            return None
        
        try:
            tire_data = []
            
            for driver in drivers:
                driver_laps = self.session.laps.pick_drivers(driver)
                if driver_laps.empty:
                    continue
                    
                for _, lap in driver_laps.iterrows():
                    if pd.notna(lap['LapTime']):
                        tire_data.append({
                            'Driver': driver,
                            'LapNumber': lap['LapNumber'],
                            'Compound': lap.get('Compound', 'Unknown'),
                            'TyreLife': lap.get('TyreLife', 0),
                            'LapTime_seconds': lap['LapTime'].total_seconds() if pd.notna(lap['LapTime']) else None
                        })
            
            if tire_data:
                return pd.DataFrame(tire_data)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            st.error(f"Error getting tire data: {str(e)}")
            return None
    
    def get_position_data(self, drivers):
        """Get position data for race progression analysis"""
        if self.session is None:
            return None
        
        try:
            position_data = []
            
            for driver in drivers:
                driver_laps = self.session.laps.pick_drivers(driver)
                if driver_laps.empty:
                    continue
                    
                for _, lap in driver_laps.iterrows():
                    if pd.notna(lap.get('Position')):
                        position_data.append({
                            'Driver': driver,
                            'LapNumber': lap['LapNumber'],
                            'Position': lap['Position'],
                            'LapTime_seconds': lap['LapTime'].total_seconds() if pd.notna(lap['LapTime']) else None
                        })
            
            if position_data:
                return pd.DataFrame(position_data)
            else:
                return pd.DataFrame()
                
        except Exception as e:
            st.error(f"Error getting position data: {str(e)}")
            return None
    
    def get_fastest_lap_telemetry(self, drivers):
        """Get fastest lap telemetry for multiple drivers"""
        if self.session is None:
            return {}
        
        telemetry_data = {}
        
        for driver in drivers:
            telemetry = self.get_driver_telemetry(driver, 'fastest')
            if telemetry is not None and not telemetry.empty:
                telemetry_data[driver] = telemetry
        
        return telemetry_data
    
    def get_session_results(self):
        """Get session results if available"""
        if self.session is None:
            return None
            
        try:
            if hasattr(self.session, 'results') and not self.session.results.empty:
                return self.session.results
            else:
                return None
        except Exception as e:
            st.error(f"Error getting session results: {str(e)}")
            return None
    
    def get_laps_data(self):
        """Get all laps data from current session"""
        if self.session is None:
            return None
            
        try:
            return self.session.laps
        except Exception as e:
            st.error(f"Error getting laps data: {str(e)}")
            return None
