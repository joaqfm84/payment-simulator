#!/usr/bin/env python3
"""
Startup script for the Canadian Wire Transfer Simulator
"""

import os
import sys
from app import app

if __name__ == '__main__':
    print("🇨🇦 Starting Canadian Wire Transfer Simulator...")
    print("📱 Frontend: http://localhost:5000")
    print("🔧 API Health: http://localhost:5000/api/health")
    print("🚀 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Shutting down Canadian Wire Transfer Simulator...")
        sys.exit(0) 