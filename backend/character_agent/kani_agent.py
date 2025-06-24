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
import ssl
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, AsyncGenerator
from kani import Kani
from kani.engines.openai import OpenAIEngine
from .actions import ActionsMixin
from .agent import Agent

# Handle imports for both standalone and package usage
try:
    # Try relative imports first (when used as package)
    from .actions import ActionsMixin
    from .agent import Agent
    from ..config.llm_config import LLMConfig
except ImportError:
    # Fall back to absolute imports (when run as standalone script)
    # Add the backend directory to Python path for imports
    backend_dir: Path = Path(__file__).parent.parent
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    
    from character_agent.actions import ActionsMixin
    from character_agent.agent import Agent
    from config.llm_config import LLMConfig


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
        # Handle SSL issues in Windows conda environments 

        # ==================== WARNING ==========================
        # (NOTE: THIS IS A WORKAROUND AND MAY CAUSE SECURITY ISSUES)
        # =======================================================
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
        agent_info = f"""
You are {self.agent.first_name} {self.agent.last_name}, a character in a multi-agent simulation.

SPATIAL MEMORY:
{spatial_memory}

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
- Current room: {self.agent.curr_room}

CAPABILITIES:
You have four main actions available:
1. move(destination_room, action_emoji) - Move to a specific room
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
    
    def _format_spatial_memory(self, environment_data: Dict[str, Any]) -> str:
        """
        Format environment data into a readable spatial memory for the agent.
        
        Args:
            environment_data (dict): The environment data loaded from environment.json
            
        Returns:
            str: Formatted spatial memory description
        """
        if not environment_data or "house" not in environment_data:
            return "No spatial memory available."
        
        house_data = environment_data["house"]
        memory_parts = []
        
        # Process first floor layout
        if "first_floor" in house_data:
            memory_parts.append("HOUSE LAYOUT (First Floor):")
            first_floor = house_data["first_floor"]
            
            for room_name, room_data in first_floor.items():
                memory_parts.append(f"\n{room_name.upper().replace('_', ' ')}:")
                
                for object_name, object_info in room_data.items():
                    if isinstance(object_info, dict):
                        # Handle nested objects (like bookshelves with left/right)
                        if any(isinstance(v, dict) and "shape" in v for v in object_info.values()):
                            memory_parts.append(f"  - {object_name.replace('_', ' ')}:")
                            for sub_name, sub_info in object_info.items():
                                if isinstance(sub_info, dict) and "shape" in sub_info:
                                    shape_coords = sub_info["shape"]
                                    interact_coords = sub_info.get("interact", [])
                                    memory_parts.append(f"    • {sub_name.replace('_', ' ')}: coordinates {shape_coords}")
                                    if interact_coords:
                                        memory_parts.append(f"      (interact at: {interact_coords})")
                        elif "shape" in object_info:
                            # Regular object with shape
                            shape_coords = object_info["shape"]
                            interact_coords = object_info.get("interact", [])
                            description = object_info.get("description", "")
                            
                            memory_parts.append(f"  - {object_name.replace('_', ' ')}: coordinates {shape_coords}")
                            if interact_coords:
                                memory_parts.append(f"    (interact at: {interact_coords})")
                            if description:
                                memory_parts.append(f"    ({description})")
        
        return "\n".join(memory_parts) if memory_parts else "No spatial memory available."
    
    
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
            print("received message: ", message)
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
                        print("parsed_result using ast.literal_eval: ", parsed_result)
                    except (ValueError, SyntaxError):
                        # If that fails, try JSON parsing
                        parsed_result: Dict[str, Any] = eval(message.content)
                        print("parsed_result using json.loads: ", parsed_result)
                    
                    # Check if this looks like one of our action results
                    if isinstance(parsed_result, dict) and 'action_type' in parsed_result:
                        # print("setting action_result")
                        action_result = parsed_result
                        break
                except (json.JSONDecodeError, TypeError, ValueError, SyntaxError) as e:
                    # If parsing fails, continue looking for other messages
                    print(f"Parsing failed with error: {e}")
                    continue
        
        # If no action was determined, default to perceive
        if not action_result:
            print("warning: fallback to default action")
            action_result: Dict[str, Any] = {
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
        message_parts: List[str] = [
            f"Current time: {self.agent.curr_time}",
            f"Your current room: {self.agent.curr_room}",
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
            message_parts.append(
                "\nConsider moving toward or interacting with one of these objects, especially if it helps you achieve your daily requirements or current goals."
            )
        else:
            message_parts.append("\nNo objects are currently visible.Consider moving to a new area to explore your environment mostly in the house if you are in the house.")
        
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
                print(f"Salience evaluation: '{event_description}' = {salience_score}")
                return max(1, min(10, salience_score))
            else:
                print(f"Could not parse salience from response: '{response_text}', defaulting to 5")
                return 5
                
        except Exception as e:
            print(f"Error in salience evaluation: {e}")
            return 5  # Default fallback 
