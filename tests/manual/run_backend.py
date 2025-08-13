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
import argparse
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up environment
os.environ.setdefault("PYTHONPATH", str(project_root))

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Multi-Agent Playground Backend Server (Manual Startup)")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Enable verbose logging (show INFO+ messages)")
    args = parser.parse_args()
    
    # Setup logging
    from backend.log_config import setup_logging
    setup_logging(verbose=args.verbose)
    
    import uvicorn
    from backend.interfaces.http.main import app
    
    print("🏠 Multi-Agent Playground Backend")
    print("================================")
    print("Starting server...")
    print("API docs will be available at: http://localhost:8000/docs")
    print("Agents endpoint: http://localhost:8000/agents/init")
    print("Objects endpoint: http://localhost:8000/objects")
    print("Game events endpoint: http://localhost:8000/game/events")
    if args.verbose:
        print("Verbose logging: ENABLED (INFO+ messages)")
    else:
        print("Verbose logging: DISABLED (WARNING+ messages only)")
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