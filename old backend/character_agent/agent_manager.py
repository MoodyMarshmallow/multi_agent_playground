"""
Multi-Agent Playground - LLM Agent Manager
==========================================
Manager for LLMAgent instances to prevent creating new agents each time.

This module implements:
- LLMAgentManager: Singleton pattern manager for agent instances
- Utility functions for creating, managing, and accessing LLM agents
- The main call_llm_agent function used by the system
"""

import asyncio
from typing import Dict, Any, Optional
from .agent import Agent
from .kani_agent import LLMAgent
import os

class LLMAgentManager:
    """
    Singleton manager for LLMAgent instances.
    """
    _instance = None
    _agents: Dict[str, LLMAgent] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMAgentManager, cls).__new__(cls)
        return cls._instance
    
    def get_agent(self, agent_id: str, api_key: Optional[str] = None) -> LLMAgent:
        """
        Get an existing LLMAgent or create a new one if it doesn't exist.
        
        Args:
            agent_id (str): The agent ID
            api_key (str, optional): OpenAI API key
            
        Returns:
            LLMAgent: The LLMAgent instance for the given agent_id
        """
        if agent_id not in self._agents:
            # Create Agent instance from agent_id
            agent_dir = f"data/agents/{agent_id}"
            agent = Agent(agent_dir)
            
            # Create and store new LLMAgent
            self._agents[agent_id] = LLMAgent(agent, api_key)
            print(f"Created new LLMAgent for agent_id: {agent_id}")
        else:
            # Reuse existing agent (data is already loaded)
            print(f"Reusing existing LLMAgent for agent_id: {agent_id}")
            
        return self._agents[agent_id]
    
    def remove_agent(self, agent_id: str):
        """
        Remove an agent from the manager.
        
        Args:
            agent_id (str): The agent ID to remove
        """
        if agent_id in self._agents:
            del self._agents[agent_id]
            print(f"Removed LLMAgent for agent_id: {agent_id}")
    
    def clear_all_agents(self):
        """
        Clear all agents from the manager.
        """
        self._agents.clear()
        print("Cleared all LLMAgents from manager")
    
    def get_active_agent_count(self) -> int:
        """
        Get the number of currently active agents.
        
        Returns:
            int: Number of active agents
        """
        return len(self._agents)
    
    def get_all_agent_summaries(self):
        """
        Return a list of summary dicts for all currently managed agents.
        """
        return [llm_agent.agent.to_summary_dict() for llm_agent in self._agents.values()]
    
    
    def preload_all_agents(self, agents_folder="data/agents"):
        """
        Loads all agent folders in the given directory into memory (if not already loaded).
        """
        for agent_id in os.listdir(agents_folder):
            agent_path = os.path.join(agents_folder, agent_id)
            if os.path.isdir(agent_path):
                self.get_agent(agent_id)


# Global instance of the agent manager
agent_manager = LLMAgentManager()


async def call_llm_for_action(agent_state: Dict[str, Any], perception_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Replacement function for call_llm_agent that uses the Kani-based LLM agent.
    
    Args:
        agent_state (dict): Current agent state
        perception_data (dict): Current perception data
        
    Returns:
        dict: Action JSON in the format expected by the frontend
    """
    # Get existing LLMAgent or create new one using the manager
    agent_id = agent_state['agent_id']
    llm_agent = agent_manager.get_agent(agent_id)
    
    # Plan next action
    action_result = await llm_agent.plan_next_action(perception_data)
    
    return action_result


def create_llm_agent(agent_id: str, api_key: Optional[str] = None) -> LLMAgent:
    """
    Create a new LLMAgent and register it in the manager.
    
    Args:
        agent_id (str): The agent ID
        api_key (str, optional): OpenAI API key
        
    Returns:
        LLMAgent: The created LLMAgent instance
    """
    return agent_manager.get_agent(agent_id, api_key)


def get_llm_agent(agent_id: str) -> Optional[LLMAgent]:
    """
    Get an existing LLMAgent if it exists.
    
    Args:
        agent_id (str): The agent ID
        
    Returns:
        LLMAgent or None: The LLMAgent instance if it exists, None otherwise
    """
    return agent_manager._agents.get(agent_id)


def remove_llm_agent(agent_id: str):
    """
    Remove an LLMAgent from the manager.
    
    Args:
        agent_id (str): The agent ID to remove
    """
    agent_manager.remove_agent(agent_id)


def clear_all_llm_agents():
    """
    Clear all LLMAgents from the manager.
    """
    agent_manager.clear_all_agents()


def get_active_agent_count() -> int:
    """
    Get the number of currently active LLMAgents.
    
    Returns:
        int: Number of active agents
    """
    return agent_manager.get_active_agent_count()


# Synchronous wrapper for compatibility with existing code
def call_llm_agent(agent_state: Dict[str, Any], perception_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synchronous wrapper for the LLM action planning function.
    This replaces the original call_llm_agent function.
    
    Args:
        agent_state (dict): Current agent state
        perception_data (dict): Current perception data
        
    Returns:
        dict: Action JSON in the format expected by the frontend
    """
    return asyncio.run(call_llm_for_action(agent_state, perception_data)) 

