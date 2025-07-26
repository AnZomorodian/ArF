"""
Modern Web App Enhancements for Track.lytix F1 Platform
Add stunning mobile-responsive styling and app-like experience
"""

# Enhanced Hero Section with Racing Animations
hero_section = """
<div style="
    background: linear-gradient(135deg, #FF0033 0%, #FF8C00 30%, #FFD700 60%, #00FFE6 100%);
    padding: 4rem 2rem;
    margin: -2rem -2rem 3rem -2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    border-radius: 0 0 40px 40px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);
">
    <div style="position: absolute; top: 0; left: -100%; width: 100%; height: 100%; 
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                animation: shine 3s infinite ease-in-out;"></div>
    
    <h1 style="
        font-family: 'Orbitron', monospace;
        font-size: clamp(3rem, 8vw, 5rem);
        font-weight: 900;
        margin: 0;
        color: white;
        text-shadow: 0 5px 15px rgba(0,0,0,0.8);
        animation: pulse 2s infinite ease-in-out;
    ">🏎️ Track.lytix</h1>
    
    <p style="
        font-size: clamp(1.2rem, 3vw, 1.8rem);
        color: rgba(255,255,255,0.95);
        font-weight: 600;
        margin: 1rem 0;
        font-family: 'Inter', sans-serif;
    ">Professional F1 Data Analysis Platform</p>
    
    <p style="
        font-size: clamp(1rem, 2.5vw, 1.3rem);
        color: rgba(255,255,255,0.85);
        margin: 1.5rem 0;
        font-weight: 500;
    ">🚀 Advanced Telemetry • 📊 Race Strategy • ⚡ Performance Analytics</p>
    
    <div style="
        display: flex;
        gap: 1rem;
        justify-content: center;
        flex-wrap: wrap;
        margin-top: 2rem;
    ">
        <span style="
            background: rgba(255,0,51,0.3);
            padding: 0.8rem 1.5rem;
            border-radius: 30px;
            color: white;
            font-weight: 700;
            border: 2px solid rgba(255,0,51,0.6);
            backdrop-filter: blur(10px);
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        ">Live F1 Data</span>
        <span style="
            background: rgba(0,255,230,0.3);
            padding: 0.8rem 1.5rem;
            border-radius: 30px;
            color: white;
            font-weight: 700;
            border: 2px solid rgba(0,255,230,0.6);
            backdrop-filter: blur(10px);
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        ">Real-time Analytics</span>
        <span style="
            background: rgba(255,215,0,0.3);
            padding: 0.8rem 1.5rem;
            border-radius: 30px;
            color: white;
            font-weight: 700;
            border: 2px solid rgba(255,215,0,0.6);
            backdrop-filter: blur(10px);
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        ">Professional Insights</span>
    </div>
</div>

<style>
@keyframes shine {
    0% { left: -100%; }
    100% { left: 100%; }
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.02); }
}
</style>
"""

# Enhanced Sidebar Styling
sidebar_enhancement = """
<style>
/* Revolutionary Sidebar */
.css-1d391kg, .css-1aumxhk {
    background: linear-gradient(180deg, rgba(5,5,5,0.98) 0%, rgba(15,15,15,0.95) 100%) !important;
    backdrop-filter: blur(25px) !important;
    border-right: 2px solid rgba(0,255,230,0.3) !important;
    box-shadow: 5px 0 20px rgba(0,255,230,0.2) !important;
}

/* Enhanced Selectboxes */
.stSelectbox > div > div {
    background: linear-gradient(145deg, rgba(20,20,20,0.9), rgba(35,35,35,0.8)) !important;
    border: 2px solid rgba(0,255,230,0.4) !important;
    border-radius: 15px !important;
    color: white !important;
    backdrop-filter: blur(15px) !important;
    transition: all 0.3s ease !important;
}

.stSelectbox > div > div:hover {
    border-color: rgba(0,255,230,0.8) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 5px 15px rgba(0,255,230,0.3) !important;
}

/* Enhanced Multiselect */
.stMultiSelect > div > div {
    background: linear-gradient(145deg, rgba(20,20,20,0.9), rgba(35,35,35,0.8)) !important;
    border: 2px solid rgba(0,255,230,0.4) !important;
    border-radius: 15px !important;
    backdrop-filter: blur(15px) !important;
}

/* Enhanced Slider */
.stSlider > div > div > div {
    background: rgba(0,255,230,0.3) !important;
}

.stSlider > div > div > div > div {
    background: linear-gradient(45deg, #FF0033, #00FFE6) !important;
    box-shadow: 0 0 10px rgba(0,255,230,0.5) !important;
}
</style>
"""

# Mobile-First Responsive Design
mobile_responsive = """
<style>
/* Mobile-First Responsive Design */
@media (max-width: 1200px) {
    .metric-card {
        padding: 2rem !important;
        margin: 1rem 0 !important;
    }
}

@media (max-width: 768px) {
    .main-header h1 {
        font-size: 3rem !important;
    }
    
    .metric-card {
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
        border-radius: 15px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px !important;
        padding: 0 0.8rem !important;
        font-size: 0.8rem !important;
    }
    
    .stDataFrame thead tr th {
        padding: 1rem 0.5rem !important;
        font-size: 0.8rem !important;
    }
    
    .stDataFrame tbody tr td {
        padding: 0.8rem 0.5rem !important;
        font-size: 0.8rem !important;
    }
}

@media (max-width: 480px) {
    .main-header {
        padding: 2rem 1rem !important;
        margin: -1rem -1rem 2rem -1rem !important;
    }
    
    .metric-card {
        padding: 1rem !important;
        border-radius: 12px !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        padding: 0.5rem !important;
        gap: 4px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 45px !important;
        padding: 0 0.6rem !important;
        font-size: 0.75rem !important;
    }
}
</style>
"""

# Performance Optimizations
performance_css = """
<style>
/* Performance Optimizations */
* {
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-rendering: optimizeLegibility;
}

.main .block-container {
    will-change: transform;
    transform: translateZ(0);
}

.metric-card, .stTabs [data-baseweb="tab"], .stButton > button {
    will-change: transform, box-shadow;
    transform: translateZ(0);
}

/* Preload animations */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}

.metric-card {
    animation: fadeInUp 0.6s ease-out forwards;
}

.metric-card:nth-child(1) { animation-delay: 0.1s; }
.metric-card:nth-child(2) { animation-delay: 0.2s; }
.metric-card:nth-child(3) { animation-delay: 0.3s; }
</style>
"""