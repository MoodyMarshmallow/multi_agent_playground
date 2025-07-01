"""
Multi-Agent Playground - Kani Agent Implementation
==================================================
LLM-powered agent implementation using the Kani library with OpenAI's GPT-4o.

This module implements the LLMAgent class which combines:
- Kani's LLM interaction capabilities
- ActionsMixin for action functions (move, interact, perceive)
- Agent state management and perception processing
"""

import asyncio
import json
import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from kani import Kani
from kani.engines.openai import OpenAIEngine
from .actions import ActionsMixin
from .agent import Agent

# Get logger for this module
logger = logging.getLogger(__name__)

# Add the backend directory to Python path for imports
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from backend.config.llm_config import LLMConfig


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
        # Handle SSL issues in Windows conda environments 

        # ==================== WARNING ==========================
        # (NOTE: THIS IS A WORKAROUND AND MAY CAUSE SECURITY ISSUES)
        # =======================================================
        try:
            engine = OpenAIEngine(
                api_key, 
                model=LLMConfig.OPENAI_MODEL,
                temperature=LLMConfig.OPENAI_TEMPERATURE,
                max_tokens=LLMConfig.OPENAI_MAX_TOKENS
            )
        except OSError as e:
            if "Invalid argument" in str(e) or "SSL" in str(e):
                # Try with custom HTTP client that handles SSL issues
                import httpx
                import ssl
                
                # Create a custom SSL context that's more permissive
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
                # Create custom HTTP client
                http_client = httpx.AsyncClient(
                    verify=False,  # Disable SSL verification for testing
                    timeout=30.0
                )
                
                from openai import AsyncOpenAI
                openai_client = AsyncOpenAI(
                    api_key=api_key,
                    http_client=http_client
                )
                
                # When providing a client, don't pass api_key to OpenAIEngine
                engine = OpenAIEngine(
                    model=LLMConfig.OPENAI_MODEL,
                    temperature=LLMConfig.OPENAI_TEMPERATURE,
                    max_tokens=LLMConfig.OPENAI_MAX_TOKENS,
                    client=openai_client
                )
                logger.warning("Warning: SSL verification disabled for testing purposes")
            else:
                raise
        
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
You are {self.agent.first_name} {self.agent.last_name}, a character in a multi-agent simulation.

PERSONALITY & BACKGROUND:
- Age: {self.agent.age}
- Backstory: {self.agent.backstory}
- Personality: {self.agent.personality}
- Occupation: {self.agent.occupation}
- Current status: {self.agent.currently}
- Lifestyle: {self.agent.lifestyle}
- Living area: {self.agent.living_area}

DAILY REQUIREMENTS:
{chr(10).join(f"- {req}" for req in self.agent.daily_req)}

CURRENT CONTEXT:
- Current time: {self.agent.curr_time}
- Current location: {self.agent.curr_tile}

CAPABILITIES:
You have four main actions available:
1. move(destination_coordinates, action_emoji) - Move to specific coordinates
2. chat(receiver, message, action_emoji) - Send messages to other agents
3. interact(object, new_state, action_emoji) - Interact with objects to change their state
4. perceive(action_emoji) - Perceive objects and agents in your visible area

BEHAVIOR GUIDELINES:
- Always stay in character based on your personality traits
- Consider your daily requirements and current schedule
- React realistically to your environment and other agents
- Use appropriate emojis to represent your actions
- Make decisions based on your current state and visible environment
- Keep actions realistic and contextually appropriate

