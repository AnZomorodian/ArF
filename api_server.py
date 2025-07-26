"""
F1 Data Platform API Server
FastAPI backend for serving F1 data to Next.js frontend
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import json
import pandas as pd
from datetime import datetime

# Import existing F1 analysis modules
from utils.data_loader import DataLoader
from utils.brake_analysis import BrakeAnalyzer
from utils.composite_performance import CompositePerformanceAnalyzer
from utils.advanced_analytics import AdvancedF1Analytics
from utils.tire_performance import TirePerformanceAnalyzer
from utils.stress_index import DriverStressAnalyzer
from utils.downforce_analysis import DownforceAnalyzer
from utils.driver_manager import DynamicDriverManager

app = FastAPI(
    title="F1 Data Analysis API",
    description="Professional Formula 1 data analysis backend API",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global data storage
session_cache = {}
current_session = None

# Pydantic models for API requests/responses
class SessionRequest(BaseModel):
    year: int
    grand_prix: str
    session_type: str

class DriversRequest(BaseModel):
    drivers: List[str]

class SessionInfo(BaseModel):
    year: int
    grand_prix: str
    session_type: str
    session_name: str
    event_name: str
    drivers: List[Dict[str, Any]]

class AnalysisResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/session/load", response_model=SessionInfo)
async def load_session(request: SessionRequest):
    """Load F1 session data"""
    global current_session, session_cache
    
    try:
        # Create cache key
        cache_key = f"{request.year}_{request.grand_prix}_{request.session_type}"
        
        # Check if session is already cached
        if cache_key in session_cache:
            current_session = session_cache[cache_key]
        else:
            # Load new session
            data_loader = DataLoader()
            session = data_loader.load_session(request.year, request.grand_prix, request.session_type)
            
            if session is None:
                raise HTTPException(status_code=404, detail="Session not found")
            
            session_cache[cache_key] = session
            current_session = session
        
        # Get driver information
        driver_manager = DynamicDriverManager(current_session)
        drivers_info = driver_manager.get_available_drivers()
        
        return SessionInfo(
            year=request.year,
            grand_prix=request.grand_prix,
            session_type=request.session_type,
            session_name=current_session.name,
            event_name=current_session.event['EventName'],
            drivers=drivers_info
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading session: {str(e)}")

@app.get("/api/drivers")
async def get_drivers():
    """Get available drivers for current session"""
    global current_session
    
    if current_session is None:
        raise HTTPException(status_code=400, detail="No session loaded")
    
    try:
        driver_manager = DynamicDriverManager(current_session)
        drivers_info = driver_manager.get_available_drivers()
        return {"drivers": drivers_info}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting drivers: {str(e)}")

@app.post("/api/analysis/telemetry", response_model=AnalysisResponse)
async def get_telemetry_analysis(request: DriversRequest):
    """Get telemetry analysis for selected drivers"""
    global current_session
    
    if current_session is None:
        raise HTTPException(status_code=400, detail="No session loaded")
    
    try:
        # Implementation would depend on telemetry analysis requirements
        # This is a placeholder structure
        analysis_data = {
            "telemetry_charts": [],
            "lap_comparisons": [],
            "sector_analysis": {}
        }
        
        return AnalysisResponse(success=True, data=analysis_data)
        
    except Exception as e:
        return AnalysisResponse(success=False, error=str(e))

@app.post("/api/analysis/brake", response_model=AnalysisResponse)
async def get_brake_analysis(request: DriversRequest):
    """Get brake analysis for selected drivers"""
    global current_session
    
    if current_session is None:
        raise HTTPException(status_code=400, detail="No session loaded")
    
    try:
        brake_analyzer = BrakeAnalyzer(current_session)
        brake_data = brake_analyzer.analyze_brake_efficiency(request.drivers)
        
        if brake_data.empty:
            return AnalysisResponse(success=False, error="No brake data available")
        
        # Convert DataFrame to JSON-serializable format
        brake_results = brake_data.to_dict('records')
        
        return AnalysisResponse(success=True, data={
            "brake_efficiency": brake_results,
            "session_info": f"{current_session.event.year} {current_session.event['EventName']} - {current_session.name}"
        })
        
    except Exception as e:
        return AnalysisResponse(success=False, error=str(e))

@app.post("/api/analysis/composite", response_model=AnalysisResponse)
async def get_composite_performance(request: DriversRequest):
    """Get composite performance analysis for selected drivers"""
    global current_session
    
    if current_session is None:
        raise HTTPException(status_code=400, detail="No session loaded")
    
    try:
        composite_analyzer = CompositePerformanceAnalyzer(current_session)
        performance_data = composite_analyzer.calculate_composite_performance(request.drivers)
        
        if performance_data.empty:
            return AnalysisResponse(success=False, error="No performance data available")
        
        # Convert DataFrame to JSON-serializable format
        performance_results = performance_data.to_dict('records')
        
        return AnalysisResponse(success=True, data={
            "composite_performance": performance_results,
            "session_info": f"{current_session.event.year} {current_session.event['EventName']} - {current_session.name}"
        })
        
    except Exception as e:
        return AnalysisResponse(success=False, error=str(e))

@app.post("/api/analysis/tire", response_model=AnalysisResponse)
async def get_tire_analysis(request: DriversRequest):
    """Get tire performance analysis for selected drivers"""
    global current_session
    
    if current_session is None:
        raise HTTPException(status_code=400, detail="No session loaded")
    
    try:
        tire_analyzer = TirePerformanceAnalyzer(current_session)
        tire_data = tire_analyzer.analyze_tire_performance(request.drivers)
        
        if tire_data.empty:
            return AnalysisResponse(success=False, error="No tire data available")
        
        # Convert DataFrame to JSON-serializable format
        tire_results = tire_data.to_dict('records')
        
        return AnalysisResponse(success=True, data={
            "tire_performance": tire_results,
            "session_info": f"{current_session.event.year} {current_session.event['EventName']} - {current_session.name}"
        })
        
    except Exception as e:
        return AnalysisResponse(success=False, error=str(e))

@app.post("/api/analysis/advanced", response_model=AnalysisResponse)
async def get_advanced_analytics(request: DriversRequest):
    """Get advanced analytics for selected drivers"""
    global current_session
    
    if current_session is None:
        raise HTTPException(status_code=400, detail="No session loaded")
    
    try:
        advanced_analytics = AdvancedF1Analytics(current_session)
        
        # Get various advanced metrics
        performance_data = advanced_analytics.calculate_comprehensive_performance_index(request.drivers)
        
        if performance_data.empty:
            return AnalysisResponse(success=False, error="No advanced analytics data available")
        
        # Convert DataFrame to JSON-serializable format
        analytics_results = performance_data.to_dict('records')
        
        return AnalysisResponse(success=True, data={
            "advanced_analytics": analytics_results,
            "session_info": f"{current_session.event.year} {current_session.event['EventName']} - {current_session.name}"
        })
        
    except Exception as e:
        return AnalysisResponse(success=False, error=str(e))

@app.get("/api/constants/teams")
async def get_team_colors():
    """Get team colors and constants"""
    from utils.constants import TEAM_COLORS, GRAND_PRIX_LIST
    
    return {
        "team_colors": TEAM_COLORS,
        "grand_prix_list": GRAND_PRIX_LIST
    }

@app.get("/api/years")
async def get_available_years():
    """Get available years for F1 data"""
    # Return reasonable range of years
    current_year = datetime.now().year
    return {
        "years": list(range(2018, current_year + 1))
    }

@app.get("/api/sessions")
async def get_session_types():
    """Get available session types"""
    return {
        "session_types": [
            {"value": "FP1", "label": "Free Practice 1"},
            {"value": "FP2", "label": "Free Practice 2"},
            {"value": "FP3", "label": "Free Practice 3"},
            {"value": "Q", "label": "Qualifying"},
            {"value": "R", "label": "Race"},
            {"value": "S", "label": "Sprint"}
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )