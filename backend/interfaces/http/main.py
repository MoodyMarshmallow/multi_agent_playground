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
import argparse
import sys
import os
from contextlib import asynccontextmanager

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Import the game controller and logging
from ...game_loop import GameLoop
from ...config.schema import WorldStateResponse, GameEvent, GameEventList, StatusMsg, GameStatus, AgentStateResponse, GameObject, AgentActionOutput
from ...log_config import setup_logging

# Setup logging based on environment variable (for uvicorn compatibility)
verbose_mode = os.getenv("VERBOSE", "false").lower() in ("true", "1", "yes")
setup_logging(verbose=verbose_mode)

# Global game controller instance
game_controller: Optional[GameLoop] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup
    global game_controller
    game_controller = GameLoop()
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


@app.get("/agent_act/next", response_model=List[AgentActionOutput])
async def get_latest_agent_actions():
    """
    Poll the latest planned actions for all agents.
    Returns only the actions that haven't been served yet.
    Each returned action is marked as served to prevent duplicate delivery.
    """
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game not initialized")
    
    # Get unserved events from the event queue
    unserved_events = game_controller.get_unserved_events()
    return unserved_events

# check if this is the same as get world state, and do we need this?
@app.get("/agents/states", response_model=List[AgentStateResponse])
async def get_agents_states(agent_ids: List[str]):
    """
    Get the current state of multiple agents.
    """
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game not initialized")
    states = []
    for agent_id in agent_ids:
        try:
            state = game_controller.get_agent_state(agent_id)
            states.append(AgentStateResponse(**state))
        except KeyError:
            continue  # skip missing
    return states



@app.get("/objects", response_model=List[GameObject])
async def get_objects():
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game not initialized")
    return [GameObject(**obj) for obj in game_controller.objects_registry.values()]



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

@app.get("/game/events", response_model=GameEventList)
async def get_game_events(since_timestamp: str = ""):
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game not initialized")
    events = game_controller.get_events_since(since_timestamp)
    # Convert AgentActionOutput to GameEvent format
    game_events = []
    for event in events:
        game_events.append(GameEvent(
            id=hash(event.timestamp) if event.timestamp else 0,
            type="agent_action",
            timestamp=event.timestamp or "",
            data=event.dict()
        ))
    return GameEventList(events=game_events)

@app.post("/game/reset", response_model=StatusMsg)
async def reset_game():
    if game_controller:
        await game_controller.reset()
    return StatusMsg(status="ok")

@app.get("/game/status", response_model=GameStatus)
async def get_game_status():
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game not initialized")
    return GameStatus(**game_controller.get_game_status())

@app.post("/game/pause", response_model=StatusMsg)
async def pause_game():
    """Pause the game loop."""
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game not initialized")
    if not game_controller.is_running:
        return StatusMsg(status="already_paused")
    await game_controller.stop()
    return StatusMsg(status="paused")

@app.post("/game/resume", response_model=StatusMsg)
async def resume_game():
    """Resume the game loop."""
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game not initialized")
    if game_controller.is_running:
        return StatusMsg(status="already_running")
    await game_controller.start()
    return StatusMsg(status="resumed")


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Multi-Agent Playground Backend Server")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Enable verbose logging (show INFO+ messages)")
    parser.add_argument("--reload", action="store_true", 
                       help="Enable auto-reload for development")
    parser.add_argument("--port", type=int, default=8000,
                       help="Port to run the server on (default: 8000)")
    args = parser.parse_args()
    
    # Setup logging based on verbose flag
    setup_logging(verbose=args.verbose)
    
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=args.port,
        reload=args.reload,
        log_level="info"
    )