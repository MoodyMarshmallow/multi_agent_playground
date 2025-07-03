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

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.config.schema import WorldStateResponse

# Import the game controller
from .game_controller import GameController

app = FastAPI(title="Multi-Agent Playground", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production!
    allow_credentials=True,
    allow_methods=["GET", "POST"], # Allow POST only for reset
    allow_headers=["*"],
)

# Global game controller instance
game_controller: Optional[GameController] = None

@app.on_event("startup")
async def startup_event():
    """Initialize and start the game controller on startup."""
    global game_controller
    game_controller = GameController()
    await game_controller.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Stop the game controller on shutdown."""
    if game_controller:
        await game_controller.stop()

# This is an example how we can wrap up the api call response in a schema
# based on new text adventure game schema
@app.get("/world_state", response_model=WorldStateResponse)
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