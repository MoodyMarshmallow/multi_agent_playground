"""
Agent Data structure
"""

class Agent: 
  def __init__(self, f_saved): 
    # PERSONA HYPERPARAMETERS
    # <vision_r> denotes the number of tiles that the persona can see around 
    # them. 
    self.vision_r = 4
    # <retention> TODO 
    self.retention = 5

    # WORLD INFORMATION
    # Perceived world time. 
    self.curr_time = None
    # Current x,y tile coordinate of the persona. 
    self.curr_tile = None
    # Perceived world daily requirement. 
    self.daily_plan_req = None
    
    # THE CORE IDENTITY OF THE PERSONA 
    # Base information about the persona.
    self.name = None
    self.first_name = None
    self.last_name = None
    self.age = None
    # L0 permanent core traits.  
    self.innate = None
    # L1 stable traits.
    self.learned = None
    # L2 external implementation. 
    self.currently = None
    self.lifestyle = None
    self.living_area = None

    # PERSONA PLANNING 
    # <daily_req> is a list of various goals the persona is aiming to achieve
    # today. 
    # e.g., ['Work on her paintings for her upcoming show', 
    #        'Take a break to watch some TV', 
    #        'Make lunch for herself', 
    #        'Work on her paintings some more', 
    #        'Go to bed early']
    # They have to be renewed at the end of the day, which is why we are
    # keeping track of when they were first generated. 
    self.daily_req = []
    # <f_daily_schedule> denotes a form of long term planning. This lays out 
    # the persona's daily plan. 
    # Note that we take the long term planning and short term decomposition 
    # appoach, which is to say that we first layout hourly schedules and 
    # gradually decompose as we go. 
    # Three things to note in the example below: 
    # 1) See how "sleeping" was not decomposed -- some of the common events 
    #    really, just mainly sleeping, are hard coded to be not decomposable.
    # 2) Some of the elements are starting to be decomposed... More of the 
    #    things will be decomposed as the day goes on (when they are 
    #    decomposed, they leave behind the original hourly action description
    #    in tact).
    # 3) The latter elements are not decomposed. When an event occurs, the
    #    non-decomposed elements go out the window.  
    # e.g., [['sleeping', 360], 
    #         ['wakes up and ... (wakes up and stretches ...)', 5], 
    #         ['wakes up and starts her morning routine (out of bed )', 10],
    #         ...
    #         ['having lunch', 60], 
    #         ['working on her painting', 180], ...]
    self.f_daily_schedule = []
    # <f_daily_schedule_hourly_org> is a replica of f_daily_schedule
    # initially, but retains the original non-decomposed version of the hourly
    # schedule. 
    # e.g., [['sleeping', 360], 
    #        ['wakes up and starts her morning routine', 120],
    #        ['working on her painting', 240], ... ['going to bed', 60]]
    self.f_daily_schedule_hourly_org = []
    
    # CURR ACTION 
    # <address> is literally the string address of where the action is taking 
    # place.  It comes in the form of 
    # "{world}:{sector}:{arena}:{game_objects}". It is important that you 
    # access this without doing negative indexing (e.g., [-1]) because the 
    # latter address elements may not be present in some cases. 
    # e.g., "dolores double studio:double studio:bedroom 1:bed"
    self.act_address = None
    # <start_time> is a python datetime instance that indicates when the 
    # action has started. 
    self.act_start_time = None
    # <duration> is the integer value that indicates the number of minutes an
    # action is meant to last. 
    self.act_duration = None
    # <description> is a string description of the action. 
    self.act_description = None
    # <pronunciatio> is the descriptive expression of the self.description. 
    # Currently, it is implemented as emojis. 
    self.act_pronunciatio = None
    # <event_form> represents the event triple that the persona is currently 
    # engaged in. 
    self.act_event = (self.name, None, None)

    # <obj_description> is a string description of the object action. 
    self.act_obj_description = None
    # <obj_pronunciatio> is the descriptive expression of the object action. 
    # Currently, it is implemented as emojis. 
    self.act_obj_pronunciatio = None
    # <obj_event_form> represents the event triple that the action object is  
    # currently engaged in. 
    self.act_obj_event = (self.name, None, None)

    # <chatting_with> is the string name of the persona that the current 
    # persona is chatting with. None if it does not exist. 
    self.chatting_with = None
    # <chat> is a list of list that saves a conversation between two personas.
    # It comes in the form of: [["Dolores Murphy", "Hi"], 
    #                           ["Maeve Jenson", "Hi"] ...]
    self.chat = None
    # <chatting_with_buffer>  
    # e.g., ["Dolores Murphy"] = self.vision_r
    self.chatting_with_buffer = dict()
    self.chatting_end_time = None

    # <path_set> is True if we've already calculated the path the persona will
    # take to execute this action. That path is stored in the persona's 
    # scratch.planned_path.
    self.act_path_set = False
    # <planned_path> is a list of x y coordinate tuples (tiles) that describe
    # the path the persona is to take to execute the <curr_action>. 
    # The list does not include the persona's current tile, and includes the 
    # destination tile. 
    # e.g., [(50, 10), (49, 10), (48, 10), ...]
    self.planned_path = []

    
"""
Memory structure per agent
"""
[
  {
    "timestamp": "2023-10-01T12:00:00Z",
    "location": "dolores double studio:double studio:bedroom 1",
    "event": "wakes up and starts her morning routine",
    "poignancy": 0.8, # 0 to 1 scale, where 1 is most poignant
    
  }
]



"""
Backend to frontend communication
action type: move, chat, toggle objects
move - location
toggle_objects: object, new state 
subclass
"""

agent_actions = [
    {
        "agent_id": "agent_123",
        "action_type": "move",
        "content": {
            "destination_coordinates": [50, 10]
        },
        "emoji": "🚶"
        # "current_tile": [50, 10],
        # "current_location": "kitchen",
    },
    {
        "agent_id": "agent_123",
        "action_type": "chat",
        "content": {
            "chatting_with": "Maeve Jenson",
            "message": "Hi Maeve, how are you?"
        },
        "emoji": "💬"
    },
    {
        "agent_id": "agent_123",
        "action_type": "toggle_objects",
        "content": {
            "object": "light switch",
            "new_state": "on"
        },
        "emoji": "💡"
    }
]

"""
Frontend to backend communication
"""

frontend_to_backend = [
    {
        "agent_id": "agent_123",
        "timestamp": "2023-10-01T12:00:00Z",
        "action_type": "move",
        "content": {
            "destination_coordinates": [50, 10]
        },
        "perception": {
            "visible_objects": {
                "bed": {"state": "unmade"},
                "light switch": {"state": "on"}
            },
            "visible_agents": ["Maeve Jenson", "Dolores Murphy"],
            "current_time": "2023-10-01T12:00:00Z"
        }
    }
]