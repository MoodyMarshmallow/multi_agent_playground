"""
Unit Tests for Prompts Module
=============================
Tests for PromptTemplates with performance validation.
"""

import pytest
import time
from string import Template

from lru_llm.utils.prompts import PromptTemplates


class TestPromptTemplates:
    """Test suite for PromptTemplates implementation."""
    
    @pytest.mark.unit
    def test_initialization(self):
        """Test PromptTemplates initialization."""
        templates = PromptTemplates()
        
        # Check that all templates are compiled
        assert isinstance(templates.perceive_template, Template)
        assert isinstance(templates.chat_template, Template)
        assert isinstance(templates.move_template, Template)
        assert isinstance(templates.interact_template, Template)
        assert isinstance(templates.system_prompt_template, Template)
        
        # Check cache initialization
        assert hasattr(templates, '_prompt_cache')
        assert hasattr(templates, '_system_cache')
    
    @pytest.mark.unit
    def test_perceive_prompt_generation(self, sample_agent_data, sample_perception_data):
        """Test perceive prompt generation."""
        templates = PromptTemplates()
        
        prompt = templates.generate_perceive_prompt(
            agent_data=sample_agent_data,
            perception_data=sample_perception_data,
            memory_context="Previous memories: Made coffee this morning.",
            timestamp="01T15:30:45"
        )
        
        # Verify prompt contains expected elements
        assert "Test Agent" in prompt
        assert "curious and methodical" in prompt
        assert "coffee_machine" in prompt
        assert "test_agent_002" in prompt
        assert "Previous memories" in prompt
        assert "01T15:30:45" in prompt
        
        # Verify prompt structure
        assert prompt.startswith("AGENT PROFILE:")
        assert "CURRENT PERCEPTION:" in prompt
        assert "MEMORY CONTEXT:" in prompt
        assert "INSTRUCTION:" in prompt
    
    @pytest.mark.unit
    def test_chat_prompt_generation(self, sample_agent_data):
        """Test chat prompt generation."""
        templates = PromptTemplates()
        
        prompt = templates.generate_chat_prompt(
            agent_data=sample_agent_data,
            target_agent="test_agent_002",
            context="We were discussing test strategies",
            message_history=[
                {"sender": "test_agent_002", "message": "How's testing going?"},
                {"sender": "test_agent_001", "message": "Making good progress!"}
            ]
        )
        
        # Verify prompt contains expected elements
        assert "Test Agent" in prompt
        assert "test_agent_002" in prompt
        assert "test strategies" in prompt
        assert "How's testing going?" in prompt
        assert "Making good progress!" in prompt
    
    @pytest.mark.unit
    def test_move_prompt_generation(self, sample_agent_data):
        """Test move prompt generation."""
        templates = PromptTemplates()
        
        prompt = templates.generate_move_prompt(
            agent_data=sample_agent_data,
            current_location="kitchen",
            movement_options=["north", "east", "west"],
            context="Need to get to the office for important meeting"
        )
        
        # Verify prompt contains expected elements
        assert "Test Agent" in prompt
        assert "kitchen" in prompt
        assert "north" in prompt and "east" in prompt and "west" in prompt
        assert "important meeting" in prompt
    
    @pytest.mark.unit
    def test_interact_prompt_generation(self, sample_agent_data):
        """Test interact prompt generation."""
        templates = PromptTemplates()
        
        prompt = templates.generate_interact_prompt(
            agent_data=sample_agent_data,
            object_name="coffee_machine",
            object_state="on",
            available_actions=["turn_off", "make_coffee", "clean"],
            context="Need caffeine to stay alert for testing"
        )
        
        # Verify prompt contains expected elements
        assert "Test Agent" in prompt
        assert "coffee_machine" in prompt
        assert "turn_off" in prompt
        assert "make_coffee" in prompt
        assert "clean" in prompt
        assert "caffeine" in prompt
    
    @pytest.mark.unit
    def test_system_prompt_generation(self, sample_agent_data):
        """Test system prompt generation."""
        templates = PromptTemplates()
        
        prompt = templates.generate_system_prompt(
            agent_data=sample_agent_data,
            action_type="perceive"
        )
        
        # Verify prompt contains expected elements
        assert "Test Agent" in prompt
        assert "curious and methodical" in prompt
        assert "Test Engineer" in prompt
        assert "perceive" in prompt
    
    @pytest.mark.unit
    def test_prompt_caching(self, sample_agent_data):
        """Test prompt caching functionality."""
        templates = PromptTemplates()
        
        # Generate system prompt multiple times
        prompt1 = templates.generate_system_prompt(sample_agent_data, "perceive")
        prompt2 = templates.generate_system_prompt(sample_agent_data, "perceive")
        
        # Should be identical (cached)
        assert prompt1 == prompt2
        
        # Check cache hit
        cache_key = f"{sample_agent_data['agent_id']}_perceive_system"
        assert cache_key in templates._system_cache.cache
    
    @pytest.mark.unit
    def test_template_validation(self):
        """Test template validation and error handling."""
        templates = PromptTemplates()
        
        # Test with missing required fields
        incomplete_agent_data = {"agent_id": "test"}
        
        try:
            prompt = templates.generate_perceive_prompt(
                agent_data=incomplete_agent_data,
                perception_data={},
                memory_context="",
                timestamp=""
            )
            # Should handle missing fields gracefully
            assert "test" in prompt
        except KeyError:
            # Or should raise appropriate error
            pass
    
    @pytest.mark.unit
    def test_context_building(self, sample_agent_data):
        """Test context building functionality."""
        templates = PromptTemplates()
        
        # Test message history formatting
        message_history = [
            {"sender": "agent1", "message": "Hello", "timestamp": "T10:00"},
            {"sender": "agent2", "message": "Hi there", "timestamp": "T10:01"}
        ]
        
        context = templates._build_message_context(message_history)
        assert "agent1" in context
        assert "Hello" in context
        assert "agent2" in context
        assert "Hi there" in context
        
        # Test movement options formatting
        movement_options = ["north", "south", "east"]
        options_text = templates._format_movement_options(movement_options)
        assert "north" in options_text
        assert "south" in options_text
        assert "east" in options_text
        
        # Test action options formatting
        actions = ["action1", "action2", "action3"]
        actions_text = templates._format_action_options(actions)
        assert "action1" in actions_text
        assert "action2" in actions_text
        assert "action3" in actions_text
    
    @pytest.mark.performance
    def test_prompt_generation_performance(self, sample_agent_data, sample_perception_data, performance_timer):
        """Test prompt generation performance."""
        templates = PromptTemplates()
        
        # Test perceive prompt performance
        performance_timer.start()
        for i in range(100):
            templates.generate_perceive_prompt(
                agent_data=sample_agent_data,
                perception_data=sample_perception_data,
                memory_context=f"Context {i}",
                timestamp=f"T{i:02d}:00:00"
            )
        perceive_time = performance_timer.stop()
        
        # Test system prompt performance (should benefit from caching)
        performance_timer.start()
        for i in range(100):
            templates.generate_system_prompt(sample_agent_data, "perceive")
        system_time = performance_timer.stop()
        
        # Performance assertions
        assert perceive_time / 100 < 0.001  # Less than 1ms per generation
        assert system_time / 100 < 0.0001   # Even faster due to caching
        
        print(f"Perceive prompt performance: {perceive_time/100:.6f}s per generation")
        print(f"System prompt performance: {system_time/100:.6f}s per generation")
    
    @pytest.mark.unit
    def test_cache_management(self, sample_agent_data):
        """Test cache management functionality."""
        templates = PromptTemplates()
        
        # Fill cache
        for i in range(10):
            templates.generate_system_prompt(sample_agent_data, f"action_{i}")
        
        initial_cache_size = len(templates._system_cache.cache)
        assert initial_cache_size > 0
        
        # Clear cache
        templates.clear_cache()
        assert len(templates._system_cache.cache) == 0
        assert len(templates._prompt_cache.cache) == 0
    
    @pytest.mark.unit
    def test_template_customization(self):
        """Test template customization capabilities."""
        templates = PromptTemplates()
        
        # Test custom template
        custom_template = Template("Custom prompt for $agent_name with $action")
        templates.perceive_template = custom_template
        
        result = templates.perceive_template.safe_substitute(
            agent_name="TestAgent",
            action="testing"
        )
        
        assert "Custom prompt for TestAgent with testing" == result
    
    @pytest.mark.unit
    def test_edge_cases(self, sample_agent_data):
        """Test edge cases and error conditions."""
        templates = PromptTemplates()
        
        # Test with empty data
        prompt = templates.generate_perceive_prompt(
            agent_data=sample_agent_data,
            perception_data={},
            memory_context="",
            timestamp=""
        )
        assert len(prompt) > 0
        
        # Test with None values
        prompt = templates.generate_chat_prompt(
            agent_data=sample_agent_data,
            target_agent="",
            context="",
            message_history=[]
        )
        assert len(prompt) > 0
        
        # Test with very long inputs
        long_context = "Very long context " * 1000
        prompt = templates.generate_move_prompt(
            agent_data=sample_agent_data,
            current_location="kitchen",
            movement_options=["north"],
            context=long_context
        )
        assert len(prompt) > len(long_context) 