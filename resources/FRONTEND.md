# Godot Frontend Implementation Guide

## Overview

This guide explains how to build a 2D JRPG-style frontend in Godot that visualizes your multi-agent text adventure game using sprites and animations. The frontend will poll the Python backend for updates and animate agent actions in real-time.

### Why Separate Frontend and Backend?

You might wonder: "Why not just build everything in Godot?" Here's why we're using this architecture:

1. **Text Adventures Are Logic-Heavy**: Your text adventure game has complex rules, item properties, character states, and action validation. Python excels at this kind of logic processing.

2. **AI Integration**: Your agents use LLMs (Large Language Models) through the kani library. Python has excellent AI/ML libraries, while Godot doesn't.

3. **Multiple Interfaces**: With separate backend/frontend, you could build multiple frontends (2D Godot, 3D Godot, web interface, command line) all using the same game logic.

4. **Team Development**: Different team members can work on game logic (Python) and visualization (Godot) simultaneously.

5. **Testing and Debugging**: You can test game logic independently of graphics, and test graphics with simulated data.

### The Visualization Challenge

Your Python backend manages an abstract world of locations, characters, and items. But humans understand games better with visual representations. Your job is to create a "window" into this abstract world where:

- Players can see where agents are located
- Item state changes are visible (empty bathtub → full bathtub)
- Agent actions are animated meaningfully
- Multiple agents can be observed simultaneously
- The game state is always clear and understandable

