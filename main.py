#!/usr/bin/env python3
"""
Track.lytix - F1 Data Analysis Platform
Main entry point for command line execution

Usage:
    python main.py

This will start the Streamlit application on http://localhost:5000
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit',
        'fastf1',
        'plotly',
        'pandas',
        'numpy',
        'scipy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def setup_streamlit_config():
    """Create Streamlit configuration directory and file"""
    config_dir = Path('.streamlit')
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / 'config.toml'
    
    config_content = """[server]
headless = true
address = "0.0.0.0"
port = 5000
runOnSave = false
fileWatcherType = "none"

[theme]
base = "dark"
primaryColor = "#00FFE6"
backgroundColor = "#0E0E0E"
secondaryBackgroundColor = "#1A1A1A"
textColor = "#FFFFFF"

[browser]
gatherUsageStats = false
"""
    
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    print("✅ Streamlit configuration created")

def main():
    """Main entry point"""
    print("🏎️  Track.lytix - F1 Data Analysis Platform")
    print("=" * 50)
    print("   Professional F1 Analytics & Telemetry Platform")
    print("   Enhanced with Brake Analysis & Performance Metrics")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found in current directory")
        print("   Please run this script from the Track.lytix project directory")
        sys.exit(1)
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    print("✅ All dependencies found")
    
    # Setup Streamlit configuration
    setup_streamlit_config()
    
    # Start Streamlit application
    print("\n🚀 Starting Track.lytix...")
    print("   Server will start on: http://localhost:5000")
    print("   Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Run Streamlit with proper configuration
        cmd = [
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "5000",
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ]
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n\n👋 Track.lytix stopped")
    except Exception as e:
        print(f"\n❌ Error starting Track.lytix: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()