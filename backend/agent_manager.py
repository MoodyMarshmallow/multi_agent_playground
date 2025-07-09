"""
Multi-Agent Playground - Agent Manager
=====================================
Manages the connection between Characters and their AI strategies using the 
text adventure games framework with Kani-based LLM agents.

This implements the agent management system described in REFACTOR.md:
- AgentStrategy protocol for different agent types
- KaniAgent for LLM-powered decision making
- AgentManager to coordinate agents with the game
"""

import os
from typing import Protocol, Optional, Dict, List

# Kani imports
from kani import Kani, ChatMessage, ai_function
from kani.engines.openai import OpenAIEngine

# Text adventure games imports
from .text_adventure_games.things import Character
from .text_adventure_games.games import Game

# Schema imports  
from .config.schema import AgentActionOutput


class AgentStrategy(Protocol):
    """
    Interface for agent decision-making strategies.
    Implement this with your kani-based LLM agents.
    """
    async def select_action(self, world_state: dict) -> str:
        """Given world state, return a command string"""
        ...





class KaniAgent(Kani):
    """
    LLM-powered agent using the kani library with function calling.
    Extends Kani directly to enable proper function calling support.
    """
    
    def __init__(self, character_name: str, persona: str, model="gpt-4o-mini", api_key: Optional[str] = None):
        self.character_name = character_name
        self.persona = persona
        
        # Get API key from environment if not provided
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        # Track recent actions to avoid loops
        self.recent_actions = []
        self.max_recent_actions = 5
        
        # Store the command submitted by the agent
        self.selected_command = None
        
        # Fix SSL certificate path issue on Windows
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
                    print(f"Fixed SSL_CERT_FILE to: {cert_file}")
                    break
        
        # Initialize kani with OpenAI
        engine = OpenAIEngine(api_key=api_key, model=model)
        
        # Create system prompt focused on function calling
        system_prompt = f"""You are {character_name}, a character in a text adventure game.

Your persona: {persona}

You will receive descriptions of your current situation including:
- Your current location and its description
- Items you can see and interact with
- Other characters present
- Your current inventory
- Available actions you can take

Based on this information, you must choose ONE action to take by calling the submit_command function.

You MUST call the submit_command function with your chosen action. Only call this function once per turn.
Example valid commands:
- go north
- get lamp
- give fish to troll
- examine door
- look
- inventory

Remember: You can only choose from the available actions provided. If unsure, submit "look" to examine your surroundings."""

        super().__init__(
            engine=engine,
            system_prompt=system_prompt
        )
    
    @ai_function()
    def submit_command(self, command: str):
        """Submit a SINGLE command you want to execute this turn.
        
        Args:
            command: The exact command you want to perform (e.g., "go north", "get lamp", "look")
        """
        self.selected_command = command.lower().strip()
        print(f"🤖 [{self.character_name}] FUNCTION CALL: submit_command('{command}') -> stored as '{self.selected_command}'")
        return f"Command '{command}' submitted successfully."
    
    async def select_action(self, world_state: dict) -> str:
        """
        Use LLM with function calling to select an action based on world state.
        """
        try:
            print(f"\n🎮 [{self.character_name}] === AGENT TURN STARTED ===")
            # Reset selected command
            self.selected_command = None
            
            # Format world state as a message
            observation = self._format_world_state(world_state)
            
            # Add recent actions context to avoid loops
            if self.recent_actions:
                observation += f"\n\nYour recent actions: {', '.join(self.recent_actions[-3:])}"
                observation += "\nTry to do something different if you've been repeating actions."
            
            # Add instruction about function calling
            observation += "\n\nYou must call the submit_command function with your chosen action."
            
            # Debug: Print the full observation sent to the LLM
            print(f"\n📋 [{self.character_name}] WORLD STATE OBSERVATION:")
            print("=" * 60)
            print(observation)
            print("=" * 60)
            
            # Get LLM response with function calling
            print(f"🧠 [{self.character_name}] Sending observation to LLM...")
            # Use full_round to allow function calling
            async for message in self.full_round(observation, max_function_rounds=1):
                print(f"🔄 [{self.character_name}] LLM message: {message.role}")
            print(f"✅ [{self.character_name}] LLM response received")
            
            # Check if a command was submitted via function call
            if self.selected_command:
                command = self.selected_command
                print(f"✅ [{self.character_name}] Function call successful: '{command}'")
            else:
                # Fallback if no function was called (shouldn't happen with proper prompting)
                print(f"⚠️  [{self.character_name}] WARNING: No submit_command function was called!")
                print(f"🔄 [{self.character_name}] Using fallback command: 'look'")
                print(f"🎯 [{self.character_name}] FINAL ACTION: 'look'\n")
                return "look"
            
            # Validate command is in available actions
            valid_commands = [a['command'].lower() for a in world_state.get('available_actions', [])]
            print(f"🔍 [{self.character_name}] Validating command '{command}' against {len(valid_commands)} available actions")
            print(f"📝 [{self.character_name}] Available commands: {valid_commands}")
            
            if command in valid_commands:
                # Track this action
                self.recent_actions.append(command)
                if len(self.recent_actions) > self.max_recent_actions:
                    self.recent_actions.pop(0)
                print(f"✅ [{self.character_name}] Command VALID: '{command}'")
                print(f"🎯 [{self.character_name}] FINAL ACTION: '{command}'\n")
                return command
            else:
                print(f"❌ [{self.character_name}] Command NOT VALID: '{command}'")
                # Try to find a close match
                for valid_cmd in valid_commands:
                    if command in valid_cmd or valid_cmd in command:
                        self.recent_actions.append(valid_cmd)
                        if len(self.recent_actions) > self.max_recent_actions:
                            self.recent_actions.pop(0)
                        print(f"🔄 [{self.character_name}] Found close match: '{command}' -> '{valid_cmd}'")
                        print(f"🎯 [{self.character_name}] FINAL ACTION: '{valid_cmd}'\n")
                        return valid_cmd
                
                # Fallback to first available action or "look"
                if valid_commands:
                    fallback = valid_commands[0]
                    self.recent_actions.append(fallback)
                    if len(self.recent_actions) > self.max_recent_actions:
                        self.recent_actions.pop(0)
                    print(f"🔄 [{self.character_name}] No match found, using first available: '{fallback}'")
                    print(f"🎯 [{self.character_name}] FINAL ACTION: '{fallback}'\n")
                    return fallback
                else:
                    print(f"🔄 [{self.character_name}] No available commands, using fallback: 'look'")
                    print(f"🎯 [{self.character_name}] FINAL ACTION: 'look'\n")
                    return "look"
                    
        except Exception as e:
            print(f"🚨 [{self.character_name}] ERROR in select_action: {e}")
            print(f"🔄 [{self.character_name}] Using emergency fallback: 'look'")
            print(f"🎯 [{self.character_name}] FINAL ACTION: 'look'\n")
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



