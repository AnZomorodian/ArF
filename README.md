# 🏎️ CEBRIC - Advanced F1 Data Analysis Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastF1](https://img.shields.io/badge/FastF1-3.6.0-green.svg)](https://github.com/theOehrly/Fast-F1)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Plotly](https://img.shields.io/badge/Plotly.js-2.29+-blue.svg)](https://plotly.com/javascript)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **CEBRIC** is a comprehensive Formula 1 data analysis platform that provides advanced race data visualization and analytics capabilities. Built with modern web technologies and professional-grade design for both local development and online deployment.

## ✨ Features

### 🔧 Core Analytics
- **Real-time Telemetry Analysis** - Speed, throttle, brake, RPM, and gear data visualization with enhanced filtering
- **4x4 Performance Analytics Grid** - Comprehensive 16-metric driver performance matrix 
- **Enhanced Tire Strategy Analysis** - Detailed compound performance with stint-by-stint breakdown
- **Advanced Track Layout Analysis** - Interactive track visualization with speed mapping and sector analysis
- **Weather Adaptation Analysis** - Driver performance consistency across different track conditions
- **Race Intelligence Metrics** - Strategic decision-making and adaptability analysis
- **Pit Stop Analysis** - Comprehensive pit stop strategy and timing analysis with proper data formatting
- **Throttle-Brake Coordination** - Advanced coordination analysis with efficiency ratings
- **Corner-by-Corner Performance** - Detailed cornering analysis with G-forces and trail braking metrics
- **Sector Dominance Analysis** - Sector-by-sector performance comparison and dominance mapping

### 🎨 Modern Interface
- **Dual Interface Options** - Traditional Streamlit and modern Next.js/TypeScript frontend
- **Professional Design** - High-contrast F1-themed styling with glass morphism effects
- **Responsive Layout** - Mobile-first design with dynamic tab system
- **Interactive Visualizations** - Plotly-powered charts with professional styling
- **Real-time Data Updates** - Live session data loading and caching

### 🚀 Technical Stack
- **Backend**: Python 3.11+, FastAPI, FastF1 library
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, Framer Motion
- **Legacy Interface**: Streamlit with custom CSS styling
- **Data Visualization**: Plotly, Recharts
- **Data Processing**: Pandas, NumPy, SciPy
- **API**: RESTful endpoints with automatic OpenAPI documentation

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11 or higher
- Node.js 18+ (for Next.js frontend)
- Git

### Quick Start with Replit
1. **Fork this repository** on Replit
2. **Install dependencies** automatically via Replit's package manager
3. **Run the application** using the configured workflows

### Local Development Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/your-username/track-lytix.git
cd track-lytix
```

#### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

#### 3. Install Node.js Dependencies (for Next.js frontend)
```bash
cd frontend-next
npm install
cd ..
```

#### 4. Configure Environment
Create a `.streamlit/config.toml` file:
```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000

[theme]
base = "dark"
```

## 🚀 Running the Application

### Option 1: Local Development (Recommended)
```bash
# Start the CEBRIC F1 Analytics platform
python api_server.py
```
This will:
- Start the FastAPI backend on `http://0.0.0.0:5000`
- Serve the web interface at `http://localhost:5000`
- Provide API documentation at `http://localhost:5000/docs`
- Configure for both local and external IP access

### Option 2: Replit Deployment (Online Access)
1. **Fork/Import to Replit**: Click "Import from GitHub" and paste the repository URL
2. **Automatic Setup**: Replit will install dependencies automatically
3. **Run the Application**: Click the "Run" button
4. **Access Online**: Your app will be available at `https://your-repl-name.your-username.repl.co`

### Option 3: Custom Port Configuration
```bash
# Run on a specific port (useful for deployment)
PORT=8000 python api_server.py
```

### Option 4: Development with Hot Reload
```bash
# For development with automatic restart on file changes
uvicorn api_server:app --host 0.0.0.0 --port 5000 --reload
```

## 🌐 Deployment Options

### Local Network Access
The application is configured to accept connections from any IP address, making it accessible from:
- **Local**: `http://localhost:5000`
- **Network**: `http://YOUR_LOCAL_IP:5000` (find your IP with `ipconfig` or `ifconfig`)
- **Development**: Accessible from other devices on your local network

### Production Deployment
For production deployment on platforms like Heroku, Railway, or cloud providers:

1. **Environment Variables**: The app automatically detects `PORT` environment variable
2. **Docker Support**: Include Docker configuration for containerized deployment
3. **HTTPS**: Configure reverse proxy (nginx) for HTTPS in production

