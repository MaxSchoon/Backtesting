#!/usr/bin/env python3
"""
Simple launcher for the Investment Strategy Backtester
"""

import subprocess
import sys
import os

def main():
    """Launch the backtesting app"""
    
    print("🚀 Investment Strategy Backtester")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists('src/backtesting/interfaces/web_app.py'):
        print("❌ Error: Web app not found.")
        print("Please run this script from the project root directory.")
        sys.exit(1)
    
    print("✅ Found web app")
    
    # Check if streamlit is installed
    try:
        import streamlit
        print("✅ Streamlit is installed")
    except ImportError:
        print("❌ Streamlit not found. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'streamlit'])
    
    print("\n🌐 Starting web interface...")
    print("📱 The app will open in your browser at http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 40)
    
    try:
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'src/backtesting/interfaces/web_app.py'])
    except KeyboardInterrupt:
        print("\n👋 App stopped. Thanks for using the Investment Strategy Backtester!")

if __name__ == "__main__":
    main()
