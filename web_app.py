#!/usr/bin/env python3
"""
F1 Analysis Platform Web Application
FastAPI backend for serving F1 data analysis
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import json
import plotly
from utils.data_loader import DataLoader
from utils.visualizations import (
    create_telemetry_plot, create_tire_strategy_plot, 
    create_race_progression_plot
)
from utils.track_dominance import create_track_dominance_plot
from utils.constants import DRIVER_TEAMS, TEAM_COLORS

# Initialize FastAPI app
app = FastAPI(title="F1 Analysis Platform", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global data loader instance
data_loader = None

# Request models
class SessionRequest(BaseModel):
    year: int
    grand_prix: str
    session_type: str

class DriverRequest(BaseModel):
    drivers: List[str]

class TelemetryRequest(BaseModel):
    drivers: List[str]
    telemetry_type: str

# Helper function to convert plotly figure to JSON safely
def plotly_to_json(fig):
    try:
        if fig is None:
            return {}
        plot_json_str = plotly.io.to_json(fig)
        return json.loads(plot_json_str)
    except Exception:
        return {}

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="صفحه اصلی یافت نشد")

@app.get("/api/grandprix")
async def get_grand_prix_list(year: int = 2024):
    """Get list of Grand Prix for a specific year"""
    try:
        # Define Grand Prix list for 2024
        grand_prix_2024 = {
            "AustralianGP": {"name": "Australian Grand Prix"},
            "BahrainGP": {"name": "Bahrain Grand Prix"},
            "SaudiArabianGP": {"name": "Saudi Arabian Grand Prix"},
            "ChineseGP": {"name": "Chinese Grand Prix"},
            "JapaneseGP": {"name": "Japanese Grand Prix"},
            "MiamiGP": {"name": "Miami Grand Prix"},
            "EmiliaRomagnaGP": {"name": "Emilia Romagna Grand Prix"},
            "MonacoGP": {"name": "Monaco Grand Prix"},
            "CanadianGP": {"name": "Canadian Grand Prix"},
            "SpanishGP": {"name": "Spanish Grand Prix"},
            "AustrianGP": {"name": "Austrian Grand Prix"},
            "BritishGP": {"name": "British Grand Prix"},
            "HungarianGP": {"name": "Hungarian Grand Prix"},
            "BelgianGP": {"name": "Belgian Grand Prix"},
            "DutchGP": {"name": "Dutch Grand Prix"},
            "ItalianGP": {"name": "Italian Grand Prix"},
            "AzerbaijanGP": {"name": "Azerbaijan Grand Prix"},
            "SingaporeGP": {"name": "Singapore Grand Prix"},
            "UnitedStatesGP": {"name": "United States Grand Prix"},
            "MexicoCityGP": {"name": "Mexico City Grand Prix"},
            "BrazilianGP": {"name": "Brazilian Grand Prix"},
            "LasVegasGP": {"name": "Las Vegas Grand Prix"},
            "QatarGP": {"name": "Qatar Grand Prix"},
            "AbuDhabiGP": {"name": "Abu Dhabi Grand Prix"}
        }
        
        if year == 2024:
            return [
                {"name": f"🏁 {gp_info['name']}", "value": gp_name}
                for gp_name, gp_info in grand_prix_2024.items()
            ]
        else:
            basic_gps = [
                "Australian Grand Prix", "Bahrain Grand Prix", "Chinese Grand Prix",
                "Japanese Grand Prix", "Miami Grand Prix", "Monaco Grand Prix",
                "Canadian Grand Prix", "Spanish Grand Prix", "British Grand Prix",
                "Hungarian Grand Prix", "Belgian Grand Prix", "Dutch Grand Prix",
                "Italian Grand Prix", "Singapore Grand Prix", "United States Grand Prix",
                "Mexico City Grand Prix", "Brazilian Grand Prix", "Abu Dhabi Grand Prix"
            ]
            return [
                {"name": f"🏁 {gp}", "value": gp.replace(" ", "")}
                for gp in basic_gps
            ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا در بارگذاری لیست گرندپری: {str(e)}")

@app.post("/api/load-session")
async def load_session(request: SessionRequest):
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
            return {"success": False, "error": "خطا در بارگذاری داده‌های جلسه"}
        
        drivers_list = data_loader.get_available_drivers()
        
        formatted_drivers = []
        for driver_abbr in drivers_list:
            team = DRIVER_TEAMS.get(driver_abbr, 'Unknown')
            team_color = TEAM_COLORS.get(team, '#FFFFFF')
            
            formatted_drivers.append({
                "abbreviation": driver_abbr,
                "full_name": driver_abbr,
                "team": team,
                "team_color": team_color,
                "driver_number": driver_abbr
            })
        
        return {
            "success": True,
            "drivers": formatted_drivers,
            "grand_prix": request.grand_prix,
            "year": request.year,
            "session_type": request.session_type
        }
        
    except Exception as e:
        return {"success": False, "error": f"خطا در بارگذاری جلسه: {str(e)}"}

@app.post("/api/telemetry")
async def generate_telemetry(request: TelemetryRequest):
    """Generate telemetry plot"""
    if not data_loader:
        raise HTTPException(status_code=400, detail="ابتدا یک جلسه بارگذاری کنید")
    
    try:
        fig = create_telemetry_plot(data_loader, request.drivers, request.telemetry_type)
        plot_json = plotly_to_json(fig)
        
        if not plot_json:
            return {"success": False, "error": "خطا در تولید نمودار تله‌متری"}
        
        return {"success": True, "plot_data": plot_json}
        
    except Exception as e:
        return {"success": False, "error": f"خطا در تولید نمودار: {str(e)}"}

@app.post("/api/tire-strategy")
async def generate_tire_strategy(request: DriverRequest):
    """Generate tire strategy plot"""
    if not data_loader:
        raise HTTPException(status_code=400, detail="ابتدا یک جلسه بارگذاری کنید")
    
    try:
        fig = create_tire_strategy_plot(data_loader, request.drivers)
        plot_json = plotly_to_json(fig)
        
        if not plot_json:
            return {"success": False, "error": "خطا در تولید نمودار استراتژی تایر"}
        
        tire_details = getattr(fig, 'stint_details', []) if fig else []
        
        return {
            "success": True, 
            "plot_data": plot_json,
            "tire_details": tire_details
        }
        
    except Exception as e:
        return {"success": False, "error": f"خطا در تولید نمودار: {str(e)}"}

@app.post("/api/race-progression")
async def generate_race_progression(request: DriverRequest):
    """Generate race progression plot"""
    if not data_loader:
        raise HTTPException(status_code=400, detail="ابتدا یک جلسه بارگذاری کنید")
    
    try:
        fig = create_race_progression_plot(data_loader, request.drivers)
        plot_json = plotly_to_json(fig)
        
        if not plot_json:
            return {"success": False, "error": "خطا در تولید نمودار پیشرفت مسابقه"}
        
        # Generate race statistics
        race_stats = []
        try:
            position_data = data_loader.get_position_data(request.drivers)
            if position_data is not None and not position_data.empty:
                for driver in request.drivers:
                    driver_data = position_data[position_data['Driver'] == driver]
                    if not driver_data.empty:
                        start_pos = int(driver_data['Position'].iloc[0])
                        end_pos = int(driver_data['Position'].iloc[-1])
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
        except Exception:
            pass
        
        return {
            "success": True,
            "plot_data": plot_json,
            "race_stats": race_stats
        }
        
    except Exception as e:
        return {"success": False, "error": f"خطا در تولید نمودار: {str(e)}"}

@app.post("/api/track-dominance")
async def generate_track_dominance(request: DriverRequest):
    """Generate track dominance plot"""
    if not data_loader:
        raise HTTPException(status_code=400, detail="ابتدا یک جلسه بارگذاری کنید")
    
    try:
        fig = create_track_dominance_plot(data_loader, request.drivers)
        plot_json = plotly_to_json(fig)
        
        if not plot_json:
            return {"success": False, "error": "خطا در تولید نمودار تسلط بر پیست"}
        
        return {"success": True, "plot_data": plot_json}
        
    except Exception as e:
        return {"success": False, "error": f"خطا در تولید نمودار: {str(e)}"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "F1 Analysis Platform API is running",
        "session_loaded": data_loader is not None
    }

if __name__ == "__main__":
    print("🏁 Starting F1 Analysis Platform...")
    print("📊 Server will be available at: http://localhost:5000")
    
    uvicorn.run(
        "web_app:app", 
        host="0.0.0.0", 
        port=5000, 
        reload=True,
        log_level="info"
    )