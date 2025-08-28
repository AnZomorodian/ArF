#!/usr/bin/env python3
"""
FastAPI server for F1 data analysis
Provides REST API endpoints for the JavaScript frontend
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Union
import uvicorn
import json

# Import existing utility modules
from utils.data_loader import DataLoader
from utils.visualizations import create_telemetry_plot, create_tire_strategy_plot, create_race_progression_plot
from utils.track_dominance import create_track_dominance_map
from utils.constants import TEAM_COLORS, SESSIONS
from utils.formatters import format_lap_time
from utils.advanced_analytics import AdvancedF1Analytics
from utils.driver_manager import DynamicDriverManager

app = FastAPI(title="Track.lytix F1 API", version="1.0.0")

# Serve static files
app.mount("/static", StaticFiles(directory="."), name="static")

# Global data loader instance
data_loader = DataLoader()

# Pydantic models for request/response
class SessionRequest(BaseModel):
    year: int
    grand_prix: str
    session_type: str

class DriversRequest(BaseModel):
    drivers: List[str]

class TelemetryRequest(BaseModel):
    drivers: List[str]
    telemetry_type: str

class DriverInfo(BaseModel):
    code: str
    abbreviation: str
    team: str
    number: Optional[str] = None

class SessionResponse(BaseModel):
    success: bool
    session_info: Optional[dict] = None
    drivers: Optional[List[DriverInfo]] = None
    error: Optional[str] = None

class DataResponse(BaseModel):
    success: bool
    data: Optional[Union[dict, List[dict]]] = None
    error: Optional[str] = None

# Serve the main HTML file
@app.get("/")
async def read_root():
    return FileResponse('index.html')

@app.get("/style.css")
async def get_css():
    return FileResponse('style.css')

@app.get("/script.js")
async def get_js():
    return FileResponse('script.js')

@app.post("/api/load-session", response_model=SessionResponse)
async def load_session(request: SessionRequest):
    """Load F1 session data"""
    try:
        success = data_loader.load_session(
            request.year, 
            request.grand_prix, 
            request.session_type
        )
        
        if success and data_loader.session is not None:
            # Get driver information
            driver_manager = DynamicDriverManager(data_loader.session)
            driver_info = driver_manager.get_driver_info()
            
            drivers = []
            for code, info in driver_info.items():
                drivers.append(DriverInfo(
                    code=code,
                    abbreviation=info['abbreviation'],
                    team=info['team_name'],
                    number=str(info.get('driver_number', 'N/A'))
                ))
            
            session_info = {
                'year': request.year,
                'grand_prix': request.grand_prix,
                'session_type': request.session_type,
                'event_name': data_loader.session.event['EventName'],
                'circuit_name': data_loader.session.event['Location']
            }
            
            return SessionResponse(
                success=True,
                session_info=session_info,
                drivers=drivers
            )
        else:
            return SessionResponse(
                success=False,
                error="Failed to load session data"
            )
            
    except Exception as e:
        return SessionResponse(
            success=False,
            error=str(e)
        )

@app.post("/api/telemetry", response_model=DataResponse)
async def get_telemetry(request: TelemetryRequest):
    """Get telemetry data for drivers"""
    try:
        if not data_loader.session:
            raise HTTPException(status_code=400, detail="No session loaded")
        
        # Create telemetry plot data
        telemetry_data = []
        
        for driver in request.drivers:
            try:
                driver_laps = data_loader.session.laps.pick_drivers([driver])
                if driver_laps.empty:
                    continue
                    
                fastest_lap = driver_laps.pick_fastest()
                telemetry = fastest_lap.get_telemetry().add_distance()
                
                # Get team color
                driver_manager = DynamicDriverManager(data_loader.session)
                driver_info = driver_manager.get_driver_info()
                team_colors = driver_manager.get_team_colors()
                team_name = driver_info[driver]['team_name']
                color = team_colors.get(team_name, '#808080')
                
                telemetry_data.append({
                    'x': telemetry['Distance'].tolist(),
                    'y': telemetry[request.telemetry_type.title()].tolist(),
                    'name': f"{driver} ({team_name})",
                    'color': color
                })
                
            except Exception as e:
                print(f"Error processing driver {driver}: {e}")
                continue
        
        if not telemetry_data:
            return DataResponse(
                success=False,
                error="No telemetry data available for selected drivers"
            )
        
        # Set appropriate Y-axis title
        y_axis_titles = {
            'speed': 'Speed (km/h)',
            'throttle': 'Throttle (%)',
            'brake': 'Brake Pressure',
            'rpm': 'RPM',
            'gear': 'Gear'
        }
        
        return DataResponse(
            success=True,
            data=telemetry_data
        )
        
    except Exception as e:
        return DataResponse(
            success=False,
            error=str(e)
        )

@app.post("/api/track-map", response_model=DataResponse)
async def get_track_map(request: DriversRequest):
    """Get track dominance map data"""
    try:
        if not data_loader.session:
            raise HTTPException(status_code=400, detail="No session loaded")
        
        # Get track coordinates and dominance data
        # This is a simplified implementation
        # In a real implementation, you'd use the track_dominance module
        
        # Get position data for the fastest lap
        driver = request.drivers[0] if request.drivers else None
        if not driver:
            return DataResponse(
                success=False,
                error="No drivers selected"
            )
        
        try:
            driver_laps = data_loader.session.laps.pick_drivers([driver])
            fastest_lap = driver_laps.pick_fastest()
            car_data = fastest_lap.get_car_data().add_distance()
            position_data = car_data[['X', 'Y', 'Distance']].dropna()
            
            return DataResponse(
                success=True,
                data={
                    'x_coords': position_data['X'].tolist(),
                    'y_coords': position_data['Y'].tolist(),
                    'colors': ['red'] * len(position_data),
                    'hover_text': [f"Distance: {d:.0f}m" for d in position_data['Distance']]
                }
            )
            
        except Exception as e:
            return DataResponse(
                success=False,
                error=f"Unable to generate track map: {str(e)}"
            )
        
    except Exception as e:
        return DataResponse(
            success=False,
            error=str(e)
        )

@app.post("/api/lap-times", response_model=DataResponse)
async def get_lap_times(request: DriversRequest):
    """Get lap time comparison data"""
    try:
        if not data_loader.session:
            raise HTTPException(status_code=400, detail="No session loaded")
        
        lap_data = []
        
        for driver in request.drivers:
            try:
                driver_laps = data_loader.session.laps.pick_drivers([driver]).pick_quicklaps()
                if not driver_laps.empty:
                    best_lap = driver_laps.pick_fastest()
                    lap_time = best_lap['LapTime']
                    if hasattr(lap_time, 'total_seconds'):
                        lap_time = lap_time.total_seconds()
                    else:
                        lap_time = float(lap_time)
                    
                    lap_data.append({
                        'Driver': driver,
                        'Best Lap Time': format_lap_time(lap_time),
                        'Lap Number': int(best_lap['LapNumber']) if best_lap['LapNumber'] is not None else 0,
                        'Compound': str(best_lap['Compound']) if best_lap['Compound'] is not None else 'Unknown'
                    })
                    
            except Exception as e:
                print(f"Error processing lap times for {driver}: {e}")
                continue
        
        return DataResponse(
            success=True,
            data=lap_data
        )
        
    except Exception as e:
        return DataResponse(
            success=False,
            error=str(e)
        )

@app.post("/api/tire-strategy", response_model=DataResponse)
async def get_tire_strategy(request: DriversRequest):
    """Get tire strategy data"""
    try:
        if not data_loader.session:
            raise HTTPException(status_code=400, detail="No session loaded")
        
        # Simplified tire strategy data
        strategy_data = []
        
        for i, driver in enumerate(request.drivers):
            try:
                driver_laps = data_loader.session.laps.pick_drivers([driver])
                if not driver_laps.empty:
                    compounds = driver_laps['Compound'].dropna().unique()
                    
                    for compound in compounds:
                        compound_laps = driver_laps[driver_laps['Compound'] == compound]
                        if not compound_laps.empty:
                            strategy_data.append({
                                'x': compound_laps['LapNumber'].tolist(),
                                'y': [i] * len(compound_laps),
                                'name': f"{driver} - {compound}",
                                'type': 'scatter',
                                'mode': 'markers',
                                'marker': {
                                    'size': 8,
                                    'color': {'SOFT': 'red', 'MEDIUM': 'yellow', 'HARD': 'white'}.get(compound, 'blue')
                                }
                            })
                            
            except Exception as e:
                print(f"Error processing tire strategy for {driver}: {e}")
                continue
        
        return DataResponse(
            success=True,
            data=strategy_data
        )
        
    except Exception as e:
        return DataResponse(
            success=False,
            error=str(e)
        )

@app.post("/api/race-progress", response_model=DataResponse)
async def get_race_progress(request: DriversRequest):
    """Get race progression data"""
    try:
        if not data_loader.session:
            raise HTTPException(status_code=400, detail="No session loaded")
        
        progress_data = []
        
        for driver in request.drivers:
            try:
                driver_laps = data_loader.session.laps.pick_drivers([driver])
                if not driver_laps.empty:
                    # Get team color
                    driver_manager = DynamicDriverManager(data_loader.session)
                    driver_info = driver_manager.get_driver_info()
                    team_colors = driver_manager.get_team_colors()
                    team_name = driver_info[driver]['team_name']
                    color = team_colors.get(team_name, '#808080')
                    
                    progress_data.append({
                        'x': driver_laps['LapNumber'].tolist(),
                        'y': driver_laps['Position'].tolist(),
                        'name': f"{driver} ({team_name})",
                        'type': 'scatter',
                        'mode': 'lines+markers',
                        'line': {'color': color, 'width': 3},
                        'marker': {'size': 6}
                    })
                    
            except Exception as e:
                print(f"Error processing race progress for {driver}: {e}")
                continue
        
        return DataResponse(
            success=True,
            data=progress_data
        )
        
    except Exception as e:
        return DataResponse(
            success=False,
            error=str(e)
        )

@app.post("/api/analytics", response_model=DataResponse)
async def get_analytics(request: DriversRequest):
    """Get advanced analytics data"""
    try:
        if not data_loader.session:
            raise HTTPException(status_code=400, detail="No session loaded")
        
        analytics = AdvancedF1Analytics(data_loader.session)
        analytics_data = []
        
        for driver in request.drivers:
            try:
                consistency = analytics.calculate_driver_consistency(driver)
                if consistency:
                    analytics_data.append({
                        'driver': driver,
                        'consistency_score': f"{consistency['consistency_score']:.3f}",
                        'fastest_lap': format_lap_time(consistency['fastest_lap']),
                        'mean_lap_time': format_lap_time(consistency['mean_lap_time']),
                        'total_laps': consistency['total_laps']
                    })
                    
            except Exception as e:
                print(f"Error processing analytics for {driver}: {e}")
                continue
        
        return DataResponse(
            success=True,
            data=analytics_data
        )
        
    except Exception as e:
        return DataResponse(
            success=False,
            error=str(e)
        )

if __name__ == "__main__":
    print("🏎️  Track.lytix F1 Analytics API Server")
    print("=" * 50)
    print("🚀 Starting server on http://0.0.0.0:5000")
    print("📊 Access the web interface at http://localhost:5000")
    print("🔧 API docs available at http://localhost:5000/docs")
    print("=" * 50)
    
    uvicorn.run(
        "api_server:app", 
        host="0.0.0.0", 
        port=5000,
        reload=True
    )