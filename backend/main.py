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
from backend.config.schema import AgentActionInput, AgentActionOutput, AgentPerception, StatusMsg, AgentPlanRequest, PlanActionResponse
from backend.server.controller import plan_next_action


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/agent_act/plan", response_model=List[PlanActionResponse])
def post_plan_action_batch(inputs: List[AgentPlanRequest]):
    """
    Step 1: Batched perception input → plan actions using LLM.
    (Does NOT update state yet.)
    """
    return [plan_next_action(input.agent_id) for input in inputs]


# @app.post("/agent_act/confirm", response_model=List[StatusMsg])
# def post_confirm_action_batch(agent_msgs: List[AgentActionInput]):
#     """
#     Step 2: Batched post-confirmation input → update state and memory.
#     """
#     for msg in agent_msgs:
#         confirm_action_and_update(msg)
#     return [StatusMsg(status="ok") for _ in agent_msgs]

# # Get the list of all interactive objects and their states
# @app.get("/objects")
# def get_objects():
#     return [obj.to_dict() for obj in object_registry.values()]
