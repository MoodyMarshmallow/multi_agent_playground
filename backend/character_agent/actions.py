"""
This file implements action functions for character agents.
"""

from typing import Annotated, Dict, Any, List
from kani import ai_function
import json
import logging

# Get logger for this module
logger = logging.getLogger(__name__)

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
        
        OPTIONS:
        - 🚶‍♂️ Walk - Slow to moderate pace, casual, relaxed
        - 🏃 Run - Fast, purposeful, slightly out of breath
        - 🐌 Crawl - Very slow, cautious, deliberate
        - 🕺 Dance - Fast, energetic, rhythmic
        
        USAGE EXAMPLES:
        - move([5, 3], "🚶‍♂️") - Walk casually to (5, 3), taking in the surroundings
        - move([10, 8], "🏃") - Run purposefully toward (10, 8), focused on destination
        - move([0, 0], "🐌") - Crawl slowly to origin, being extra cautious
        - move([7, 2], "🚶‍♂️") - Walk deliberately to (7, 2), observing carefully
        - move([3, 7], "🕺") - Dance energetically to (3, 7), full of rhythm
        - move([12, 4], "🚶‍♂️") - Walk stealthily to (12, 4), trying to be quiet
        - move([1, 9], "🕺") - Dance joyfully to (1, 9), expressing happiness
        
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
        
        # Log JSON for debugging/logging
        logger.debug(f"Move action: {json.dumps(action_json, indent=2)}")
        
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
        
        INTERACTION OPTIONS:
        - 🤲 Gentle handling - treating object with respect and care
        - 💪 Forceful grip - using strength, determined application
        - 🔨 Hammering approach - repetitive, mechanical, tool-like force
        - 🥊 Combative interaction - treating object as opponent
        - ⚔️ Weapon-like precision - sharp, cutting, focused destruction
        - 🧠 Intellectual approach - thinking through the mechanism
        - 🔬 Scientific method - systematic, experimental, analytical
        - 🎨 Artistic touch - creative, expressive, aesthetically aware
        - ⚙️ Mechanical understanding - seeing how parts work together
        - 🔍 Detective work - looking for clues in the object
        
        USAGE EXAMPLES:
        - interact("ancient tome", "opened", "🤲") - Gently open sacred book with careful reverence
        - interact("stuck door", "opened", "💪") - Force open door with determined strength
        - interact("delicate mechanism", "activated", "🔧") - Skillfully activate complex device with mechanical precision
        - interact("musical instrument", "playing", "🎨") - Artistically play beautiful melody with creative expression
        - interact("broken fence", "repaired", "🔨") - Hammer fence back into working order with repetitive force
        - interact("secret panel", "opened", "🔍") - Investigate and discover hidden mechanism through detective work
        - interact("locked chest", "opened", "🧠") - Think through the locking mechanism intellectually
        - interact("laboratory equipment", "activated", "🔬") - Systematically operate scientific instruments
        - interact("enemy barrier", "destroyed", "⚔️") - Cut through obstacle with weapon-like precision
        - interact("stubborn bolt", "loosened", "🥊") - Fight against the resistant mechanical part
        
        BEST PRACTICES:
        - Think about your character's skill level with this type of object
        - Match the emoji to both the action and your character's feelings about it
        - Remember that how you interact reveals personality traits
        - Some objects may require multiple interaction attempts
        - Consider the consequences of your interaction method
        
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
        
        # Log JSON for debugging/logging
        logger.debug(f"Interact action: {json.dumps(action_json, indent=2)}")
        
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
        
        COMMUNICATION OPTIONS:
        - 💬 Normal conversation - casual, friendly chat
        - 😊 Happy chat - cheerful, positive interaction
        - 🤔 Thoughtful discussion - serious, contemplative
        - 😰 Nervous communication - hesitant, worried
        - 😤 Frustrated talking - annoyed, impatient
        - 🗣️ Loud announcement - calling out, making sure to be heard
        - 🤫 Whispered secret - quiet, confidential communication
        - 📢 Public declaration - speaking to multiple people
        
        USAGE EXAMPLES:
        - chat("alex_001", "Hey Alex! How's your painting coming along?", "😊") - Friendly check-in
        - chat("alan_002", "Would you like to grab lunch together?", "🍽️") - Meal invitation
        - chat("neighbor_003", "Excuse me, have you seen my cat?", "😰") - Worried inquiry
        - chat("friend_004", "I just finished my masterpiece!", "🎉") - Excited announcement
        - chat("coworker_005", "Can we discuss the project deadline?", "🤔") - Professional conversation
        - chat("stranger_006", "Hello there! Welcome to the neighborhood!", "👋") - Welcoming greeting
        - chat("roommate_007", "Could you please keep it down? I'm trying to work.", "😤") - Polite complaint
        - chat("best_friend_008", "I have some amazing news to share with you!", "🤫") - Sharing secrets
        
        BEST PRACTICES:
        - Stay in character - messages should reflect your personality and current mood
        - Be contextually appropriate - consider your relationship with the receiver
        - Use natural language - avoid robotic or overly formal speech unless that fits your character
        - Match your emoji to your message tone and personality
        - Consider the situation - formal vs casual, public vs private conversations
        - React to recent events or conversations in your responses
        - Keep messages concise but meaningful
        - Use your character's vocabulary and speaking style
        - Consider your character's emotional state when crafting messages
        - Remember your daily goals and how conversation might help achieve them

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
        
        # Log JSON for debugging/logging
        logger.debug(f"Chat action: {json.dumps(action_json, indent=2)}")
        
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
        
        # Log JSON for debugging/logging
        logger.debug(f"Perceive action: {json.dumps(action_json, indent=2)}")
        
        return action_json
        
        
        