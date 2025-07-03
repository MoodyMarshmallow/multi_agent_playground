"""
Optimized LRU Cache Implementation
=================================
Provides O(1) access, insertion, and deletion for agent data caching.
"""

from typing import Any, Dict, Optional, Tuple
from collections import OrderedDict
import time


class LRUCache:
    """
    Optimized LRU Cache with O(1) operations for agent data.
    
    Time Complexities:
    - get(): O(1)
    - put(): O(1) 
    - delete(): O(1)
    - clear(): O(1)
    
    Space Complexity: O(capacity)
    """
    
    def __init__(self, capacity: int = 256, ttl_seconds: int = 3600, ttl: float = None):
        """
        Initialize LRU cache with capacity and TTL.
        
        Args:
            capacity: Maximum number of items to store
            ttl_seconds: Time-to-live for cached items (default 1 hour)
            ttl: Alternative TTL parameter for backwards compatibility (in seconds)
        """
        self.capacity = capacity
        # Handle both ttl_seconds and ttl parameters for compatibility
        if ttl is not None:
            self.ttl_seconds = ttl
        else:
            self.ttl_seconds = ttl_seconds
        self._cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        # For backwards compatibility with tests that expect .cache attribute
        self.cache = {}
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get item from cache with O(1) time complexity.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            return None
        
        value, timestamp = self._cache[key]
        
        # Check TTL
        if time.time() - timestamp > self.ttl_seconds:
            del self._cache[key]
            return None
        
        # Move to end (most recently used) - O(1) operation
        self._cache.move_to_end(key)
        return value
    
    def put(self, key: str, value: Any) -> None:
        """
        Put item in cache with O(1) time complexity.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        current_time = time.time()
        
        if key in self._cache:
            # Update existing key - O(1)
            self._cache[key] = (value, current_time)
            self._cache.move_to_end(key)
        else:
            # Add new key
            if len(self._cache) >= self.capacity:
                # Remove least recently used item - O(1)
                removed_key, _ = self._cache.popitem(last=False)
                # Also remove from backwards compatibility cache
                self.cache.pop(removed_key, None)
            
            self._cache[key] = (value, current_time)
        
        # Update backwards compatibility cache attribute
        self.cache[key] = value
    
    def delete(self, key: str) -> bool:
        """
        Delete item from cache with O(1) time complexity.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if key existed and was deleted, False otherwise
        """
        if key in self._cache:
            del self._cache[key]
            self.cache.pop(key, None)
            return True
        return False
    
    def clear(self) -> None:
        """Clear all items from the cache."""
        self.cache.clear()
        self._cache.clear()
    
    def size(self) -> int:
        """Get current cache size with O(1) time complexity."""
        return len(self._cache)
    
    def __len__(self) -> int:
        """Get current cache size with O(1) time complexity."""
        return len(self._cache)
    
    def cleanup_expired(self) -> int:
        """
        Remove expired items from cache.
        
        Returns:
            Number of items removed
        
        Note: This is O(n) but called periodically, not in critical path
        """
        current_time = time.time()
        expired_keys = []
        
        for key, (_, timestamp) in self._cache.items():
            if current_time - timestamp > self.ttl_seconds:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
            self.cache.pop(key, None)
        
        return len(expired_keys)

    @property
    def size(self) -> int:
        """Return current cache size."""
        return len(self.cache)


class AgentDataCache:
    """
    Specialized cache for agent data with optimized access patterns.
    
    Provides O(1) access to:
    - Agent state data
    - Memory contexts
    - Location information
    - Conversation history
    """
    
    def __init__(self, data_dir: str = None, agent_id: str = "default", capacity: int = 500):
        """Initialize with separate caches for different data types."""
        self.data_dir = data_dir
        self.agent_id = agent_id
        self.perception_cache = LRUCache(capacity // 4, ttl_seconds=1800)  # 30 min
        self.memory_cache = LRUCache(capacity // 4, ttl_seconds=3600)  # 1 hour
        self.location_cache = LRUCache(capacity // 4, ttl_seconds=600)  # 10 min
        self.prompt_cache = LRUCache(capacity // 4, ttl_seconds=1800)  # 30 min
        
        # Legacy compatibility
        self.agent_states = self.perception_cache
        self.memory_contexts = self.memory_cache
        self.location_data = self.location_cache
        self.conversation_history = self.prompt_cache
    
    def get_agent_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent state with O(1) access."""
        return self.agent_states.get(agent_id)
    
    def cache_agent_state(self, agent_id: str, state: Dict[str, Any]) -> None:
        """Cache agent state with O(1) insertion."""
        self.agent_states.put(agent_id, state)
    
    def get_memory_context(self, agent_id: str, context_key: str) -> Optional[list]:
        """Get memory context with O(1) access."""
        cache_key = f"{agent_id}:{context_key}"
        return self.memory_contexts.get(cache_key)
    
    def cache_memory_context(self, agent_id: str, context_key: str, memories: list) -> None:
        """Cache memory context with O(1) insertion."""
        cache_key = f"{agent_id}:{context_key}"
        self.memory_contexts.put(cache_key, memories)
    
    def get_location_data(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get location data with O(1) access."""
        return self.location_data.get(agent_id)
    
    def cache_location_data(self, agent_id: str, location: Dict[str, Any]) -> None:
        """Cache location data with O(1) insertion."""
        self.location_data.put(agent_id, location)
    
    def get_conversation_history(self, conversation_id: str) -> Optional[list]:
        """Get conversation history with O(1) access."""
        return self.conversation_history.get(conversation_id)
    
    def cache_conversation_history(self, conversation_id: str, history: list) -> None:
        """Cache conversation history with O(1) insertion."""
        self.conversation_history.put(conversation_id, history)
    
    def clear_agent_data(self, agent_id: str) -> None:
        """Clear all cached data for an agent with O(1) operations."""
        self.agent_states.delete(agent_id)
        self.location_data.delete(agent_id)
        
        # Clean memory contexts - O(k) where k is number of context types
        context_keys = ["conversation", "location", "interaction", "perception"]
        for context_key in context_keys:
            cache_key = f"{agent_id}:{context_key}"
            self.memory_contexts.delete(cache_key)
    
    def cleanup_expired(self) -> int:
        """Clean up expired entries across all caches."""
        total_cleaned = 0
        total_cleaned += self.agent_states.cleanup_expired()
        total_cleaned += self.memory_contexts.cleanup_expired()
        total_cleaned += self.location_data.cleanup_expired()
        total_cleaned += self.conversation_history.cleanup_expired()
        return total_cleaned 
    
    # Methods expected by tests
    def cache_perception(self, timestamp: str, data: Dict[str, Any]) -> None:
        """Cache perception data."""
        self.perception_cache.put(timestamp, data)
    
    def get_perception(self, timestamp: str) -> Optional[Dict[str, Any]]:
        """Get perception data."""
        return self.perception_cache.get(timestamp)
    
    def cache_memory(self, key: str, data: list) -> None:
        """Cache memory data."""
        self.memory_cache.put(key, data)
    
    def get_memory(self, key: str) -> Optional[list]:
        """Get memory data."""
        return self.memory_cache.get(key)
    
    def cache_location(self, room: str, data: Dict[str, Any]) -> None:
        """Cache location data."""
        self.location_cache.put(room, data)
    
    def get_location(self, room: str) -> Optional[Dict[str, Any]]:
        """Get location data."""
        return self.location_cache.get(room)
    
    def cache_prompt(self, key: str, data: str) -> None:
        """Cache prompt data."""
        self.prompt_cache.put(key, data)
    
    def get_prompt(self, key: str) -> Optional[str]:
        """Get prompt data."""
        return self.prompt_cache.get(key)
    
    def save_cache(self) -> None:
        """Save cache to disk."""
        if not self.data_dir:
            return
        
        import json
        from pathlib import Path
        
        cache_dir = Path(self.data_dir)
        cache_dir.mkdir(exist_ok=True)
        
        cache_data = {
            'perception': dict(self.perception_cache.cache),
            'memory': dict(self.memory_cache.cache),
            'location': dict(self.location_cache.cache),
            'prompt': dict(self.prompt_cache.cache)
        }
        
        cache_file = cache_dir / f"{self.agent_id}_cache.json"
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
    
    def load_cache(self) -> None:
        """Load cache from disk."""
        if not self.data_dir:
            return
        
        import json
        from pathlib import Path
        
        cache_file = Path(self.data_dir) / f"{self.agent_id}_cache.json"
        if not cache_file.exists():
            return
        
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Restore cached data
            for key, value in cache_data.get('perception', {}).items():
                self.perception_cache.put(key, value)
            
            for key, value in cache_data.get('memory', {}).items():
                self.memory_cache.put(key, value)
            
            for key, value in cache_data.get('location', {}).items():
                self.location_cache.put(key, value)
            
            for key, value in cache_data.get('prompt', {}).items():
                self.prompt_cache.put(key, value)
                
        except (json.JSONDecodeError, KeyError, IOError):
            # Gracefully handle corrupted cache files
            pass
    
    def invalidate_perception(self) -> None:
        """Invalidate perception cache."""
        self.perception_cache.clear()
    
    def invalidate_all(self) -> None:
        """Invalidate all caches."""
        self.perception_cache.clear()
        self.memory_cache.clear()
        self.location_cache.clear()
        self.prompt_cache.clear()