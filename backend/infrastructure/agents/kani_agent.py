"""
KaniAgent - LLM-powered agent implementation
============================================
Contains the KaniAgent class and AgentStrategy protocol for LLM-based
decision making in the text adventure game framework.
"""

import os
import logging
from typing import Protocol, Optional, Any

# Kani imports
from kani import Kani, ChatMessage, ai_function
from kani.engines.openai import OpenAIEngine

# Module-level logger
logger = logging.getLogger(__name__)


class AgentStrategy(Protocol):
    """
    Interface for agent decision-making strategies.
    Implement this with your kani-based LLM agents.
    """
    async def select_action(self, action_result: str) -> str:
        """Given action result, return a command string"""
        ...


class KaniAgent(Kani):
    """
    LLM-powered agent using the kani library with function calling.
    Extends Kani directly to enable proper function calling support.
    """
    
    def __init__(self, character_name: str, persona: str, initial_world_state: Optional[str] = None, model="gpt-4o-mini", api_key: Optional[str] = None, engine: Optional[Any] = None):
        self.character_name = character_name
        self.persona = persona
        
        # Track recent actions to avoid loops
        self.recent_actions = []
        self.max_recent_actions = 5
        
        # Determine engine to use
        if engine is not None:
            # Use provided engine (new approach)
            kani_engine = engine
        else:
            # Create OpenAI engine (backward compatibility)
            if api_key is None:
                api_key = os.getenv("OPENAI_API_KEY")
            
            if not api_key:
                raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
            
            kani_engine = OpenAIEngine(api_key=api_key, model=model)
        
        # Store the command submitted by the agent
        self.selected_command = None
        
        # Fix SSL certificate path issue on Windows (only for OpenAI engines)
        if engine is None:
            import ssl
            original_ssl_cert_file = os.environ.get("SSL_CERT_FILE")
            if original_ssl_cert_file and not original_ssl_cert_file.endswith(('.pem', '.crt')):
                # If SSL_CERT_FILE points to a directory, fix it
                potential_cert_files = [
                    os.path.join(original_ssl_cert_file, "cacert.pem"),
                    os.path.join(original_ssl_cert_file, "cert.pem"),
                    "C:/Users/milos/.conda/envs/kani_env/Library/ssl/cacert.pem",
                    "C:/Users/milos/.conda/envs/kani_env/Lib/site-packages/certifi/cacert.pem"
                ]
                
                for cert_file in potential_cert_files:
                    if os.path.exists(cert_file):
                        os.environ["SSL_CERT_FILE"] = cert_file
                        logger.info(f"Fixed SSL_CERT_FILE to: {cert_file}")
                        break
        
        # Create system prompt focused on function calling
        system_prompt = f"""You are {character_name}, a character in a text adventure game.

Your persona: {persona}

You will receive descriptions of your current situation including:
- Your current location and its description
- Items you can see and interact with
- Other characters present
- Your current inventory
- Available actions you can take
- Any pending chat requests

Based on this information, you must choose ONE action to take by calling the submit_command function.

You MUST call the submit_command function with your chosen action. Only call this function once per turn.
Example valid commands:
- go north
- get lamp
- give fish to troll
- examine door
- look
- inventory

CHAT SYSTEM:
- Use 'look' to see other characters you can chat with
- Send chat requests: "chat_request [name] [reason]" (e.g., "chat_request Alice Want to discuss the plan?")
- Respond to requests: "chat_response [request_id] accept" or "chat_response [request_id] reject"
- Send messages: "chat [name] [message]" (only after accepting a chat request)
- Chat responses don't end your turn, but messages do

Remember: You can only choose from the available actions provided. If unsure, submit "look" to examine your surroundings."""

        super().__init__(
            engine=kani_engine,
            system_prompt=system_prompt
        )
        
        # Store initial world state to be sent as first user message
        self.initial_world_state = initial_world_state
        self.initial_context_sent = False
    
    @ai_function()
    def submit_command(self, command: str):
        """Submit a SINGLE command you want to execute this turn.
        
        Args:
            command: The exact command you want to perform (e.g., "go north", "get lamp", "look")
        """
        self.selected_command = command.lower().strip()
        logger.debug(f"[{self.character_name}] FUNCTION CALL: submit_command('{command}') -> stored as '{self.selected_command}'")
        return f"Command '{command}' submitted successfully."
    
    async def select_action(self, action_result: str) -> str:
        """
        Use LLM with function calling to select an action based on previous action result.
        On first call, sends initial world state as first user message.
        """
        try:
            logger.info(f"[{self.character_name}] Agent turn started")
            # Reset selected command
            self.selected_command = None
            
            # Handle first turn: send initial world state as first user message
            if not self.initial_context_sent and self.initial_world_state:
                logger.info(f"[{self.character_name}] Sending initial world state as first user message")
                observation = self.initial_world_state
                self.initial_context_sent = True
            else:
                # Subsequent turns: use action result from previous turn
                observation = action_result
            
            # Add recent actions context to avoid loops
            if self.recent_actions:
                observation += f"\n\nYour recent actions: {', '.join(self.recent_actions[-3:])}"
                observation += "\nTry to do something different if you've been repeating actions."
            
            # Add instruction about function calling
            observation += "\n\nYou must call the submit_command function with your chosen action. Submit \"look\" to show what commands you can take."
            
            # Debug: Log the full observation sent to the LLM
            logger.debug(f"[{self.character_name}] OBSERVATION:")
            logger.debug(observation)
            
            # Get LLM response with function calling
            logger.debug(f"[{self.character_name}] Sending observation to LLM...")
            async for message in self.full_round(observation, max_function_rounds=1):
                logger.debug(f"[{self.character_name}] LLM message: {message.role}")
            logger.debug(f"[{self.character_name}] LLM response received")
            
            # Check if a command was submitted via function call
            if self.selected_command:
                command = self.selected_command
                logger.info(f"[{self.character_name}] Function call successful: '{command}'")
                
                # Track this action
                self.recent_actions.append(command)
                if len(self.recent_actions) > self.max_recent_actions:
                    self.recent_actions.pop(0)
                    
                logger.info(f"[{self.character_name}] FINAL ACTION: '{command}'")
                return command
            else:
                # Fallback if no function was called
                logger.warning(f"[{self.character_name}] No submit_command function was called!")
                logger.info(f"[{self.character_name}] Using fallback command: 'look'")
                logger.info(f"[{self.character_name}] FINAL ACTION: 'look'")
                return "look"
                    
        except Exception as e:
            logger.error(f"[{self.character_name}] ERROR in select_action: {e}")
            logger.info(f"[{self.character_name}] Using emergency fallback: 'look'")
            logger.info(f"[{self.character_name}] FINAL ACTION: 'look'")
            return "look"  # Safe fallback
    
    def _format_world_state(self, state: dict) -> str:
        """Format world state into readable observation."""
        lines = []
        
        # Location
        location_info = state.get('location', {})
        lines.append(f"You are at: {location_info.get('name', 'Unknown Location')}")
        if location_info.get('description'):
            lines.append(location_info['description'])
        
        # Inventory
        inventory = state.get('inventory', [])
        if inventory:
            lines.append(f"\nYou are carrying: {', '.join(inventory)}")
        else:
            lines.append("\nYou are not carrying anything.")
        
        # Visible items
        visible_items = state.get('visible_items', [])
        if visible_items:
            lines.append("\nYou can see:")
            for item in visible_items:
                lines.append(f"  - {item.get('name', 'item')}: {item.get('description', 'an item')}")
        
        # Other characters
        visible_characters = state.get('visible_characters', [])
        if visible_characters:
            lines.append("\nOther characters here:")
            for char in visible_characters:
                lines.append(f"  - {char.get('name', 'character')}: {char.get('description', 'a character')}")
        
        # Available exits
        available_exits = state.get('available_exits', [])
        if available_exits:
            lines.append(f"\nAvailable exits: {', '.join(available_exits)}")
        
        # Available actions
        available_actions = state.get('available_actions', [])
        if available_actions:
            lines.append("\nAvailable actions:")
            for action in available_actions:
                lines.append(f"  - {action['command']}: {action.get('description', 'perform action')}")
        
        return '\n'.join(lines)


