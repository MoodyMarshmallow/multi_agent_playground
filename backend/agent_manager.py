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
from kani import Kani, ChatMessage
from kani.engines.openai import OpenAIEngine

# Text adventure games imports
from .text_adventure_games.things import Character
from .text_adventure_games.game_controller import GameController


class AgentStrategy(Protocol):
    """
    Interface for agent decision-making strategies.
    Implement this with your kani-based LLM agents.
    """
    async def select_action(self, world_state: dict) -> str:
        """Given world state, return a command string"""
        ...





class KaniAgent:
    """
    LLM-powered agent using the kani library.
    """
    def __init__(self, character_name: str, persona: str, model="gpt-4o-mini", api_key: Optional[str] = None):
        self.character_name = character_name
        self.persona = persona
        
        # Get API key from environment if not provided
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        # Initialize kani with OpenAI
        engine = OpenAIEngine(api_key=api_key, model=model)
        
        # Create system prompt
        system_prompt = f"""You are {character_name}, a character in a text adventure game.

Your persona: {persona}

You will receive descriptions of your current situation including:
- Your current location and its description
- Items you can see and interact with
- Other characters present
- Your current inventory
- Available actions you can take

Based on this information, choose ONE action to take. Always respond with just the command, nothing else.

Example responses:
- go north
- get lamp
- give fish to troll
- examine door
- look
- inventory

Remember: You can only choose from the available actions provided. If unsure, use "look" to examine your surroundings."""

        self.kani = Kani(
            engine=engine,
            system_prompt=system_prompt
        )
        
        # Track recent actions to avoid loops
        self.recent_actions = []
        self.max_recent_actions = 5
    
    async def select_action(self, world_state: dict) -> str:
        """
        Use LLM to select an action based on world state.
        """
        try:
            # Format world state as a message
            observation = self._format_world_state(world_state)
            
            # Add recent actions context to avoid loops
            if self.recent_actions:
                observation += f"\n\nYour recent actions: {', '.join(self.recent_actions[-3:])}"
                observation += "\nTry to do something different if you've been repeating actions."
            
            # Get LLM response
            response = await self.kani.chat_round(observation)
            
            # Extract just the command (first line, stripped)
            command = response.text.strip().split('\n')[0].lower()
            
            # Validate command is in available actions
            valid_commands = [a['command'].lower() for a in world_state.get('available_actions', [])]
            
            if command in valid_commands:
                # Track this action
                self.recent_actions.append(command)
                if len(self.recent_actions) > self.max_recent_actions:
                    self.recent_actions.pop(0)
                return command
            else:
                # Try to find a close match
                for valid_cmd in valid_commands:
                    if command in valid_cmd or valid_cmd in command:
                        self.recent_actions.append(valid_cmd)
                        if len(self.recent_actions) > self.max_recent_actions:
                            self.recent_actions.pop(0)
                        return valid_cmd
                
                # Fallback to first available action or "look"
                if valid_commands:
                    fallback = valid_commands[0]
                    self.recent_actions.append(fallback)
                    if len(self.recent_actions) > self.max_recent_actions:
                        self.recent_actions.pop(0)
                    return fallback
                else:
                    return "look"
                    
        except Exception as e:
            print(f"Error in KaniAgent.select_action for {self.character_name}: {e}")
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
    def __init__(self, game: GameController):
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
    
    async def execute_agent_turn(self, agent: Character) -> tuple[Optional[str], Optional[str]]:
        """
        Have an agent take their turn using their strategy.
        
        Returns:
            A tuple of (command, result), or (None, None) if no strategy.
        """
        if agent.name not in self.agent_strategies:
            return None, None
            
        # Get world state from agent's perspective
        world_state = self.get_world_state_for_agent(agent)
        
        # Let the strategy decide
        strategy = self.agent_strategies[agent.name]
        command = await strategy.select_action(world_state)
        
        # Execute the command
        print(f"\n{agent.name}: {command}")
        result = self.game.parser.parse_command(command, character=agent)
        print(f"Result: {result}")
        
        return command, result
    
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
    
     