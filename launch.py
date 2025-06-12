#!/usr/bin/env python3
"""
Simple launcher for Ultimate RSI Tracker
"""

import subprocess
import sys
import os

def main():
    print("🚀 Launching Ultimate RSI Tracker...")
    print("📊 Professional Stock Analysis Dashboard")
    print("")
    
    # Check if main file exists
    if os.path.exists('ultimate_rsi_tracker_complete.py'):
        launcher_file = 'ultimate_rsi_tracker_complete.py'
        print("✅ Found complete version")
    elif os.path.exists('ultimate_rsi_tracker.py'):
        launcher_file = 'ultimate_rsi_tracker.py'
        print("✅ Found main version")
    else:
        print("❌ Error: RSI tracker files not found")
        print("Please ensure you're in the correct directory.")
        return
    
    try:
        # Launch the application
        print(f"🔧 Starting {launcher_file}...")
        subprocess.run([sys.executable, launcher_file])
    except KeyboardInterrupt:
        print("\n👋 RSI Tracker closed by user")
    except Exception as e:
        print(f"❌ Error launching RSI Tracker: {e}")
        print("📋 Try running directly: python ultimate_rsi_tracker_complete.py")

if __name__ == "__main__":
    main()
