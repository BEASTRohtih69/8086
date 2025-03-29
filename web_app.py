#!/usr/bin/env python3
"""
8086 Simulator - Web Application
A web-based interface for the 8086 microprocessor simulator.
"""

import os
from app import app

if __name__ == "__main__":
    # Create temp directory if it doesn't exist
    os.makedirs('temp', exist_ok=True)
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)