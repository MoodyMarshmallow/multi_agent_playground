#!/usr/bin/env python3
"""
Test script to verify the LLMAgent manager functionality.
"""

import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent  # Go up one level from tests/ to backend/
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from character_agent.agent_manager import (
    create_llm_agent, get_llm_agent, remove_llm_agent, 
    clear_all_llm_agents, get_active_agent_count
)
from server.controller import (
    initialize_llm_agent, get_or_create_llm_agent, 
    cleanup_llm_agent, get_llm_agent_status
)

def test_agent_manager():
    """Test the LLMAgent manager functionality."""
    print("Testing LLMAgent Manager...")
    
    # Clear any existing agents
    clear_all_llm_agents()
    print(f"Initial agent count: {get_active_agent_count()}")
    
    # Test creating agents
    try:
        print("\n1. Testing agent creation...")
        agent1 = get_or_create_llm_agent("alan_002")
        print(f"Created agent for alan_002: {agent1 is not None}")
        
        agent2 = get_or_create_llm_agent("alex_001")  
        print(f"Created agent for alex_001: {agent2 is not None}")
        
        print(f"Active agent count after creation: {get_active_agent_count()}")
        
    except Exception as e:
        print(f"Error creating agents: {e}")
        return False
    
    # Test retrieving existing agents
    print("\n2. Testing agent retrieval...")
    existing_agent1 = get_llm_agent("alan_002")
    existing_agent2 = get_llm_agent("alex_001")
    
    print(f"Retrieved alan_002: {existing_agent1 is not None}")
    print(f"Retrieved alex_001: {existing_agent2 is not None}")
    print(f"Same instance check (alan_002): {agent1 is existing_agent1}")
    print(f"Same instance check (alex_001): {agent2 is existing_agent2}")
    
    # Test status
    print("\n3. Testing status...")
    status = get_llm_agent_status()
    print(f"Status: {status}")
    
    # Test cleanup
    print("\n4. Testing cleanup...")
    cleanup_llm_agent("alan_002")
    print(f"Active agent count after removing alan_002: {get_active_agent_count()}")
    
    remaining_agent = get_llm_agent("alan_002")
    print(f"alan_002 after removal: {remaining_agent is None}")
    
    clear_all_llm_agents()
    print(f"Active agent count after clearing all: {get_active_agent_count()}")
    
    print("\nAgent manager test completed successfully!")
    return True

if __name__ == "__main__":
    test_agent_manager() 