MEMORY AND SALIENCE:
- Your experiences are stored in memory with different levels of importance (salience)
- When evaluating events, consider your personal perspective and emotional response
- Rate routine activities lower (1-3), meaningful interactions higher (4-7), and life-changing events highest (8-10)
- Your personality traits affect what you find important or trivial

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
        
        # Get LLM response with function calling - iterate through the async generator
        action_result = None
        async for message in self.full_round(context_message):
            logger.debug(f"Received message: {message}")
            # Check if this is a function result message
            if message.role.value == 'function' and message.content:
                # print("In If statement")
                # Try to parse the function result as Python dict string or JSON
                try:
                    import ast
                    import json
                    # print("imported ast and json")
                    
                    # First try to parse as Python dict using ast.literal_eval
                    try:
                        parsed_result = ast.literal_eval(message.content)
                        logger.debug(f"Parsed result using ast.literal_eval: {parsed_result}")
                    except (ValueError, SyntaxError):
                        # If that fails, try JSON parsing
                        parsed_result = json.loads(message.content)
                        logger.debug(f"Parsed result using json.loads: {parsed_result}")
                    
                    # Check if this looks like one of our action results
                    action_result = parsed_result
                    break
                except Exception as e:
                    logger.error(f"Parsing failed with error: {e}")
                    continue
        
        if action_result is None:
            logger.warning("Warning: fallback to default action")
            # Fallback action - just perceive
            action_result = {
                "agent_id": self.agent_id,
                "action_type": "perceive",
                "content": {},
                "emoji": "👀"
            }
        
        # Save agent state after action planning
        self.agent.save()
        self.agent.save_memory()
        
        return action_result
    
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
            message_parts.append(
            "\nConsider moving toward or interacting with one of these objects, especially if it helps you achieve your daily requirements or current goals."
            )
        else:
            message_parts.append("\nNo objects are currently visible.Consider moving to a new area to explore your environment mostly in the house if you are in the house.")
        
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
        
        message_parts.append(
        "\nWhat would you like to do next? Most of the time, you should choose to move or interact with objects or agents unless you have a specific reason to perceive again. Only perceive again if you have new information to check."
        )
        
        return "\n".join(message_parts)
    
    async def evaluate_event_salience(self, event_description: str) -> int:
        """
        Evaluate the salience (importance) of an event for memory storage.
        
        Args:
            event_description (str): Description of the event that occurred
            
        Returns:
            int: Salience score from 1-10
        """
        try:
            # Use a simple text-based approach instead of function calling
            # This is more reliable for salience evaluation
            prompt = f"""Based on your personality and what matters to you, rate how important this event is from 1-10:

Event: "{event_description}"

YOUR CHARACTERISTICS:
- Backstory: {self.agent.backstory}
- Personality: {self.agent.personality}
- Occupation: {self.agent.occupation}
- Lifestyle: {self.agent.lifestyle}

SALIENCE SCORING GUIDELINES:
Rate events on a scale from 1-10 based on their importance to your character:

TRIVIAL EVENTS (1-2):
- Routine observations with no personal significance
- Seeing common objects in expected places
- Regular daily activities that happen frequently
- Minor environmental changes that don't affect you

LOW IMPORTANCE (3-4):
- Interactions with familiar objects for routine purposes
- Brief, casual conversations about mundane topics
- Minor changes in your environment
- Completing simple, everyday tasks

MODERATE IMPORTANCE (5-6):
- Meaningful conversations with other agents
- Discovering new objects or areas
- Completing important daily requirements
- Social interactions that reveal personality or relationships
- Learning something new about your environment

HIGH IMPORTANCE (7-8):
- Significant social conflicts or emotional moments
- Major discoveries or revelations
- Events that change your understanding of the world
- Interactions that significantly impact relationships
- Achieving important personal goals

LIFE-CHANGING EVENTS (9-10):
- Traumatic or extremely joyful experiences
- Major life decisions or turning points
- Events that fundamentally change your character
- Profound emotional experiences
- Life-threatening or life-saving situations

FACTORS TO CONSIDER:
- Personal relevance: How much does this affect YOU specifically?
- Emotional impact: How strongly did this make you feel?
- Uniqueness: How rare or unusual is this event?
- Consequences: Will this event influence your future actions?
- Relationships: Does this significantly affect your connections with others?
- Goal relevance: Does this help or hinder your personal objectives?

EXAMPLES:
- "I saw a bed in the bedroom" (routine observation) = 1-2
- "I talked with John about the weather" (casual chat) = 3-4
- "I discovered a hidden room I've never seen before" (new discovery) = 6-7
- "Sarah told me she's moving away forever" (relationship impact) = 8-9
- "I barely escaped a dangerous situation" (life-threatening) = 9-10

Remember: Score based on YOUR character's perspective and personality.
What's important to one character might be trivial to another.

Respond with ONLY a number from 1-10, nothing else."""

            # Get response without function calling
            response = await self.chat_round(prompt, include_functions=False)
            
            # Extract the number from the response
            response_text = response.text.strip()
            
            # Try to extract a number from the response
            import re
            numbers = re.findall(r'\b([1-9]|10)\b', response_text)
            
            if numbers:
                salience_score = int(numbers[0])
                logger.debug(f"Salience evaluation: '{event_description}' = {salience_score}")
                return max(1, min(10, salience_score))
            else:
                logger.warning(f"No response received for salience evaluation, defaulting to 5")
                return 5
                
        except Exception as e:
            logger.error(f"Error in salience evaluation: {e}")
            return 5  # Default fallback 