class ManualAgent:
    """
    Manual agent implementation that prompts the developer to select actions.
    Implements the AgentStrategy protocol for debugging and testing purposes.
    """
    
    def __init__(self, character_name: str, persona: Optional[str] = None):
        self.character_name = character_name
        self.persona = persona or f"Manual control for {character_name}"
        
    async def select_action(self, action_result: str) -> str:
        """
        Prompt the developer to manually select an action based on action result.
        Note: ManualAgent ignores action_result and shows current world state.
        """
        # ManualAgent UI output (always shown to user for manual control)
        print(f"\n{'='*60}")
        print(f"MANUAL CONTROL - {self.character_name}")
        print(f"{'='*60}")
        
        print(f"Previous action result: {action_result}")
        print(f"Note: ManualAgent always shows available actions. Use 'look' to see full world state.")
        
        # For now, return "look" to get world state, since ManualAgent needs to see available actions
        # TODO: This needs to be refactored to work with the new architecture
        print("ManualAgent temporarily disabled - use 'look' to see world state")
        
        # Log the manual agent activation
        logger.info(f"ManualAgent {self.character_name} prompting for manual input")
        return "look"
    
    def _display_world_state(self, state: dict):
        """Display the current world state in a readable format."""
        # ManualAgent UI output (always shown to user for manual control)
        print("What you see around you:")
        
        # Location information
        location_info = state.get('location', {})
        print(f"\nLocation: {location_info.get('name', 'Unknown')}")
        if location_info.get('description'):
            print(f"Description: {location_info['description']}")
        
        # Inventory
        inventory = state.get('inventory', [])
        if inventory:
            print(f"\nInventory: {', '.join(inventory)}")
        else:
            print("\nInventory: Empty")
        
        # Visible items
        visible_items = state.get('visible_items', [])
        if visible_items:
            print(f"\nVisible Items:")
            for item in visible_items:
                name = item.get('name', 'unknown item')
                description = item.get('description', 'no description')
                print(f"  - {name}: {description}")
        
        # Other characters
        visible_characters = state.get('visible_characters', [])
        if visible_characters:
            print(f"\nOther Characters:")
            for char in visible_characters:
                name = char.get('name', 'unknown character')
                description = char.get('description', 'no description')
                print(f"  - {name}: {description}")
        
        # Available exits
        available_exits = state.get('available_exits', [])
        if available_exits:
            print(f"\nExits: {', '.join(available_exits)}")