"""
Dynamic Driver Management Module
Fetches current driver-team mappings from FastF1 session data
"""

import pandas as pd


class DynamicDriverManager:
    """Manages driver information dynamically from session data"""
    
    def __init__(self, session):
        self.session = session
        self._driver_info = None
        self._team_mappings = None
        
    def get_driver_info(self):
        """Get comprehensive driver information from session"""
        if self._driver_info is None:
            self._driver_info = {}
            
            try:
                # Get driver info from session
                drivers = self.session.drivers
                
                for driver_code in drivers:
                    driver_data = self.session.get_driver(driver_code)
                    
                    if driver_data is not None:
                        self._driver_info[driver_code] = {
                            'full_name': f"{driver_data.get('FirstName', '')} {driver_data.get('LastName', '')}".strip(),
                            'abbreviation': driver_data.get('Abbreviation', driver_code),
                            'team_name': driver_data.get('TeamName', 'Unknown'),
                            'team_color': driver_data.get('TeamColor', '#808080'),
                            'driver_number': driver_data.get('DriverNumber', ''),
                            'country_code': driver_data.get('CountryCode', ''),
                            'broadcast_name': driver_data.get('BroadcastName', driver_code)
                        }
                        
            except Exception as e:
                print(f"Error fetching driver info: {e}")
                
        return self._driver_info
    
    def get_team_mappings(self):
        """Get current driver-team mappings for this session"""
        if self._team_mappings is None:
            driver_info = self.get_driver_info()
            self._team_mappings = {}
            
            for driver_code, info in driver_info.items():
                self._team_mappings[driver_code] = info['team_name']
                
        return self._team_mappings
    
    def get_team_colors(self):
        """Get team colors from session data"""
        driver_info = self.get_driver_info()
        team_colors = {}
        
        for driver_code, info in driver_info.items():
            team_name = info['team_name']
            if team_name not in team_colors:
                # Convert hex color if it starts with #
                color = info['team_color']
                if color and not color.startswith('#'):
                    color = f"#{color}"
                team_colors[team_name] = color or '#808080'
                
        return team_colors
    
    def get_driver_display_names(self):
        """Get formatted driver names for display"""
        driver_info = self.get_driver_info()
        display_names = {}
        
        for driver_code, info in driver_info.items():
            # Use abbreviation if available, otherwise use the driver code
            display_name = info.get('abbreviation', driver_code)
            display_names[driver_code] = display_name
            
        return display_names
    
    def get_drivers_by_team(self):
        """Group drivers by their teams"""
        driver_info = self.get_driver_info()
        teams = {}
        
        for driver_code, info in driver_info.items():
            team_name = info['team_name']
            if team_name not in teams:
                teams[team_name] = []
            teams[team_name].append({
                'code': driver_code,
                'name': info.get('abbreviation', driver_code),
                'full_name': info.get('full_name', driver_code),
                'number': info.get('driver_number', '')
            })
            
        return teams