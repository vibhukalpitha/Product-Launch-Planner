#!/usr/bin/env python3
"""
Apple Market Analyzer Dashboard Launcher
This script provides an easy way to launch the Streamlit dashboard
"""

import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit',
        'pandas',
        'numpy',
        'matplotlib',
        'seaborn',
        'plotly',
        'Pillow'
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
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def check_data_files():
    """Check if required data files exist"""
    required_files = [
        'Walmart_customer_fixed.csv',
        'apple_ratings/apple_ratings_summary.txt',
        'apple_sales/apple_sales_summary.txt',
        'price_elasticity/price_elasticity_summary.txt',
        'product_domination/product_domination_summary.txt'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("⚠️  Missing data files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("\n💡 Some features may not work without these files")
        return False
    
    print("✅ All required data files found")
    return True

def launch_dashboard():
    """Launch the Streamlit dashboard"""
    try:
        print("🚀 Launching Apple Market Analyzer Dashboard...")
        print("📊 Dashboard will open in your default browser")
        print("🔗 URL: http://localhost:8501")
        print("\n" + "="*50)
        
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error launching dashboard: {str(e)}")
        print("💡 Try running manually: streamlit run app.py")

def main():
    """Main function"""
    print("🍎 Apple Market Analyzer Dashboard Launcher")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("❌ app.py not found in current directory")
        print("💡 Make sure you're in the Daniru folder")
        return
    
    # Check requirements
    if not check_requirements():
        return
    
    # Check data files
    check_data_files()
    
    print("\n" + "="*50)
    
    # Launch dashboard
    launch_dashboard()

if __name__ == "__main__":
    main()
