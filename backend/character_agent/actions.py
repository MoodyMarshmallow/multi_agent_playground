"""
This file implements action functions for character agents.
"""

from typing import Annotated, Dict, Any, List
from kani import ai_function
import json

class ActionsMixin:
    """
    This class implements action functions for character agents.
    Produces JSON output to send to the frontend.
    """
    
    def __init__(self):
        # This should be set by the character class that uses this mixin
        self.agent_id = getattr(self, 'agent_id', 'unknown_agent')
    
    @ai_function()
    def move(self,
             destination_coordinates: Annotated[List[int], "The coordinates to move to as [x, y]"],
             action_emoji: Annotated[str, "The emoji representing the action"]
             ) -> Dict[str, Any]:
        """        
        This function allows your character agent to navigate in a 2D coordinate space.
        Follow these guidelines for optimal movement behavior:
        
        COORDINATE SYSTEM:
        - Use integer coordinates only: [x, y] format
        - X-axis: horizontal movement (positive = right, negative = left)
        - Y-axis: vertical movement (positive = up, negative = down)
        - Origin [0, 0] is typically at the bottom-left or center of the grid
        - Always provide coordinates as a list of two integers: [x, y]
        
        MOVEMENT STRATEGY:
        Focus on HOW you move rather than just WHERE you move. The manner of movement is everything - 
        it reveals your character's personality, emotional state, intentions, and current circumstances.
        
        EMOJI SELECTION FOR MOVEMENT MANNER:
        The emoji is the soul of your movement. Choose it to paint a vivid picture of HOW your character is moving:
        
        PACE AND ENERGY LEVELS:
        - 🚶 Casual stroll - relaxed, unhurried, observing surroundings
        - 🚶‍♂️ Determined walk - purposeful stride, focused forward movement
        - 🏃 Urgent run - time-sensitive, slightly out of breath, quick steps
        - 🏃‍♀️ Athletic sprint - powerful, coordinated, maximum speed
        - 🐌 Slow creep - cautious, deliberate, trying not to be noticed
        - ⚡ Lightning dash - sudden burst, explosive movement, startling speed
        - 🦶 Tiptoeing - silent, careful, avoiding detection or disturbance
        - 🕺 Bouncy step - energetic, rhythmic, possibly dancing while moving
        
        EMOTIONAL MOVEMENT EXPRESSIONS:
        - 😊 Cheerful skip - light-hearted, optimistic, spring in step
        - 😰 Nervous shuffle - hesitant, looking around, uncertain footing
        - 😤 Angry stomp - heavy footfalls, forceful, possibly clenched fists
        - 🤔 Thoughtful pace - measured steps, pausing occasionally, contemplative
        - 😴 Weary trudge - dragging feet, shoulders slumped, low energy
        - 😍 Eager rush - excited, can barely contain enthusiasm, quick but clumsy
        - 😎 Cool swagger - confident, smooth, owns the space
        - 🥺 Reluctant drift - doesn't really want to go, slow, looking back
        - 😏 Sneaky slink - mischievous, keeping to shadows, up to something
        
        SITUATIONAL MOVEMENT STYLES:
        - 🔍 Investigative prowl - alert, scanning, ready to stop and examine
        - 🎯 Focused beeline - direct, unwavering, tunnel vision toward goal
        - 🌊 Fluid glide - smooth, graceful, like water flowing
        - 🏠 Homeward shuffle - familiar territory, relaxed, muscle memory
        - 🚪 Exit seeking - purposeful but not panicked, looking for way out
        - 🛡️ Defensive retreat - cautious, watching for threats, ready to dodge
        - 🎪 Playful bound - joyful, unpredictable, maybe hopping or skipping
        - 🤝 Social approach - friendly, open body language, inviting
        - 💼 Professional stride - business-like, efficient, time-conscious
        - 🎭 Dramatic flourish - theatrical, exaggerated, making a statement
        
        STEALTH AND CAUTION MODES:
        - 👻 Ghost walk - nearly invisible, avoiding all contact
        - 🕵️ Spy creep - methodical, checking corners, gathering intel
        - 🦝 Mischief sneak - playful stealth, up to harmless trouble
        - 🐱 Cat prowl - graceful, silent, predatory awareness
        - 🦉 Wise observation - moving to better vantage points, studying
        
        SOCIAL MOVEMENT EXPRESSIONS:
        - 💃 Attention-seeking strut - wants to be noticed, confident display
        - 🙈 Embarrassed scurry - trying to avoid attention, head down
        - 🤗 Welcoming approach - arms slightly open, warm invitation
        - 💔 Heartbroken wander - aimless, heavy, emotionally lost
        - 🎉 Celebratory dance-walk - can't contain joy, rhythm in every step
        
        USAGE EXAMPLES:
        - move([5, 3], "😰") - Nervously shuffle to (5, 3), hesitant and looking around
        - move([10, 8], "🎯") - March with focused determination toward (10, 8), unwavering
        - move([0, 0], "😴") - Trudge wearily home to origin, shoulders slumped, exhausted
        - move([7, 2], "🕵️") - Creep methodically to (7, 2) to investigate, checking corners
        - move([3, 7], "💃") - Strut confidently to (3, 7), wanting everyone to notice
        - move([12, 4], "🐱") - Prowl silently to (12, 4) with predatory grace
        - move([1, 9], "🎉") - Dance-walk joyfully to (1, 9), rhythm in every step
        
        BEST PRACTICES:
        - Think like an actor: HOW would your character move in this emotional state?
        - The emoji should tell a story about your character's inner world
        - Match movement style to current circumstances and personality
        - Consider what your body language communicates to others
        - Let the manner of movement reveal character development and plot
        - Use movement as a form of non-verbal storytelling
        - Choose emojis that would make sense if someone was watching your character
        
        Returns JSON action for frontend communication.
        """
        action_json = {
            "agent_id": getattr(self, 'agent_id', 'unknown_agent'),
            "action_type": "move",
            "content": {
                "destination_coordinates": destination_coordinates
            },
            "emoji": action_emoji
        }
        
        # Print JSON for debugging/logging
        print(f"Move action: {json.dumps(action_json, indent=2)}")
        
        return action_json
    
    @ai_function()
    def interact(self,
                 object: Annotated[str, "The object to interact with"],
                 new_state: Annotated[str, "The state the object should be changed to"],
                 action_emoji: Annotated[str, "The emoji representing the action"]
                 ) -> Dict[str, Any]:
        """
        This function allows your character to engage with objects in the environment.
        Focus on HOW you interact rather than just WHAT you interact with. The manner of interaction is everything - 
        it reveals your character's relationship with objects, emotional state, skill level, and intentions.
        
        OBJECT INTERACTION PRINCIPLES:
        - object: Be specific about what you're interacting with (e.g., "red_door", "wooden_chest", "glowing_crystal")
        - new_state: Describe the intended result clearly (e.g., "opened", "lit", "activated", "broken", "repaired")
        - Consider the physical and emotional effort required for the interaction
        
        EMOJI SELECTION FOR INTERACTION MANNER:
        The emoji is the soul of your interaction. Choose it to paint a vivid picture of HOW your character approaches and handles objects:
        
        GENTLE AND CAREFUL INTERACTIONS:
        - 🤲 Gentle handling - treating object with respect and care
        - 🕊️ Delicate touch - barely making contact, afraid to damage
        - 👐 Open approach - welcoming, embracing the object's purpose
        - 🌸 Tender care - nurturing, protective, loving interaction
        - 🦋 Feather-light touch - minimal contact, graceful handling
        - 🙏 Reverent interaction - treating object as sacred or precious
        - 💝 Cherishing touch - appreciating the object's value
        
        FORCEFUL AND AGGRESSIVE INTERACTIONS:
        - 💪 Forceful grip - using strength, determined application
        - ⚡ Explosive action - sudden, powerful, overwhelming force
        - 🔨 Hammering approach - repetitive, mechanical, tool-like force
        - 😤 Frustrated handling - impatient, rough, losing composure
        - 🥊 Combative interaction - treating object as opponent
        - 💥 Destructive force - intentionally breaking or damaging
        - ⚔️ Weapon-like precision - sharp, cutting, focused destruction
        
        SKILLED AND TECHNICAL INTERACTIONS:
        - 🔧 Technical manipulation - skilled, knowing exactly what to do
        - 🎯 Precise targeting - surgical accuracy, hitting exact spots
        - 🧠 Intellectual approach - thinking through the mechanism
        - 🔬 Scientific method - systematic, experimental, analytical
        - 🎨 Artistic touch - creative, expressive, aesthetically aware
        - 🏆 Masterful handling - expert-level skill, confident execution
        - ⚙️ Mechanical understanding - seeing how parts work together
        
        EMOTIONAL INTERACTION STYLES:
        - 😊 Joyful engagement - happy to interact, positive energy
        - 😰 Nervous fumbling - uncertain, shaky hands, hesitant approach
        - 🤔 Contemplative handling - thoughtful, studying before acting
        - 😍 Fascinated exploration - captivated, can't help but touch
        - 😒 Reluctant compliance - doing it but not wanting to
        - 🥺 Pleading interaction - begging the object to work
        - 😎 Cool confidence - smooth, assured, no doubt about success
        - 🤯 Overwhelmed confusion - too complex, mind blown by object
        
        SOCIAL AND COMMUNICATIVE INTERACTIONS:
        - 🤝 Cooperative approach - working with the object as partner
        - 💬 Communicative touch - trying to "talk" to the object
        - 🎭 Performative interaction - making a show of the action
        - 🤗 Friendly embrace - treating object like a friend
        - 🙋 Attention-seeking - wanting others to notice the interaction
        - 👥 Group coordination - interacting as part of team effort
        - 🎪 Playful experimentation - having fun with the interaction
        
        STEALTH AND SECRETIVE INTERACTIONS:
        - 🤫 Silent operation - trying not to make noise
        - 👻 Invisible touch - hoping no one notices
        - 🕵️ Investigative probing - searching for hidden mechanisms
        - 🦝 Sneaky manipulation - mischievous, unauthorized interaction
        - 🌙 Midnight stealth - operating under cover of darkness
        - 🔍 Detective work - looking for clues in the object
        
        USAGE EXAMPLES:
        - interact("ancient tome", "opened", "🙏") - Reverently open sacred book with deep respect
        - interact("stuck door", "opened", "💪") - Force open door with determined strength
        - interact("delicate mechanism", "activated", "🔧") - Skillfully activate complex device
        - interact("mysterious orb", "glowing", "😰") - Nervously touch orb, hands shaking
        - interact("musical instrument", "playing", "🎨") - Artistically play beautiful melody
        - interact("broken fence", "repaired", "🔨") - Hammer fence back into working order
        - interact("secret panel", "opened", "🕵️") - Investigate and discover hidden mechanism
        
        BEST PRACTICES:
        - Think about your character's skill level with this type of object
        - Consider the emotional weight of the interaction
        - Match the emoji to both the action and your character's feelings about it
        - Remember that how you interact reveals personality traits
        - Some objects may require multiple interaction attempts
        - Consider the consequences of your interaction method
        - Use interactions to show character growth and learning
        
        Returns JSON action for frontend communication.
        """
        action_json = {
            "agent_id": getattr(self, 'agent_id', 'unknown_agent'),
            "action_type": "interact",
            "content": {
                "object": object,
                "new_state": new_state
            },
            "emoji": action_emoji
        }
        
        # Print JSON for debugging/logging
        print(f"Interact action: {json.dumps(action_json, indent=2)}")
        
        return action_json
    
    @ai_function()
    def chat(self,
             receiver: Annotated[str, "The agent ID of who you want to chat with"],
             message: Annotated[str, "The message you want to send"],
             action_emoji: Annotated[str, "The emoji representing the action"]
             ) -> Dict[str, Any]:
        """
        This function allows your character to send messages to other agents.
        
        CHAT GUIDELINES:
        - receiver: Use the exact agent_id of who you want to talk to
        - message: Keep messages natural and in-character
        - action_emoji: Choose an emoji that represents your communication style
        
        COMMUNICATION EMOJIS:
        - 💬 Normal conversation - casual, friendly chat
        - 😊 Happy chat - cheerful, positive interaction
        - 🤔 Thoughtful discussion - serious, contemplative
        - 😰 Nervous communication - hesitant, worried
        - 😤 Frustrated talking - annoyed, impatient
        - 🗣️ Loud announcement - calling out, making sure to be heard
        - 🤫 Whispered secret - quiet, confidential communication
        - 📢 Public declaration - speaking to multiple people
        
        Returns JSON action for frontend communication.
        """
        action_json = {
            "agent_id": getattr(self, 'agent_id', 'unknown_agent'),
            "action_type": "chat",
            "content": {
                "receiver": receiver,
                "message": message
            },
            "emoji": action_emoji
        }
        
        # Print JSON for debugging/logging
        print(f"Chat action: {json.dumps(action_json, indent=2)}")
        
        return action_json
    
    @ai_function()
    def perceive(self,
                 action_emoji: Annotated[str, "The emoji representing the action"]
                 ) -> Dict[str, Any]:
        """
        This function allows your character to observe the environment and gather information.
        
        PERCEPTION GUIDELINES:
        - Use this to actively look around and understand your surroundings
        - Good for getting updated information about objects and other agents
        - Useful when you need to reassess the situation
        
        PERCEPTION EMOJIS:
        - 👀 General observation - looking around, taking in the scene
        - 🔍 Detailed investigation - searching for specific things
        - 🦉 Wise observation - thoughtful, careful examination
        - 😕 Confused looking - trying to understand what's happening
        - 🤔 Contemplative observation - thinking while observing
        - 👁️ Focused attention - concentrating on something specific
        - 🕵️ Detective work - investigating, looking for clues
        
        Returns JSON action for frontend communication.
        """
        action_json = {
            "agent_id": getattr(self, 'agent_id', 'unknown_agent'),
            "action_type": "perceive",
            "content": {},
            "emoji": action_emoji
        }
        
        # Print JSON for debugging/logging
        print(f"Perceive action: {json.dumps(action_json, indent=2)}")
        
        return action_json
        
        
        