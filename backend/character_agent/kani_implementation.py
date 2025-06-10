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
import ssl
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, AsyncGenerator
from kani import Kani
from kani.engines.openai import OpenAIEngine
from kani.models import ChatMessage

from .actions import ActionsMixin
from .agent import Agent

# Add the backend directory to Python path for imports
backend_dir: Path = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from ..config.llm_config import LLMConfig


class LLMAgent(Kani, ActionsMixin):
    """
    Character agent for the Multi-Agent Playground.
    """
    
    agent_id: str
    agent: Agent
    
    def __init__(self, agent: Agent, api_key: Optional[str] = None) -> None:
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
        # Initialize OpenAI engine with proper SSL handling
        try:
            engine: OpenAIEngine = OpenAIEngine(
                api_key, 
                model=LLMConfig.OPENAI_MODEL,
                temperature=LLMConfig.OPENAI_TEMPERATURE,
                max_tokens=LLMConfig.OPENAI_MAX_TOKENS
            )
        except OSError as e:
            if "Invalid argument" in str(e) or "SSL" in str(e):
                # Handle SSL issues securely by updating certificate bundle
                import httpx
                import ssl
                import certifi
                
                # Create SSL context with proper certificate verification
                ssl_context: ssl.SSLContext = ssl.create_default_context(cafile=certifi.where())
                ssl_context.check_hostname = True
                ssl_context.verify_mode = ssl.CERT_REQUIRED
                
                # Create HTTP client with proper SSL configuration
                http_client: httpx.AsyncClient = httpx.AsyncClient(
                    verify=ssl_context,
                    timeout=30.0,
                    follow_redirects=True
                )
                
                from openai import AsyncOpenAI
                try:
                    openai_client: AsyncOpenAI = AsyncOpenAI(
                        api_key=api_key,
                        http_client=http_client
                    )
                    
                    engine = OpenAIEngine(
                        model=LLMConfig.OPENAI_MODEL,
                        temperature=LLMConfig.OPENAI_TEMPERATURE,
                        max_tokens=LLMConfig.OPENAI_MAX_TOKENS,
                        client=openai_client
                    )
                    print("Using custom SSL configuration with certificate verification")
                except Exception as ssl_error:
                    # If SSL still fails, provide clear error message instead of bypassing security
                    raise RuntimeError(
                        f"SSL configuration failed: {ssl_error}. "
                        "Please update your SSL certificates or check your network configuration. "
                        "Consider updating certifi package: pip install --upgrade certifi"
                    ) from ssl_error
            else:
                raise
        
        # Initialize Kani with system prompt
        system_prompt: str = self._build_system_prompt()
        super().__init__(engine, system_prompt=system_prompt)
        
        # Initialize ActionsMixin
        ActionsMixin.__init__(self)
    
    def _build_system_prompt(self) -> str:
        """
        Build the system prompt that defines the agent's personality and capabilities.
        
        Returns:
            str: The system prompt for the LLM
        """
        agent_info: str = f"""
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
3. perceive(content, action_emoji) - Perceive objects and agents in your visible area

BEHAVIOR GUIDELINES:
- Always stay in character based on your personality traits
- Consider your daily requirements and current schedule
- React realistically to your environment and other agents
- Use appropriate emojis to represent your actions
- Make decisions based on your current state and visible environment
- Keep actions realistic and contextually appropriate

JSON FORMATTING GUIDELINES:
- Always use double quotes (\\") to label strings in the files.

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
        context_message: str = self._build_context_message(perception_data)
        
        # Get LLM response with function calling - iterate through the async generator
        action_result: Optional[Dict[str, Any]] = None
        message: ChatMessage
        async for message in self.full_round(context_message):
            # Check if this is a function result message
            if message.role.value == 'function' and message.content:
                # Try to parse the function result as Dict.
                try:
                    parsed_result: Dict[str, Any] = eval(message.content)
                    # Check if this looks like one of our action results
                    if isinstance(parsed_result, dict) and 'action_type' in parsed_result:
                        action_result = parsed_result
                        break
                except (json.JSONDecodeError, TypeError):
                    # If parsing fails, continue looking for other messages
                    continue
        
        # If no action was determined, default to perceive
        if not action_result:
            action_result: Dict[str, Any] = {
                "agent_id": self.agent_id,
                "action_type": "perceive",
                "content": {},
                "emoji": "👀"
            }
        
        return action_result
    

    def _build_context_message(self, perception_data: Dict[str, Any]) -> str:
        """
        Build a context message describing the current situation to the LLM.
        
        Args:
            perception_data (dict): Current perception data
            
        Returns:
            str: Context message for the LLM
        """
        message_parts: List[str] = [
            f"Current time: {self.agent.curr_time}",
            f"Your current location: {self.agent.curr_tile}",
            f"You are currently: {self.agent.currently}",
        ]
        
        # Add visible objects information
        visible_objects: Dict[str, Any] = perception_data.get("visible_objects", {})
        if visible_objects:
            message_parts.append("\nVisible objects around you:")
            obj_name: str
            obj_info: Dict[str, Any]
            for obj_name, obj_info in visible_objects.items():
                state: str = obj_info.get("state", "unknown")
                location: str = obj_info.get("location", "unknown")
                message_parts.append(f"- {obj_name}: {state} (at {location})")
        else:
            message_parts.append("\nNo objects are currently visible.")
        
        # Add visible agents information
        visible_agents: List[str] = perception_data.get("visible_agents", [])
        if visible_agents:
            message_parts.append(f"\nOther agents nearby: {', '.join(visible_agents)}")
        else:
            message_parts.append("\nNo other agents are currently visible.")
        
        # Add recent memories if available
        if self.agent.memory:
            recent_memories: List[Dict[str, Any]] = self.agent.memory[-3:]  # Last 3 memories
            message_parts.append("\nRecent memories:")
            memory: Dict[str, Any]
            for memory in recent_memories:
                message_parts.append(f"- {memory['timestamp']}: {memory['event']} (at {memory['location']})")
        
        message_parts.append("\nWhat would you like to do next? Please use one of your available actions (move, interact, or perceive).")
        
        return "\n".join(message_parts)


    @staticmethod
    async def call_llm_for_action(agent_state: Dict[str, Any], perception_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Replacement function for call_llm_agent that uses the Kani-based LLM agent.
        
        Args:
            agent_state (dict): Current agent state
            perception_data (dict): Current perception data
            
        Returns:
            dict: Action JSON in the format expected by the frontend
        """
        # Create Agent instance from state
        agent_dir: str = f"data/agents/{agent_state['agent_id']}"
        agent: Agent = Agent(agent_dir)
        
        # Create LLM agent
        llm_agent: LLMAgent = LLMAgent(agent)
        
        # Plan next action
        action_result: Dict[str, Any] = await llm_agent.plan_next_action(perception_data)
        
        return action_result


    # Synchronous wrapper for compatibility with existing code
    @staticmethod
    def call_llm_agent(agent_state: Dict[str, Any], perception_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronous wrapper for the LLM action planning function.
        This replaces the original call_llm_agent function.
        
        Args:
            agent_state (dict): Current agent state
            perception_data (dict): Current perception data
            
        Returns:
            dict: Action JSON in the format expected by the frontend
        """
        return asyncio.run(LLMAgent.call_llm_for_action(agent_state, perception_data)) 
