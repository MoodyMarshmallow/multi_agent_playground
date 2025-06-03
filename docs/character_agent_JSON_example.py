"""
Character JSON Data Structure Documentation
=======================================

This file documents the JSON data structures and communication protocols
used by characters in the multi-agent playground system.

Table of Contents:
1. Character Core Structure
2. Memory System
3. Backend-to-Frontend Communication
4. Frontend-to-Backend Communication
"""

# =============================================================================
# 1. CHARACTER CORE STRUCTURE
# =============================================================================

class Character:
    """
    Core data structure representing a character in the simulation.
    
    This class defines all the attributes that make up an agent's state,
    including their identity, planning, current actions, and spatial information.
    """
    
    def __init__(self, f_saved):
        
        # =====================================================================
        # CHARACTER HYPERPARAMETERS
        # =====================================================================
        
        # vision_r: int
        # Number of tiles the character can see around them
        self.vision_r = 4
        
        # retention: int  
        # TODO: Define retention mechanism
        self.retention = 5

        # =====================================================================
        # WORLD INFORMATION
        # =====================================================================
        
        # curr_time: datetime | None
        # Current perceived world time
        self.curr_time = None
        
        # curr_tile: tuple[int, int] | None
        # Current (x, y) tile coordinates of the character
        self.curr_tile = None
        
        # daily_plan_req: str | None
        # Perceived world daily requirement
        self.daily_plan_req = None
        
        # =====================================================================
        # CORE IDENTITY
        # =====================================================================
        
        # Basic Information
        # -----------------
        # name: str | None - Full name of the character
        self.name = None
        
        # first_name: str | None - First name
        self.first_name = None
        
        # last_name: str | None - Last name  
        self.last_name = None
        
        # age: int | None - Age in years
        self.age = None
        
        # Personality Layers
        # ------------------
        # innate: str | None - L0: Permanent core traits
        self.innate = None
        
        # learned: str | None - L1: Stable learned traits
        self.learned = None
        
        # currently: str | None - L2: Current state/activity
        self.currently = None
        
        # lifestyle: str | None - General lifestyle description
        self.lifestyle = None
        
        # living_area: str | None - Where the character lives
        self.living_area = None

        # =====================================================================
        # PLANNING SYSTEM
        # =====================================================================
        
        # Daily Requirements
        # ------------------
        # daily_req: list[str]
        # List of goals the character aims to achieve today
        # Must be renewed at the end of each day
        # 
        # Example:
        # [
        #     'Work on her paintings for her upcoming show',
        #     'Take a break to watch some TV', 
        #     'Make lunch for herself',
        #     'Work on her paintings some more',
        #     'Go to bed early'
        # ]
        self.daily_req = []
        
        # Daily Schedule (Decomposed)
        # ---------------------------
        # f_daily_schedule: list[list[str, int]]
        # Long-term planning with hierarchical decomposition
        # 
        # Format: [['action_description', duration_in_minutes], ...]
        # 
        # Key features:
        # 1. Some events (like 'sleeping') are not decomposed
        # 2. Events get progressively decomposed as the day progresses
        # 3. Non-decomposed future events may be replaced when new events occur
        #
        # Example:
        # [
        #     ['sleeping', 360],
        #     ['wakes up and stretches ...', 5], 
        #     ['wakes up and starts her morning routine (out of bed)', 10],
        #     ['having lunch', 60],
        #     ['working on her painting', 180]
        # ]
        self.f_daily_schedule = []
        
        # Daily Schedule (Original)
        # -------------------------
        # f_daily_schedule_hourly_org: list[list[str, int]]
        # Replica of f_daily_schedule that retains original non-decomposed hourly schedule
        #
        # Example:
        # [
        #     ['sleeping', 360], 
        #     ['wakes up and starts her morning routine', 120],
        #     ['working on her painting', 240],
        #     ['going to bed', 60]
        # ]
        self.f_daily_schedule_hourly_org = []
        
        # =====================================================================
        # CURRENT ACTION
        # =====================================================================
        
        # Location & Timing
        # -----------------
        # act_address: str | None
        # String address where action takes place
        # Format: "{world}:{sector}:{arena}:{game_objects}"
        # WARNING: Avoid negative indexing as latter elements may be missing
        # 
        # Example: "world 1:residential buildings:dolores double studio:bedroom 1:bed"
        self.act_address = None
        
        # act_start_time: datetime | None
        # When the current action started
        self.act_start_time = None
        
        # act_duration: int | None  
        # Duration of action in minutes
        self.act_duration = None
        
        # Action Description
        # ------------------
        # act_description: str | None
        # Text description of the current action
        self.act_description = None
        
        # act_pronunciation: str | None
        # Descriptive expression (currently implemented as emojis)
        self.act_pronunciation = None
        
        # act_event: tuple[str, Any, Any]
        # Event triple (subject, verb, object) for current character engagement
        self.act_event = (self.name, None, None)

        # Object Interaction
        # ------------------
        # act_obj_description: str | None
        # Description of object being interacted with
        self.act_obj_description = None
        
        # act_obj_pronunciation: str | None
        # Descriptive expression for object action (emojis)
        self.act_obj_pronunciation = None
        
        # act_obj_event: tuple[str, Any, Any]
        # Event triple (subject, verb, object) for object interaction
        self.act_obj_event = (self.name, None, None)

        # =====================================================================
        # SOCIAL INTERACTIONS
        # =====================================================================
        
        # chatting_with: str | None
        # Name of character currently being chatted with (None if not chatting)
        self.chatting_with = None
        
        # chat: list[list[str, str]] | None
        # Conversation log between two personas
        # Format: [["Speaker Name", "Message"], ...]
        # 
        # Example:
        # [
        #     ["Dolores Murphy", "Hi"], 
        #     ["Maeve Jenson", "Hi back!"]
        # ]
        self.chat = None
        
        # chatting_with_buffer: dict[str, int]
        # Tracks chatting history (name -> vision_r value)
        self.chatting_with_buffer = dict()
        
        # chatting_end_time: datetime | None
        # When current chat session will end
        self.chatting_end_time = None

        # =====================================================================
        # PATHFINDING
        # =====================================================================
        
        # act_path_set: bool
        # Whether path for current action has been calculated
        self.act_path_set = False
        
        # planned_path: list[tuple[int, int]]
        # List of (x, y) coordinate tuples describing movement path
        # Excludes current tile, includes destination tile
        # 
        # Example: [(50, 10), (49, 10), (48, 10)]
        self.planned_path = []


