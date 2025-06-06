"""
Multi-Agent Playground - LLM Agent Implementation
=================================================
LLM-powered agent implementation using the Kani library with OpenAI's GPT-4o.

This module implements the LLMAgent class which combines:
- Kani's LLM interaction capabilities
- ActionsMixin for action functions (move, interact, perceive)
- Agent state management and perception processing
"""

import asyncio
import json
import os
from typing import Dict, Any, Optional
from kani import Kani
from kani.engines.openai import OpenAIEngine
from .actions import ActionsMixin
from .agent import Agent
from ..config.llm_config import LLMConfig


class LLMAgent(Kani, ActionsMixin):
    """
    Character agent for the Multi-Agent Playground.
    """
    
    def __init__(self, agent: Agent, api_key: Optional[str] = None):
        """
        Initialize the character agent with Kani engine and agent state.
        
        Args:
            agent (Agent): The agent instance containing state and configuration
            api_key (str, optional): OpenAI API key. If not provided, will try to get from environment.
        """
        # Set agent_id for ActionsMixin
        self.agent_id = agent.agent_id
        self.agent = agent
        
        # Get API key from environment if not provided
        if api_key is None:
            api_key = LLMConfig.get_openai_api_key()
        
        # Initialize Kani engine with GPT-4o
        engine = OpenAIEngine(
            api_key, 
            model=LLMConfig.OPENAI_MODEL,
            temperature=LLMConfig.OPENAI_TEMPERATURE,
            max_tokens=LLMConfig.OPENAI_MAX_TOKENS
        )
        
        # Initialize Kani with system prompt
        system_prompt = self._build_system_prompt()
        super().__init__(engine, system_prompt=system_prompt)
        
        # Initialize ActionsMixin
        ActionsMixin.__init__(self)
    
    def _build_system_prompt(self) -> str:
        """
        Build the system prompt that defines the agent's personality and capabilities.
        
        Returns:
            str: The system prompt for the LLM
        """
        agent_info = f"""
You are {self.agent.name}, a character in a multi-agent simulation.

PERSONALITY & BACKGROUND:
- Age: {self.agent.age}
- Innate traits: {self.agent.innate}
- Learned behaviors: {self.agent.learned}
- Current status: {self.agent.currently}
- Lifestyle: {self.agent.lifestyle}
- Living area: {self.agent.living_area}

DAILY REQUIREMENTS:
{chr(10).join(f"- {req}" for req in self.agent.daily_req)}

CURRENT CONTEXT:
- Current time: {self.agent.curr_time}
- Current location: {self.agent.curr_tile}
- Current activity: {self.agent.act_description}

CAPABILITIES:
You have three main actions available:
1. move(destination_coordinates, action_emoji) - Move to specific coordinates
2. interact(object, new_state, action_emoji) - Interact with objects to change their state
3. perceive(action_emoji) - Perceive objects and agents in your visible area

BEHAVIOR GUIDELINES:
- Always stay in character based on your personality traits
- Consider your daily requirements and current schedule
- React realistically to your environment and other agents
- Use appropriate emojis to represent your actions
- Make decisions based on your current state and visible environment
- Keep actions realistic and contextually appropriate

When deciding on actions:
1. Consider your current needs and daily requirements
2. Observe your environment through perception
3. Plan logical next steps based on your personality and goals
4. Choose appropriate emojis that match your action and mood

Respond naturally as {self.agent.first_name} would, and use the available action functions to interact with the world.
"""
        return agent_info
    
    async def plan_next_action(self, perception_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Plan the next action based on current perception and agent state.
        
        Args:
            perception_data (dict): Current perception data from the environment
            
        Returns:
            dict: Action JSON in the format expected by the frontend
        """
        # Update agent's perception
        self.agent.update_perception(perception_data)
        
        # Build context message for the LLM
        context_message = self._build_context_message(perception_data)
        
        # Get LLM response with function calling
        response = await self.chat_round(context_message)
        
        # The response should contain a function call result
        # If the LLM called one of our action functions, it will return the JSON
        if hasattr(response, 'function_calls') and response.function_calls:
            # Get the last function call result (should be our action)
            last_call = response.function_calls[-1]
            if hasattr(last_call, 'result') and isinstance(last_call.result, dict):
                return last_call.result
        
        # Fallback: if no function was called, default to perceive action
        return {
            "agent_id": self.agent_id,
            "action_type": "perceive",
            "content": {},
            "emoji": "👀"
        }
    
    def _build_context_message(self, perception_data: Dict[str, Any]) -> str:
        """
        Build a context message describing the current situation to the LLM.
        
        Args:
            perception_data (dict): Current perception data
            
        Returns:
            str: Context message for the LLM
        """
        message_parts = [
            f"Current time: {self.agent.curr_time}",
            f"Your current location: {self.agent.curr_tile}",
            f"You are currently: {self.agent.currently}",
        ]
        
        # Add visible objects information
        visible_objects = perception_data.get("visible_objects", {})
        if visible_objects:
            message_parts.append("\nVisible objects around you:")
            for obj_name, obj_info in visible_objects.items():
                state = obj_info.get("state", "unknown")
                location = obj_info.get("location", "unknown")
                message_parts.append(f"- {obj_name}: {state} (at {location})")
        else:
            message_parts.append("\nNo objects are currently visible.")
        
        # Add visible agents information
        visible_agents = perception_data.get("visible_agents", [])
        if visible_agents:
            message_parts.append(f"\nOther agents nearby: {', '.join(visible_agents)}")
        else:
            message_parts.append("\nNo other agents are currently visible.")
        
        # Add recent memories if available
        if self.agent.memory:
            recent_memories = self.agent.memory[-3:]  # Last 3 memories
            message_parts.append("\nRecent memories:")
            for memory in recent_memories:
                message_parts.append(f"- {memory['timestamp']}: {memory['event']} (at {memory['location']})")
        
        message_parts.append("\nWhat would you like to do next? Please use one of your available actions (move, interact, or perceive).")
        
        return "\n".join(message_parts)


async def call_llm_for_action(agent_state: Dict[str, Any], perception_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Replacement function for call_llm_or_ReAct that uses the Kani-based LLM agent.
    
    Args:
        agent_state (dict): Current agent state
        perception_data (dict): Current perception data
        
    Returns:
        dict: Action JSON in the format expected by the frontend
    """
    # Create Agent instance from state
    agent_dir = f"data/agents/{agent_state['agent_id']}"
    agent = Agent(agent_dir)
    
    # Create LLM agent
    llm_agent = LLMAgent(agent)
    
    # Plan next action
    action_result = await llm_agent.plan_next_action(perception_data)
    
    return action_result


# Synchronous wrapper for compatibility with existing code
def call_llm_or_ReAct(agent_state: Dict[str, Any], perception_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synchronous wrapper for the LLM action planning function.
    This replaces the original call_llm_or_ReAct function.
    
    Args:
        agent_state (dict): Current agent state
        perception_data (dict): Current perception data
        
    Returns:
        dict: Action JSON in the format expected by the frontend
    """
    return asyncio.run(call_llm_for_action(agent_state, perception_data)) 