Think of your Godot frontend as a "live map" that updates automatically as the Python backend changes the game world.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Setting Up the Godot Project](#setting-up-the-godot-project)
3. [Backend Communication](#backend-communication)
4. [Scene Structure](#scene-structure)
5. [Character System](#character-system)
6. [Animation System](#animation-system)
7. [UI Implementation](#ui-implementation)
8. [Event Processing](#event-processing)
9. [Testing and Debugging](#testing-and-debugging)
10. [Performance Optimization](#performance-optimization)

---

## Architecture Overview

### Communication Flow

```
Python Backend (Game Engine)
    ↓ HTTP/JSON API
Godot Frontend (Visualization)
    ↓ User Interaction
Python Backend (Command Processing)
```

### Key Principles

1. **Backend Authority**: Python backend owns all game state and logic
   - *Why?* The backend has the "source of truth." If Godot tries to track game state independently, they can get out of sync, leading to confusing bugs.
   - *Example:* If an agent picks up an item, only the Python backend decides if that's allowed. Godot just animates the result.

2. **Frontend Display**: Godot only handles visualization and user interaction
   - *Why?* Godot is excellent at graphics, animation, and user interfaces, but not at complex game logic.
   - *Example:* Godot knows how to animate a character walking, but Python decides where they can walk.

3. **Event-Driven**: Frontend reacts to events from backend
   - *Why?* This ensures Godot always shows what actually happened, not what it thinks should happen.
   - *Example:* When Agent A gives an item to Agent B, Python sends a "give" event, and Godot animates the exchange.

4. **Polling Model**: Frontend regularly checks for updates (not real-time WebSocket)
   - *Why?* Polling is simpler to implement and debug. Since this isn't a fast-paced action game, checking every 500ms is fine.
   - *Alternative:* Real-time WebSockets are more complex but could be added later if needed.

5. **Replay Capability**: Frontend can reconstruct any game state from events
   - *Why?* This makes debugging easier and allows "time travel" - you can replay the game from any point.
   - *Example:* If something looks wrong, you can replay all events from the beginning to see what happened.

---

## Setting Up the Godot Project

### Project Structure

**Understanding the File Organization:**

The project structure separates concerns to make development easier:

- **scenes/**: Contains Godot scene files (.tscn) - these are like "templates" for game objects
- **scripts/**: Contains GDScript files (.gd) - these add behavior to scenes
- **assets/**: Contains art assets organized by type
- **backend/**: Contains or links to your Python text adventure game

This separation means:
- Artists can work on assets without touching code
- Programmers can modify scripts without breaking scenes
- The Python backend can be developed independently

```
MultiAgentPlayground/
├── scenes/
│   ├── Main.tscn              # Root scene
│   ├── House.tscn             # Main game environment
│   ├── Character.tscn         # Agent character prefab
│   ├── Item.tscn              # Interactive item prefab
│   └── UI/
│       ├── GameUI.tscn        # Main UI overlay
│       ├── AgentPanel.tscn    # Individual agent status
│       └── LogPanel.tscn      # Action log display
├── scripts/
│   ├── GameManager.gd         # Main game controller
│   ├── BackendConnector.gd    # Python backend communication
│   ├── Character.gd           # Character controller
│   ├── House.gd               # Environment manager
│   └── UI/
│       ├── GameUI.gd
│       ├── AgentPanel.gd
│       └── LogPanel.gd
├── assets/
│   ├── characters/            # Character sprite sheets and animations
│   │   ├── player/
│   │   │   ├── player_idle.png
│   │   │   ├── player_walk.png
│   │   │   └── player_action.png
│   │   ├── troll/
│   │   └── guard/
│   ├── items/                 # Item sprites with state variations
│   │   ├── bathtub_empty.png
│   │   ├── bathtub_full.png
│   │   ├── lamp_off.png
│   │   ├── lamp_on.png
│   │   └── ...
│   ├── environments/          # Room backgrounds and furniture
│   │   ├── living_room_bg.png
│   │   ├── kitchen_bg.png
│   │   └── furniture_sprites.png
│   └── ui/                    # UI sprites and icons
│       ├── panel_bg.png
│       ├── icons/
│       └── fonts/
└── backend/
    └── text_adventure_games/  # Python backend (symlink or copy)
```

### Godot Project Settings

1. **Create New Project**: Choose 2D for JRPG sprite-based visualization
   - *Why 2D?* Simpler to implement, easier to create art assets, and perfect for the "top-down house view" you're building.

2. **Set Main Scene**: Point to `scenes/Main.tscn`
   - *Why?* This tells Godot which scene to load first when the game starts.

3. **Configure Input Map**: Add keys for manual testing (WASD, Space, etc.)
   - *Why?* During development, you'll want to manually trigger events, send test commands, or debug the frontend without waiting for AI agents.

4. **Enable HTTP**: Ensure HTTPRequest node is available
   - *Why?* This is how Godot will communicate with your Python backend over HTTP.

---

## Backend Communication

**The Communication Bridge:**

Your Python backend and Godot frontend are separate programs that need to communicate. Think of them as two people who need to pass notes back and forth:

- **Godot asks**: "What's the current game state?" or "What events happened recently?"
- **Python responds**: "Here's the current state" or "Agent A moved north, Agent B picked up a lamp"
- **Godot requests**: Godot might take an input text command from the player and then ask Python "Please execute this command: 'player go north'"
- **Python responds**: "Command executed successfully" or "Command failed: no exit north"

### Why HTTP Instead of Direct Integration?

1. **Language Independence**: HTTP works between any programming languages
2. **Network Ready**: Later, you could run Python on a server and Godot on multiple clients
3. **Debugging Friendly**: You can test the API with web browsers, curl, or Postman
4. **Standard Protocol**: HTTP is well-understood and has good tooling

### 1. HTTP Server in Python

First, add a simple HTTP server to your Python backend:

**What this does:** Creates a web server inside your Python game that Godot can talk to. It's like adding a telephone to your Python program that Godot can call.

```python
# text_adventure_games/http_server.py

# These imports give us the tools to create a web server
from http.server import HTTPServer, BaseHTTPRequestHandler
import json  # For converting Python data to/from JSON format
import threading  # For running the server without blocking the game
from urllib.parse import urlparse, parse_qs  # For parsing web requests

class GameHTTPHandler(BaseHTTPRequestHandler):
    """Handles HTTP requests from Godot frontend.
    
    Think of this as a translator between Godot's HTTP requests 
    and your Python game's methods.
    """
    def __init__(self, game_instance, *args, **kwargs):
        self.game = game_instance  # Reference to your text adventure game
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests from Godot
        
        GET requests are for retrieving information (like asking 'what happened?')
        We support two main requests:
        - /game_state: "Tell me everything about the current game"
        - /events: "Tell me what happened since event #X"
        """
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/game_state':
            self.send_game_state()
        elif parsed_path.path == '/events':
            self.send_events(parsed_path.query)
        else:
            self.send_error(404)  # "I don't understand that request"
    
    def do_POST(self):
        """Handle POST requests from Godot
        
        POST requests are for sending information (like 'please do this')
        We support:
        - /command: "Please execute this game command"
        """
        if self.path == '/command':
            self.handle_command()
        else:
            self.send_error(404)
    
    def send_game_state(self):
        """Send current game state
        
        This is like taking a photograph of the entire game world
        and sending it to Godot. Godot uses this to set up the 
        initial display and to resync if it gets confused.
        """
        try:
            # Get state for all agents
            state = {
                'locations': {},     # All rooms and what's in them
                'characters': {},    # All characters and their status
                'current_turn': getattr(self.game, 'current_agent_index', 0),
                'turn_order': getattr(self.game, 'turn_order', []),
                'game_over': self.game.game_over
            }
            
            # Add location data - convert Python objects to simple dictionaries
            for name, location in self.game.locations.items():
                state['locations'][name] = {
                    'name': location.name,
                    'description': location.description,
                    'connections': list(location.connections.keys()),  # Which directions you can go
                    'items': [item.name for item in location.items.values()],  # What objects are here
                    'characters': list(location.characters.keys())  # Who is in this room
                }
            
            # Add character data - what Godot needs to display each character
            for name, character in self.game.characters.items():
                state['characters'][name] = {
                    'name': character.name,
                    'description': character.description,
                    'location': character.location.name if character.location else None,  # Where are they?
                    'inventory': list(character.inventory.keys())  # What are they carrying?
                }
            
            self.send_json_response(state)
        except Exception as e:
            self.send_error(500, str(e))
    
    def send_events(self, query_string):
        """Send events since last ID
        
        This is like asking "What happened since I last checked?"
        Godot remembers the last event ID it saw, and asks for everything newer.
        This way, Godot can animate each action that occurred.
        """
        try:
            params = parse_qs(query_string)
            last_id = int(params.get('since', ['0'])[0])  # "Show me events after #X"
            
            events = self.game.get_events_since(last_id)
            self.send_json_response({'events': events})
        except Exception as e:
            self.send_error(500, str(e))
    
    def handle_command(self):
        """Process command from Godot
        
        This allows Godot to send text commands to the game, like:
        - "player go north" (manual testing)
        - "troll eat fish" (simulating agent actions)
        - "look" (refresh the view)
        """
        try:
            # Read the JSON data Godot sent us
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            command = data.get('command', '')
            if command:
                # Send the command to the game's parser (same as typing it in console)
                self.game.parser.parse_command(command)
                self.send_json_response({'success': True})
            else:
                self.send_json_response({'success': False, 'error': 'No command provided'})
        except Exception as e:
            self.send_error(500, str(e))
    
    def send_json_response(self, data):
        """Send JSON response"""
        json_data = json.dumps(data, indent=2)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')  # For CORS
        self.send_header('Content-Length', len(json_data))
        self.end_headers()
        self.wfile.write(json_data.encode('utf-8'))

def start_game_server(game, port=8080):
    """Start HTTP server for the game
    
    This creates and starts the web server that Godot will connect to.
    It runs in a separate thread so your Python game can continue 
    running while also serving web requests.
    """
    def handler(*args, **kwargs):
        return GameHTTPHandler(game, *args, **kwargs)
    
    server = HTTPServer(('localhost', port), handler)
    
    # Run in separate thread so game can continue
    # daemon=True means the thread will exit when the main program exits
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    print(f"Game server started on http://localhost:{port}")
    print(f"Godot can now connect to: http://localhost:{port}/game_state")
    return server
```

### 2. Backend Connector in Godot

**What this does:** Creates the "telephone" on the Godot side that calls your Python backend. This script handles all communication between Godot and Python.

**Key responsibilities:**
1. **Polling**: Regularly ask Python "what's new?"
2. **Event Processing**: Receive and forward events to the game manager
3. **Command Sending**: Send manual commands for testing
4. **Error Handling**: Deal with network problems gracefully

Create `scripts/BackendConnector.gd`:

```gdscript
# BackendConnector.gd
extends Node

# Signals are Godot's way of notifying other parts of your code when something happens
# Think of them as announcements: "Hey everyone, I just received game state!"
signal game_state_received(state)  # "I got the full game state from Python"
signal events_received(events)     # "I got new events from Python"
signal command_sent(success)       # "I tried to send a command, here's if it worked"

const BASE_URL = "http://localhost:8080"  # Where our Python backend is running
var http_request: HTTPRequest  # Godot's tool for making web requests
var last_event_id: int = 0    # Remember the last event we saw (avoid duplicates)
var poll_timer: Timer         # Automatically check for updates every few seconds

func _ready():
    # Create HTTP request node - this is Godot's built-in web client
    http_request = HTTPRequest.new()
    add_child(http_request)
    http_request.request_completed.connect(_on_request_completed)
    
    # Create polling timer - automatically check for updates
    poll_timer = Timer.new()
    add_child(poll_timer)
    poll_timer.wait_time = 0.5  # Poll every 500ms (twice per second)
    poll_timer.timeout.connect(_poll_for_events)
    poll_timer.start()
    
    print("Backend connector ready - will poll Python every 500ms")

func _poll_for_events():
    """Regularly check for new events
    
    This runs automatically every 500ms. It's like asking Python:
    'Did anything happen since I last checked?'
    """
    request_events()

func request_game_state():
    """Get current game state from backend
    
    Use this when you need the complete current state - usually at startup
    or when something goes wrong and you need to resync.
    """
    var url = BASE_URL + "/game_state"
    print("Requesting full game state from: ", url)
    http_request.request(url)

func request_events():
    """Get events since last known event
    
    This is the main polling method - check what happened recently.
    We pass the last_event_id so Python only sends us new events.
    """
    var url = BASE_URL + "/events?since=" + str(last_event_id)
    # Uncomment for debugging: print("Checking for events since: ", last_event_id)
    http_request.request(url)

func send_command(command: String):
    """Send a command to the backend
    
    Use this to send text commands to the Python game, like:
    - Manual testing: send_command('player go north')
    - Simulating agent actions: send_command('troll attack player')
    """
    var url = BASE_URL + "/command"
    var headers = ["Content-Type: application/json"]
    var json_data = JSON.stringify({"command": command})
    
    print("Sending command to Python: ", command)
    http_request.request(url, headers, HTTPClient.METHOD_POST, json_data)

func _on_request_completed(result: int, response_code: int, headers: PackedStringArray, body: PackedByteArray):
    """Handle HTTP response
    
    This gets called whenever we receive a response from Python.
    We need to figure out what type of response it is and handle it appropriately.
    """
    if response_code != 200:
        print("HTTP Error: ", response_code)
        print("Make sure your Python backend is running on port 8080!")
        return
    
    var json = JSON.new()
    var parse_result = json.parse(body.get_string_from_utf8())
    
    if parse_result != OK:
        print("JSON Parse Error")
        return
    
    var data = json.data
    
    # Determine what type of response this is
    if "events" in data:
        _handle_events_response(data.events)
    elif "locations" in data:
        _handle_game_state_response(data)
    elif "success" in data:
        _handle_command_response(data)

func _handle_events_response(events: Array):
    """Process new events from backend
    
    Events are the heart of the system - they tell us what actions happened.
    Each event represents one thing that occurred in the game world.
    """
    for event in events:
        if event.id > last_event_id:
            last_event_id = event.id  # Remember the newest event we've seen
    
    if events.size() > 0:
        print("Received ", events.size(), " new events from Python")
        events_received.emit(events)  # Tell the GameManager about these events

func _handle_game_state_response(state: Dictionary):
    """Process game state from backend
    
    Game state is the complete current state of the world.
    This is used at startup or to resync when needed.
    """
    print("Received full game state with ", state.locations.size(), " locations and ", state.characters.size(), " characters")
    game_state_received.emit(state)

func _handle_command_response(response: Dictionary):
    """Process command response
    
    This tells us if our command was executed successfully.
    """
    if response.success:
        print("Command executed successfully")
    else:
        print("Command failed: ", response.get("error", "Unknown error"))
    command_sent.emit(response.success)
```

---

## Scene Structure

**Understanding Godot Scenes:**

In Godot, a "scene" is like a blueprint or template for game objects. Think of scenes as LEGO instruction manuals - they tell you how to put pieces together to create something specific.

**Why organize scenes this way?**
- **Separation of Concerns**: Each scene has one main job
- **Reusability**: You can use the same Character scene for multiple agents
- **Team Development**: Different people can work on different scenes
- **Testing**: You can test scenes independently

### Main Scene Setup

**What this does:** Creates the "root" of your entire game - everything else hangs off this main scene.

Create `scenes/Main.tscn` with this structure:

```
Main (Node2D)
├── BackendConnector (BackendConnector script)  # Talks to Python
├── GameManager (GameManager script)            # Coordinates everything
├── House (House scene instance)                # The visual world
├── UI (GameUI scene instance)                  # User interface overlay
└── Camera2D                                    # What the player sees
```

**Node explanations:**
- **Node2D**: The base for 2D games (vs Node for non-visual or Node3D for 3D)
- **BackendConnector**: Handles all Python communication
- **GameManager**: The "brain" that coordinates between Python events and Godot visuals
- **House**: The visual representation of your game world
- **UI**: Panels, buttons, text that overlay the game world
- **Camera2D**: Controls what part of the world the player sees

### House Scene

**What this does:** Creates the visual representation of your text adventure's locations. Instead of just text descriptions like "You are in the kitchen," players see an actual kitchen.

**Why use layers?** In 2D games, you need to control what appears in front of what. Layers let you organize visual elements:
- **Background**: Room layouts, wallpaper, flooring
- **Furniture**: Couches, tables, appliances (behind characters)
- **Characters**: Agents and NPCs (in front of furniture)
- **UI**: Text, buttons, health bars (in front of everything)

Create `scenes/House.tscn` for 2D sprite-based layout:

```
House (Node2D)
├── BackgroundLayer (CanvasLayer) # Layer -1 for backgrounds
│   ├── LivingRoomBG (Sprite2D)   # Room background images
│   ├── KitchenBG (Sprite2D) 
│   ├── BedroomBG (Sprite2D)
│   └── BathroomBG (Sprite2D)
├── FurnitureLayer (Node2D)      # Layer 0 for furniture/items
│   ├── StaticFurniture (Node2D)    # Non-interactive decorations
│   └── InteractiveItems (Node2D)   # Items agents can use
├── CharacterLayer (Node2D)      # Layer 1 for characters
└── UILayer (CanvasLayer)        # Layer 2 for UI overlays
```

**Mapping Text Adventure to Visuals:**
Your Python backend has abstract "locations" with "connections." This scene gives each location a visual position and shows the connections as spatial relationships. For example:
- Python: `kitchen.connections['north'] = living_room`
- Godot: Kitchen sprite is south of Living Room sprite

### Room Positioning

**The Challenge:** Your Python backend thinks in terms of abstract connections ("kitchen connects north to living room"), but Godot needs concrete pixel positions ("kitchen sprite at (400, 300), living room sprite at (400, 100)").

**The Solution:** Create a mapping from room names to screen positions. This lets you:
1. Position room backgrounds at specific coordinates
2. Move characters between rooms by moving them between coordinates
3. Maintain the spatial relationships implied by the text adventure

Define room positions in `scripts/House.gd`:

```gdscript
# House.gd
extends Node2D

# Room positions in pixels - this maps abstract room names to concrete screen coordinates
# Think of this as creating a floor plan where each room has a specific location
var room_positions = {
    "Living Room": Vector2(400, 300),  # Center-bottom of screen
    "Kitchen": Vector2(400, 100),      # North of living room
    "Bedroom": Vector2(700, 300),      # East of living room  
    "Bathroom": Vector2(700, 100),     # Northeast corner
    "Dining Room": Vector2(700, 200)   # Between kitchen and bedroom
}

# Why these positions? They create a logical house layout:
# [Kitchen]     [Bathroom]
#    |             |
# [Living Room] [Dining] [Bedroom]
# 
# This matches common text adventure connection patterns

# Room size for collision detection and visual bounds
# This defines how big each room appears on screen
var room_size = Vector2(200, 150)  # 200 pixels wide, 150 pixels tall

@onready var rooms_node = $Rooms
@onready var characters_node = $Characters
@onready var items_node = $Items

func _ready():
    setup_rooms()

func setup_rooms():
    """Create sprite-based room layout
    
    This function transforms your abstract text adventure locations
    into visual rooms that players can see.
    """
    # Load room background sprites - these are the "wallpaper" for each room
    var room_sprites = {
        "Living Room": preload("res://assets/environments/living_room_bg.png"),
        "Kitchen": preload("res://assets/environments/kitchen_bg.png"),
        "Bedroom": preload("res://assets/environments/bedroom_bg.png"),
        "Bathroom": preload("res://assets/environments/bathroom_bg.png"),
        "Dining Room": preload("res://assets/environments/dining_room_bg.png")
    }
    
    # Create a visual sprite for each room
    for room_name in room_positions:
        var room_sprite = Sprite2D.new()
        room_sprite.texture = room_sprites.get(room_name)
        room_sprite.position = room_positions[room_name]
        $BackgroundLayer.add_child(room_sprite)
        
        # Add furniture specific to each room
        setup_room_furniture(room_name)
        
        print("Created room: ", room_name, " at position: ", room_positions[room_name])

func setup_room_furniture(room_name: String):
    """Add furniture sprites to each room"""
    var furniture_data = {
        "Living Room": [
            {"sprite": "couch", "position": Vector2(-40, 30)},
            {"sprite": "tv", "position": Vector2(0, -40)},
            {"sprite": "coffee_table", "position": Vector2(0, 10)}
        ],
        "Kitchen": [
            {"sprite": "refrigerator", "position": Vector2(-60, -20)},
            {"sprite": "stove", "position": Vector2(60, -20)},
            {"sprite": "counter", "position": Vector2(0, 20)}
        ],
        "Bathroom": [
            {"sprite": "bathtub", "position": Vector2(-30, 20)},
            {"sprite": "toilet", "position": Vector2(30, 30)},
            {"sprite": "sink", "position": Vector2(40, -30)}
        ],
        "Bedroom": [
            {"sprite": "bed", "position": Vector2(0, 20)},
            {"sprite": "dresser", "position": Vector2(-50, -20)},
            {"sprite": "nightstand", "position": Vector2(40, 0)}
        ]
    }
    
    if room_name in furniture_data:
        var room_pos = room_positions[room_name]
        for furniture in furniture_data[room_name]:
            create_furniture_sprite(furniture.sprite, room_pos + furniture.position)

func create_furniture_sprite(furniture_name: String, position: Vector2):
    """Create a furniture sprite"""
    var furniture_sprite = Sprite2D.new()
    var texture_path = "res://assets/environments/furniture/" + furniture_name + ".png"
    
    if ResourceLoader.exists(texture_path):
        furniture_sprite.texture = load(texture_path)
        furniture_sprite.position = position
        $FurnitureLayer/StaticFurniture.add_child(furniture_sprite)
    else:
        # Create placeholder colored rectangle
        var placeholder = ColorRect.new()
        placeholder.size = Vector2(40, 30)
        placeholder.position = position - placeholder.size / 2
        placeholder.color = Color.BROWN
        $FurnitureLayer/StaticFurniture.add_child(placeholder)
        
        # Add label for development
        var label = Label.new()
        label.text = furniture_name
        label.position = position
        label.add_theme_color_override("font_color", Color.WHITE)
        $FurnitureLayer/StaticFurniture.add_child(label)

func get_room_position(room_name: String) -> Vector2:
    """Get pixel position for a room
    
    This is the bridge between Python's abstract rooms and Godot's concrete positions.
    When Python says 'Agent moved to Kitchen', this tells us where Kitchen is on screen.
    """
    var position = room_positions.get(room_name, Vector2.ZERO)
    if position == Vector2.ZERO:
        print("Warning: Unknown room name: ", room_name)
    return position
```

---

## Character System

**The Core Challenge:** Your Python backend has abstract "Character" objects with properties like location, inventory, and state. But humans understand characters better when they can see them move, act, and express emotions.

**What we're building:** A visual character system that:
1. **Represents Agents Visually**: Each AI agent gets a sprite that players can see
2. **Shows State Changes**: When an agent is "thinking" (waiting for LLM response), we show a thinking animation
3. **Animates Actions**: When Python says "agent picked up item," we show a pickup animation
4. **Displays Information**: Character names, status, current action

### Character Scene

**Why this structure?** We separate character components by function:
- **Visuals**: Everything related to how the character looks
- **Collision**: For detecting clicks or interactions
- **UI**: Text and icons that float above the character
- **Movement**: Smooth movement between rooms

Create `scenes/Character.tscn` for 2D sprite animation:

```
Character (CharacterBody2D)
├── Visuals (Node2D)                    # All visual elements
│   ├── Sprite2D                        # The main character image
│   │   └── Texture (current animation frame)
│   ├── AnimationPlayer (for sprite animations)  # Built-in animation system
│   └── AnimationTree (for blend trees)         # Advanced animation blending
├── CollisionShape2D                    # For mouse clicks and interaction
├── UI (Node2D)                         # Information display
│   ├── NameLabel (Label)               # Character name floating above
│   └── StatusIcons (Node2D)            # Visual status indicators
│       ├── ThinkingIcon (Sprite2D)     # Shows when LLM is processing
│       └── ActionIcon (Sprite2D)       # Shows current action type
└── Movement (Node2D)                   # Smooth movement system
    └── Tween                           # Built-in smooth animation
```

**Node type explanations:**
- **CharacterBody2D**: Built for moving objects with collision detection
- **Sprite2D**: Displays a 2D image (your character's appearance)
- **AnimationPlayer**: Godot's system for animating properties over time
- **Label**: For displaying text (character names, status)
- **Tween**: For smooth transitions (moving between rooms)

### Character Controller

**What this script does:** Bridges the gap between Python's abstract character data and Godot's visual character representation. 

**Key responsibilities:**
1. **State Management**: Track character's current state (idle, walking, thinking, acting)
2. **Sprite Management**: Load and switch between different character images
3. **Animation**: Smoothly animate actions and state changes
4. **Visual Feedback**: Show what the character is doing or thinking

**The Sprite State System:** Unlike simple games where characters have one image, your agents need different sprites for different states:
- **Idle**: Normal standing pose
- **Walk**: Walking animation frames
- **Action**: Generic "doing something" pose
- **Thinking**: Contemplative pose (while LLM processes)

Create `scripts/Character.gd`:

```gdscript
# Character.gd
extends CharacterBody2D

@export var character_name: String = ""
@export var move_speed: float = 200.0

# Sprite management - references to our visual components
@onready var sprite = $Visuals/Sprite2D                    # The main character image
@onready var animation_player = $Visuals/AnimationPlayer   # For animating sprite changes
@onready var animation_tree = $Visuals/AnimationTree       # For complex animation blending
@onready var name_label = $UI/NameLabel                    # Character name display
@onready var thinking_icon = $UI/StatusIcons/ThinkingIcon  # "Agent is thinking" indicator
@onready var action_icon = $UI/StatusIcons/ActionIcon      # "Agent is acting" indicator
@onready var tween = $Movement/Tween                       # For smooth movement

# Sprite textures for different states
# This dictionary holds different images for different character states
# Think of it like a character's "wardrobe" - different outfits for different activities
var sprite_textures = {
    "idle": null,      # Normal standing around
    "walk": null,      # Walking between rooms
    "action": null,    # Performing actions (get, drop, etc.)
    "thinking": null   # Waiting for LLM to decide what to do
}

# Current facing direction (for sprite flipping)
# This lets characters face the direction they're moving
var facing_direction: int = 1  # 1 = right, -1 = left

var current_room: String = ""
var target_position: Vector2
var is_moving: bool = false

signal movement_completed
signal action_completed

func _ready():
    name_label.text = character_name
    target_position = global_position
    load_character_sprites()
    setup_animations()
    
    # Hide status icons by default
    thinking_icon.visible = false
    action_icon.visible = false

func load_character_sprites():
    """Load all sprite variations for this character
    
    This function loads different images for different character states.
    Each character should have their own folder with these images:
    - character_name/idle.png
    - character_name/walk.png  
    - character_name/action.png
    - character_name/thinking.png
    """
    var base_path = "res://assets/characters/" + character_name.to_lower() + "/"
    
    # Try to load each sprite state
    sprite_textures["idle"] = load(base_path + "idle.png")
    sprite_textures["walk"] = load(base_path + "walk.png")
    sprite_textures["action"] = load(base_path + "action.png")
    sprite_textures["thinking"] = load(base_path + "thinking.png")
    
    # Set initial sprite to idle state
    set_sprite_state("idle")
    
    print("Loaded sprites for character: ", character_name)

func setup_animations():
    """Setup animation player with sprite frame animations"""
    # Create idle animation
    var idle_anim = Animation.new()
    idle_anim.length = 2.0
    idle_anim.loop_mode = Animation.LOOP_LINEAR
    
    # Create walk animation
    var walk_anim = Animation.new()
    walk_anim.length = 0.8
    walk_anim.loop_mode = Animation.LOOP_LINEAR
    
    # Add to animation library
    var library = AnimationLibrary.new()
    library.add_animation("idle", idle_anim)
    library.add_animation("walk", walk_anim)
    animation_player.add_animation_library("default", library)

func set_sprite_state(state: String):
    """Change character sprite based on current state
    
    This is the key function that visually represents what the character is doing.
    When Python tells us an agent is thinking, we call set_sprite_state('thinking')
    When they start moving, we call set_sprite_state('walk')
    """
    if state in sprite_textures and sprite_textures[state]:
        sprite.texture = sprite_textures[state]
        
        # Update sprite flip based on facing direction
        # This makes characters face the direction they're moving
        sprite.flip_h = (facing_direction < 0)
        
        print(character_name, " changed to state: ", state)
    else:
        print("Warning: No sprite found for state: ", state, " for character: ", character_name)

func _physics_process(delta):
    if is_moving:
        var direction = (target_position - global_position).normalized()
        if global_position.distance_to(target_position) > 5.0:
            velocity = direction * move_speed
            move_and_slide()
        else:
            global_position = target_position
            velocity = Vector2.ZERO
            is_moving = false
            movement_completed.emit()

func move_to_room(room_name: String, house: Node2D):
    """Move character to a specific room
    
    This function translates Python's abstract movement ('agent moved to kitchen')
    into visual movement (character sprite moves to kitchen coordinates).
    """
    var room_pos = house.get_room_position(room_name)
    if room_pos != Vector2.ZERO:
        current_room = room_name
        move_to_position(room_pos)
        print(character_name, " moving to room: ", room_name, " at position: ", room_pos)
    else:
        print("Error: Cannot move ", character_name, " to unknown room: ", room_name)

func move_to_position(pos: Vector2):
    """Move character to specific position
    
    This handles the visual movement from current position to target position.
    It includes:
    - Updating facing direction based on movement
    - Changing to walking sprite
    - Adding walking animation effects
    """
    target_position = pos
    is_moving = true
    
    # Update facing direction based on movement
    # This makes the character face the direction they're moving
    if pos.x > global_position.x:
        facing_direction = 1   # Moving right
    elif pos.x < global_position.x:
        facing_direction = -1  # Moving left
    
    # Change to walking sprite and animation
    set_sprite_state("walk")
    if animation_player.has_animation("walk"):
        animation_player.play("walk")
    
    # Show movement with a slight bob effect (makes walking look more natural)
    var bob_tween = create_tween()
    bob_tween.tween_method(_apply_walk_bob, 0.0, PI * 2, 0.8)
    
func _apply_walk_bob(progress: float):
    """Create subtle bobbing effect while walking"""
    if is_moving:
        sprite.offset.y = sin(progress * 4) * 2

func show_thinking_state(duration: float = 2.0):
    """Show character in thinking state for LLM processing
    
    This is crucial for multi-agent visualization! When an AI agent
    is waiting for the LLM to decide what to do next, we show
    a visual "thinking" state so players understand why the agent
    isn't moving.
    
    Without this, players would see agents just freeze randomly,
    which would be confusing.
    """
    set_sprite_state("thinking")
    thinking_icon.visible = true
    
    var think_tween = create_tween()
    think_tween.tween_property(thinking_icon, "modulate:a", 1.0, 0.3)
    think_tween.tween_method(_bob_thinking_icon, 0, PI * duration, duration)
    
    # Auto-hide after duration
    await get_tree().create_timer(duration).timeout
    hide_thinking_state()

func hide_thinking_state():
    """Hide thinking state"""
    var hide_tween = create_tween()
    hide_tween.tween_property(thinking_icon, "modulate:a", 0.0, 0.2)
    await hide_tween.finished
    thinking_icon.visible = false
    set_sprite_state("idle")

func show_action_feedback(action_type: String):
    """Show brief action feedback icon
    
    This provides immediate visual feedback when an action occurs.
    Even before the full animation plays, players can see a quick
    color-coded icon that indicates what type of action happened.
    
    This is especially important in multi-agent games where several
    agents might be acting simultaneously.
    """
    action_icon.visible = true
    
    # Set appropriate icon color based on action type
    # This creates a visual "language" for different actions
    match action_type:
        "get":
            action_icon.modulate = Color.GREEN     # Green = acquisition
        "drop":
            action_icon.modulate = Color.YELLOW    # Yellow = release
        "give":
            action_icon.modulate = Color.BLUE      # Blue = interaction
        "move":
            action_icon.modulate = Color.CYAN      # Cyan = movement
        _:
            action_icon.modulate = Color.WHITE     # White = generic
    
    # Animate the icon: grow then shrink
    var feedback_tween = create_tween()
    feedback_tween.tween_property(action_icon, "scale", Vector2.ONE * 1.5, 0.2)
    feedback_tween.tween_property(action_icon, "scale", Vector2.ZERO, 0.3)
    
    await feedback_tween.finished
    action_icon.visible = false

func perform_action(action_type: String, target: String = ""):
    """Animate a specific action
    
    This function translates Python action events into visual animations.
    When Python sends 'agent picked up lamp', this function receives 'get'
    and plays the appropriate pickup animation.
    """
    print(character_name, " performing action: ", action_type, " on: ", target)
    
    match action_type:
        "get":
            animate_pickup()
        "drop":
            animate_drop()
        "give":
            animate_give()
        "examine":
            animate_examine()
        _:
            # Default action animation for unknown actions
            animate_generic_action()

func animate_pickup():
    """Animation for picking up items"""
    set_sprite_state("action")
    
    # Crouch down animation
    var pickup_tween = create_tween()
    pickup_tween.parallel().tween_property(self, "scale", Vector2(1.0, 0.7), 0.2)
    pickup_tween.parallel().tween_property(sprite, "offset", Vector2(0, 10), 0.2)
    
    await pickup_tween.finished
    
    # Return to normal
    var return_tween = create_tween()
    return_tween.parallel().tween_property(self, "scale", Vector2.ONE, 0.2)
    return_tween.parallel().tween_property(sprite, "offset", Vector2.ZERO, 0.2)
    
    await return_tween.finished
    set_sprite_state("idle")
    action_completed.emit()

func animate_drop():
    """Animation for dropping items"""
    if tween:
        tween.tween_property(self, "rotation", 0.2, 0.1)
        tween.tween_property(self, "rotation", 0.0, 0.1)
    
    await get_tree().create_timer(0.2).timeout
    action_completed.emit()

func animate_give():
    """Animation for giving items to others"""
    # Gesture toward another character
    if tween:
        tween.tween_property(sprite, "offset", Vector2(10, 0), 0.3)
        tween.tween_property(sprite, "offset", Vector2.ZERO, 0.3)
    
    await get_tree().create_timer(0.6).timeout
    action_completed.emit()

func animate_examine():
    """Animation for examining things"""
    set_sprite_state("thinking")
    
    # Show thinking icon
    thinking_icon.visible = true
    var think_tween = create_tween()
    think_tween.tween_property(thinking_icon, "modulate:a", 1.0, 0.3)
    
    # Lean forward and add question mark bob
    var examine_tween = create_tween()
    examine_tween.parallel().tween_property(sprite, "offset", Vector2(5, -2), 0.3)
    examine_tween.parallel().tween_method(_bob_thinking_icon, 0, PI * 3, 1.0)
    
    await examine_tween.finished
    
    # Hide thinking icon and return to normal
    var hide_tween = create_tween()
    hide_tween.parallel().tween_property(thinking_icon, "modulate:a", 0.0, 0.2)
    hide_tween.parallel().tween_property(sprite, "offset", Vector2.ZERO, 0.2)
    
    await hide_tween.finished
    thinking_icon.visible = false
    set_sprite_state("idle")
    action_completed.emit()

func _bob_thinking_icon(progress: float):
    """Make thinking icon bob up and down"""
    thinking_icon.position.y = -20 + sin(progress) * 3

func animate_generic_action():
    """Default animation for unknown actions"""
    # Simple bounce
    if tween:
        tween.tween_property(self, "position:y", position.y - 10, 0.2)
        tween.tween_property(self, "position:y", position.y, 0.2)
    
    await get_tree().create_timer(0.4).timeout
    action_completed.emit()
```

---

## Item System and State Management

**The State Challenge:** In your text adventure, items have properties that change over time:
- A bathtub can be empty or full
- A lamp can be on or off
- A door can be open or closed
- A container can be empty or full of items

But how do you show these states visually? The solution is **state-based sprites** - different images for different states.

**Why This Matters for Multi-Agent Games:**
When Agent A fills the bathtub and Agent B later tries to use it, players need to see that the bathtub is already full. Visual state representation prevents confusion about what's possible.

### Item Scene Structure

**What this does:** Creates a flexible item system where each item can have multiple visual states and can change appearance based on Python backend events.

Create `scenes/Item.tscn` for state-based item sprites:

```
Item (Node2D)
├── Visuals (Node2D)                      # All visual elements
│   ├── Sprite2D                          # Main item image (changes based on state)
│   ├── AnimationPlayer                   # For state transition animations
│   └── EffectSprites (Node2D)            # For glows, sparkles, steam, etc.
├── Interaction (Area2D)                  # For detecting mouse clicks
│   └── CollisionShape2D                  # Defines clickable area
└── StateManager (Node)                   # Custom script for state changes
```

**Why this structure?**
- **Visuals**: Separate visual elements from interaction logic
- **Interaction**: Let players click on items (useful for manual testing)
- **StateManager**: Clean separation between visual representation and state logic

### Item State System

**The Core Idea:** Each item maintains a dictionary of state → sprite mappings. When the Python backend sends an event like "bathtub changed from empty to full," we:
1. Update our internal state
2. Load the new sprite
3. Animate the transition
4. Add appropriate visual effects

Create `scripts/Item.gd` to handle state-based sprite changes:

```gdscript
# Item.gd
extends Node2D

@export var item_name: String = ""           # Name from Python backend (e.g., "bathtub")
@export var current_state: String = "default" # Current visual state

# References to child nodes
@onready var sprite = $Visuals/Sprite2D                # Main item sprite
@onready var animation_player = $Visuals/AnimationPlayer  # For state transitions
@onready var effect_sprites = $Visuals/EffectSprites      # For visual effects
@onready var interaction_area = $Interaction              # For mouse interaction

# State-based sprites - the heart of the system
# This dictionary maps state names to texture resources
var state_textures: Dictionary = {}  # e.g., {"empty": texture1, "full": texture2}
var is_gettable: bool = true         # Can agents pick this up?
var is_interactive: bool = true      # Can players click on it?

signal item_interacted(item_name, state)  # Emitted when player clicks the item

func _ready():
    load_item_sprites()
    setup_interaction()
    update_visual_state()

func load_item_sprites():
    """Load all sprite states for this item
    
    This function implements a naming convention for item states.
    For a bathtub, it would look for:
    - bathtub_empty.png
    - bathtub_full.png
    - bathtub_default.png
    
    This convention makes it easy for artists to create state variations.
    """
    var base_path = "res://assets/items/" + item_name.to_lower() + "/"
    
    # Common state patterns for items
    # These cover most text adventure item states
    var state_files = {
        "default": "_default.png",    # Normal/inactive state
        "empty": "_empty.png",        # Container is empty
        "full": "_full.png",          # Container is full
        "on": "_on.png",              # Device is powered on
        "off": "_off.png",            # Device is powered off
        "open": "_open.png",          # Door/container is open
        "closed": "_closed.png",      # Door/container is closed
        "lit": "_lit.png",            # Light source is active
        "unlit": "_unlit.png",        # Light source is inactive
        "broken": "_broken.png",      # Item is damaged
        "used": "_used.png"           # Item has been used/consumed
    }
    
    # Try to load each state sprite
    for state in state_files:
        var path = base_path + item_name.to_lower() + state_files[state]
        if ResourceLoader.exists(path):
            state_textures[state] = load(path)
            print("Loaded ", state, " sprite for ", item_name)
    
    # Always have a default if no specific states found
    if state_textures.is_empty():
        var default_path = "res://assets/items/" + item_name.to_lower() + ".png"
        if ResourceLoader.exists(default_path):
            state_textures["default"] = load(default_path)
            print("Loaded default sprite for ", item_name)
        else:
            print("Warning: No sprites found for item: ", item_name)

func setup_interaction():
    """Setup interaction area for clickable items"""
    if is_interactive:
        interaction_area.input_event.connect(_on_item_clicked)
        interaction_area.mouse_entered.connect(_on_mouse_enter)
        interaction_area.mouse_exited.connect(_on_mouse_exit)

func set_state(new_state: String, animate: bool = true):
    """Change item state and update visuals
    
    This is the key function that connects Python backend events
    to visual changes. When Python says 'bathtub is now full',
    this function changes the sprite from empty to full.
    """
    if new_state == current_state:
        return  # No change needed
    
    var old_state = current_state
    current_state = new_state
    
    print(item_name, " changing state from ", old_state, " to ", new_state)
    
    if animate:
        animate_state_change(old_state, new_state)
    else:
        update_visual_state()
    
    item_interacted.emit(item_name, new_state)

func update_visual_state():
    """Update sprite based on current state
    
    This function actually changes what the player sees.
    It's the final step in the Python → Godot state chain.
    """
    if current_state in state_textures:
        sprite.texture = state_textures[current_state]
    elif "default" in state_textures:
        sprite.texture = state_textures["default"]
        print("Warning: No sprite for state '", current_state, "' using default")
    
    # Add state-specific effects (glow, particles, etc.)
    update_effects_for_state()

func update_effects_for_state():
    """Add visual effects based on current state
    
    Visual effects make state changes more obvious and engaging.
    Instead of just swapping sprites, we add glows, particles,
    animations that draw the player's attention to changes.
    """
    # Clear existing effects
    for child in effect_sprites.get_children():
        child.queue_free()
    
    # Add effects for specific states
    match current_state:
        "lit", "on":
            add_glow_effect(Color.YELLOW, 1.2)  # Yellow glow for lights
        "full":
            if item_name.to_lower().contains("bathtub"):
                add_water_ripple_effect()  # Water animation
        "broken":
            add_damage_particles()      # Smoke/sparks for broken items
        "empty":
            # Could add "dusty" or "dry" effects here

func add_glow_effect(color: Color, intensity: float):
    """Add glowing effect for lit items"""
    var glow = Sprite2D.new()
    glow.texture = sprite.texture
    glow.modulate = color
    glow.modulate.a = 0.3 * intensity
    glow.scale = Vector2.ONE * (1.0 + 0.1 * intensity)
    effect_sprites.add_child(glow)
    
    # Animate glow pulsing
    var tween = create_tween()
    tween.set_loops()
    tween.tween_property(glow, "modulate:a", 0.1, 1.0)
    tween.tween_property(glow, "modulate:a", 0.4, 1.0)

func add_water_ripple_effect():
    """Add water ripple effect for bathtub"""
    # Create simple animated ripples
    for i in range(3):
        var ripple = create_ripple_sprite()
        ripple.position = Vector2(randf_range(-20, 20), randf_range(-10, 10))
        effect_sprites.add_child(ripple)
        
        # Animate ripple expanding and fading
        var tween = create_tween()
        tween.set_loops()
        tween.tween_delay(i * 0.5)  # Stagger ripples
        tween.parallel().tween_property(ripple, "scale", Vector2.ONE * 2, 1.5)
        tween.parallel().tween_property(ripple, "modulate:a", 0.0, 1.5)
        tween.tween_callback(func(): 
            ripple.scale = Vector2.ONE * 0.1
            ripple.modulate.a = 0.6
        )

func create_ripple_sprite() -> Sprite2D:
    """Create a simple ripple sprite"""
    var ripple = Sprite2D.new()
    # You would load a ripple texture here
    # ripple.texture = preload("res://assets/effects/ripple.png")
    ripple.modulate = Color.CYAN
    ripple.modulate.a = 0.6
    ripple.scale = Vector2.ONE * 0.1
    return ripple

func animate_state_change(from_state: String, to_state: String):
    """Animate transition between states
    
    Different state changes deserve different animations:
    - Filling/emptying should be smooth
    - Breaking should be dramatic
    - Turning on/off should be quick
    
    This makes the world feel more alive and responsive.
    """
    match [from_state, to_state]:
        ["empty", "full"], ["off", "on"], ["closed", "open"]:
            # Smooth transition animation for gradual changes
            animate_smooth_transition()
        ["default", "broken"]:
            # Dramatic break animation for destructive changes
            animate_break_effect()
        _:
            # Default fade transition for other changes
            animate_fade_transition()

func animate_smooth_transition():
    """Smooth state transition with scaling"""
    var tween = create_tween()
    tween.tween_property(self, "scale", Vector2.ONE * 1.1, 0.2)
    tween.tween_callback(update_visual_state)
    tween.tween_property(self, "scale", Vector2.ONE, 0.2)

func animate_fade_transition():
    """Fade out, change, fade in"""
    var tween = create_tween()
    tween.tween_property(sprite, "modulate:a", 0.0, 0.3)
    tween.tween_callback(update_visual_state)
    tween.tween_property(sprite, "modulate:a", 1.0, 0.3)

func _on_item_clicked(viewport, event, shape_idx):
    """Handle mouse clicks on item"""
    if event is InputEventMouseButton and event.pressed:
        # Emit signal for game manager to handle
        item_interacted.emit(item_name, current_state)

func _on_mouse_enter():
    """Show hover effect"""
    var tween = create_tween()
    tween.tween_property(self, "modulate", Color.WHITE * 1.2, 0.1)

func _on_mouse_exit():
    """Remove hover effect"""
    var tween = create_tween()
    tween.tween_property(self, "modulate", Color.WHITE, 0.1)
```

### Dynamic Item Management

**The Challenge:** Your Python backend creates and destroys items dynamically. A character might craft a new item, or an existing item might break and disappear. Your Godot frontend needs to create and remove visual representations accordingly.

**The Solution:** The GameManager monitors backend events and creates/destroys item sprites as needed. It also manages item positioning within rooms.

Add to `scripts/GameManager.gd`:

```gdscript
# Add to GameManager.gd

func setup_items(locations_data: Dictionary):
    """Create item sprites based on backend state
    
    This function runs at startup to create visual representations
    of all items that exist in the Python backend.
    """
    for location_name in locations_data:
        var location_data = locations_data[location_name]
        var items_in_location = location_data.get("items", [])
        
        print("Setting up items for location: ", location_name)
        for item_name in items_in_location:
            if not items.has(item_name):
                create_item_sprite(item_name, location_name)

func create_item_sprite(item_name: String, location_name: String):
    """Create and position an item sprite
    
    This function bridges Python's abstract items with Godot's visual items.
    It creates the sprite, positions it appropriately within the room,
    and connects it to interaction systems.
    """
    var item_scene = preload("res://scenes/Item.tscn")
    var item = item_scene.instantiate()
    item.item_name = item_name
    
    # Position item in the correct room with appropriate offset
    var room_pos = house.get_room_position(location_name)
    item.position = room_pos + get_item_offset(item_name, location_name)
    
    house.items_node.add_child(item)
    items[item_name] = item
    
    # Connect to item interaction signals for manual testing
    item.item_interacted.connect(_on_item_interacted)
    
    print("Created item sprite: ", item_name, " at position: ", item.position)

func get_item_offset(item_name: String, location_name: String) -> Vector2:
    """Get position offset for item within room
    
    This function positions items logically within rooms.
    A bathtub should be in a specific spot in the bathroom,
    not randomly floating around.
    """
    # Define where specific items appear in each room
    # This creates a more realistic and consistent world
    var item_positions = {
        "bathtub": {"Bathroom": Vector2(-30, 20)},      # Left side of bathroom
        "lamp": {                                       # Lamps in multiple rooms
            "Living Room": Vector2(40, -30),           # Near seating area
            "Bedroom": Vector2(-40, -20)               # Bedside table
        },
        "stove": {"Kitchen": Vector2(-50, 10)},        # Kitchen counter area
        "book": {"Living Room": Vector2(0, 30)},       # Coffee table
        "refrigerator": {"Kitchen": Vector2(60, -20)}, # Opposite wall from stove
        "bed": {"Bedroom": Vector2(0, 20)}             # Center of bedroom
    }
    
    if item_name in item_positions and location_name in item_positions[item_name]:
        return item_positions[item_name][location_name]
    
    # Default random position within room bounds (for unknown items)
    print("Using random position for unknown item: ", item_name, " in ", location_name)
    return Vector2(randf_range(-60, 60), randf_range(-40, 40))

func _on_item_interacted(item_name: String, state: String):
    """Handle item interactions from frontend"""
    print("Item interacted: ", item_name, " in state: ", state)
    # Could send interaction to backend if needed
    # backend_connector.send_command("examine " + item_name)

func update_item_state(item_name: String, new_state: String):
    """Update item state from backend events
    
    This function is called when Python sends events like:
    'bathtub changed from empty to full'
    'lamp turned on'
    'door opened'
    
    It finds the visual item and updates its appearance.
    """
    if items.has(item_name):
        items[item_name].set_state(new_state, true)
        print("Updated item ", item_name, " to state: ", new_state)
    else:
        print("Warning: Tried to update unknown item: ", item_name)
```

---

## Animation System

**The Animation Challenge:** Your Python backend processes actions instantly - when an agent picks up an item, the item immediately disappears from the location and appears in inventory. But players need to see what happened!

**The Solution:** An animation queue system that:
1. **Receives Events**: Gets a stream of events from Python
2. **Queues Animations**: Stores them in order to prevent overlapping
3. **Plays Sequentially**: Shows one animation at a time so players can follow
4. **Provides Feedback**: Gives visual confirmation that actions occurred

**Why Sequential?** If multiple agents act simultaneously, playing all animations at once would be chaotic. Sequential animation lets players understand what each agent did.

### Event Animation Manager

**What this does:** Serves as the "director" of your visual world. It receives abstract events from Python and orchestrates concrete animations in Godot.

Create `scripts/GameManager.gd`:

```gdscript
# GameManager.gd
extends Node

@onready var backend_connector = $BackendConnector
@onready var house = $House
@onready var ui = $UI

var characters: Dictionary = {}    # name -> Character node (visual representations)
var items: Dictionary = {}         # name -> Item node (visual representations) 
var animation_queue: Array = []    # Events waiting to be animated
var current_animation: Dictionary = {}  # Currently playing animation

func _ready():
    # Connect to backend signals
    backend_connector.game_state_received.connect(_on_game_state_received)
    backend_connector.events_received.connect(_on_events_received)
    
    # Request initial game state
    backend_connector.request_game_state()

func _on_game_state_received(state: Dictionary):
    """Handle initial game state or state refresh"""
    print("Game state received: ", state)
    setup_characters(state.characters)
    setup_items(state.locations)

func setup_characters(characters_data: Dictionary):
    """Create or update character nodes"""
    for char_name in characters_data:
        var char_data = characters_data[char_name]
        
        if not characters.has(char_name):
            # Create new character
            var character_scene = preload("res://scenes/Character.tscn")
            var character = character_scene.instantiate()
            character.character_name = char_name
            house.characters_node.add_child(character)
            characters[char_name] = character
        
        # Update character position
        var character = characters[char_name]
        if char_data.location:
            character.move_to_room(char_data.location, house)

func _on_events_received(events: Array):
    """Handle new events from backend
    
    This is where Python events enter the Godot animation system.
    Each event represents something that happened in the game world
    that needs to be shown to the player.
    """
    print("Received ", events.size(), " events from Python backend")
    
    for event in events:
        animation_queue.append(event)
        print("Queued animation for event: ", event.type)
    
    # Start processing queue if not already animating
    if animation_queue.size() > 0 and current_animation.is_empty():
        process_next_animation()

func process_next_animation():
    """Process the next event in the animation queue
    
    This maintains the sequential nature of animations.
    Only one animation plays at a time, ensuring players
    can follow the action clearly.
    """
    if animation_queue.is_empty():
        return
    
    current_animation = animation_queue.pop_front()
    print("Starting animation for: ", current_animation.type)
    animate_event(current_animation)

func animate_event(event: Dictionary):
    """Animate a specific event
    
    This is the main event → animation dispatcher.
    It maps Python event types to specific animation functions.
    
    Each animation function handles:
    1. Finding the relevant visual objects
    2. Playing appropriate animations
    3. Updating visual state
    4. Signaling when complete
    """
    print("Animating event: ", event.type, " with data: ", event.data)
    
    match event.type:
        "move":
            animate_movement(event.data)
        "get":
            animate_get_item(event.data)
        "drop":
            animate_drop_item(event.data)
        "give":
            animate_give_item(event.data)
        "examine":
            animate_examine(event.data)
        "state_change":  # For item state changes
            animate_state_change(event.data)
        _:
            # Unknown event type, log and finish
            print("Warning: Unknown event type: ", event.type)
            finish_current_animation()

func animate_movement(data: Dictionary):
    """Animate character movement"""
    var char_name = data.character
    var to_location = data.to_location
    
    if characters.has(char_name):
        var character = characters[char_name]
        character.movement_completed.connect(_on_animation_finished, CONNECT_ONE_SHOT)
        character.move_to_room(to_location, house)
        
        # Show action feedback
        character.show_action_feedback("move")
    else:
        finish_current_animation()

func animate_get_item(data: Dictionary):
    """Animate item pickup
    
    This function visualizes the abstract concept 'character got item'.
    It shows:
    1. Character performing pickup action
    2. Item moving toward character  
    3. Item disappearing (now in inventory)
    4. Visual feedback about the action
    """
    var char_name = data.character
    var item_name = data.item
    
    print(char_name, " picking up ", item_name)
    
    if characters.has(char_name):
        var character = characters[char_name]
        character.action_completed.connect(_on_animation_finished, CONNECT_ONE_SHOT)
        character.perform_action("get", item_name)
        character.show_action_feedback("get")
        
        # Animate item moving to character then hide
        if items.has(item_name):
            var item = items[item_name]
            # Create smooth movement from item to character
            var item_tween = create_tween()
            item_tween.parallel().tween_property(item, "global_position", character.global_position, 0.3)
            item_tween.parallel().tween_property(item, "scale", Vector2.ZERO, 0.3)
            await item_tween.finished
            item.visible = false  # Item is now "in inventory"
            item.scale = Vector2.ONE  # Reset scale for when dropped later
        else:
            print("Warning: Item ", item_name, " not found for pickup animation")
    else:
        print("Warning: Character ", char_name, " not found for pickup animation")
        finish_current_animation()

func animate_drop_item(data: Dictionary):
    """Animate item drop"""
    var char_name = data.character
    var item_name = data.item
    
    if characters.has(char_name):
        var character = characters[char_name]
        character.action_completed.connect(_on_animation_finished, CONNECT_ONE_SHOT)
        character.perform_action("drop", item_name)
        
        # Show item in scene at character location
        if items.has(item_name):
            items[item_name].global_position = character.global_position
            items[item_name].visible = true
    else:
        finish_current_animation()

func _on_animation_finished():
    """Called when current animation completes"""
    finish_current_animation()

func finish_current_animation():
    """Clean up current animation and start next"""
    current_animation = {}
    
    # Process next animation after a short delay
    await get_tree().create_timer(0.1).timeout
    process_next_animation()
```

---

## UI Implementation

### Game UI Layout

Create `scenes/UI/GameUI.tscn`:

```
GameUI (Control)
├── VBoxContainer
│   ├── TopPanel (HBoxContainer)
│   │   ├── TurnLabel (Label)
│   │   └── GameStatusLabel (Label)
│   ├── CenterPanel (HBoxContainer)
│   │   ├── LeftSidebar (VBoxContainer)
│   │   │   ├── AgentPanelContainer
│   │   │   └── ManualControls
│   │   └── MainView (empty - house scene shows here)
│   └── BottomPanel (HBoxContainer)
│       ├── ActionLog (LogPanel scene)
│       └── CommandInput (LineEdit)
```

### Game UI Controller

Create `scripts/UI/GameUI.gd`:

```gdscript
# GameUI.gd
extends Control

@onready var turn_label = $VBoxContainer/TopPanel/TurnLabel
@onready var status_label = $VBoxContainer/TopPanel/GameStatusLabel
@onready var agent_container = $VBoxContainer/CenterPanel/LeftSidebar/AgentPanelContainer
@onready var action_log = $VBoxContainer/BottomPanel/ActionLog
@onready var command_input = $VBoxContainer/BottomPanel/CommandInput

var agent_panels: Dictionary = {}

func _ready():
    # Connect manual command input
    command_input.text_submitted.connect(_on_command_submitted)

func update_turn_display(current_agent: String, turn_number: int):
    """Update the current turn display"""
    turn_label.text = "Turn %d - %s's Turn" % [turn_number, current_agent]

func update_game_status(game_over: bool, winner: String = ""):
    """Update game status display"""
    if game_over:
        if winner:
            status_label.text = "Game Over - %s Wins!" % winner
        else:
            status_label.text = "Game Over"
        status_label.modulate = Color.RED
    else:
        status_label.text = "Game Running"
        status_label.modulate = Color.GREEN

func create_agent_panel(agent_name: String):
    """Create UI panel for an agent"""
    var panel_scene = preload("res://scenes/UI/AgentPanel.tscn")
    var panel = panel_scene.instantiate()
    panel.setup(agent_name)
    agent_container.add_child(panel)
    agent_panels[agent_name] = panel

func update_agent_panel(agent_name: String, data: Dictionary):
    """Update agent panel with current data"""
    if agent_panels.has(agent_name):
        agent_panels[agent_name].update_display(data)

func add_log_entry(text: String, agent_name: String = ""):
    """Add entry to action log"""
    action_log.add_entry(text, agent_name)

func _on_command_submitted(command: String):
    """Handle manual command input"""
    if command.strip() != "":
        var game_manager = get_tree().get_first_node_in_group("game_manager")
        if game_manager:
            game_manager.backend_connector.send_command(command)
        command_input.text = ""
```

### Agent Panel

Create `scenes/UI/AgentPanel.tscn`:

```
AgentPanel (PanelContainer)
└── VBoxContainer
    ├── NameLabel (Label)
    ├── LocationLabel (Label)
    ├── InventoryLabel (Label)
    └── InventoryList (ItemList)
```

Create `scripts/UI/AgentPanel.gd`:

```gdscript
# AgentPanel.gd
extends PanelContainer

@onready var name_label = $VBoxContainer/NameLabel
@onready var location_label = $VBoxContainer/LocationLabel
@onready var inventory_label = $VBoxContainer/InventoryLabel
@onready var inventory_list = $VBoxContainer/InventoryList

var agent_name: String

func setup(agent_name: String):
    """Initialize panel for specific agent"""
    self.agent_name = agent_name
    name_label.text = agent_name
    update_display({})

func update_display(data: Dictionary):
    """Update panel with agent data"""
    # Update location
    var location = data.get("location", "Unknown")
    location_label.text = "Location: " + location
    
    # Update inventory
    var inventory = data.get("inventory", [])
    if inventory.is_empty():
        inventory_label.text = "Inventory: Empty"
        inventory_list.visible = false
    else:
        inventory_label.text = "Inventory:"
        inventory_list.visible = true
        inventory_list.clear()
        for item in inventory:
            inventory_list.add_item(item)
```

---

## Event Processing

### Detailed Event Handling

Expand the GameManager to handle all event types:

```gdscript
# Add to GameManager.gd

func animate_event(event: Dictionary):
    """Animate a specific event with detailed handling"""
    print("Animating event: ", event)
    
    # Log the event to UI
    var log_text = format_event_for_log(event)
    ui.add_log_entry(log_text, event.data.get("character", ""))
    
    match event.type:
        "move":
            animate_movement(event.data)
        "get":
            animate_get_item(event.data)
        "drop":
            animate_drop_item(event.data)
        "give":
            animate_give_item(event.data)
        "examine":
            animate_examine(event.data)
        "attack":
            animate_attack(event.data)
        "eat":
            animate_eat(event.data)
        "talk":
            animate_talk(event.data)
        _:
            # Unknown event type
            ui.add_log_entry("Unknown action: " + str(event), "System")
            finish_current_animation()

func format_event_for_log(event: Dictionary) -> String:
    """Convert event to readable log text"""
    var data = event.data
    var char_name = data.get("character", "Someone")
    
    match event.type:
        "move":
            return "%s moved %s to %s" % [char_name, data.get("direction", ""), data.get("to_location", "")]
        "get":
            return "%s picked up %s" % [char_name, data.get("item", "something")]
        "drop":
            return "%s dropped %s" % [char_name, data.get("item", "something")]
        "give":
            return "%s gave %s to %s" % [char_name, data.get("item", "something"), data.get("recipient", "someone")]
        "examine":
            return "%s examined %s" % [char_name, data.get("target", "something")]
        _:
            return "%s performed action: %s" % [char_name, event.type]
```

---

## Testing and Debugging

### Debug Mode

Add debug features to help development:

```gdscript
# Add to GameManager.gd

var debug_mode: bool = true
var debug_panel: Control

func _ready():
    # ... existing code ...
    
    if debug_mode:
        setup_debug_panel()

func setup_debug_panel():
    """Create debug panel for development"""
    debug_panel = preload("res://scenes/UI/DebugPanel.tscn").instantiate()
    add_child(debug_panel)
    debug_panel.position = Vector2(10, 10)

func _input(event):
    if debug_mode and event.is_action_pressed("ui_accept"):  # Space key
        # Trigger manual update
        backend_connector.request_game_state()
    
    if debug_mode and event.is_action_pressed("ui_cancel"):  # Escape key
        # Skip current animation
        finish_current_animation()
```

### Debug Panel

Create `scenes/UI/DebugPanel.tscn`:

```
DebugPanel (PanelContainer)
└── VBoxContainer
    ├── RefreshButton (Button) "Refresh State"
    ├── SpeedSlider (HSlider) "Animation Speed"
    ├── EventCountLabel (Label)
    └── ConnectionStatusLabel (Label)
```

---

## Performance Optimization

### Efficient Polling

Optimize the backend polling to reduce unnecessary requests:

```gdscript
# Improve BackendConnector.gd

var last_poll_time: float = 0.0
var poll_interval: float = 0.5
var adaptive_polling: bool = true

func _poll_for_events():
    """Smart polling that adapts to activity"""
    var current_time = Time.get_time_dict_from_system()["second"]
    
    # If we recently received events, poll more frequently
    if adaptive_polling and last_event_id > 0:
        poll_interval = 0.2  # Poll faster when active
    else:
        poll_interval = 1.0  # Poll slower when idle
    
    request_events()

func _handle_events_response(events: Array):
    """Process events and adjust polling"""
    if events.size() > 0:
        last_poll_time = Time.get_time_dict_from_system()["second"]
        # Reset poll timer with new interval
        poll_timer.wait_time = poll_interval
    
    # ... rest of existing code ...
```

### Memory Management

Prevent memory leaks with proper cleanup:

```gdscript
# Add to GameManager.gd

var max_log_entries: int = 100
var max_animation_queue: int = 50

func _on_events_received(events: Array):
    """Handle events with memory management"""
    # Limit animation queue size
    for event in events:
        if animation_queue.size() < max_animation_queue:
            animation_queue.append(event)
        else:
            print("Animation queue full, dropping event: ", event.type)
    
    # Start processing if needed
    if animation_queue.size() > 0 and current_animation.is_empty():
        process_next_animation()

func cleanup_old_ui_elements():
    """Remove old UI elements to prevent memory buildup"""
    # Limit action log entries
    if ui.action_log.get_entry_count() > max_log_entries:
        ui.action_log.remove_old_entries(20)  # Remove oldest 20 entries
```

---

## Deployment and Distribution

### Building the Project

1. **Export Settings**: 
   - Go to Project → Export
   - Add your target platforms (Windows, Mac, Linux, Web)
   - Configure export templates

2. **Include Python Backend**:
   - Copy Python backend to `backend/` folder in exported project
   - Include Python runtime or create standalone executable

3. **Startup Script**:
   - Create launcher that starts Python backend first
   - Then launches Godot frontend

### Example Launcher Script (Python)

```python
# launcher.py
import subprocess
import sys
import time
import os

def start_backend():
    """Start the Python backend server"""
    backend_path = os.path.join(os.path.dirname(__file__), "backend")
    sys.path.insert(0, backend_path)
    
    from text_adventure_games.http_server import start_game_server
    from action_castle import build_game
    
    # Create game with agents
    game = build_game()
    # Add your agent setup here
    
    # Start server
    server = start_game_server(game, port=8080)
    return server

def start_frontend():
    """Start the Godot frontend"""
    if sys.platform == "win32":
        executable = "MultiAgentPlayground.exe"
    elif sys.platform == "darwin":
        executable = "MultiAgentPlayground.app"
    else:
        executable = "MultiAgentPlayground.x86_64"
    
    subprocess.Popen([executable])

if __name__ == "__main__":
    print("Starting Multi-Agent Playground...")
    
    # Start backend
    print("Starting backend server...")
    server = start_backend()
    
    # Wait for server to be ready
    time.sleep(2)
    
    # Start frontend
    print("Starting frontend...")
    start_frontend()
    
    # Keep backend running
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down...")
        server.shutdown()
```

---

## Sprite Organization and Asset Guidelines

### Character Sprite Sheets

For efficient animation, organize character sprites as sheets:

```
character_sheet.png layout:
[idle_1][idle_2][idle_3][idle_4]
[walk_1][walk_2][walk_3][walk_4] 
[action_1][action_2][action_3][action_4]
[thinking_1][thinking_2][thinking_3][thinking_4]
```

### Recommended Asset Sizes

- **Character sprites**: 32x32 or 64x64 pixels
- **Item sprites**: 24x24 to 48x48 pixels  
- **Room backgrounds**: 200x150 to 400x300 pixels
- **UI elements**: Variable, but consistent theme

### State Naming Conventions

For consistency across all items, use these state suffixes:

- `_default.png` - Normal/inactive state
- `_active.png` - When being used/interacted with
- `_empty.png` / `_full.png` - Container states
- `_on.png` / `_off.png` - Power/activation states
- `_open.png` / `_closed.png` - Door/container states
- `_lit.png` / `_unlit.png` - Light source states
- `_clean.png` / `_dirty.png` - Cleanliness states
- `_broken.png` - Damaged state

### Animation Timing Guidelines

- **Character movement**: 0.5-1.0 seconds between rooms
- **Item state changes**: 0.3-0.5 seconds for transitions
- **Action animations**: 0.4-0.8 seconds total
- **UI feedback**: 0.1-0.2 seconds for responsiveness
- **Thinking/planning**: 1-3 seconds (with visual indicator)

---

## Next Steps

1. **Start with Basic Sprites**: Create simple placeholder sprites first
2. **Implement Room Layout**: Get sprite-based room backgrounds working
3. **Add Character Animation**: Implement walking and action sprites
4. **Create Item States**: Build bathtub empty/full as first example
5. **Connect Backend Events**: Process state changes from game events
6. **Polish Animations**: Add effects, particles, and smooth transitions
7. **Optimize Performance**: Implement sprite atlasing and efficient updates

## Troubleshooting Common Issues

### Connection Problems
- Check if Python backend is running on correct port
- Verify CORS headers are set for web builds
- Test with curl or browser to verify API endpoints

### Animation Issues
- Ensure animations complete before starting next one
- Add timeout fallbacks for stuck animations
- Debug with console logs to trace event flow
- Check sprite paths are correct and textures load properly

### Sprite Loading Issues
- Verify sprite file paths match naming conventions
- Ensure all sprites are imported with correct settings
- Check that state textures dictionary is populated correctly
- Use placeholder sprites for missing assets during development

### Performance Problems
- Reduce polling frequency for stable connections
- Limit animation queue size to prevent backlog
- Profile memory usage in Godot debugger

This frontend implementation provides a solid foundation for visualizing your multi-agent text adventure game with room for creative enhancements!
