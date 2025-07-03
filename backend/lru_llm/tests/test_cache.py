"""
Unit Tests for Cache Module
===========================
Tests for LRUCache and AgentDataCache with performance validation.
"""

import pytest
import time
import json
from pathlib import Path

from lru_llm.utils.cache import LRUCache, AgentDataCache


class TestLRUCache:
    """Test suite for LRUCache implementation."""
    
    @pytest.mark.unit
    def test_cache_initialization(self):
        """Test cache initialization with different capacities."""
        cache = LRUCache(capacity=100)
        assert cache.capacity == 100
        assert len(cache) == 0
        assert cache.cache == {}
        
        # Test default capacity
        default_cache = LRUCache()
        assert default_cache.capacity == 256
    
    @pytest.mark.unit
    def test_basic_operations(self):
        """Test basic get, put, delete operations."""
        cache = LRUCache(capacity=3)
        
        # Test put and get
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"
        assert len(cache) == 1
        
        # Test non-existent key
        assert cache.get("nonexistent") is None
        
        # Test delete
        cache.delete("key1")
        assert cache.get("key1") is None
        assert len(cache) == 0
    
    @pytest.mark.unit
    def test_lru_eviction(self):
        """Test LRU eviction policy."""
        cache = LRUCache(capacity=3)
        
        # Fill cache to capacity
        cache.put("key1", "value1")
        cache.put("key2", "value2") 
        cache.put("key3", "value3")
        assert len(cache) == 3
        
        # Access key1 to make it most recently used
        cache.get("key1")
        
        # Add new item, should evict key2 (least recently used)
        cache.put("key4", "value4")
        assert len(cache) == 3
        assert cache.get("key2") is None
        assert cache.get("key1") == "value1"
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"
    
    @pytest.mark.unit
    def test_ttl_expiration(self):
        """Test TTL (time-to-live) functionality."""
        cache = LRUCache(capacity=10, ttl=0.1)  # 100ms TTL
        
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Wait for TTL to expire
        time.sleep(0.15)
        assert cache.get("key1") is None
        assert len(cache) == 0
    
    @pytest.mark.unit
    def test_clear_cache(self):
        """Test cache clearing."""
        cache = LRUCache(capacity=10)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        assert len(cache) == 2
        
        cache.clear()
        assert len(cache) == 0
        assert cache.get("key1") is None
        assert cache.get("key2") is None
    
    @pytest.mark.unit
    def test_update_existing_key(self):
        """Test updating existing keys."""
        cache = LRUCache(capacity=3)
        
        cache.put("key1", "value1")
        cache.put("key1", "updated_value1")
        
        assert cache.get("key1") == "updated_value1"
        assert len(cache) == 1
    
    @pytest.mark.performance
    def test_cache_performance(self, performance_timer):
        """Test O(1) performance characteristics."""
        cache = LRUCache(capacity=10000)
        
        # Test put performance
        performance_timer.start()
        for i in range(1000):
            cache.put(f"key_{i}", f"value_{i}")
        put_time = performance_timer.stop()
        
        # Test get performance
        performance_timer.start()
        for i in range(1000):
            cache.get(f"key_{i}")
        get_time = performance_timer.stop()
        
        # Performance should be very fast (under 1ms per operation average)
        assert put_time / 1000 < 0.001  # Less than 1ms per put
        assert get_time / 1000 < 0.001  # Less than 1ms per get
        
        print(f"Put performance: {put_time/1000:.6f}s per operation")
        print(f"Get performance: {get_time/1000:.6f}s per operation")


