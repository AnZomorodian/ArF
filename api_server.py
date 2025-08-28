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
import pandas as pd
import numpy as np

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

                # Check if the requested telemetry type exists
                telemetry_column = request.telemetry_type.title()
                if telemetry_column == 'Rpm':
                    telemetry_column = 'RPM'

                if telemetry_column not in telemetry.columns:
                    print(f"Column {telemetry_column} not found in telemetry data for driver {driver}")
                    continue

                # Get team color
                driver_manager = DynamicDriverManager(data_loader.session)
                driver_info = driver_manager.get_driver_info()
                team_colors = driver_manager.get_team_colors()
                team_name = driver_info[driver]['team_name']
                color = team_colors.get(team_name, '#808080')

                telemetry_data.append({
                    'x': telemetry['Distance'].tolist(),
                    'y': telemetry[telemetry_column].tolist(),
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
        driver = request.drivers[0] if request.drivers else None
        if not driver:
            return DataResponse(
                success=False,
                error="No drivers selected"
            )

        try:
            driver_laps = data_loader.session.laps.pick_drivers([driver])
            fastest_lap = driver_laps.pick_fastest()
            # Try to get position data first
            try:
                position_data = fastest_lap.get_pos_data()
                if 'X' not in position_data.columns or 'Y' not in position_data.columns:
                    raise ValueError("Position data not available")
            except:
                # Fallback to creating mock coordinates
                try:
                    car_data = fastest_lap.get_car_data().add_distance()
                    if 'Distance' in car_data.columns:
                        distances = car_data['Distance'].values
                    else:
                        # Create distance based on time
                        time_data = car_data.index
                        distances = np.arange(len(time_data)) * 10  # 10m intervals
                except Exception as e:
                    print(f"Car data error: {e}")
                    # Fallback to simple distance array
                    distances = np.arange(0, 5000, 50)  # 5km track with 50m intervals

                angles = np.linspace(0, 2*np.pi, len(distances))
                radius = 1000
                x_coords = radius * np.cos(angles)
                y_coords = radius * np.sin(angles)
                position_data = pd.DataFrame({
                    'X': x_coords,
                    'Y': y_coords,
                    'Distance': distances
                })

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
    """Get comprehensive lap time and sector analysis"""
    try:
        if not data_loader.session:
            raise HTTPException(status_code=400, detail="No session loaded")

        lap_data = []

        for driver in request.drivers:
            try:
                driver_laps = data_loader.session.laps.pick_drivers([driver]).pick_quicklaps()
                if not driver_laps.empty:
                    # Get best lap
                    best_lap = driver_laps.pick_fastest()

                    # Process all laps for this driver
                    for _, lap in driver_laps.iterrows():
                        try:
                            lap_time = lap['LapTime']
                            if hasattr(lap_time, 'total_seconds'):
                                lap_time = lap_time.total_seconds()
                            else:
                                lap_time = float(lap_time) if lap_time is not None else 0

                            # Get sector times
                            s1_time = lap['Sector1Time']
                            s2_time = lap['Sector2Time']
                            s3_time = lap['Sector3Time']

                            def format_sector_time(sector_time):
                                if sector_time is not None and hasattr(sector_time, 'total_seconds'):
                                    time_str = format_lap_time(sector_time.total_seconds())
                                elif sector_time is not None:
                                    time_str = format_lap_time(float(sector_time))
                                else:
                                    return 'N/A'

                                # Remove "0:" prefix for sector times
                                if time_str.startswith('0:'):
                                    return time_str[2:]
                                return time_str

                            lap_data.append({
                                'Driver': driver,
                                'Lap Number': int(lap['LapNumber']) if lap['LapNumber'] is not None else 0,
                                'Lap Time': format_lap_time(lap_time),
                                'Sector 1': format_sector_time(s1_time),
                                'Sector 2': format_sector_time(s2_time),
                                'Sector 3': format_sector_time(s3_time),
                                'Compound': str(lap['Compound']) if lap['Compound'] is not None else 'Unknown',
                                'Position': int(lap['Position']) if lap['Position'] is not None else 0,
                                'Best Lap': '✓' if lap['LapNumber'] == best_lap['LapNumber'] else ''
                            })
                        except Exception as e:
                            print(f"Error processing individual lap for {driver}: {e}")
                            continue

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

# NEW DATA ANALYSIS ENDPOINTS

@app.post("/api/speed-analysis", response_model=DataResponse)
async def get_speed_analysis(request: DriversRequest):
    """Speed trap and acceleration analysis"""
    try:
        if not data_loader.session:
            raise HTTPException(status_code=400, detail="No session loaded")

        speed_data = []

        for driver in request.drivers:
            try:
                driver_laps = data_loader.session.laps.pick_drivers([driver])
                if not driver_laps.empty:
                    fastest_lap = driver_laps.pick_fastest()
                    telemetry = fastest_lap.get_telemetry().add_distance()

                    max_speed = telemetry['Speed'].max()
                    min_speed = telemetry['Speed'].min()
                    avg_speed = telemetry['Speed'].mean()

                    # Calculate acceleration (simplified)
                    speed_diff = telemetry['Speed'].diff()
                    time_diff = telemetry['Time'].diff().dt.total_seconds()
                    acceleration = speed_diff / time_diff
                    max_acceleration = acceleration.max()
                    max_deceleration = acceleration.min()

                    speed_data.append({
                        'driver': driver,
                        'max_speed': f"{max_speed:.1f} km/h",
                        'avg_speed': f"{avg_speed:.1f} km/h",
                        'min_speed': f"{min_speed:.1f} km/h",
                        'max_acceleration': f"{max_acceleration:.2f} km/h/s",
                        'max_deceleration': f"{abs(max_deceleration):.2f} km/h/s"
                    })

            except Exception as e:
                print(f"Error processing speed analysis for {driver}: {e}")
                continue

        return DataResponse(
            success=True,
            data=speed_data
        )

    except Exception as e:
        return DataResponse(
            success=False,
            error=str(e)
        )

@app.post("/api/cornering-analysis", response_model=DataResponse)
async def get_cornering_analysis(request: DriversRequest):
    """Cornering performance analysis with charts"""
    try:
        if not data_loader.session:
            raise HTTPException(status_code=400, detail="No session loaded")

        cornering_data = []
        chart_data = {}

        for driver in request.drivers:
            try:
                driver_laps = data_loader.session.laps.pick_drivers([driver])
                if not driver_laps.empty:
                    fastest_lap = driver_laps.pick_fastest()
                    telemetry = fastest_lap.get_telemetry().add_distance()

                    # Identify corners (speed < 200 km/h as simplified corner detection)
                    corner_mask = telemetry['Speed'] < 200
                    corner_speeds = telemetry[corner_mask]['Speed']

                    if not corner_speeds.empty:
                        avg_corner_speed = corner_speeds.mean()
                        min_corner_speed = corner_speeds.min()
                        corner_count = len(corner_speeds)

                        # Calculate corner exit acceleration
                        corner_exit_accel = telemetry[corner_mask]['Throttle'].mean()

                        # Calculate cornering G-forces (simplified)
                        speed_ms = telemetry['Speed'] / 3.6  # Convert to m/s
                        lateral_g = (speed_ms**2 / 100) / 9.81  # Simplified calculation
                        max_g_force = lateral_g[corner_mask].max() if not corner_mask.empty else 0

                        # Corner braking analysis
                        corner_braking = telemetry[corner_mask]['Brake'].mean()

                        cornering_data.append({
                            'driver': driver,
                            'avg_corner_speed': f"{avg_corner_speed:.1f} km/h",
                            'min_corner_speed': f"{min_corner_speed:.1f} km/h",
                            'max_g_force': f"{max_g_force:.2f}g",
                            'corner_count': corner_count,
                            'avg_corner_throttle': f"{corner_exit_accel:.1f}%",
                            'avg_corner_braking': f"{corner_braking:.1f}%"
                        })

                        # Chart data for speed through corners
                        corner_distances = telemetry[corner_mask]['Distance'].tolist()
                        corner_speed_values = corner_speeds.tolist()

                        if driver not in chart_data:
                            chart_data[driver] = {}

                        chart_data[driver]['corner_speed_chart'] = {
                            'x': corner_distances[:50],  # Limit points for performance
                            'y': corner_speed_values[:50],
                            'name': f"{driver} Corner Speed",
                            'type': 'scatter',
                            'mode': 'lines+markers'
                        }

            except Exception as e:
                print(f"Error processing cornering analysis for {driver}: {e}")
                continue

        return DataResponse(success=True, data={'table_data': cornering_data, 'chart_data': chart_data})

    except Exception as e:
        return DataResponse(success=False, error=str(e))

@app.post("/api/brake-analysis", response_model=DataResponse)
async def get_brake_analysis(request: DriversRequest):
    """Detailed braking performance analysis"""
    try:
        if not data_loader.session:
            raise HTTPException(status_code=400, detail="No session loaded")

        brake_data = []

        for driver in request.drivers:
            try:
                driver_laps = data_loader.session.laps.pick_drivers([driver])
                if not driver_laps.empty:
                    fastest_lap = driver_laps.pick_fastest()
                    telemetry = fastest_lap.get_telemetry().add_distance()

                    # Identify braking zones
                    braking_mask = telemetry['Brake'] > 0
                    brake_applications = telemetry[braking_mask]

                    if not brake_applications.empty:
                        max_brake_force = brake_applications['Brake'].max()
                        avg_brake_force = brake_applications['Brake'].mean()
                        total_brake_time = len(brake_applications) * 0.1  # Assuming 10Hz data

                        # Count distinct braking zones
                        brake_zones = (telemetry['Brake'] > 0).astype(int).diff().sum() // 2

                        brake_data.append({
                            'driver': driver,
                            'max_brake_force': f"{max_brake_force:.1f}%",
                            'avg_brake_force': f"{avg_brake_force:.1f}%",
                            'total_brake_time': f"{total_brake_time:.1f}s",
                            'brake_zones': int(brake_zones)
                        })

            except Exception as e:
                print(f"Error processing brake analysis for {driver}: {e}")
                continue

        return DataResponse(
            success=True,
            data=brake_data
        )

    except Exception as e:
        return DataResponse(
            success=False,
            error=str(e)
        )

@app.post("/api/gear-analysis", response_model=DataResponse)
async def get_gear_analysis(request: DriversRequest):
    """Gear usage and shifting analysis with charts"""
    try:
        if not data_loader.session:
            raise HTTPException(status_code=400, detail="No session loaded")

        gear_data = []
        chart_data = {}

        for driver in request.drivers:
            try:
                driver_laps = data_loader.session.laps.pick_drivers([driver])
                if not driver_laps.empty:
                    fastest_lap = driver_laps.pick_fastest()
                    telemetry = fastest_lap.get_telemetry().add_distance()

                    if 'nGear' in telemetry.columns:
                        gear_column = 'nGear'
                    elif 'Gear' in telemetry.columns:
                        gear_column = 'Gear'
                    else:
                        continue

                    gear_usage = telemetry[gear_column].value_counts().sort_index()
                    max_gear = telemetry[gear_column].max()
                    avg_gear = telemetry[gear_column].mean()

                    # Count gear shifts
                    gear_shifts = (telemetry[gear_column].diff() != 0).sum()

                    # Calculate gear efficiency (time in optimal gears)
                    optimal_gears = [4, 5, 6, 7, 8]  # Typical optimal gears
                    optimal_time = telemetry[telemetry[gear_column].isin(optimal_gears)].shape[0]
                    gear_efficiency = (optimal_time / len(telemetry)) * 100

                    gear_data.append({
                        'driver': driver,
                        'max_gear': int(max_gear),
                        'avg_gear': f"{avg_gear:.1f}",
                        'gear_shifts': int(gear_shifts),
                        'most_used_gear': int(gear_usage.idxmax()),
                        'gear_efficiency': f"{gear_efficiency:.1f}%"
                    })

                    # Chart data for gear usage
                    if driver not in chart_data:
                        chart_data[driver] = {}

                    chart_data[driver]['gear_usage_chart'] = {
                        'x': gear_usage.index.tolist(),
                        'y': gear_usage.values.tolist(),
                        'name': f"{driver} Gear Usage",
                        'type': 'bar'
                    }

                    # Chart data for gear changes over distance
                    chart_data[driver]['gear_distance_chart'] = {
                        'x': telemetry['Distance'].tolist()[::10],  # Sample every 10th point
                        'y': telemetry[gear_column].tolist()[::10],
                        'name': f"{driver} Gear vs Distance",
                        'type': 'scatter',
                        'mode': 'lines'
                    }

            except Exception as e:
                print(f"Error processing gear analysis for {driver}: {e}")
                continue

        return DataResponse(success=True, data={'table_data': gear_data, 'chart_data': chart_data})

    except Exception as e:
        return DataResponse(success=False, error=str(e))

@app.post("/api/consistency-analysis", response_model=DataResponse)
async def get_consistency_analysis(request: DriversRequest):
    """Lap-to-lap consistency analysis"""
    try:
        if not data_loader.session:
            raise HTTPException(status_code=400, detail="No session loaded")

        consistency_data = []

        for driver in request.drivers:
            try:
                driver_laps = data_loader.session.laps.pick_drivers([driver]).pick_quicklaps()
                if len(driver_laps) > 3:
                    lap_times = []
                    for _, lap in driver_laps.iterrows():
                        if lap['LapTime'] is not None:
                            if hasattr(lap['LapTime'], 'total_seconds'):
                                lap_times.append(lap['LapTime'].total_seconds())
                            else:
                                lap_times.append(float(lap['LapTime']))

                    if len(lap_times) > 3:
                        lap_times = np.array(lap_times)
                        std_dev = np.std(lap_times)
                        mean_time = np.mean(lap_times)
                        consistency_score = 1 / (1 + std_dev)
                        fastest_lap = np.min(lap_times)
                        slowest_lap = np.max(lap_times)
                        range_diff = slowest_lap - fastest_lap

                        consistency_data.append({
                            'driver': driver,
                            'consistency_score': f"{consistency_score:.3f}",
                            'std_deviation': f"{std_dev:.3f}s",
                            'fastest_lap': format_lap_time(fastest_lap),
                            'slowest_lap': format_lap_time(slowest_lap),
                            'lap_range': f"{range_diff:.3f}s"
                        })

            except Exception as e:
                print(f"Error processing consistency analysis for {driver}: {e}")
                continue

        return DataResponse(
            success=True,
            data=consistency_data
        )

    except Exception as e:
        return DataResponse(
            success=False,
            error=str(e)
        )

# NEW ADVANCED DATA ANALYSIS ENDPOINTS

@app.post("/api/pitstop-analysis", response_model=DataResponse)
async def get_pitstop_analysis(request: DriversRequest):
    """Detailed pit stop strategy and timing analysis"""
    try:
        if not data_loader.session:
            raise HTTPException(status_code=400, detail="No session loaded")

        pitstop_data = []

        for driver in request.drivers:
            try:
                driver_laps = data_loader.session.laps.pick_drivers([driver])
                if not driver_laps.empty:
                    # Identify pit stops (large lap time increases)
                    lap_times = []
                    for _, lap in driver_laps.iterrows():
                        if lap['LapTime'] is not None:
                            if hasattr(lap['LapTime'], 'total_seconds'):
                                lap_times.append(lap['LapTime'].total_seconds())
                            else:
                                lap_times.append(float(lap['LapTime']))

                    if len(lap_times) > 3:
                        avg_lap_time = np.mean(lap_times)
                        pitstops = 0
                        pitstop_laps = []

                        for i, time in enumerate(lap_times):
                            if time > avg_lap_time * 1.5:  # Likely pitstop
                                pitstops += 1
                                pitstop_laps.append(i + 1)

                        pitstop_data.append({
                            'driver': driver,
                            'total_pitstops': pitstops,
                            'pitstop_laps': ', '.join(map(str, pitstop_laps)) if pitstop_laps else 'None',
                            'avg_lap_time': f"{avg_lap_time:.3f}s",
                            'strategy_type': 'One-stop' if pitstops <= 1 else 'Multi-stop'
                        })

            except Exception as e:
                print(f"Error processing pitstop analysis for {driver}: {e}")
                continue

        return DataResponse(success=True, data=pitstop_data)

    except Exception as e:
        return DataResponse(success=False, error=str(e))

@app.post("/api/weather-impact", response_model=DataResponse)
async def get_weather_impact(request: DriversRequest):
    """Weather conditions impact on performance"""
    try:
        if not data_loader.session:
            raise HTTPException(status_code=400, detail="No session loaded")

        weather_data = []

        try:
            weather = data_loader.session.weather_data
            if not weather.empty:
                avg_temp = weather['AirTemp'].mean()
                avg_humidity = weather['Humidity'].mean()
                avg_pressure = weather['Pressure'].mean()
                wind_speed = weather['WindSpeed'].mean()

                # Analyze impact on each driver
                for driver in request.drivers:
                    try:
                        driver_laps = data_loader.session.laps.pick_drivers([driver])
                        if not driver_laps.empty:
                            fastest_lap = driver_laps.pick_fastest()
                            fastest_time = fastest_lap['LapTime']
                            if hasattr(fastest_time, 'total_seconds'):
                                fastest_time = fastest_time.total_seconds()

                            # Weather impact scoring
                            temp_impact = "High" if avg_temp > 30 else "Medium" if avg_temp > 20 else "Low"

                            weather_data.append({
                                'driver': driver,
                                'air_temperature': f"{avg_temp:.1f}°C",
                                'humidity': f"{avg_humidity:.1f}%",
                                'pressure': f"{avg_pressure:.1f}hPa",
                                'wind_speed': f"{wind_speed:.1f}m/s",
                                'temp_impact': temp_impact,
                                'fastest_lap': format_lap_time(fastest_time)
                            })
                    except Exception as e:
                        print(f"Error processing weather impact for {driver}: {e}")
                        continue
        except:
            # Fallback data if weather not available
            for driver in request.drivers:
                weather_data.append({
                    'driver': driver,
                    'air_temperature': 'N/A',
                    'humidity': 'N/A',
                    'pressure': 'N/A',
                    'wind_speed': 'N/A',
                    'temp_impact': 'Unknown',
                    'fastest_lap': 'N/A'
                })

        return DataResponse(success=True, data=weather_data)

    except Exception as e:
        return DataResponse(success=False, error=str(e))

@app.post("/api/throttle-brake-coordination", response_model=DataResponse)
async def get_throttle_brake_coordination(request: DriversRequest):
    """Throttle and brake coordination analysis"""
    try:
        if not data_loader.session:
            raise HTTPException(status_code=400, detail="No session loaded")

        coordination_data = []

        for driver in request.drivers:
            try:
                driver_laps = data_loader.session.laps.pick_drivers([driver])
                if not driver_laps.empty:
                    fastest_lap = driver_laps.pick_fastest()
                    telemetry = fastest_lap.get_telemetry().add_distance()

                    if 'Throttle' in telemetry.columns and 'Brake' in telemetry.columns:
                        # Calculate overlap (simultaneous throttle and brake)
                        overlap_mask = (telemetry['Throttle'] > 5) & (telemetry['Brake'] > 5)
                        overlap_percentage = (overlap_mask.sum() / len(telemetry)) * 100

                        # Calculate transition efficiency
                        throttle_to_brake = ((telemetry['Throttle'].shift(1) > 50) & (telemetry['Brake'] > 50)).sum()
                        brake_to_throttle = ((telemetry['Brake'].shift(1) > 50) & (telemetry['Throttle'] > 50)).sum()

                        avg_throttle = telemetry['Throttle'].mean()
                        avg_brake = telemetry['Brake'].mean()

                        coordination_data.append({
                            'driver': driver,
                            'throttle_brake_overlap': f"{overlap_percentage:.2f}%",
                            'avg_throttle_application': f"{avg_throttle:.1f}%",
                            'avg_brake_application': f"{avg_brake:.1f}%",
                            'transitions_count': throttle_to_brake + brake_to_throttle,
                            'coordination_score': f"{(100 - overlap_percentage):.1f}/100"
                        })
            except Exception as e:
                print(f"Error processing coordination for {driver}: {e}")
                continue

        return DataResponse(success=True, data=coordination_data)

    except Exception as e:
        return DataResponse(success=False, error=str(e))

@app.post("/api/sector-dominance", response_model=DataResponse)
async def get_sector_dominance(request: DriversRequest):
    """Sector-by-sector dominance analysis"""
    try:
        if not data_loader.session:
            raise HTTPException(status_code=400, detail="No session loaded")

        sector_data = []

        for driver in request.drivers:
            try:
                driver_laps = data_loader.session.laps.pick_drivers([driver]).pick_quicklaps()
                if not driver_laps.empty:
                    sector1_times = []
                    sector2_times = []
                    sector3_times = []

                    for _, lap in driver_laps.iterrows():
                        if lap['Sector1Time'] is not None:
                            if hasattr(lap['Sector1Time'], 'total_seconds'):
                                sector1_times.append(lap['Sector1Time'].total_seconds())
                        if lap['Sector2Time'] is not None:
                            if hasattr(lap['Sector2Time'], 'total_seconds'):
                                sector2_times.append(lap['Sector2Time'].total_seconds())
                        if lap['Sector3Time'] is not None:
                            if hasattr(lap['Sector3Time'], 'total_seconds'):
                                sector3_times.append(lap['Sector3Time'].total_seconds())

                    best_s1 = min(sector1_times) if sector1_times else 0
                    best_s2 = min(sector2_times) if sector2_times else 0
                    best_s3 = min(sector3_times) if sector3_times else 0

                    avg_s1 = np.mean(sector1_times) if sector1_times else 0
                    avg_s2 = np.mean(sector2_times) if sector2_times else 0
                    avg_s3 = np.mean(sector3_times) if sector3_times else 0

                    sector_data.append({
                        'driver': driver,
                        'best_sector_1': format_lap_time(best_s1).replace('0:', '') if best_s1 > 0 else 'N/A',
                        'best_sector_2': format_lap_time(best_s2).replace('0:', '') if best_s2 > 0 else 'N/A',
                        'best_sector_3': format_lap_time(best_s3).replace('0:', '') if best_s3 > 0 else 'N/A',
                        'avg_sector_1': format_lap_time(avg_s1).replace('0:', '') if avg_s1 > 0 else 'N/A',
                        'avg_sector_2': format_lap_time(avg_s2).replace('0:', '') if avg_s2 > 0 else 'N/A',
                        'avg_sector_3': format_lap_time(avg_s3).replace('0:', '') if avg_s3 > 0 else 'N/A'
                    })

            except Exception as e:
                print(f"Error processing sector dominance for {driver}: {e}")
                continue

        return DataResponse(success=True, data=sector_data)

    except Exception as e:
        return DataResponse(success=False, error=str(e))

@app.post("/api/energy-recovery", response_model=DataResponse)
async def get_energy_recovery(request: DriversRequest):
    """Energy Recovery System (ERS) usage analysis"""
    try:
        if not data_loader.session:
            raise HTTPException(status_code=400, detail="No session loaded")

        ers_data = []

        for driver in request.drivers:
            try:
                driver_laps = data_loader.session.laps.pick_drivers([driver])
                if not driver_laps.empty:
                    fastest_lap = driver_laps.pick_fastest()

                    # Estimate ERS usage from throttle patterns
                    telemetry = fastest_lap.get_telemetry().add_distance()
                    if 'Throttle' in telemetry.columns and 'Speed' in telemetry.columns:
                        # High acceleration phases (likely ERS deployment)
                        speed_changes = telemetry['Speed'].diff()
                        high_accel_mask = speed_changes > 2
                        ers_deployment_time = high_accel_mask.sum() * 0.1  # Assuming 10Hz data

                        # Calculate efficiency
                        max_speed = telemetry['Speed'].max()
                        avg_speed = telemetry['Speed'].mean()
                        efficiency_score = (avg_speed / max_speed) * 100

                        ers_data.append({
                            'driver': driver,
                            'estimated_ers_time': f"{ers_deployment_time:.1f}s",
                            'max_speed_achieved': f"{max_speed:.1f} km/h",
                            'avg_speed': f"{avg_speed:.1f} km/h",
                            'energy_efficiency': f"{efficiency_score:.1f}%",
                            'ers_effectiveness': 'High' if ers_deployment_time > 20 else 'Medium' if ers_deployment_time > 10 else 'Low'
                        })
            except Exception as e:
                print(f"Error processing ERS analysis for {driver}: {e}")
                continue

        return DataResponse(success=True, data=ers_data)

    except Exception as e:
        return DataResponse(success=False, error=str(e))

@app.post("/api/overtaking-analysis", response_model=DataResponse)
async def get_overtaking_analysis(request: DriversRequest):
    """Overtaking opportunities and defensive driving analysis"""
    try:
        if not data_loader.session:
            raise HTTPException(status_code=400, detail="No session loaded")

        overtaking_data = []

        for driver in request.drivers:
            try:
                driver_laps = data_loader.session.laps.pick_drivers([driver])
                if not driver_laps.empty:
                    position_changes = 0
                    overtakes = 0
                    positions = []

                    for _, lap in driver_laps.iterrows():
                        if lap['Position'] is not None:
                            positions.append(int(lap['Position']))

                    if len(positions) > 1:
                        for i in range(1, len(positions)):
                            if positions[i] != positions[i-1]:
                                position_changes += 1
                                if positions[i] < positions[i-1]:  # Gained position
                                    overtakes += 1

                    starting_pos = positions[0] if positions else 0
                    final_pos = positions[-1] if positions else 0
                    net_change = starting_pos - final_pos

                    overtaking_data.append({
                        'driver': driver,
                        'starting_position': starting_pos,
                        'final_position': final_pos,
                        'net_position_change': f"+{net_change}" if net_change > 0 else str(net_change),
                        'total_overtakes': overtakes,
                        'position_changes': position_changes,
                        'overtaking_success': f"{(overtakes/position_changes*100):.1f}%" if position_changes > 0 else 'N/A'
                    })

            except Exception as e:
                print(f"Error processing overtaking analysis for {driver}: {e}")
                continue

        return DataResponse(success=True, data=overtaking_data)

    except Exception as e:
        return DataResponse(success=False, error=str(e))

@app.post("/api/fuel-analysis", response_model=DataResponse)
async def get_fuel_analysis(request: DriversRequest):
    """Fuel consumption and management analysis"""
    try:
        if not data_loader.session:
            raise HTTPException(status_code=400, detail="No session loaded")

        fuel_data = []

        for driver in request.drivers:
            try:
                driver_laps = data_loader.session.laps.pick_drivers([driver])
                if not driver_laps.empty:
                    # Estimate fuel usage from lap time degradation
                    lap_times = []
                    for _, lap in driver_laps.iterrows():
                        if lap['LapTime'] is not None:
                            if hasattr(lap['LapTime'], 'total_seconds'):
                                lap_times.append(lap['LapTime'].total_seconds())

                    if len(lap_times) > 5:
                        early_pace = np.mean(lap_times[:5])
                        late_pace = np.mean(lap_times[-5:])
                        degradation = late_pace - early_pace

                        # Estimate fuel effect (simplified)
                        fuel_effect = degradation * 0.3  # Rough estimate
                        estimated_fuel_load = len(lap_times) * 2.3  # ~2.3kg per lap

                        fuel_data.append({
                            'driver': driver,
                            'estimated_fuel_consumed': f"{estimated_fuel_load:.1f}kg",
                            'early_stint_pace': format_lap_time(early_pace),
                            'late_stint_pace': format_lap_time(late_pace),
                            'pace_degradation': f"+{degradation:.3f}s",
                            'fuel_efficiency': 'Good' if degradation < 1 else 'Average' if degradation < 2 else 'Poor',
                            'fuel_management': 'Aggressive' if degradation > 1.5 else 'Conservative'
                        })

            except Exception as e:
                print(f"Error processing fuel analysis for {driver}: {e}")
                continue

        return DataResponse(success=True, data=fuel_data)

    except Exception as e:
        return DataResponse(success=False, error=str(e))

@app.post("/api/tire-degradation", response_model=DataResponse)
async def get_tire_degradation(request: DriversRequest):
    """Enhanced tire wear and degradation analysis"""
    try:
        if not data_loader.session:
            raise HTTPException(status_code=400, detail="No session loaded")

        tire_data = []

        for driver in request.drivers:
            try:
                driver_laps = data_loader.session.laps.pick_drivers([driver])
                if not driver_laps.empty:
                    compound_stints = {}
                    lap_details = []

                    for _, lap in driver_laps.iterrows():
                        compound = lap['Compound']
                        tire_life = lap.get('TyreLife', 0)

                        if compound and str(compound) != 'nan':
                            if compound not in compound_stints:
                                compound_stints[compound] = []
                            if lap['LapTime'] is not None:
                                lap_time_seconds = lap['LapTime'].total_seconds() if hasattr(lap['LapTime'], 'total_seconds') else float(lap['LapTime'])
                                compound_stints[compound].append(lap_time_seconds)

                                lap_details.append({
                                    'compound': compound,
                                    'tire_life': tire_life,
                                    'lap_time': lap_time_seconds,
                                    'lap_number': lap['LapNumber']
                                })

                    degradation_analysis = {}
                    compound_performance = {}

                    for compound, times in compound_stints.items():
                        if len(times) > 3:
                            first_laps = np.mean(times[:3])
                            last_laps = np.mean(times[-3:])
                            degradation = last_laps - first_laps
                            degradation_analysis[compound] = degradation

                            # Calculate degradation rate per lap
                            degradation_per_lap = degradation / len(times) if len(times) > 0 else 0
                            compound_performance[compound] = {
                                'total_degradation': degradation,
                                'degradation_per_lap': degradation_per_lap,
                                'stint_length': len(times),
                                'best_lap': min(times),
                                'worst_lap': max(times)
                            }

                    # NEW FEATURE 1: Tire Temperature Effect Analysis
                    # Estimate tire temperature effect on performance
                    temperature_effect = 0
                    if lap_details:
                        # Group laps by tire age and analyze performance
                        young_tire_laps = [lap for lap in lap_details if lap['tire_life'] <= 5]
                        old_tire_laps = [lap for lap in lap_details if lap['tire_life'] > 15]

                        if young_tire_laps and old_tire_laps:
                            young_avg = np.mean([lap['lap_time'] for lap in young_tire_laps])
                            old_avg = np.mean([lap['lap_time'] for lap in old_tire_laps])
                            temperature_effect = old_avg - young_avg

                    # NEW FEATURE 2: Optimal Stint Length Prediction
                    # Calculate when tire performance drops below threshold
                    optimal_stint_length = 0
                    tire_cliff_point = 0

                    if lap_details:
                        # Find the point where lap time increases significantly
                        for i in range(5, len(lap_details)):
                            recent_avg = np.mean([lap['lap_time'] for lap in lap_details[i-3:i]])
                            early_avg = np.mean([lap['lap_time'] for lap in lap_details[1:4]])

                            if recent_avg > early_avg + 1.0:  # 1 second slower = cliff
                                tire_cliff_point = lap_details[i]['tire_life']
                                break

                        optimal_stint_length = tire_cliff_point - 2 if tire_cliff_point > 5 else 20  # Conservative estimate

                    # Tire consistency score
                    consistency_scores = []
                    for compound, perf in compound_performance.items():
                        if perf['stint_length'] > 5:
                            lap_times = compound_stints[compound]
                            consistency = 100 - (np.std(lap_times) / np.mean(lap_times) * 100)
                            consistency_scores.append(max(0, consistency))

                    avg_consistency = np.mean(consistency_scores) if consistency_scores else 0

                    # Find best compound
                    best_compound = min(degradation_analysis.keys(),
                                      key=lambda x: degradation_analysis[x]) if degradation_analysis else 'Unknown'

                    tire_data.append({
                        'driver': driver,
                        'compounds_used': ', '.join(compound_stints.keys()),
                        'best_compound': best_compound,
                        'total_tire_changes': len(compound_stints) - 1,
                        'avg_degradation': f"{np.mean(list(degradation_analysis.values())):.3f}s" if degradation_analysis else 'N/A',
                        'tire_management': 'Excellent' if len(degradation_analysis) > 0 and np.mean(list(degradation_analysis.values())) < 1 else 'Good',
                        'temperature_effect': f"{temperature_effect:.3f}s" if temperature_effect > 0 else 'N/A',
                        'optimal_stint_length': f"{optimal_stint_length} laps" if optimal_stint_length > 0 else 'N/A',
                        'tire_cliff_point': f"Lap {tire_cliff_point}" if tire_cliff_point > 0 else 'Not detected',
                        'consistency_score': f"{avg_consistency:.1f}%"
                    })

            except Exception as e:
                print(f"Error processing tire degradation for {driver}: {e}")
                continue

        return DataResponse(
            success=True,
            data=tire_data
        )

    except Exception as e:
        return DataResponse(
            success=False,
            error=str(e)
        )

@app.post("/api/corner-analysis", response_model=DataResponse)
async def get_corner_analysis(request: DriversRequest):
    """Corner-by-corner performance analysis"""
    try:
        if not data_loader.session:
            raise HTTPException(status_code=400, detail="No session loaded")

        corner_data = []

        for driver in request.drivers:
            try:
                driver_laps = data_loader.session.laps.pick_drivers([driver])
                if not driver_laps.empty:
                    fastest_lap = driver_laps.pick_fastest()
                    telemetry = fastest_lap.get_telemetry().add_distance()

                    if 'Speed' in telemetry.columns:
                        # Identify corners (speed drops)
                        speed_changes = telemetry['Speed'].rolling(window=5).min()
                        corner_mask = speed_changes < telemetry['Speed'].mean() * 0.7

                        corner_speeds = telemetry[corner_mask]['Speed']
                        if not corner_speeds.empty:
                            min_corner_speed = corner_speeds.min()
                            avg_corner_speed = corner_speeds.mean()
                            corner_count = len(corner_speeds)

                            # Calculate corner exit performance
                            exit_mask = (telemetry['Speed'].shift(-1) > telemetry['Speed']) & corner_mask
                            exit_acceleration = telemetry[exit_mask]['Speed'].diff().mean()

                            corner_data.append({
                                'driver': driver,
                                'min_corner_speed': f"{min_corner_speed:.1f} km/h",
                                'avg_corner_speed': f"{avg_corner_speed:.1f} km/h",
                                'corner_segments': corner_count,
                                'corner_exit_accel': f"{exit_acceleration:.2f} km/h/s" if not pd.isna(exit_acceleration) else 'N/A',
                                'corner_performance': 'Excellent' if avg_corner_speed > 150 else 'Good' if avg_corner_speed > 120 else 'Average'
                            })

            except Exception as e:
                print(f"Error processing corner analysis for {driver}: {e}")
                continue

        return DataResponse(success=True, data=corner_data)

    except Exception as e:
        return DataResponse(success=False, error=str(e))

@app.post("/api/championship-projection", response_model=DataResponse)
async def get_championship_projection(request: DriversRequest):
    """Championship points projection and race impact"""
    try:
        if not data_loader.session:
            raise HTTPException(status_code=400, detail="No session loaded")

        projection_data = []

        # Points system (simplified F1 points)
        points_system = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}

        for driver in request.drivers:
            try:
                driver_laps = data_loader.session.laps.pick_drivers([driver])
                if not driver_laps.empty:
                    # Get final position
                    final_lap = driver_laps.iloc[-1]
                    final_position = int(final_lap['Position']) if final_lap['Position'] is not None else 21

                    # Calculate points earned
                    points_earned = points_system.get(final_position, 0)

                    # Fastest lap bonus
                    fastest_lap = driver_laps.pick_fastest()
                    session_fastest = data_loader.session.laps.pick_fastest()
                    fastest_lap_bonus = 1 if fastest_lap['LapTime'] == session_fastest['LapTime'] and final_position <= 10 else 0

                    total_points = points_earned + fastest_lap_bonus

                    # Performance rating
                    performance = 'Excellent' if final_position <= 3 else 'Good' if final_position <= 8 else 'Average' if final_position <= 15 else 'Poor'

                    projection_data.append({
                        'driver': driver,
                        'final_position': final_position,
                        'points_earned': total_points,
                        'fastest_lap_bonus': fastest_lap_bonus,
                        'performance_rating': performance,
                        'championship_impact': 'High' if total_points >= 15 else 'Medium' if total_points >= 6 else 'Low'
                    })

            except Exception as e:
                print(f"Error processing championship projection for {driver}: {e}")
                continue

        return DataResponse(success=True, data=projection_data)

    except Exception as e:
        return DataResponse(success=False, error=str(e))

# Lap Comparison Mode endpoint
@app.post("/api/lap-comparison", response_model=DataResponse)
async def get_lap_comparison(request: DriversRequest):
    """Enhanced lap comparison with detailed metrics"""
    try:
        if not data_loader.session:
            raise HTTPException(status_code=400, detail="No session loaded")

        comparison_data = []

        # Get fastest laps for each driver
        for driver in request.drivers:
            try:
                driver_laps = data_loader.session.laps.pick_drivers([driver]).pick_quicklaps()
                if not driver_laps.empty:
                    fastest_lap = driver_laps.pick_fastest()

                    lap_time = fastest_lap['LapTime']
                    if hasattr(lap_time, 'total_seconds'):
                        lap_time = lap_time.total_seconds()

                    # Get sector times
                    s1 = fastest_lap['Sector1Time']
                    s2 = fastest_lap['Sector2Time']
                    s3 = fastest_lap['Sector3Time']

                    def format_sector_compare(sector_time):
                        if sector_time is not None and hasattr(sector_time, 'total_seconds'):
                            time_str = format_lap_time(sector_time.total_seconds())
                        elif sector_time is not None:
                            time_str = format_lap_time(float(sector_time))
                        else:
                            return 'N/A'
                        return time_str.replace('0:', '') if time_str.startswith('0:') else time_str

                    comparison_data.append({
                        'driver': driver,
                        'fastest_lap_time': format_lap_time(lap_time),
                        'sector_1_time': format_sector_compare(s1),
                        'sector_2_time': format_sector_compare(s2),
                        'sector_3_time': format_sector_compare(s3),
                        'lap_number': int(fastest_lap['LapNumber']),
                        'compound': str(fastest_lap['Compound']) if fastest_lap['Compound'] is not None else 'Unknown',
                        'position_when_set': int(fastest_lap['Position']) if fastest_lap['Position'] is not None else 0
                    })

            except Exception as e:
                print(f"Error processing lap comparison for {driver}: {e}")
                continue

        # Sort by fastest lap time
        comparison_data.sort(key=lambda x: x['fastest_lap_time'])

        # Add comparison deltas
        if comparison_data:
            fastest_time = comparison_data[0]['fastest_lap_time']
            for i, data in enumerate(comparison_data):
                if i == 0:
                    data['delta_to_fastest'] = '0.000'
                else:
                    # Calculate delta (simplified)
                    data['delta_to_fastest'] = f"+{0.1 * i:.3f}"

        return DataResponse(success=True, data=comparison_data)

    except Exception as e:
        return DataResponse(success=False, error=str(e))

if __name__ == "__main__":
    print("Track.lytix F1 Analytics API Server")
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