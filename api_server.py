#!/usr/bin/env python3
"""
F1 Analysis Platform API Server
FastAPI backend for serving F1 data analysis
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import json
import os
from utils.data_loader import DataLoader
from utils.visualizations import (
    create_telemetry_plot, create_tire_strategy_plot, 
    create_race_progression_plot
)
from utils.track_dominance import create_track_dominance_plot
from utils.constants import GRAND_PRIX_2024, DRIVER_TEAMS, TEAM_COLORS
import plotly.graph_objects as go
import plotly

# Initialize FastAPI app
app = FastAPI(title="F1 Analysis Platform API", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global data loader instance
data_loader = None

# Pydantic models for request/response
class SessionRequest(BaseModel):
    year: int
    grand_prix: str
    session_type: str

class DriverRequest(BaseModel):
    drivers: List[str]

class TelemetryRequest(BaseModel):
    drivers: List[str]
    telemetry_type: str

class GrandPrixInfo(BaseModel):
    name: str
    value: str

# API Routes

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="صفحه اصلی یافت نشد")

@app.get("/api/grandprix")
async def get_grand_prix_list(year: int = 2024) -> List[GrandPrixInfo]:
    """Get list of Grand Prix for a specific year"""
    try:
        if year == 2024:
            return [
                GrandPrixInfo(name=f"🏁 {gp_info['name']}", value=gp_name)
                for gp_name, gp_info in GRAND_PRIX_2024.items()
            ]
        else:
            # For other years, return a basic list
            basic_gps = [
                "Australian Grand Prix", "Bahrain Grand Prix", "Saudi Arabian Grand Prix",
                "Chinese Grand Prix", "Japanese Grand Prix", "Miami Grand Prix",
                "Emilia Romagna Grand Prix", "Monaco Grand Prix", "Canadian Grand Prix",
                "Spanish Grand Prix", "Austrian Grand Prix", "British Grand Prix",
                "Hungarian Grand Prix", "Belgian Grand Prix", "Dutch Grand Prix",
                "Italian Grand Prix", "Azerbaijan Grand Prix", "Singapore Grand Prix",
                "United States Grand Prix", "Mexico City Grand Prix", "Brazilian Grand Prix",
                "Las Vegas Grand Prix", "Qatar Grand Prix", "Abu Dhabi Grand Prix"
            ]
            return [
                GrandPrixInfo(name=f"🏁 {gp}", value=gp.replace(" ", ""))
                for gp in basic_gps
            ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا در بارگذاری لیست گرندپری: {str(e)}")

@app.post("/api/load-session")
async def load_session(request: SessionRequest) -> Dict[str, Any]:
    """Load F1 session data"""
    global data_loader
    
    try:
        data_loader = DataLoader()
        success = data_loader.load_session(
            year=request.year,
            grand_prix=request.grand_prix,
            session_type=request.session_type
        )
        
        if not success:
            return {
                "success": False,
                "error": "خطا در بارگذاری داده‌های جلسه"
            }
        
        # Get available drivers
        drivers_list = data_loader.get_available_drivers()
        
        # Format driver information
        formatted_drivers = []
        for driver_abbr in drivers_list:
            team = DRIVER_TEAMS.get(driver_abbr, 'Unknown')
            team_color = TEAM_COLORS.get(team, '#FFFFFF')
            
            formatted_drivers.append({
                "abbreviation": driver_abbr,
                "full_name": driver_abbr,  # You might want to add a full name mapping
                "team": team,
                "team_color": team_color,
                "driver_number": driver_abbr  # This should be the actual driver number
            })
        
        return {
            "success": True,
            "session_data": {
                "year": request.year,
                "grand_prix": request.grand_prix,
                "session_type": request.session_type
            },
            "drivers": formatted_drivers,
            "grand_prix": request.grand_prix,
            "year": request.year,
            "session_type": request.session_type
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"خطا در بارگذاری جلسه: {str(e)}"
        }

@app.post("/api/telemetry")
async def generate_telemetry(request: TelemetryRequest) -> Dict[str, Any]:
    """Generate telemetry plot for selected drivers"""
    if not data_loader:
        raise HTTPException(status_code=400, detail="ابتدا یک جلسه بارگذاری کنید")
    
    try:
        fig = create_telemetry_plot(data_loader, request.drivers, request.telemetry_type)
        
        if fig is None:
            return {
                "success": False,
                "error": "خطا در تولید نمودار تله‌متری"
            }
        
        # Convert plot to JSON
        plot_json = json.loads(plotly.io.to_json(fig))
        
        return {
            "success": True,
            "plot_data": plot_json
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"خطا در تولید نمودار: {str(e)}"
        }

@app.post("/api/tire-strategy")
async def generate_tire_strategy(request: DriverRequest) -> Dict[str, Any]:
    """Generate tire strategy plot for selected drivers"""
    if not data_loader:
        raise HTTPException(status_code=400, detail="ابتدا یک جلسه بارگذاری کنید")
    
    try:
        fig = create_tire_strategy_plot(data_loader, request.drivers)
        
        if fig is None:
            return {
                "success": False,
                "error": "خطا در تولید نمودار استراتژی تایر"
            }
        
        # Convert plot to JSON
        plot_json = json.loads(plotly.io.to_json(fig))
        
        # Get tire details if available
        tire_details = []
        if hasattr(fig, 'stint_details'):
            tire_details = fig.stint_details
        
        return {
            "success": True,
            "plot_data": plot_json,
            "tire_details": tire_details
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"خطا در تولید نمودار: {str(e)}"
        }

@app.post("/api/race-progression")
async def generate_race_progression(request: DriverRequest) -> Dict[str, Any]:
    """Generate race progression plot for selected drivers"""
    if not data_loader:
        raise HTTPException(status_code=400, detail="ابتدا یک جلسه بارگذاری کنید")
    
    try:
        fig = create_race_progression_plot(data_loader, request.drivers)
        
        if fig is None:
            return {
                "success": False,
                "error": "خطا در تولید نمودار پیشرفت مسابقه"
            }
        
        # Convert plot to JSON
        plot_json = json.loads(plotly.io.to_json(fig))
        
        # Generate race statistics
        race_stats = []
        try:
            position_data = data_loader.get_position_data(request.drivers)
            if position_data is not None and not position_data.empty:
                for driver in request.drivers:
                    driver_data = position_data[position_data['Driver'] == driver]
                    if not driver_data.empty:
                        start_pos = driver_data['Position'].iloc[0]
                        end_pos = driver_data['Position'].iloc[-1]
                        position_change = start_pos - end_pos
                        
                        if position_change > 0:
                            change_text = f"+{position_change} موقعیت بهبود"
                        elif position_change < 0:
                            change_text = f"{position_change} موقعیت افت"
                        else:
                            change_text = "بدون تغییر موقعیت"
                        
                        race_stats.append({
                            "title": f"{driver}",
                            "value": f"P{start_pos} → P{end_pos}",
                            "description": change_text
                        })
        except:
            pass
        
        return {
            "success": True,
            "plot_data": plot_json,
            "race_stats": race_stats
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"خطا در تولید نمودار: {str(e)}"
        }

@app.post("/api/track-dominance")
async def generate_track_dominance(request: DriverRequest) -> Dict[str, Any]:
    """Generate track dominance plot for selected drivers"""
    if not data_loader:
        raise HTTPException(status_code=400, detail="ابتدا یک جلسه بارگذاری کنید")
    
    try:
        fig = create_track_dominance_plot(data_loader, request.drivers)
        
        if fig is None:
            return {
                "success": False,
                "error": "خطا در تولید نمودار تسلط بر پیست"
            }
        
        # Convert plot to JSON
        plot_json = json.loads(plotly.io.to_json(fig))
        
        return {
            "success": True,
            "plot_data": plot_json
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"خطا در تولید نمودار: {str(e)}"
        }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "F1 Analysis Platform API is running",
        "session_loaded": data_loader is not None
    }

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "مسیر مورد نظر یافت نشد"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "خطای داخلی سرور"}
    )

if __name__ == "__main__":
    print("🏁 Starting F1 Analysis Platform API Server...")
    print("📊 Server will be available at: http://localhost:5000")
    print("🔧 API documentation: http://localhost:5000/docs")
    
    uvicorn.run(
        "api_server:app", 
        host="0.0.0.0", 
        port=5000, 
        reload=True,
        log_level="info"
    )