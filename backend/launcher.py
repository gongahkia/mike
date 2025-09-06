#!/usr/bin/env python3
import sys
import os

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Now import and run the app
if __name__ == '__main__':
    # Import with the correct path setup
    from app import app
    print("🚀 Backend server starting on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
