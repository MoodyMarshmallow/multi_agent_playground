"""
Pytest Configuration and Fixtures
=================================
Common test fixtures and configuration for the test suite.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List
import json
import time


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_agent_data():
    """Sample agent data for testing."""
    return {
        "agent_id": "test_agent_001",
        "first_name": "Test",
        "last_name": "Agent",
        "age": 25,
        "occupation": "Test Engineer",
        "personality": "curious and methodical",
        "backstory": "A test agent created for validation purposes",
        "currently": "running unit tests",
        "daily_req": [
            "Run comprehensive tests",
            "Validate performance",
            "Check edge cases"
        ]
    }


@pytest.fixture
def sample_perception_data():
    """Sample perception data for testing."""
    return {
        "timestamp": "01T15:30:45",
        "current_tile": [21, 8],
        "visible_objects": {
            "coffee_machine": {
                "room": "kitchen",
                "position": [21, 8],
                "state": "on"
            },
            "refrigerator": {
                "room": "kitchen", 
                "position": [22, 8],
                "state": "closed"
            }
        },
        "visible_agents": ["test_agent_002", "test_agent_003"],
        "chatable_agents": ["test_agent_002"],
        "heard_messages": [
            {
                "sender": "test_agent_002",
                "receiver": "test_agent_001",
                "message": "How's the testing going?",
                "timestamp": "01T15:29:30"
            }
        ]
    }


@pytest.fixture
def sample_memories():
    """Sample memory data for testing."""
    return [
        {
            "id": "test_agent_001_0",
            "timestamp": "01T15:00:00",
            "location": "kitchen",
            "event": "Made coffee and started testing",
            "salience": 6,
            "tags": ["daily_routine", "work"],
            "created_at": time.time() - 1800
        },
        {
            "id": "test_agent_001_1", 
            "timestamp": "01T15:15:00",
            "location": "kitchen",
            "event": "Discussed test strategy with colleague",
            "salience": 8,
            "tags": ["conversation", "work", "planning"],
            "created_at": time.time() - 900
        },
        {
            "id": "test_agent_001_2",
            "timestamp": "01T15:25:00", 
            "location": "office",
            "event": "Reviewed code for optimization",
            "salience": 7,
            "tags": ["work", "technical", "review"],
            "created_at": time.time() - 300
        }
    ]


@pytest.fixture
def sample_object_registry():
    """Sample object registry for testing."""
    class MockObject:
        def __init__(self, position, room, state):
            self.position = position
            self.room = room
            self.state = state
    
    return {
        "coffee_machine": MockObject([21, 8], "kitchen", "on"),
        "refrigerator": MockObject([22, 8], "kitchen", "closed"),
        "desk": MockObject([20, 10], "office", "clean"),
        "computer": MockObject([20, 10], "office", "running")
    }


@pytest.fixture
def mock_agent_dir(temp_dir):
    """Create mock agent directory structure."""
    agent_dir = temp_dir / "data" / "agents" / "test_agent_001"
    agent_dir.mkdir(parents=True, exist_ok=True)
    
    # Create agent.json
    agent_data = {
        "agent_id": "test_agent_001",
        "first_name": "Test",
        "last_name": "Agent",
        "age": 25,
        "curr_tile": [21, 8]
    }
    
    with open(agent_dir / "agent.json", 'w') as f:
        json.dump(agent_data, f, indent=2)
    
    # Create memory.json
    memory_data = {
        "episodic_memory": [
            {
                "timestamp": "01T14:30:00",
                "location": "kitchen",
                "event": "Started daily routine",
                "salience": 5,
                "tags": ["daily_routine"]
            }
        ]
    }
    
    with open(agent_dir / "memory.json", 'w') as f:
        json.dump(memory_data, f, indent=2)
    
    return agent_dir


@pytest.fixture
def performance_timer():
    """Timer fixture for performance testing."""
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.perf_counter()
        
        def stop(self):
            self.end_time = time.perf_counter()
            return self.elapsed()
        
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return 0
    
    return Timer()


# Test configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    ) 