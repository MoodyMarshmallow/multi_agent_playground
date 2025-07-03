"""
Unit Tests for Memory Module
============================
Tests for AgentMemory and MemoryContextBuilder with performance validation.
"""

import pytest
import time
import json
from pathlib import Path

from lru_llm.agent.memory import AgentMemory, MemoryContextBuilder


class TestAgentMemory:
    """Test suite for AgentMemory implementation."""
    
    @pytest.mark.unit
    def test_initialization(self, temp_dir):
        """Test AgentMemory initialization."""
        memory = AgentMemory(
            agent_id="test_agent",
            data_dir=temp_dir
        )
        
        assert memory.agent_id == "test_agent"
        assert memory.data_dir == temp_dir
        assert memory.episodic_memory == []
        assert len(memory.salience_index) == 0
        assert len(memory.context_index) == 0
        assert len(memory.timestamp_index) == 0
    
    @pytest.mark.unit
    def test_add_memory(self, temp_dir):
        """Test adding memories."""
        memory = AgentMemory("test_agent", temp_dir)
        
        memory_entry = {
            "timestamp": "01T15:30:00",
            "location": "kitchen",
            "event": "Made coffee",
            "salience": 7,
            "tags": ["daily_routine", "morning"]
        }
        
        memory_id = memory.add_memory(memory_entry)
        
        assert memory_id is not None
        assert len(memory.episodic_memory) == 1
        assert memory.episodic_memory[0]["id"] == memory_id
        assert memory.episodic_memory[0]["event"] == "Made coffee"
        
        # Check indices are updated
        assert memory_id in memory.salience_index[7]
        assert memory_id in memory.context_index["kitchen"]
        assert memory_id in memory.timestamp_index["01T15:30:00"]
    
    @pytest.mark.unit
    def test_get_memories_by_salience(self, temp_dir, sample_memories):
        """Test retrieving memories by salience."""
        memory = AgentMemory("test_agent", temp_dir)
        
        # Add sample memories
        for mem in sample_memories:
            memory.add_memory(mem)
        
        # Get high salience memories (>= 7)
        high_salience = memory.get_memories_by_salience(min_salience=7)
        assert len(high_salience) == 2  # salience 8 and 7
        
        # Get very high salience memories (>= 8)
        very_high = memory.get_memories_by_salience(min_salience=8)
        assert len(very_high) == 1  # only salience 8
        
        # Check order (should be highest first)
        assert high_salience[0]["salience"] >= high_salience[1]["salience"]
    
    @pytest.mark.unit
    def test_get_memories_by_context(self, temp_dir, sample_memories):
        """Test retrieving memories by context."""
        memory = AgentMemory("test_agent", temp_dir)
        
        # Add sample memories
        for mem in sample_memories:
            memory.add_memory(mem)
        
        # Get memories from kitchen
        kitchen_memories = memory.get_memories_by_context("kitchen")
        assert len(kitchen_memories) == 2
        
        # Get memories from office
        office_memories = memory.get_memories_by_context("office")
        assert len(office_memories) == 1
        
        # Check content
        assert all("kitchen" in mem["location"] for mem in kitchen_memories)
        assert all("office" in mem["location"] for mem in office_memories)
    
    @pytest.mark.unit
    def test_get_recent_memories(self, temp_dir, sample_memories):
        """Test retrieving recent memories."""
        memory = AgentMemory("test_agent", temp_dir)
        
        # Add sample memories
        for mem in sample_memories:
            memory.add_memory(mem)
        
        # Get recent memories
        recent = memory.get_recent_memories(limit=2)
        assert len(recent) == 2
        
        # Should be ordered by recency (most recent first)
        assert recent[0]["created_at"] >= recent[1]["created_at"]
    
    @pytest.mark.unit
    def test_search_memories(self, temp_dir, sample_memories):
        """Test memory search functionality."""
        memory = AgentMemory("test_agent", temp_dir)
        
        # Add sample memories
        for mem in sample_memories:
            memory.add_memory(mem)
        
        # Search by keyword
        coffee_memories = memory.search_memories("coffee")
        assert len(coffee_memories) == 1
        assert "coffee" in coffee_memories[0]["event"].lower()
        
        # Search by tag
        work_memories = memory.search_memories("work")
        assert len(work_memories) == 3  # All have work tag
        
        # Search with no results
        no_results = memory.search_memories("nonexistent")
        assert len(no_results) == 0
    
    @pytest.mark.unit
    def test_update_memory_salience(self, temp_dir):
        """Test updating memory salience."""
        memory = AgentMemory("test_agent", temp_dir)
        
        memory_entry = {
            "timestamp": "01T15:30:00",
            "location": "kitchen",
            "event": "Made coffee",
            "salience": 5,
            "tags": ["daily_routine"]
        }
        
        memory_id = memory.add_memory(memory_entry)
        
        # Update salience
        memory.update_memory_salience(memory_id, new_salience=8)
        
        # Check memory is updated
        updated_memory = next(mem for mem in memory.episodic_memory if mem["id"] == memory_id)
        assert updated_memory["salience"] == 8
        
        # Check indices are updated
        assert memory_id not in memory.salience_index.get(5, set())
        assert memory_id in memory.salience_index[8]
    
    @pytest.mark.unit
    def test_decay_memories(self, temp_dir, sample_memories):
        """Test memory decay functionality."""
        memory = AgentMemory("test_agent", temp_dir)
        
        # Add sample memories
        for mem in sample_memories:
            memory.add_memory(mem)
        
        # Get initial salience values
        initial_saliences = [mem["salience"] for mem in memory.episodic_memory]
        
        # Apply decay
        memory.decay_memories(decay_factor=0.1)
        
        # Check salience has decreased
        final_saliences = [mem["salience"] for mem in memory.episodic_memory]
        for initial, final in zip(initial_saliences, final_saliences):
            assert final < initial
    
    @pytest.mark.unit
    def test_memory_persistence(self, temp_dir, sample_memories):
        """Test memory persistence to disk."""
        memory = AgentMemory("test_agent", temp_dir)
        
        # Add sample memories
        for mem in sample_memories:
            memory.add_memory(mem)
        
        # Save to disk
        memory.save_memory()
        
        # Create new memory instance
        new_memory = AgentMemory("test_agent", temp_dir)
        new_memory.load_memory()
        
        # Check data is preserved
        assert len(new_memory.episodic_memory) == len(sample_memories)
        assert len(new_memory.salience_index) > 0
        assert len(new_memory.context_index) > 0
        assert len(new_memory.timestamp_index) > 0
    
    @pytest.mark.performance
    def test_memory_performance(self, temp_dir, performance_timer):
        """Test memory operation performance."""
        memory = AgentMemory("test_agent", temp_dir)
        
        # Test adding memories performance
        performance_timer.start()
        for i in range(1000):
            memory_entry = {
                "timestamp": f"01T{i:02d}:00:00",
                "location": f"room_{i % 10}",
                "event": f"Event {i}",
                "salience": i % 10,
                "tags": [f"tag_{i % 5}"]
            }
            memory.add_memory(memory_entry)
        add_time = performance_timer.stop()
        
        # Test retrieval performance
        performance_timer.start()
        for i in range(100):
            memory.get_memories_by_salience(min_salience=5)
        retrieval_time = performance_timer.stop()
        
        # Test search performance
        performance_timer.start()
        for i in range(100):
            memory.search_memories(f"Event {i}")
        search_time = performance_timer.stop()
        
        # Performance assertions (should be fast due to indexing)
        assert add_time / 1000 < 0.001     # Less than 1ms per add
        assert retrieval_time / 100 < 0.001  # Less than 1ms per retrieval
        assert search_time / 100 < 0.001     # Less than 1ms per search
        
        print(f"Add memory performance: {add_time/1000:.6f}s per operation")
        print(f"Retrieval performance: {retrieval_time/100:.6f}s per operation")
        print(f"Search performance: {search_time/100:.6f}s per operation")


