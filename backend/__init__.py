# Backend module for multi-agent playground

from .agent import Agent

__all__ = [
    'Agent',
]

# Import other modules conditionally to avoid circular imports
def get_agent_manager():
    from .agent_manager import AgentManager, KaniAgent, SimpleRandomAgent
    return AgentManager, KaniAgent, SimpleRandomAgent

def get_game_controller():
    from .game_controller import GameController
    return GameController 