#!/usr/bin/env python3
"""
Flask Portfolio Application
Run this script to start the development server
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    try:
        from app import app
        print("🚀 Starting Flask Portfolio Application...")
        print("📁 Static files: static/")
        print("📄 Templates: templates/")
        print("🌐 Server will be available at: http://localhost:5000")
        print("🛑 Press Ctrl+C to stop the server")
        print("-" * 50)
        
        app.run(debug=True, host='0.0.0.0', port=5000)
    except ImportError as e:
        print("❌ Error: Flask not installed!")
        print("📦 Please install requirements first:")
        print("   pip install -r requirements.txt")
        print(f"   Error details: {e}")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