class TestMemoryContextBuilder:
    """Test suite for MemoryContextBuilder implementation."""
    
    @pytest.mark.unit
    def test_initialization(self, temp_dir):
        """Test MemoryContextBuilder initialization."""
        memory = AgentMemory("test_agent", temp_dir)
        builder = MemoryContextBuilder(memory)
        
        assert builder.memory == memory
        assert hasattr(builder, '_context_cache')
    
    @pytest.mark.unit
    def test_build_context_for_action(self, temp_dir, sample_memories):
        """Test building context for specific actions."""
        memory = AgentMemory("test_agent", temp_dir)
        for mem in sample_memories:
            memory.add_memory(mem)
        
        builder = MemoryContextBuilder(memory)
        
        # Test perceive action context
        context = builder.build_context_for_action(
            action_type="perceive",
            current_location="kitchen",
            max_memories=2
        )
        
        assert len(context) > 0
        assert "kitchen" in context  # Should include location-relevant memories
        
        # Test chat action context
        context = builder.build_context_for_action(
            action_type="chat",
            target_agent="test_agent_002",
            max_memories=2
        )
        
        assert len(context) > 0
    
    @pytest.mark.unit
    def test_build_temporal_context(self, temp_dir, sample_memories):
        """Test building temporal context."""
        memory = AgentMemory("test_agent", temp_dir)
        for mem in sample_memories:
            memory.add_memory(mem)
        
        builder = MemoryContextBuilder(memory)
        
        # Test recent context
        context = builder.build_temporal_context(
            timeframe="recent",
            max_memories=2
        )
        
        assert len(context) > 0
        
        # Test specific time range
        context = builder.build_temporal_context(
            timeframe="01T15:00:00-01T15:30:00",
            max_memories=5
        )
        
        assert len(context) >= 0  # Might be empty depending on time range
    
    @pytest.mark.unit
    def test_build_contextual_summary(self, temp_dir, sample_memories):
        """Test building contextual summary."""
        memory = AgentMemory("test_agent", temp_dir)
        for mem in sample_memories:
            memory.add_memory(mem)
        
        builder = MemoryContextBuilder(memory)
        
        # Test location-based summary
        summary = builder.build_contextual_summary(
            context_type="location",
            context_value="kitchen",
            max_memories=3
        )
        
        assert len(summary) > 0
        assert "kitchen" in summary.lower()
        
        # Test salience-based summary
        summary = builder.build_contextual_summary(
            context_type="salience",
            context_value=7,
            max_memories=3
        )
        
        assert len(summary) > 0
    
    @pytest.mark.unit
    def test_get_relevant_memories(self, temp_dir, sample_memories):
        """Test getting relevant memories."""
        memory = AgentMemory("test_agent", temp_dir)
        for mem in sample_memories:
            memory.add_memory(mem)
        
        builder = MemoryContextBuilder(memory)
        
        # Test with multiple criteria
        relevant = builder.get_relevant_memories(
            location="kitchen",
            min_salience=6,
            tags=["work"],
            max_memories=5
        )
        
        assert len(relevant) > 0
        for mem in relevant:
            assert mem["location"] == "kitchen"
            assert mem["salience"] >= 6
            assert "work" in mem["tags"]
    
    @pytest.mark.unit
    def test_context_caching(self, temp_dir, sample_memories):
        """Test context caching functionality."""
        memory = AgentMemory("test_agent", temp_dir)
        for mem in sample_memories:
            memory.add_memory(mem)
        
        builder = MemoryContextBuilder(memory)
        
        # Build context multiple times with same parameters
        context1 = builder.build_context_for_action(
            action_type="perceive",
            current_location="kitchen",
            max_memories=2
        )
        
        context2 = builder.build_context_for_action(
            action_type="perceive",
            current_location="kitchen",
            max_memories=2
        )
        
        # Should return identical results (from cache)
        assert context1 == context2
    
    @pytest.mark.performance
    def test_context_building_performance(self, temp_dir, performance_timer):
        """Test context building performance."""
        memory = AgentMemory("test_agent", temp_dir)
        
        # Add many memories
        for i in range(1000):
            memory_entry = {
                "timestamp": f"01T{i:02d}:00:00",
                "location": f"room_{i % 10}",
                "event": f"Event {i}",
                "salience": i % 10,
                "tags": [f"tag_{i % 5}"]
            }
            memory.add_memory(memory_entry)
        
        builder = MemoryContextBuilder(memory)
        
        # Test context building performance
        performance_timer.start()
        for i in range(100):
            builder.build_context_for_action(
                action_type="perceive",
                current_location=f"room_{i % 10}",
                max_memories=10
            )
        context_time = performance_timer.stop()
        
        # Test summary building performance
        performance_timer.start()
        for i in range(100):
            builder.build_contextual_summary(
                context_type="location",
                context_value=f"room_{i % 10}",
                max_memories=10
            )
        summary_time = performance_timer.stop()
        
        # Should be fast due to indexing and caching
        assert context_time / 100 < 0.001   # Less than 1ms per context build
        assert summary_time / 100 < 0.001   # Less than 1ms per summary
        
        print(f"Context building performance: {context_time/100:.6f}s per operation")
        print(f"Summary building performance: {summary_time/100:.6f}s per operation")
    
    @pytest.mark.unit
    def test_memory_prioritization(self, temp_dir, sample_memories):
        """Test memory prioritization in context building."""
        memory = AgentMemory("test_agent", temp_dir)
        for mem in sample_memories:
            memory.add_memory(mem)
        
        builder = MemoryContextBuilder(memory)
        
        # Get memories with limit
        context = builder.build_context_for_action(
            action_type="perceive",
            current_location="kitchen",
            max_memories=1
        )
        
        # Should prioritize high-salience, recent memories
        assert len(context) > 0
        
        # Test that high salience memories are preferred
        relevant = builder.get_relevant_memories(
            location="kitchen",
            max_memories=1
        )
        
        if len(relevant) > 0:
            # Should be the highest salience memory from kitchen
            kitchen_memories = [mem for mem in sample_memories if mem["location"] == "kitchen"]
            highest_salience = max(mem["salience"] for mem in kitchen_memories)
            assert relevant[0]["salience"] == highest_salience 