class AgentManager:
    """
    Manages the connection between Characters and their AI strategies.
    """
    def __init__(self, game: Game):
        self.game = game
        self.agent_strategies: Dict[str, AgentStrategy] = {}
        
        # Add turn management
        self.active_agents: List[str] = []
        self.current_agent_index = 0
        
    def register_agent_strategy(self, character_name: str, strategy: AgentStrategy):
        """
        Connect an AI strategy to a character.
        
        Args:
            character_name: Name of the character
            strategy: Object implementing AgentStrategy (e.g., kani agent)
        """
        if character_name not in self.game.characters:
            raise ValueError(f"Character {character_name} not found")
        
        self.agent_strategies[character_name] = strategy
        
        # Add to active agents list if not already there
        if character_name not in self.active_agents:
            self.active_agents.append(character_name)
    
    async def execute_agent_turn(self, agent: Character) -> Optional[AgentActionOutput]:
        """
        Have an agent take their turn using their strategy.
        
        Returns:
            AgentActionOutput schema if an action was executed, None if no strategy or error.
        """
        if agent.name not in self.agent_strategies:
            return None
            
        try:
            # Get world state from agent's perspective
            world_state = self.get_world_state_for_agent(agent)
            
            # Let the strategy decide
            strategy = self.agent_strategies[agent.name]
            command = await strategy.select_action(world_state)
            
            # Execute the command
            print(f"\n{agent.name}: {command}")
            result = self.game.parser.parse_command(command, character=agent)
            
            # Format result for readable output
            if isinstance(result, tuple) and len(result) >= 1:
                description = result[0]
                print(f"Result:")
                print("─" * 50)
                print(description)
                print("─" * 50)
            else:
                print(f"Result: {result}")
            
            # Get the schema immediately after execution
            action_schema = self.game.get_schema()
            return action_schema
            
        except Exception as e:
            print(f"Error in execute_agent_turn for {agent.name}: {e}")
            return None
    
    def get_world_state_for_agent(self, agent: Character) -> dict:
        """
        Get the observable world state for an agent.
        
        Returns:
            Dict containing location info, inventory, and available actions
        """
        location = agent.location
        
        state = {
            'agent_name': agent.name,
            'location': {
                'name': location.name,
                'description': location.description
            },
            'inventory': list(agent.inventory.keys()),
            'visible_items': [
                {'name': item.name, 'description': item.description}
                for item in location.items.values()
            ],
            'visible_characters': [
                {'name': char.name, 'description': char.description}
                for char in location.characters.values()
                if char.name != agent.name
            ],
            'available_exits': list(location.connections.keys()),
            'available_actions': self.get_available_actions_for_agent(agent)
        }
        
        return state
    
    def get_available_actions_for_agent(self, agent: Character) -> List[dict]:
        """
        Return all actions currently available to a character.
        
        Returns:
            List of dicts with 'command' and 'description' keys
        """
        available = []
        location = agent.location
        
        # Movement actions
        for direction, connected_loc in location.connections.items():
            # Check if the connection is blocked (we'll add this check later)
            available.append({
                'command': f"go {direction}",
                'description': f"Move {direction} to {connected_loc.name}"
            })
        
        # Item actions
        for item_name, item in location.items.items():
            if item.get_property("gettable") is not False:  # Default to gettable
                available.append({
                    'command': f"get {item_name}",
                    'description': f"Pick up the {item.description}"
                })
        
        # Inventory actions
        for item_name, item in agent.inventory.items():
            available.append({
                'command': f"drop {item_name}",
                'description': f"Drop the {item.description}"
            })
        
        # Character interaction actions
        for other_name, other_char in location.characters.items():
            if other_name != agent.name:
                # Give actions
                for item_name in agent.inventory:
                    available.append({
                        'command': f"give {item_name} to {other_name}",
                        'description': f"Give {item_name} to {other_char.description}"
                    })
        
        # Always available actions
        available.extend([
            {'command': 'look', 'description': 'Examine your surroundings'},
            {'command': 'inventory', 'description': 'Check what you are carrying'}
        ])
        
        return available
    
    def get_next_agent(self) -> Optional[Character]:
        """Get the next agent in turn order."""
        if not self.active_agents:
            return None
            
        agent_name = self.active_agents[self.current_agent_index]
        return self.game.characters.get(agent_name)
    
    def advance_turn(self):
        """Move to the next agent's turn."""
        if self.active_agents:
            self.current_agent_index = (self.current_agent_index + 1) % len(self.active_agents)
    
     