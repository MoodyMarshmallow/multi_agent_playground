#!/usr/bin/env python3
"""
Multi-Agent Playground Backend Server Startup Script
===================================================

This script starts the combined backend server that integrates:
- Text adventure games framework
- Multi-agent support with Kani LLM agents
- HTTP endpoints for frontend communication

Usage:
    python run_backend.py

The server will start on http://localhost:8000
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up environment
os.environ.setdefault("PYTHONPATH", str(project_root))

if __name__ == "__main__":
    import uvicorn
    from backend.main import app
    
    print("🏠 Multi-Agent Playground Backend")
    print("================================")
    print("Starting server...")
    print("API docs will be available at: http://localhost:8000/docs")
    print("Agents endpoint: http://localhost:8000/agents/init")
    print("Objects endpoint: http://localhost:8000/objects")
    print("Game events endpoint: http://localhost:8000/game/events")
    print("\nPress Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000,
            log_level="info",
            reload=False  # Set to True for development
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("\nMake sure you have all dependencies installed:")
        print("pip install fastapi uvicorn kani openai python-dotenv")
        sys.exit(1) 