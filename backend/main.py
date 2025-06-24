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
from backend.logging import setup_logging
setup_logging()
import logging
logger = logging.getLogger(__name__)
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.config.schema import AgentActionInput, AgentActionOutput, AgentPerception, StatusMsg, AgentPlanRequest
from backend.server.controller import plan_next_action, confirm_action_and_update


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/agent_act/plan", response_model=List[AgentActionOutput])
def post_plan_action_batch(inputs: List[AgentPlanRequest]):
    """
    Step 1: Batched perception input → plan actions using LLM.
    (Does NOT update state yet.)
    """
    logger.info(f"Received /agent_act/plan request for {len(inputs)} agents: {[input.agent_id for input in inputs]}")
    try:
        results = [plan_next_action(input.agent_id, input.perception) for input in inputs]
        logger.info(f"Planned actions for {len(results)} agents.")
        return results
    except Exception as e:
        logger.error(f"Error in /agent_act/plan: {e}")
        raise


@app.post("/agent_act/confirm", response_model=List[StatusMsg])
def post_confirm_action_batch(agent_msgs: List[AgentActionInput]):
    """
    Step 2: Batched post-confirmation input → update state and memory.
    """
    logger.info(f"Received /agent_act/confirm request for {len(agent_msgs)} agents: {[msg.agent_id for msg in agent_msgs]}")
    try:
        for msg in agent_msgs:
            logger.debug(f"Confirming action for agent {msg.agent_id}: {msg.action}")
            confirm_action_and_update(msg)
        logger.info(f"Confirmed actions for {len(agent_msgs)} agents.")
        return [StatusMsg(status="ok") for _ in agent_msgs]
    except Exception as e:
        logger.error(f"Error in /agent_act/confirm: {e}")
        raise

