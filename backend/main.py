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
from fastapi.responses import JSONResponse

from backend.config.schema import (
    AgentActionInput, AgentActionOutput, AgentPerception, 
    StatusMsg, AgentPlanRequest, PlanActionResponse, AgentSummary
)
from backend.server.controller import plan_next_action
from backend.character_agent.agent_manager import agent_manager
from backend.objects.object_registry import object_registry, initialize_objects

# NEW: Import your game loop singleton
# TODO: need to implement specific details of game loop and text adventure logic 
from backend.game_loop import game_loop

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production!
    allow_credentials=True,
    allow_methods=["GET", "POST"], # Allow POST only for reset
    allow_headers=["*"],
)

# NEW: Start the background game loop at server startup
@app.on_event("startup")
def on_startup():
    game_loop.start_background_loop()

@app.post("/agent_act/plan", response_model=List[PlanActionResponse])
def post_plan_action_batch(agent_ids: List[str]):
    """
    Step 1: Batched perception input → plan actions using LLM.
    (Does NOT update state yet.)
    """
    return [plan_next_action(agent_id) for agent_id in agent_ids]

# New: Event polling endpoint (optional, for frontend to get recent actions)
@app.get("/actions")
def get_actions(since_tick: int = 0):
    return game_loop.get_event_log(since_tick)

# Get the list of all agents and their summaries
@app.get("/agents/init", response_model=List[AgentSummary])
def get_all_agents_init():
    """
    Return the complete state of the game world, including agents, 
    objects, and locations.
    """
    if not game_controller:
        raise HTTPException(status_code=500, detail="Game not initialized")
    
    return game_controller.get_world_state()

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
