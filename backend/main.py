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
import json
import os
from pathlib import Path

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import schemas from old backend (we'll adapt these)
from .config.schema import (
    AgentSummary, 
    PlanActionResponse,
    AgentPerception,
    AgentActionInput,
    AgentActionOutput,
    BackendAction,
    MoveBackendAction,
    ChatBackendAction,
    InteractBackendAction,
    PerceiveBackendAction,
    Message
)

# Import text adventure games framework
from .text_adventure_games.games import Game
from .text_adventure_games.things import Character, Location, Item

# Import multi-agent components
from .agent_manager import AgentManager, KaniAgent
from .game_controller import GameController

app = FastAPI(title="Multi-Agent Playground", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global game controller instance
game_controller: Optional[GameController] = None

@app.on_event("startup")
async def startup_event():
    """Initialize the game world and agents on startup."""
    global game_controller
    game_controller = GameController()
    await game_controller.initialize()

@app.post("/agent_act/plan", response_model=List[PlanActionResponse])
async def post_plan_action_batch(agent_ids: List[str]):
    """
    Step 1: Batched perception input → plan actions using LLM.
    (Does NOT update state yet.)
    """
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game not initialized")
    
    results = []
    for agent_id in agent_ids:
        try:
            result = await game_controller.plan_agent_action(agent_id)
            results.append(result)
        except Exception as e:
            # Return a default action on error
            results.append(PlanActionResponse(
                action=AgentActionOutput(
                    agent_id=agent_id,
                    action=PerceiveBackendAction(action_type="perceive"),
                    emoji="❌",
                    current_room=None
                ),
                perception=AgentPerception()
            ))
    
    return results

@app.post("/agent_act/confirm")
async def post_confirm_action(action_input: AgentActionInput):
    """
    Step 2: Confirm action execution and update game state.
    """
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game not initialized")
    
    try:
        await game_controller.confirm_agent_action(action_input)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/agents/init", response_model=List[AgentSummary])
async def get_all_agents_init():
    """
    Return summary information for all agents (for frontend init).
    """
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game not initialized")
    
    return game_controller.get_all_agent_summaries()

@app.get("/agents/{agent_id}/state")
async def get_agent_state(agent_id: str):
    """
    Get current state of a specific agent.
    """
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game not initialized")
    
    try:
        return game_controller.get_agent_state(agent_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

@app.get("/objects")
async def get_objects():
    """
    Get all interactive objects and their states.
    """
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game not initialized")
    
    return game_controller.get_all_objects()

@app.post("/objects/reset")
async def reset_objects():
    """
    Reset all objects to their initial state.
    """
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game not initialized")
    
    game_controller.reset_objects()
    return {"status": "ok"}

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
    Reset the entire game to initial state.
    """
    global game_controller
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