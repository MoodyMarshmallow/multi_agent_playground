#!/usr/bin/env python3
"""
Agent Chat Functionality Tests
==============================

Test cases to verify agents will use chat functionality when given the opportunity.
Tests chat requests, responses, and message exchanges between agents.
"""

import pytest
import asyncio
import os
import logging

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Environment variables from .env file won't be loaded.")

# Configure logging for debug mode
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Set specific loggers for detailed debugging
parsing_logger = logging.getLogger('backend.text_adventure_games.parsing')
parsing_logger.setLevel(logging.DEBUG)

agent_logger = logging.getLogger('backend.agent.agent_strategies')
agent_logger.setLevel(logging.DEBUG)

game_logger = logging.getLogger('backend.game_loop')
game_logger.setLevel(logging.DEBUG)

# Make sure all loggers use console handler
for logger_name in ['backend.text_adventure_games.parsing', 'backend.agent.agent_strategies', 'backend.game_loop']:
    logger_obj = logging.getLogger(logger_name)
    if not logger_obj.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger_obj.addHandler(console_handler)

print("Debug logging enabled for all chat functionality tests")

from backend.testing.agent_goal_test import AgentGoalTest
from backend.testing.agent_test_runner import AgentTestRunner
from backend.testing.criteria import LocationCriterion, ActionCriterion, Criterion
from backend.testing.config import WorldStateConfig, AgentConfig
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class ChatInteractionCriterion(Criterion):
    """Custom criterion to check if agent engaged in chat interactions"""
    min_chat_actions: int = 1
    should_send_request: bool = True
    should_respond_to_request: bool = True
    
    def check(self, game_state: Dict[str, Any], action_history: List[Any]) -> bool:
        """Check if agent performed chat-related actions"""
        chat_actions = []
        
        for action in action_history:
            action_str = str(action).lower()
            if any(chat_cmd in action_str for chat_cmd in ['chat_request', 'chat_response', 'chat ']):
                chat_actions.append(action_str)
        
        return len(chat_actions) >= self.min_chat_actions
    
    def describe(self) -> str:
        """Return a human-readable description of the criterion."""
        return f"Agent should engage in chat (min {self.min_chat_actions} chat actions)"


