"""
Multi-Agent Playground - Combined FastAPI Backend Server
======================================================
Main entry point for the FastAPI backend that handles multi-agent simulation
using the text adventure games framework.

This combines:
- HTTP endpoints from the old backend for frontend communication
- Text adventure games framework as the underlying game engine
- Multi-agent support with turn-based system
- Agent manager for LLM-powered agents
"""

from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import asyncio
from contextlib import asynccontextmanager

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Import the game controller
from .game_controller import GameController

# Global game controller instance
game_controller: Optional[GameController] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup
    global game_controller
    game_controller = GameController()
    await game_controller.start()
    
    yield
    
    # Shutdown
    if game_controller:
        await game_controller.stop()

app = FastAPI(title="Multi-Agent Playground", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production!
    allow_credentials=True,
    allow_methods=["GET", "POST"], # Allow POST only for reset
    allow_headers=["*"],
)

@app.get("/world_state")
async def get_world_state():
    """
    Return the complete state of the game world, including agents, 
    objects, and locations.
    """
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game not initialized")
    state = game_controller.get_world_state()
    return WorldStateResponse(**state)

@app.get("/game/events")
async def get_game_events(since_id: int = 0):
    """
    Get game events since the specified ID for frontend visualization.
    """
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game not initialized")
    
    return game_controller.get_events_since(since_id)

@app.post("/game/reset")
async def reset_game():
    """
    Reset the entire game to its initial state.
    """
    if game_controller:
        await game_controller.reset()
    return {"status": "ok"}

@app.get("/game/status")
async def get_game_status():
    """
    Get current game status and statistics.
    """
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game not initialized")
    
    return game_controller.get_game_status()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)