### Replit-Specific Features
- **Always On**: Keep your app running 24/7 with Replit's Always On feature
- **Custom Domain**: Connect your own domain to your Replit deployment
- **Environment Secrets**: Use Replit's secrets manager for sensitive configuration

## 📊 Usage Guide

### Getting Started
1. **Select Session Data**:
   - Choose year (2018-2025)
   - Select Grand Prix event
   - Pick session type (Practice, Qualifying, Race, Sprint)

2. **Load Data**: Click "Load Session Data" to fetch telemetry information

3. **Choose Drivers**: Select drivers for comparison analysis

4. **Explore Analytics**:
   - **Telemetry**: Speed, throttle, brake, and gear analysis
   - **Lap Analysis**: Sector times and lap progression
   - **Tire Strategy**: Compound performance and pit stop analysis
   - **Track Dominance**: Fastest sectors visualization
   - **Advanced Analytics**: Performance index and ML clustering
   - **Brake Analysis**: Efficiency and force metrics
   - **Composite Performance**: Multi-factor driver evaluation

### Advanced Features
- **Data Export**: Download charts and analysis data
- **Real-time Updates**: Live session data refresh
- **Professional Styling**: High-contrast design for better visibility
- **Mobile Support**: Responsive design for all devices

## 🔧 API Documentation

### Core Endpoints
- `POST /api/session/load` - Load F1 session data
- `GET /api/drivers` - Get available drivers
- `POST /api/analysis/telemetry` - Telemetry analysis
- `POST /api/analysis/brake` - Brake performance analysis
- `POST /api/analysis/composite` - Composite performance metrics
- `POST /api/analysis/tire` - Tire strategy analysis
- `GET /api/constants/teams` - Team colors and constants

### Example API Usage
```python
import requests

# Load session data
response = requests.post("http://localhost:8000/api/session/load", json={
    "year": 2024,
    "grand_prix": "Monaco",
    "session_type": "R"
})

# Get brake analysis
response = requests.post("http://localhost:8000/api/analysis/brake", json={
    "drivers": ["VER", "HAM", "LEC"]
})
```

## 📁 Project Structure

```
track-lytix/
├── app.py                      # Main Streamlit application
├── api_server.py               # FastAPI backend server
├── requirements.txt            # Python dependencies
├── replit.md                   # Project documentation
├── 
├── utils/                      # Core analysis modules
│   ├── data_loader.py          # F1 data loading and caching
│   ├── brake_analysis.py       # Brake efficiency analysis
│   ├── composite_performance.py # Performance index calculations
│   ├── advanced_analytics.py   # ML-powered analytics
│   ├── tire_performance.py     # Tire strategy analysis
│   ├── visualizations.py       # Plotly chart generation
│   ├── constants.py            # F1 team colors and data
│   └── ...                     # Additional analysis modules
├── 
├── frontend-next/              # Next.js TypeScript frontend
│   ├── app/                    # Next.js 14 app directory
│   │   ├── components/         # React components
│   │   ├── globals.css         # Global styles
│   │   ├── layout.tsx          # Root layout
│   │   └── page.tsx            # Main page
│   ├── package.json            # Node.js dependencies
│   ├── tailwind.config.js      # Tailwind CSS configuration
│   └── next.config.js          # Next.js configuration
└── 
└── .streamlit/                 # Streamlit configuration
    └── config.toml             # Server settings
```

## 🎨 Customization

### Styling
- Modify `app.py` CSS variables for color themes
- Update `frontend-next/tailwind.config.js` for frontend styling
- Customize team colors in `utils/constants.py`

### Adding New Analysis
1. Create new module in `utils/` directory
2. Add corresponding API endpoint in `api_server.py`
3. Import and integrate in `app.py`
4. Add frontend component in `frontend-next/app/components/`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-analysis`
3. Commit changes: `git commit -am 'Add new analysis feature'`
4. Push to branch: `git push origin feature/new-analysis`
5. Submit a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastF1** - Official F1 data access library
- **Streamlit** - Web application framework
- **Next.js** - React framework for production
- **Plotly** - Interactive visualization library
- **Formula 1** - For providing official timing data

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/track-lytix/issues)
- **Documentation**: [Project Wiki](https://github.com/your-username/track-lytix/wiki)
- **API Docs**: `http://localhost:8000/api/docs` (when running)

---

<div align="center">
  <h3>🏎️ Built for F1 Enthusiasts, by F1 Enthusiasts</h3>
  <p>Track.lytix - Professional Formula 1 Data Analysis Platform</p>
</div>