"""
Formatting utilities for F1 data display
"""

import pandas as pd
import numpy as np
from datetime import timedelta

def format_lap_time(lap_time):
    """Format lap time to M:SS.mmm format"""
    if pd.isna(lap_time):
        return "N/A"
    
    if isinstance(lap_time, str):
        return lap_time
    
    if isinstance(lap_time, timedelta):
        total_seconds = lap_time.total_seconds()
    else:
        total_seconds = float(lap_time)
    
    if total_seconds <= 0:
        return "N/A"
    
    minutes = int(total_seconds // 60)
    seconds = total_seconds % 60
    
    return f"{minutes}:{seconds:06.3f}"

def format_sector_time(sector_time):
    """Format sector time to SS.mmm format"""
    if pd.isna(sector_time):
        return "N/A"
    
    if isinstance(sector_time, timedelta):
        total_seconds = sector_time.total_seconds()
    else:
        total_seconds = float(sector_time)
    
    if total_seconds <= 0:
        return "N/A"
    
    return f"{total_seconds:06.3f}"

def get_lap_time_color_class(position):
    """Get CSS class for lap time based on position"""
    if position == 1:
        return "fastest-lap"
    elif position == 2:
        return "second-lap"
    elif position == 3:
        return "third-lap"
    else:
        return ""

def format_gap_time(gap_seconds):
    """Format gap time between drivers"""
    if pd.isna(gap_seconds) or gap_seconds == 0:
        return "0.000"
    
    if gap_seconds >= 60:
        minutes = int(gap_seconds // 60)
        seconds = gap_seconds % 60
        return f"+{minutes}:{seconds:06.3f}"
    else:
        return f"+{gap_seconds:.3f}"

def get_position_change_text(start_pos, end_pos):
    """Get formatted text for position changes"""
    change = start_pos - end_pos
    if change > 0:
        return f"📈 +{change}", "success"
    elif change < 0:
        return f"📉 {change}", "error"
    else:
        return "➡️ 0", "info"

def format_tire_age(tire_life):
    """Format tire age display"""
    if pd.isna(tire_life) or tire_life == 0:
        return "New"
    else:
        return f"{int(tire_life)} laps"