class TestAgentDataCache:
    """Test suite for AgentDataCache implementation."""
    
    @pytest.mark.unit
    def test_initialization(self, temp_dir):
        """Test AgentDataCache initialization."""
        cache = AgentDataCache(data_dir=temp_dir, agent_id="test_agent")
        
        assert cache.agent_id == "test_agent"
        assert cache.data_dir == temp_dir
        assert isinstance(cache.perception_cache, LRUCache)
        assert isinstance(cache.memory_cache, LRUCache)
        assert isinstance(cache.location_cache, LRUCache)
        assert isinstance(cache.prompt_cache, LRUCache)
    
    @pytest.mark.unit
    def test_perception_caching(self, temp_dir, sample_perception_data):
        """Test perception data caching."""
        cache = AgentDataCache(data_dir=temp_dir, agent_id="test_agent")
        
        timestamp = "01T15:30:45"
        cache.cache_perception(timestamp, sample_perception_data)
        
        cached_data = cache.get_perception(timestamp)
        assert cached_data == sample_perception_data
        
        # Test non-existent timestamp
        assert cache.get_perception("nonexistent") is None
    
    @pytest.mark.unit
    def test_memory_caching(self, temp_dir):
        """Test memory data caching."""
        cache = AgentDataCache(data_dir=temp_dir, agent_id="test_agent")
        
        memory_key = "high_salience_memories"
        memory_data = [
            {"event": "important meeting", "salience": 9},
            {"event": "casual conversation", "salience": 8}
        ]
        
        cache.cache_memory(memory_key, memory_data)
        cached_data = cache.get_memory(memory_key)
        
        assert cached_data == memory_data
    
    @pytest.mark.unit
    def test_location_caching(self, temp_dir):
        """Test location data caching."""
        cache = AgentDataCache(data_dir=temp_dir, agent_id="test_agent")
        
        room = "kitchen"
        location_data = {
            "adjacent_rooms": ["living_room", "dining_room"],
            "objects": ["coffee_machine", "refrigerator"],
            "movement_options": ["north", "east"]
        }
        
        cache.cache_location(room, location_data)
        cached_data = cache.get_location(room)
        
        assert cached_data == location_data
    
    @pytest.mark.unit
    def test_prompt_caching(self, temp_dir):
        """Test prompt caching."""
        cache = AgentDataCache(data_dir=temp_dir, agent_id="test_agent")
        
        prompt_key = "perceive_template_current_context"
        prompt_data = "You are in the kitchen. What do you observe?"
        
        cache.cache_prompt(prompt_key, prompt_data)
        cached_data = cache.get_prompt(prompt_key)
        
        assert cached_data == prompt_data
    
    @pytest.mark.unit
    def test_cache_persistence(self, temp_dir, sample_perception_data):
        """Test cache persistence to disk."""
        cache = AgentDataCache(data_dir=temp_dir, agent_id="test_agent")
        
        # Cache some data
        cache.cache_perception("01T15:30:45", sample_perception_data)
        cache.cache_memory("test_memories", [{"event": "test"}])
        
        # Save to disk
        cache.save_cache()
        
        # Create new cache instance
        new_cache = AgentDataCache(data_dir=temp_dir, agent_id="test_agent")
        new_cache.load_cache()
        
        # Verify data persistence
        assert new_cache.get_perception("01T15:30:45") == sample_perception_data
        assert new_cache.get_memory("test_memories") == [{"event": "test"}]
    
    @pytest.mark.unit
    def test_cache_invalidation(self, temp_dir):
        """Test cache invalidation functionality."""
        cache = AgentDataCache(data_dir=temp_dir, agent_id="test_agent")
        
        # Cache some data
        cache.cache_perception("01T15:30:45", {"test": "data"})
        cache.cache_memory("test_key", [{"test": "memory"}])
        
        # Invalidate specific cache
        cache.invalidate_perception()
        assert cache.get_perception("01T15:30:45") is None
        assert cache.get_memory("test_key") == [{"test": "memory"}]  # Should still exist
        
        # Invalidate all caches
        cache.cache_memory("test_key2", [{"test": "memory2"}])
        cache.invalidate_all()
        assert cache.get_memory("test_key") is None
        assert cache.get_memory("test_key2") is None
    
    @pytest.mark.performance
    def test_agent_cache_performance(self, temp_dir, performance_timer):
        """Test AgentDataCache performance."""
        cache = AgentDataCache(data_dir=temp_dir, agent_id="test_agent")
        
        # Test perception caching performance
        performance_timer.start()
        for i in range(100):
            cache.cache_perception(f"timestamp_{i}", {"data": f"perception_{i}"})
        perception_cache_time = performance_timer.stop()
        
        # Test perception retrieval performance
        performance_timer.start()
        for i in range(100):
            cache.get_perception(f"timestamp_{i}")
        perception_get_time = performance_timer.stop()
        
        # Should be very fast
        assert perception_cache_time / 100 < 0.001  # Less than 1ms per operation
        assert perception_get_time / 100 < 0.001   # Less than 1ms per operation
        
        print(f"Perception cache performance: {perception_cache_time/100:.6f}s per operation")
        print(f"Perception get performance: {perception_get_time/100:.6f}s per operation")
    
    @pytest.mark.unit
    def test_error_handling(self, temp_dir):
        """Test error handling in cache operations."""
        cache = AgentDataCache(data_dir=temp_dir, agent_id="test_agent")
        
        # Test with None values
        cache.cache_perception("test", None)
        assert cache.get_perception("test") is None
        
        # Test with empty strings
        cache.cache_prompt("empty", "")
        assert cache.get_prompt("empty") == ""
        
        # Test loading non-existent cache file
        cache.load_cache()  # Should not raise error
        
        # Test saving to read-only directory (if we can simulate it)
        # This would depend on OS permissions 