# =============================================================================
# 2. MEMORY SYSTEM
# =============================================================================

"""
Memory Structure per Agent
--------------------------

Each agent maintains a memory system with timestamped events, locations,
and emotional significance ratings.
"""

# Memory Entry Schema
memory_structure_example = [
    {
        "timestamp": "2023-10-01T12:00:00Z",          # str: ISO 8601 format
        "location": "dolores double studio:double studio:bedroom 1",  # str: Location address
        "event": "wakes up and starts her morning routine",           # str: Event description  
        "poignancy": 5  # int: Emotional significance (0=low, 10=high)
    }
]


# =============================================================================
# 3. BACKEND-TO-FRONTEND COMMUNICATION
# =============================================================================

"""
Agent Actions
-------------

The backend sends agent actions to the frontend for visualization.
Supported action types: move, chat, interact
"""

# Action Type Schemas
agent_actions = [
    # Movement Action
    {
        "agent_id": "agent_123",                      # str: Unique agent identifier
        "action_type": "move",                        # str: Type of action
        "content": {
            "destination_coordinates": [50, 10]       # list[int, int]: Target (x, y)
        },
        "emoji": "🚶",                               # str: Visual representation
        
        # Optional fields:
        # "current_tile": [50, 10],                  # list[int, int]: Current position
        # "current_location": "kitchen"              # str: Semantic location
    },
    
    # Chat Action  
    {
        "agent_id": "agent_123",                      # str: Agent identifier
        "action_type": "chat",                        # str: Action type
        "content": {
            "chatting_with": "Maeve Jenson",          # str: Target agent name
            "message": "Hi Maeve, how are you?"       # str: Chat message
        },
        "emoji": "💬"                                # str: Visual representation
    },
    
    # Interaction Action
    {
        "agent_id": "agent_123",                      # str: Agent identifier  
        "action_type": "interact",                    # str: Action type
        "content": {
            "object": "light switch",                 # str: Object being interacted with
            "new_state": "on"                         # str: New state after interaction
        },
        "emoji": "💡"                                # str: Visual representation
    }
]


# =============================================================================
# 4. FRONTEND-TO-BACKEND COMMUNICATION  
# =============================================================================

"""
Frontend Messages
-----------------

Messages sent from frontend to backend include agent actions
along with environmental perception data.
"""

# Frontend Message Schema
frontend_to_backend = [
    {
        "agent_id": "agent_123",                      # str: Agent identifier
        "timestamp": "2023-10-01T12:00:00Z",         # str: When action occurred
        "action_type": "move",                        # str: Type of action performed
        "content": {
            "destination_coordinates": [50, 10]       # list[int, int]: Movement target
        },
        "perception": {
            # Objects currently visible to the agent
            "visible_objects": {                      # dict[str, dict]: Object states
                "bed": {"state": "unmade"},
                "light switch": {"state": "on"}
            },
            # Other agents currently visible  
            "visible_agents": [                       # list[str]: Agent names in sight
                "Maeve Jenson", 
                "Dolores Murphy"
            ],
            # Current world time as perceived by agent
            "current_time": "2023-10-01T12:00:00Z"   # str: Agent's perceived time
        }
    }
]


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

"""
Example Usage Patterns
-----------------------

1. Creating a new agent:
   agent = Agent(f_saved=None)
   agent.name = "John Doe"
   agent.vision_r = 4

2. Setting up daily schedule:
   agent.daily_req = ["Go to work", "Have lunch", "Exercise"]
   agent.f_daily_schedule = [["work", 480], ["lunch", 60], ["exercise", 120]]

3. Handling movement:
   agent.act_address = "office:main floor:desk 1"
   agent.planned_path = [(10, 5), (11, 5), (12, 5)]
   agent.act_path_set = True

4. Managing conversations:
   agent.chatting_with = "Alice"
   agent.chat = [["John Doe", "Hello"], ["Alice", "Hi there!"]]
"""
