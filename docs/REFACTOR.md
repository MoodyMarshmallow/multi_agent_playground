# Refactoring Plan: From Single-Player to Multi-Agent Playground

## Overview

This document provides a step-by-step plan to refactor the `text_adventure_games` framework from a single-player system to a multi-agent simulation environment. Each section explains what needs to change, why it's important, and how to implement it.

## Table of Contents

1. [Understanding the Current Architecture](#understanding-the-current-architecture)
2. [Step 1: Enable Multiple Active Characters](#step-1-enable-multiple-active-characters)
3. [Step 2: Implement Turn-Based System](#step-2-implement-turn-based-system)
4. [Step 3: Create Action Discovery System](#step-3-create-action-discovery-system)
5. [Step 4: Add Agent Manager](#step-4-add-agent-manager)
6. [Step 5: Create Event Queue for Frontend](#step-5-create-event-queue-for-frontend)
7. [Step 6: Integrate with Kani for LLM Agents](#step-6-integrate-with-kani-for-llm-agents)
8. [Step 7: Build the House Environment](#step-7-build-the-house-environment)
9. [Testing Strategy](#testing-strategy)
10. [Common Pitfalls and Solutions](#common-pitfalls-and-solutions)

---

## Understanding the Current Architecture

### Current Limitations

The framework currently assumes:
- **Single player**: Only `self.player` can take actions
- **Blocking input**: `game_loop()` waits for keyboard input
- **No action discovery**: Agents must guess valid commands
- **No event history**: Frontend can't replay what happened

### What We're Building

A system where:
- Multiple AI agents take turns acting in the world
- Each agent uses an LLM to decide what to do
- The Godot frontend can visualize all actions
- Agents can discover what actions are available

---

## Step 1: Enable Multiple Active Characters

### Why This Change?

Currently, the game tracks NPCs but only the player can take actions. We need all characters to be "active agents."

### Implementation

#### 1.1 Modify `Game.__init__()` in `games.py`

```python
class Game:
    def __init__(
        self,
        start_at: Location,
        player: Character,  # Keep for compatibility
        characters=None,
        custom_actions=None,
    ):
        # ... existing code ...
        
        # NEW: Track which characters are active agents
        self.active_agents = set()
        self.active_agents.add(player.name)
        
        # NEW: Track whose turn it is
        self.current_agent_index = 0
        self.turn_order = []
```

#### 1.2 Add Method to Register Agents

```python
def register_agent(self, character: Character):
    """
    Mark a character as an active agent who can take turns.
    
    Args:
        character: The Character to make an active agent
    """
    if character.name not in self.characters:
        raise ValueError(f"Character {character.name} not in game")
    
    self.active_agents.add(character.name)
    self.turn_order.append(character.name)
```

### Testing This Step

```python
# Create game as before
game = build_game()

# Register the troll as an active agent
game.register_agent(game.characters["troll"])

# Now both player and troll are active agents
print(game.active_agents)  # {'player', 'troll'}
```

---

## Step 2: Implement Turn-Based System

### Why This Change?

We need to replace the keyboard input loop with a system where each agent gets one action per turn.

### Implementation

#### 2.1 Create New Turn-Based Game Loop

```python
def turn_based_loop(self, max_turns=1000):
    """
    Run a turn-based game where each agent acts in sequence.
    
    Args:
        max_turns: Maximum number of turns before stopping
    """
    self.parser.parse_command("look")  # Initial description
    
    turn_count = 0
    while turn_count < max_turns and not self.is_game_over():
        # Get current agent
        agent_name = self.turn_order[self.current_agent_index]
        agent = self.characters[agent_name]
        
        # Let the agent take their turn
        self.execute_agent_turn(agent)
        
        # Move to next agent
        self.current_agent_index = (self.current_agent_index + 1) % len(self.turn_order)
        turn_count += 1
    
    if turn_count >= max_turns:
        print(f"Game ended after {max_turns} turns")
```

#### 2.2 Create Agent Turn Execution

```python
def execute_agent_turn(self, agent: Character):
    """
    Execute one turn for an agent.
    
    Args:
        agent: The Character whose turn it is
    """
    # For now, just print whose turn it is
    # We'll replace this with actual agent logic later
    print(f"\n=== {agent.name}'s turn ===")
    
    # Placeholder: agents do nothing for now
    # This is where we'll integrate LLM decision-making
    pass
```

### Important Note

Notice we're NOT deleting the original `game_loop()`. This lets us still test with human players!

---

## Step 3: Create Action Discovery System

### Why This Change?

Agents need to know what actions are possible instead of guessing. This dramatically improves LLM performance.

### Implementation

#### 3.1 Add Action Discovery to Parser

In `parsing.py`, add:

```python
def get_available_actions(self, character: Character) -> list[dict]:
    """
    Return all actions currently available to a character.
    
    Returns:
        List of dicts with 'command' and 'description' keys
    """
    available = []
    location = character.location
    
    # Movement actions
    for direction, connected_loc in location.connections.items():
        if not location.is_blocked(direction, character):
            available.append({
                'command': f"go {direction}",
                'description': f"Move {direction} to {connected_loc.name}"
            })
    
    # Item actions
    for item_name, item in location.items.items():
        if item.get_property("gettable"):
            available.append({
                'command': f"get {item_name}",
                'description': f"Pick up the {item.description}"
            })
    
    # Inventory actions
    for item_name, item in character.inventory.items():
        available.append({
            'command': f"drop {item_name}",
            'description': f"Drop the {item.description}"
        })
        
        # Check for special commands on items
        for special_cmd in item.get_command_hints():
            available.append({
                'command': special_cmd,
                'description': f"Special action with {item_name}"
            })
    
    # Character interaction actions
    for other_name, other_char in location.characters.items():
        if other_name != character.name:
            # Give actions
            for item_name in character.inventory:
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
```

#### 3.2 Create World State Method

In `games.py`, add:

```python
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
        'inventory': [item.name for item in agent.inventory.values()],
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
        'available_actions': self.parser.get_available_actions(agent)
    }
    
    return state
```

### Testing This Step

```python
# Get available actions for the player
state = game.get_world_state_for_agent(game.player)
print("Available actions:")
for action in state['available_actions']:
    print(f"  - {action['command']}: {action['description']}")
```

---

## Step 4: Add Agent Manager

### Why This Change?

We need a clean way to connect AI agents (using kani/LLMs) to game characters.

### Implementation

#### 4.1 Create `agent_manager.py`

Create a new file in the package:

```python
# text_adventure_games/agent_manager.py

from typing import Protocol, Optional
from .things import Character
from .games import Game

class AgentStrategy(Protocol):
    """
    Interface for agent decision-making strategies.
    Implement this with your kani-based LLM agents.
    """
    def select_action(self, world_state: dict) -> str:
        """Given world state, return a command string"""
        ...

class SimpleRandomAgent:
    """Example agent that picks random actions"""
    def select_action(self, world_state: dict) -> str:
        import random
        actions = world_state['available_actions']
        if actions:
            return random.choice(actions)['command']
        return "look"

class AgentManager:
    """
    Manages the connection between Characters and their AI strategies.
    """
    def __init__(self, game: Game):
        self.game = game
        self.agent_strategies = {}  # character_name -> AgentStrategy
        
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
        self.game.register_agent(self.game.characters[character_name])
    
    def execute_agent_turn(self, agent: Character) -> Optional[str]:
        """
        Have an agent take their turn using their strategy.
        
        Returns:
            The command executed, or None if no strategy
        """
        if agent.name not in self.agent_strategies:
            return None
            
        # Get world state from agent's perspective
        world_state = self.game.get_world_state_for_agent(agent)
        
        # Let the strategy decide
        strategy = self.agent_strategies[agent.name]
        command = strategy.select_action(world_state)
        
        # Execute the command
        print(f"\n{agent.name}: {command}")
        self.game.parser.parse_command(f"{agent.name} {command}")
        
        return command
```

#### 4.2 Update Game to Use Agent Manager

In `games.py`:

```python
def execute_agent_turn(self, agent: Character):
    """
    Execute one turn for an agent.
    """
    # Check if we have an agent manager
    if hasattr(self, 'agent_manager') and self.agent_manager:
        result = self.agent_manager.execute_agent_turn(agent)
        if result is not None:
            return
    
    # Fallback for agents without strategies
    print(f"{agent.name} does nothing (no strategy assigned)")
```

### Usage Example

```python
from text_adventure_games.agent_manager import AgentManager, SimpleRandomAgent

# Create game and agent manager
game = build_game()
agent_manager = AgentManager(game)
game.agent_manager = agent_manager

# Register a random strategy for the troll
agent_manager.register_agent_strategy("troll", SimpleRandomAgent())

# Run the game
game.turn_based_loop(max_turns=10)
```

---

## Step 5: Create Event Queue for Frontend

### Why This Change?

The Godot frontend needs to know what happened so it can animate actions.

### Implementation

#### 5.1 Add Event Tracking

In `games.py`:

```python
def __init__(self, ...):
    # ... existing code ...
    
    # NEW: Event queue for frontend
    self.event_queue = []
    self.event_id_counter = 0

def add_event(self, event_type: str, data: dict):
    """
    Add an event to the queue for frontend consumption.
    
    Args:
        event_type: Type of event (e.g., 'move', 'get', 'drop')
        data: Event-specific data
    """
    self.event_id_counter += 1
    event = {
        'id': self.event_id_counter,
        'type': event_type,
        'timestamp': self.event_id_counter,  # Simple turn counter
        'data': data
    }
    self.event_queue.append(event)

def get_events_since(self, last_event_id: int) -> list[dict]:
    """
    Get all events after the given ID.
    
    Args:
        last_event_id: ID of last processed event
        
    Returns:
        List of new events
    """
    return [e for e in self.event_queue if e['id'] > last_event_id]
```

#### 5.2 Modify Actions to Create Events

For example, in `actions/locations.py`, update the `Go` action:

```python
def apply_effects(self):
    """
    Moves a character. (Assumes that the preconditions are met.)
    """
    # ... existing movement code ...
    
    # NEW: Create event for frontend
    self.game.add_event('move', {
        'character': self.character.name,
        'from_location': from_loc.name,
        'to_location': to_loc.name,
        'direction': self.direction
    })
```

Do similar updates for Get, Drop, Give, etc.

### Frontend Integration

Your Godot frontend can poll for updates:

```gdscript
# Pseudo-code for Godot
func check_for_updates():
    var events = backend.get_events_since(last_event_id)
    for event in events:
        animate_event(event)
        last_event_id = event.id
```

---

## Step 6: Integrate with Kani for LLM Agents

### Why This Change?

This is where agents actually become intelligent using LLMs.

### Implementation

#### 6.1 Create Kani Agent Strategy

Create `kani_agent.py`:

```python
# text_adventure_games/kani_agent.py

from kani import Kani, ai_function, ChatMessage
from kani.engines.openai import OpenAIEngine

class KaniAgent:
    """
    LLM-powered agent using the kani library.
    """
    def __init__(self, character_name: str, persona: str, model="gpt-4"):
        self.character_name = character_name
        self.persona = persona
        
        # Initialize kani with OpenAI
        engine = OpenAIEngine(model=model)
        
        # Create system prompt
        system_prompt = f"""You are {character_name}, a character in a text adventure game.

Your persona: {persona}

You will receive descriptions of your current situation including:
- Your current location
- Items you can see
- Other characters present
- Available actions you can take

Based on this information, choose ONE action to take. Always respond with just the command, nothing else.

Example responses:
- go north
- get lamp
- give fish to troll
- examine door

Remember: You can only choose from the available actions provided."""

        self.kani = Kani(
            engine=engine,
            system_prompt=system_prompt
        )
    
    def select_action(self, world_state: dict) -> str:
        """
        Use LLM to select an action based on world state.
        """
        # Format world state as a message
        observation = self._format_world_state(world_state)
        
        # Get LLM response
        response = self.kani.chat_round(observation)
        
        # Extract just the command (first line, stripped)
        command = response.content.strip().split('\n')[0]
        
        # Validate command is in available actions
        valid_commands = [a['command'] for a in world_state['available_actions']]
        if command not in valid_commands:
            # Fallback to first available action
            if valid_commands:
                command = valid_commands[0]
            else:
                command = "look"
        
        return command
    
    def _format_world_state(self, state: dict) -> str:
        """Format world state into readable observation."""
        lines = []
        
        # Location
        lines.append(f"You are at: {state['location']['name']}")
        lines.append(state['location']['description'])
        
        # Inventory
        if state['inventory']:
            lines.append(f"\nYou are carrying: {', '.join(state['inventory'])}")
        else:
            lines.append("\nYou are not carrying anything.")
        
        # Visible items
        if state['visible_items']:
            lines.append("\nYou can see:")
            for item in state['visible_items']:
                lines.append(f"  - {item['name']}: {item['description']}")
        
        # Other characters
        if state['visible_characters']:
            lines.append("\nOther characters here:")
            for char in state['visible_characters']:
                lines.append(f"  - {char['name']}: {char['description']}")
        
        # Available actions
        lines.append("\nAvailable actions:")
        for action in state['available_actions']:
            lines.append(f"  - {action['command']}: {action['description']}")
        
        return '\n'.join(lines)
```

#### 6.2 Use Kani Agents in Game

```python
from text_adventure_games.kani_agent import KaniAgent

# Create game and agent manager
game = build_game()
agent_manager = AgentManager(game)
game.agent_manager = agent_manager

# Create LLM-powered troll
troll_agent = KaniAgent(
    character_name="troll",
    persona="I am hungry. I guard the bridge and demand food."
)
agent_manager.register_agent_strategy("troll", troll_agent)

# Create LLM-powered guard  
guard_agent = KaniAgent(
    character_name="guard",
    persona="I am suspicious of strangers. I protect the castle."
)
agent_manager.register_agent_strategy("guard", guard_agent)

# Run the simulation
game.turn_based_loop(max_turns=50)
```

---

## Step 7: Build the House Environment

### Implementation

Create `house_builder.py`:

```python
# text_adventure_games/environments/house_builder.py

from text_adventure_games import things

def build_house():
    """
    Create a house environment matching your Godot scene.
    """
    # Create rooms
    living_room = things.Location(
        "Living Room",
        "A cozy living room with a comfortable couch and TV."
    )
    
    kitchen = things.Location(
        "Kitchen", 
        "A modern kitchen with stainless steel appliances."
    )
    
    bathroom = things.Location(
        "Bathroom",
        "A clean bathroom with a bathtub and sink."
    )
    
    bedroom = things.Location(
        "Bedroom",
        "A peaceful bedroom with a large bed and dresser."
    )
    
    dining_room = things.Location(
        "Dining Room",
        "A formal dining room with a wooden table."
    )
    
    # Connect rooms
    living_room.add_connection("north", kitchen)
    living_room.add_connection("east", bedroom)
    kitchen.add_connection("east", dining_room)
    dining_room.add_connection("south", bedroom)
    bedroom.add_connection("north", bathroom)
    
    # Add furniture (non-gettable items)
    couch = things.Item("couch", "a comfortable couch", "A plush three-seater couch.")
    couch.set_property("gettable", False)
    living_room.add_item(couch)
    
    refrigerator = things.Item("refrigerator", "a large refrigerator", "A stainless steel refrigerator.")
    refrigerator.set_property("gettable", False)
    refrigerator.set_property("is_container", True)
    kitchen.add_item(refrigerator)
    
    # Add gettable items
    apple = things.Item("apple", "a red apple", "A fresh, crispy apple.")
    apple.set_property("is_food", True)
    refrigerator.add_item(apple)  # Note: Needs container support
    
    book = things.Item("book", "a mystery novel", "A well-worn mystery novel.")
    living_room.add_item(book)
    
    return living_room  # Starting location
```

---

## Testing Strategy

### 1. Unit Test Each Component

```python
# Test agent registration
def test_agent_registration():
    game = build_game()
    initial_count = len(game.active_agents)
    
    game.register_agent(game.characters["troll"])
    assert len(game.active_agents) == initial_count + 1

# Test action discovery
def test_action_discovery():
    game = build_game()
    actions = game.parser.get_available_actions(game.player)
    
    # Should have at least look and inventory
    commands = [a['command'] for a in actions]
    assert 'look' in commands
    assert 'inventory' in commands
```

### 2. Integration Test with Simple Agents

Start with deterministic agents before using LLMs:

```python
class ScriptedAgent:
    """Agent that follows a predefined script"""
    def __init__(self, commands):
        self.commands = commands
        self.index = 0
    
    def select_action(self, world_state):
        if self.index < len(self.commands):
            command = self.commands[self.index]
            self.index += 1
            return command
        return "look"

# Test with scripted agents
troll_script = ScriptedAgent(["get pole", "go south", "catch fish"])
```

### 3. Test with OpenAI Playground

Before implementing kani agents, test prompts manually:

1. Go to https://platform.openai.com/playground/prompts
2. Set system prompt to your agent's persona
3. Paste world state observations as user messages
4. See what commands the LLM generates
5. Refine prompts based on results

---

## Common Pitfalls and Solutions

### Pitfall 1: Commands Don't Specify Actor

**Problem**: Parser expects "get lamp" but agents generate "troll get lamp"

**Solution**: Modify parser to extract character from multi-agent commands:

```python
def parse_command(self, command: str):
    # Check if command starts with character name
    words = command.split(maxsplit=1)
    if len(words) >= 2 and words[0] in self.game.characters:
        character_name = words[0]
        actual_command = words[1]
        # Process command for specific character
    else:
        # Process command for current player
        actual_command = command
```

### Pitfall 2: Agents Take Invalid Actions

**Problem**: LLM generates commands that aren't available

**Solution**: 
1. Always validate against available actions
2. Provide clear examples in system prompt
3. Use temperature=0 for more deterministic behavior

### Pitfall 3: Infinite Loops

**Problem**: Agents keep doing the same action

**Solution**: Add recent action history to world state:

```python
state['recent_actions'] = agent.get_recent_actions(n=5)
```

### Pitfall 4: Race Conditions with Frontend

**Problem**: Frontend polls while backend is mid-turn

**Solution**: Add transaction-like behavior:

```python
def begin_turn(self):
    self.in_turn = True

def end_turn(self):
    self.in_turn = False
    
def get_events_since(self, last_id):
    if self.in_turn:
        return []  # Don't send partial turn data
    return [e for e in self.event_queue if e['id'] > last_id]
```

---

## Next Steps

1. **Start Small**: Get two agents taking turns before adding more
2. **Test Without LLMs**: Use scripted agents first
3. **Add LLMs Gradually**: Start with simple personas
4. **Monitor Costs**: LLM calls add up - cache when possible
5. **Profile Performance**: Turn time should be < 1 second

## Resources

- Kani documentation: https://kani.readthedocs.io/
- OpenAI Playground: https://platform.openai.com/playground/
- Example multi-agent games: Look at "AI Dungeon" architecture

Good luck with your multi-agent playground! Remember: incremental progress is key. Get one thing working before moving to the next.