"""
Multi-Agent Playground - FastAPI Backend Server
==============================================
Main entry point for the FastAPI backend that handles agent simulation.

This file defines the core API endpoints that enable communication between
the frontend (Godot) and the backend agent system. It provides endpoints for:
- Planning agent actions based on current perception
- Confirming and updating agent state after action execution
- Retrieving current agent state

The server follows a two-step action protocol:
1. /agent_act/plan - Get next action plan from agent
2. /agent_act/confirm - Confirm execution and update agent memory
"""
from dotenv import load_dotenv
from typing import List
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.config.schema import AgentActionInput, AgentActionOutput, AgentPerception, StatusMsg, AgentPlanRequest, PlanActionResponse, AgentSummary
from backend.server.controller import plan_next_action
from backend.character_agent.agent_manager import agent_manager
from backend.objects.object_registry import object_registry, initialize_objects

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/agent_act/plan", response_model=List[PlanActionResponse])
def post_plan_action_batch(agent_ids: List[str]):
    """
    Step 1: Batched perception input → plan actions using LLM.
    (Does NOT update state yet.)
    """
    return [plan_next_action(agent_id) for agent_id in agent_ids]

# Get the list of all agents and their summaries
@app.get("/agents/init", response_model=List[AgentSummary])
def get_all_agents_init():
    """
    Return summary information for all agents (for frontend init).
    """
    agent_manager.preload_all_agents()
    return agent_manager.get_all_agent_summaries()

# Get the list of all interactive objects and their states
@app.get("/objects")
def get_objects():
    return [obj.to_dict() for obj in object_registry.values()]

# Optional: if you want to reset the objects to their initial state
@app.post("/objects/reset")
def reset_objects():
    initialize_objects()
    return {"status": "ok"}