@pytest.mark.asyncio
async def test_agent_initiates_chat_request():
    """Test that an agent will send chat requests when encountering other agents"""
    print("Running chat initiation test...")
    
    test = AgentGoalTest(
        name="chat_initiation_test",
        description="Agent should send chat requests to other agents when they meet",
        initial_world_state=WorldStateConfig(
            agent_location="Entry Room",
            character_locations={
                "Bob": "Entry Room"  # Put another character in same room
            }
        ),
        agent_config=AgentConfig(
            persona="I am a social person who loves to chat and meet new people. When I see someone, I always try to start a conversation.",
            name="social_agent",
            model="gpt-4.1-mini"
        ),
        success_criteria=[
            ChatInteractionCriterion(min_chat_actions=1, should_send_request=True),
        ],
        max_turns=15
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    print(f"\nChat Initiation Test: {'PASSED' if result.success else 'FAILED'}")
    print(f"Turns taken: {result.turns_taken}")
    print(f"Action sequence: {result.action_sequence}")
    
    # Check if agent actually sent chat requests
    chat_actions = [action for action in result.action_sequence if 'chat_request' in str(action).lower()]
    print(f"Chat requests sent: {len(chat_actions)}")
    
    assert result.success, f"Agent failed to initiate chat: {result.error_message}"
    assert len(chat_actions) > 0, "Agent should have sent at least one chat request"


@pytest.mark.asyncio 
async def test_agent_responds_to_chat_request():
    """Test that an agent will respond to incoming chat requests"""
    print("\nRunning chat response test...")
    
    test = AgentGoalTest(
        name="chat_response_test", 
        description="Agent should respond to chat requests from other agents",
        initial_world_state=WorldStateConfig(
            agent_location="Kitchen",
            character_locations={
                "Alice": "Kitchen"
            }
        ),
        agent_config=AgentConfig(
            persona="I am friendly and responsive. When someone wants to chat with me, I always accept and engage in conversation.",
            name="responsive_agent",
            model="gpt-4.1-mini"
        ),
        success_criteria=[
            ChatInteractionCriterion(min_chat_actions=1, should_respond_to_request=True),
        ],
        max_turns=20
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    print(f"\nChat Response Test: {'PASSED' if result.success else 'FAILED'}")
    print(f"Turns taken: {result.turns_taken}")
    print(f"Action sequence: {result.action_sequence}")
    
    # Check if agent responded to requests
    response_actions = [action for action in result.action_sequence if 'chat_response' in str(action).lower()]
    print(f"Chat responses given: {len(response_actions)}")
    
    assert result.success, f"Agent failed to respond to chat: {result.error_message}"


@pytest.mark.asyncio
async def test_agent_chat_conversation_flow():
    """Test full conversation flow: request -> response -> message exchange"""
    print("\nRunning full conversation flow test...")
    
    test = AgentGoalTest(
        name="conversation_flow_test",
        description="Agent should engage in full conversation: send request, get response, exchange messages",
        initial_world_state=WorldStateConfig(
            agent_location="Living Room",
            character_locations={
                "Charlie": "Living Room"
            }
        ),
        agent_config=AgentConfig(
            persona="I am very social and love long conversations. I always try to chat with people I meet and continue conversations once they start.",
            name="conversational_agent", 
            model="gpt-4.1-mini"
        ),
        success_criteria=[
            ChatInteractionCriterion(min_chat_actions=3),  # Request + response + at least 1 message
        ],
        max_turns=25
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    print(f"\nConversation Flow Test: {'PASSED' if result.success else 'FAILED'}")
    print(f"Turns taken: {result.turns_taken}")
    print(f"Action sequence: {result.action_sequence}")
    
    # Analyze conversation components
    chat_requests = [action for action in result.action_sequence if 'chat_request' in str(action).lower()]
    chat_responses = [action for action in result.action_sequence if 'chat_response' in str(action).lower()]
    chat_messages = [action for action in result.action_sequence if str(action).lower().startswith('chat ') and 'chat_' not in str(action).lower()]
    
    print(f"Chat requests: {len(chat_requests)}")
    print(f"Chat responses: {len(chat_responses)}")  
    print(f"Chat messages: {len(chat_messages)}")
    
    total_chat_actions = len(chat_requests) + len(chat_responses) + len(chat_messages)
    
    assert result.success, f"Conversation flow failed: {result.error_message}"
    assert total_chat_actions >= 3, f"Expected at least 3 chat actions, got {total_chat_actions}"


@pytest.mark.asyncio
async def test_agent_discovers_chat_capability():
    """Test that agent discovers and uses chat functionality through exploration"""
    print("\nRunning chat discovery test...")
    
    test = AgentGoalTest(
        name="chat_discovery_test",
        description="Agent should discover chat capabilities by looking around and interacting",
        initial_world_state=WorldStateConfig(
            agent_location="Bedroom",
            character_locations={
                "Diana": "Bedroom"
            }
        ),
        agent_config=AgentConfig(
            persona="I am curious and observant. I like to explore my surroundings thoroughly and discover what I can do. I enjoy meeting new people.",
            name="discovery_agent",
            model="gpt-4.1-mini"
        ),
        success_criteria=[
            ActionCriterion(action_type="look"),  # Must look to discover chat options
            ChatInteractionCriterion(min_chat_actions=1),  # Must attempt to chat
        ],
        max_turns=20
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    print(f"\nChat Discovery Test: {'PASSED' if result.success else 'FAILED'}")
    print(f"Turns taken: {result.turns_taken}")
    print(f"Action sequence: {result.action_sequence}")
    
    # Check that agent looked around (to discover chat options) and then used chat
    look_actions = [action for action in result.action_sequence if str(action).lower() == 'look']
    chat_actions = [action for action in result.action_sequence if any(chat_cmd in str(action).lower() for chat_cmd in ['chat_request', 'chat_response', 'chat '])]
    
    print(f"Look actions: {len(look_actions)}")
    print(f"Chat actions: {len(chat_actions)}")
    
    assert result.success, f"Chat discovery failed: {result.error_message}"
    assert len(look_actions) > 0, "Agent should have used 'look' to discover chat options"
    assert len(chat_actions) > 0, "Agent should have attempted to use chat functionality"


@pytest.mark.asyncio
async def test_agent_chat_with_kani_history():
    """Test that agents maintain conversation context using Kani's chat history"""
    print("\nRunning Kani chat history test...")
    
    # Create a custom agent config that should maintain conversation context
    test = AgentGoalTest(
        name="kani_history_test", 
        description="Agent should maintain conversation context and reference previous messages",
        initial_world_state=WorldStateConfig(
            agent_location="Garden",
            character_locations={
                "Eva": "Garden"
            }
        ),
        agent_config=AgentConfig(
            persona="I have excellent memory and always reference previous parts of conversations. I build on what was said before and maintain context throughout discussions.",
            name="memory_agent",
            model="gpt-4.1-mini"
        ),
        success_criteria=[
            ChatInteractionCriterion(min_chat_actions=2),  # At least 2 chat interactions
        ],
        max_turns=30
    )
    
    runner = AgentTestRunner()
    result = await runner.run_test(test)
    
    print(f"\nKani History Test: {'PASSED' if result.success else 'FAILED'}")
    print(f"Turns taken: {result.turns_taken}")
    print(f"Action sequence: {result.action_sequence}")
    
    # Look for signs of conversation continuity (this is hard to test automatically,
    # but we can at least verify multiple chat interactions occurred)
    chat_actions = [action for action in result.action_sequence if any(chat_cmd in str(action).lower() for chat_cmd in ['chat_request', 'chat_response', 'chat '])]
    
    print(f"Total chat interactions: {len(chat_actions)}")
    if len(chat_actions) >= 2:
        print("✓ Agent engaged in multiple chat interactions (suggests context maintenance)")
    
    assert result.success, f"Kani history test failed: {result.error_message}" 
    assert len(chat_actions) >= 2, f"Expected at least 2 chat interactions for context testing, got {len(chat_actions)}"


if __name__ == "__main__":
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key to run these tests.")
        exit(1)
    
    async def run_all_tests():
        """Run all chat functionality tests"""
        print("Agent Chat Functionality Test Suite")
        print("=" * 50)
        
        try:
            await test_agent_initiates_chat_request()
            await test_agent_responds_to_chat_request() 
            await test_agent_chat_conversation_flow()
            await test_agent_discovers_chat_capability()
            await test_agent_chat_with_kani_history()
            
            print("\n" + "=" * 50)
            print("All chat functionality tests completed!")
            
        except Exception as e:
            print(f"Error running chat tests: {e}")
            import traceback
            traceback.print_exc()
    
    # Run tests manually if called directly
    asyncio.run(run_all_tests())