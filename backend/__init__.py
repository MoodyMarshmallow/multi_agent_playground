# Backend module for multi-agent playground

__all__ = [
    'AgentManager',
    'KaniAgent', 
    'GameLoop'
]

# Import other modules conditionally to avoid circular imports
def get_agent_manager():
    from .agent_manager import AgentManager, KaniAgent
    return AgentManager, KaniAgent

def get_game_controller():
    from .game_loop import GameLoop
    return GameLoop 