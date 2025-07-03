"""
Arush LLM - Kani Agent Implementation
====================================
Main KaniAgent class that extends Kani with optimized agent capabilities.

This module provides the core KaniAgent class which integrates:
- Kani framework for LLM interactions
- Four core actions: perceive, chat, move, interact
- Memory and location management
- Response parsing and validation
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from kani import Kani, ai_function
from kani.engines.openai import OpenAIEngine

# Add the backend directory to Python path for imports
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from backend.config.llm_config import LLMConfig
from ..utils.prompts import PromptTemplates
from ..utils.parsers import ResponseParser, ActionValidator
from .memory import AgentMemory, MemoryContextBuilder
from .location import LocationTracker


class KaniAgentError(Exception):
    """Custom exception for Kani agent-related errors"""
    pass


class KaniAgent(Kani):
    """
    Main agent class extending Kani with four core capabilities:
    1. Perceive - observe environment 
    2. Chat - communicate with other agents
    3. Move - navigate in space
    4. Interact - manipulate objects
    """
    
    def __init__(self, agent_data: Dict[str, Any], agent_dir: str, api_key: Optional[str] = None):
        """
        Initialize KaniAgent with agent data and components.
        
        Args:
            agent_data (Dict[str, Any]): Agent configuration from agent.json
            agent_dir (str): Path to agent directory
            api_key (str, optional): OpenAI API key. If not provided, will try to get from environment.
        """
        self.agent_id = agent_data["agent_id"]
        self.agent_data = agent_data
        self.agent_dir = Path(agent_dir)
        
        # Initialize arush_llm components
        self.memory = AgentMemory(self.agent_id, agent_dir)
        self.location_tracker = LocationTracker(self.agent_id, agent_dir)
        self.memory_context_builder = MemoryContextBuilder(self.memory)
        
        # Runtime perception data
        self.current_perception = {}
        
        # Get API key from environment if not provided
        if api_key is None:
            api_key = LLMConfig.get_openai_api_key()
        
        # Initialize Kani engine
        engine = self._create_kani_engine(api_key)
        
        # Build system prompt
        system_prompt = self._build_system_prompt()
        
        # Initialize parent Kani class
        super().__init__(engine, system_prompt=system_prompt)
    
    def _create_kani_engine(self, api_key: str) -> OpenAIEngine:
        """Create configured Kani engine using existing config."""
        try:
            return OpenAIEngine(
                api_key,
                model=LLMConfig.OPENAI_MODEL,
                temperature=LLMConfig.OPENAI_TEMPERATURE,
                max_tokens=LLMConfig.OPENAI_MAX_TOKENS
            )
        except OSError as e:
            if "Invalid argument" in str(e) or "SSL" in str(e):
                # Handle SSL issues in development environments
                import httpx
                import ssl
                from openai import AsyncOpenAI
                
                # Create custom HTTP client with SSL handling
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
                http_client = httpx.AsyncClient(
                    verify=False,
                    timeout=30.0
                )
                
                openai_client = AsyncOpenAI(
                    api_key=api_key,
                    http_client=http_client
                )
                
                return OpenAIEngine(
                    model=LLMConfig.OPENAI_MODEL,
                    temperature=LLMConfig.OPENAI_TEMPERATURE,
                    max_tokens=LLMConfig.OPENAI_MAX_TOKENS,
                    client=openai_client
                )
            else:
                raise
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt that defines the agent's personality and capabilities."""
        return PromptTemplates.build_system_prompt(self.agent_data)
    
    async def safe_kani_call(self, prompt: str) -> str:
        """Wrapper for Kani calls with retry logic."""
        for attempt in range(LLMConfig.KANI_RETRY_ATTEMPTS):
            try:
                response = await asyncio.wait_for(
                    self.chat_round(prompt),
                    timeout=LLMConfig.KANI_TIMEOUT
                )
                return response.text
            except Exception as e:
                if attempt == LLMConfig.KANI_RETRY_ATTEMPTS - 1:
                    raise KaniAgentError(f"Failed after {attempt + 1} attempts: {e}")
                await asyncio.sleep(1)  # Brief delay before retry
    
    def update_perception(self, perception_data: Dict[str, Any]):
        """Update agent's current perception of the environment."""
        self.current_perception = perception_data
        
        # Update location if present
        current_tile = perception_data.get("current_tile")
        if current_tile:
            self.location_tracker.update_position(current_tile)
            self.agent_data["curr_tile"] = current_tile
        
        # Update time if present
        current_time = perception_data.get("current_time")
        if current_time:
            self.agent_data["curr_time"] = current_time
    
    # ========== AI FUNCTIONS (Kani Actions) ==========
    
    @ai_function()
    def perceive(
        self,
        content: str,
        action_emoji: str = "👁️"
    ) -> Dict[str, Any]:
        """
        Observe and analyze the current environment.
        
        Args:
            content: What you observe, notice, or want to communicate about your environment
            action_emoji: Emoji representing your perception action
            
        Returns:
            Dict[str, Any]: Action JSON for frontend communication
        """
        action_json = {
            "agent_id": self.agent_id,
            "action_type": "perceive",
            "content": {
                "perception": content
            },
            "emoji": action_emoji
        }
        
        # Add memory event for significant perceptions
        if content and len(content) > 10:  # Only for meaningful perceptions
            timestamp = self.agent_data.get("curr_time", datetime.now().isoformat())
            location = self.agent_data.get("curr_tile", "unknown")
            self.memory.add_event(timestamp, str(location), f"Perceived: {content}", 3)
        
        return action_json
    
    @ai_function()
    def chat(
        self,
        receiver: str,
        message: str,
        action_emoji: str = "💬"
    ) -> Dict[str, Any]:
        """
        Send a message to another agent.
        
        Args:
            receiver: The agent ID of who you want to chat with
            message: The message you want to send
            action_emoji: Emoji representing your communication style
            
        Returns:
            Dict[str, Any]: Action JSON for frontend communication
        """
        action_json = {
            "agent_id": self.agent_id,
            "action_type": "chat",
            "content": {
                "receiver": receiver,
                "message": message
            },
            "emoji": action_emoji
        }
        
        # Add memory event for conversations
        timestamp = self.agent_data.get("curr_time", datetime.now().isoformat())
        location = self.agent_data.get("curr_tile", "unknown")
        self.memory.add_event(
            timestamp, 
            str(location), 
            f"Chatted with {receiver}: {message}", 
            5  # Conversations are moderately important
        )
        
        return action_json
    
    @ai_function()
    def move(
        self,
        destination_coordinates: List[int],
        action_emoji: str = "🚶"
    ) -> Dict[str, Any]:
        """
        Move to a specific location in the environment.
        
        Args:
            destination_coordinates: The coordinates to move to as [x, y]
            action_emoji: Emoji representing your movement style
            
        Returns:
            Dict[str, Any]: Action JSON for frontend communication
        """
        action_json = {
            "agent_id": self.agent_id,
            "action_type": "move",
            "content": {
                "destination_coordinates": destination_coordinates
            },
            "emoji": action_emoji
        }
        
        # Update location tracker
        self.location_tracker.update_position(destination_coordinates)
        
        # Add memory event for significant movements
        timestamp = self.agent_data.get("curr_time", datetime.now().isoformat())
        current_location = self.agent_data.get("curr_tile", "unknown")
        self.memory.add_event(
            timestamp,
            str(current_location),
            f"Moved to {destination_coordinates}",
            2  # Movement is low salience unless significant
        )
        
        return action_json
    
    @ai_function()
    def interact(
        self,
        object_name: str,
        new_state: str,
        action_emoji: str = "🤝"
    ) -> Dict[str, Any]:
        """
        Interact with an object in the environment.
        
        Args:
            object_name: The object to interact with
            new_state: The state the object should be changed to
            action_emoji: Emoji representing your interaction style
            
        Returns:
            Dict[str, Any]: Action JSON for frontend communication
        """
        action_json = {
            "agent_id": self.agent_id,
            "action_type": "interact",
            "content": {
                "object": object_name,
                "new_state": new_state
            },
            "emoji": action_emoji
        }
        
        # Add memory event for interactions
        timestamp = self.agent_data.get("curr_time", datetime.now().isoformat())
        location = self.agent_data.get("curr_tile", "unknown")
        self.memory.add_event(
            timestamp,
            str(location),
            f"Interacted with {object_name}: changed to {new_state}",
            4  # Interactions are moderately important
        )
        
        return action_json
    
    # ========== HIGH-LEVEL PLANNING METHODS ==========
    
    async def plan_next_action(self, perception_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Plan the next action based on current perception and agent state.
        
        Args:
            perception_data (Dict[str, Any]): Current perception data from environment
            
        Returns:
            Dict[str, Any]: Action JSON in the format expected by the frontend
        """
        # Update perception
        self.update_perception(perception_data)
        
        # Build context message for decision making
        context_message = self._build_context_message(perception_data)
        
        # Get LLM response with function calling
        action_result = None
        try:
            async for message in self.full_round(context_message):
                # Check if this is a function result message
                if message.role.value == 'function' and message.content:
                    try:
                        # Parse the function result
                        import ast
                        try:
                            parsed_result = ast.literal_eval(message.content)
                        except (ValueError, SyntaxError):
                            parsed_result = json.loads(message.content)
                        
                        if isinstance(parsed_result, dict) and "action_type" in parsed_result:
                            action_result = parsed_result
                            break
                    except Exception as e:
                        print(f"Warning: Could not parse function result: {e}")
                        continue
            
            # If no function result found, return a default perceive action
            if action_result is None:
                action_result = {
                    "agent_id": self.agent_id,
                    "action_type": "perceive",
                    "content": {
                        "perception": "Observing the environment"
                    },
                    "emoji": "👁️"
                }
            
            # Validate the action result
            if ActionValidator.validate_action(action_result):
                return action_result
            else:
                # Return safe fallback if validation fails
                return {
                    "agent_id": self.agent_id,
                    "action_type": "perceive",
                    "content": {
                        "perception": "Thinking about what to do next"
                    },
                    "emoji": "🤔"
                }
                
        except Exception as e:
            print(f"Error in plan_next_action: {e}")
            # Return safe fallback action
            return {
                "agent_id": self.agent_id,
                "action_type": "perceive",
                "content": {
                    "perception": "Taking a moment to observe"
                },
                "emoji": "👁️"
            }
    
    def _build_context_message(self, perception_data: Dict[str, Any]) -> str:
        """Build context message for LLM decision making."""
        # Get relevant memories
        relevant_memories = self.memory_context_builder.get_context_memories(
            perception_data, limit=5
        )
        
        # Build the context prompt
        context_prompt = PromptTemplates.build_action_planning_prompt(
            agent_data=self.agent_data,
            perception_data=perception_data,
            relevant_memories=relevant_memories
        )
        
        return context_prompt
    
    async def evaluate_event_salience(self, event_description: str) -> int:
        """
        Use LLM to evaluate the importance/salience of an event.
        
        Args:
            event_description (str): Description of the event
            
        Returns:
            int: Salience score from 1-10
        """
        salience_prompt = PromptTemplates.build_salience_evaluation_prompt(
            self.agent_data, event_description
        )
        
        try:
            response = await self.safe_kani_call(salience_prompt)
            salience = ResponseParser.parse_salience_score(response)
            return max(1, min(10, salience))  # Clamp to 1-10 range
        except Exception as e:
            print(f"Warning: Could not evaluate salience for event: {e}")
            return 5  # Default medium salience
    
    def save_agent_data(self):
        """Save agent data back to agent.json file."""
        agent_json_path = self.agent_dir / "agent.json"
        with open(agent_json_path, "w", encoding="utf-8") as f:
            json.dump(self.agent_data, f, indent=2, ensure_ascii=False) 