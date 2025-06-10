"""
Multi-Agent Playground - Server Package
=======================================
Server package containing FastAPI controller logic for agent action processing.

This package implements the two-step action processing pipeline:
1. Action Planning: Receives perception data and plans next action  
2. Action Confirmation: Updates agent state and memory after action execution

The controller acts as an intermediary between the FastAPI endpoints
and the agent system, handling the flow of perception data, action
planning, and state updates for all agents in the simulation.

Author: Multi-Agent Playground Team
Version: 1.0.0
"""

from .controller import plan_next_action, confirm_action_and_update

__version__ = "1.0.0"

__all__ = [
    "plan_next_action",
    "confirm_action_and_update",
]
