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

def get_local_ip():
    """Get local IP address for network access"""
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def main():
    """Main entry point"""
    print("🏎️  Track.lytix - F1 Data Analysis Platform")
    print("=" * 60)
    print("   Professional F1 Analytics & Telemetry Platform")
    print("   ✓ Enhanced Brake Configurations Analysis")
    print("   ✓ Composite Performance Index Calculations")
    print("   ✓ Advanced Telemetry & Race Strategy Analytics")
    print("=" * 60)
    
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
    
    # Get network information
    local_ip = get_local_ip()
    
    # Start Streamlit application
    print("\n🚀 Starting Track.lytix F1 Platform...")
    print("=" * 60)
    print("📱 ACCESS URLS:")
    print(f"   🖥️  Local:    http://localhost:5000")
    print(f"   🌐 Network:  http://{local_ip}:5000")
    print(f"   ☁️  Online:   http://0.0.0.0:5000 (if deployed)")
    print("=" * 60)
    print("📊 AVAILABLE ANALYSES:")
    print("   • Telemetry Comparison & Speed Analysis")
    print("   • Brake Configurations & Efficiency")
    print("   • Composite Performance Index")
    print("   • Tire Strategy & Degradation")
    print("   • Track Dominance Mapping")
    print("   • Advanced Driver Analytics")
    print("=" * 60)
    print("⚠️  Press Ctrl+C to stop the server")
    print("")
    
    try:
        # Run Streamlit with proper configuration for both local and online testing
        cmd = [
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "5000",
            "--server.address", "0.0.0.0",
            "--server.headless", "true",
            "--server.runOnSave", "true",
            "--server.allowRunOnSave", "true"
        ]
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n\n👋 Track.lytix F1 Platform stopped gracefully")
        print("   Thank you for using Track.lytix!")
    except Exception as e:
        print(f"\n❌ Error starting Track.lytix: {e}")
        print("   Please check your Python installation and dependencies")
        sys.exit(1)

if __name__ == "__main__":
    main()