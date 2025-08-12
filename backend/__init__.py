# Backend module for multi-agent playground

# Items will be available through get_* functions to avoid circular imports
__all__ = []

# Import other modules conditionally to avoid circular imports
def get_agent_manager():
    from .domain.agent.manager import AgentManager
    from .domain.agent.agent_strategies import KaniAgent
    return AgentManager, KaniAgent

def get_game_controller():
    from .application.game_loop import GameLoop
    return GameLoop
