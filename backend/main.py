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
from .config.schema import WorldStateResponse, GameEvent, GameEventList, StatusMsg, GameStatus, PlanActionResponse, AgentStateResponse, GameObject, AgentActionOutput

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


@app.get("/agent_act/next", response_model=List[AgentActionOutput])
async def get_latest_agent_actions():
    """
    Poll the latest planned actions for all agents.
    Returns only the actions that are available.
    Each returned action is removed from the backend store to prevent duplicate delivery.
    """
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game not initialized")
    
    actions = []
    # Copy the keys to avoid modifying the dict while iterating
    for agent_id in list(game_controller.latest_agent_actions.keys()):
        plan = game_controller.latest_agent_actions[agent_id]
        actions.append(plan)
        # Remove after serving, so it's not returned next poll
        del game_controller.latest_agent_actions[agent_id]
    return actions

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
async def get_game_events(since_id: int = 0):
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game not initialized")
    events = game_controller.get_events_since(since_id)
    # Ensure each event matches GameEvent
    return GameEventList(events=[GameEvent(**e) for e in events])

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)