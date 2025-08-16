"""
Test Configuration Classes
==========================

Configuration classes for setting up test scenarios.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class WorldStateConfig:
    """Configuration for initial world state."""
    agent_location: str = "Entry Room"
    agent_inventory: List[str] = field(default_factory=list)
    world_items: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    character_locations: Dict[str, str] = field(default_factory=dict)
    custom_state: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentConfig:
    """Configuration for the test agent."""
    name: str = "test_agent"
    persona: str = "I am a helpful agent who follows instructions."
    model: str = "gpt-4.1-mini"
    api_key: Optional[str] = None


@dataclass
class BehaviorAnalysis:
    """Analysis of agent behavior during test."""
    decision_quality_score: float = 0.0  # 0-1 scale
    efficiency_score: float = 0.0  # 0-1 scale
    action_diversity: float = 0.0  # How varied were the actions
    loop_detection: List[str] = field(default_factory=list)  # Detected repetitive behavior
    invalid_actions: List[str] = field(default_factory=list)  # Actions that failed
    reasoning_quality: str = "Not analyzed"  # Analysis of agent's reasoning