"""
Server launcher for AI Exam System
"""
import os
import sys
import webbrowser
from threading import Timer
from app import app

def open_browser():
    """Open browser after server starts"""
    webbrowser.open('http://localhost:5000/')

if __name__ == '__main__':
    print("="*60)
    print("AI-POWERED ORAL EXAM SYSTEM - WEB INTERFACE")
    print("="*60)
    print("\nStarting Flask server...")
    print("Dashboard will open at: http://localhost:5000/")
    print("\nPress CTRL+C to stop the server\n")

    # Open browser after 1.5 seconds
    Timer(1.5, open_browser).start()

    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
