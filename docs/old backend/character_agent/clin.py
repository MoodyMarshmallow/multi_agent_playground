from kani import Kani
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Union, Tuple, Set
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
import hashlib


@dataclass
class MemoryEntry:
    """Represents a single memory entry with X->Y relation"""
    X: str
    relation: str  # "is", "should", "may", "doesn't"
    Y: str
    context: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
    memory_id: Optional[int] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class VectorStoreInterface:
    """Placeholder interface for vector embedding storage of overflow memories"""
    
    def __init__(self):
        # TODO: Initialize vector store connection/client
        pass
    
    def store_batch(self, memories: List[MemoryEntry], batch_id: str) -> bool:
        """
        Store a batch of overflow memories as vector embeddings
        
        Args:
            memories: List of MemoryEntry objects to embed and store
            batch_id: Unique identifier for this batch of memories
            
        Returns:
            bool: Success status
        """
        # TODO: Convert memories to embeddings and store in vector database
        # Example: convert each memory to text, embed with sentence transformer,
        # store in vector DB with metadata for retrieval
        print(f"[PLACEHOLDER] Storing {len(memories)} memories to vector store with batch_id: {batch_id}")
        return True
    
    def similarity_search(self, query_text: str, top_k: int = 5) -> List[MemoryEntry]:
        """
        Search for similar memories in vector store
        
        Args:
            query_text: Text to search for similar memories
            top_k: Number of results to return
            
        Returns:
            List of similar MemoryEntry objects
        """
        # TODO: Embed query_text, perform similarity search, return results
        print(f"[PLACEHOLDER] Vector similarity search for: '{query_text}', top_k: {top_k}")
        return []


class SimpleBloomFilter:
    """Simple Bloom filter implementation for fast negative lookups"""
    
    def __init__(self, capacity: int = 10000, error_rate: float = 0.1):
        self.capacity = capacity
        self.error_rate = error_rate
        self.bit_array_size = self._calculate_bit_array_size()
        self.hash_count = self._calculate_hash_count()
        self.bit_array = [False] * self.bit_array_size
    
    def _calculate_bit_array_size(self) -> int:
        import math
        return int(-self.capacity * math.log(self.error_rate) / (math.log(2) ** 2))
    
    def _calculate_hash_count(self) -> int:
        import math
        return int(self.bit_array_size * math.log(2) / self.capacity)
    
    def _hash(self, item: str, seed: int) -> int:
        hash_obj = hashlib.md5((item + str(seed)).encode())
        return int(hash_obj.hexdigest(), 16) % self.bit_array_size
    
    def add(self, item: str):
        for i in range(self.hash_count):
            index = self._hash(item.lower(), i)
            self.bit_array[index] = True
    
    def contains(self, item: str) -> bool:
        for i in range(self.hash_count):
            index = self._hash(item.lower(), i)
            if not self.bit_array[index]:
                return False
        return True


class LRUCache:
    """Simple LRU cache for query results"""
    
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.cache = {}
        self.order = deque()
    
    def get(self, key: str) -> Optional[List[MemoryEntry]]:
        if key in self.cache:
            # Move to end (most recently used)
            self.order.remove(key)
            self.order.append(key)
            return self.cache[key]
        return None
    
    def put(self, key: str, value: List[MemoryEntry]):
        if key in self.cache:
            # Update existing
            self.order.remove(key)
        elif len(self.cache) >= self.capacity:
            # Remove least recently used
            lru_key = self.order.popleft()
            del self.cache[lru_key]
        
        self.cache[key] = value
        self.order.append(key)
    
    def invalidate(self):
        """Clear all cached results"""
        self.cache.clear()
        self.order.clear()


class CLIN_X2YMemory:
    """
    Optimized continual, causal, and spatial memory class for Simulacra agents.
    Manages (X, relation, Y) triplets with O(1) operations using ring buffer and hash indexing.
    Overflow memories are stored in vector embeddings.
    """
    
    VALID_RELATIONS = {"is", "should", "may", "doesn't"}
    
    def __init__(self, meta_memory_every: int = 100, meta_memory_prompt: Optional[str] = None, 
                 max_memories: Optional[int] = 1000, overflow_batch_size: int = 50):
        """
        Initialize the optimized CLIN_X2YMemory system.
        
        Args:
            meta_memory_every: Number of entries before meta-memory synthesis
            meta_memory_prompt: Custom prompt for meta-memory generation
            max_memories: Maximum number of memories in active ring buffer
            overflow_batch_size: Number of memories to batch when moving to vector store
        """
        # Ring buffer for active memories
        self.max_memories = max_memories or 1000
        self.ring_buffer: List[Optional[MemoryEntry]] = [None] * self.max_memories
        self.current_position = 0
        self.buffer_full = False
        
        # Hash indexes for O(1) lookups
        self.x_index: Dict[str, Set[int]] = defaultdict(set)
        self.y_index: Dict[str, Set[int]] = defaultdict(set)
        self.relation_index: Dict[str, Set[int]] = defaultdict(set)
        self.context_index: Dict[str, Set[int]] = defaultdict(set)
        
        # Real-time statistics for O(1) stats
        self.context_counts: Dict[str, int] = defaultdict(int)
        self.relation_counts: Dict[str, int] = defaultdict(int)
        self.total_active_memories = 0
        self.most_common_context: Optional[str] = None
        self.most_common_relation: Optional[str] = None
        
        # Bloom filters for fast negative lookups
        self.x_bloom = SimpleBloomFilter()
        self.y_bloom = SimpleBloomFilter()
        self.context_bloom = SimpleBloomFilter()
        
        # LRU cache for query results
        self.query_cache = LRUCache(capacity=50)
        
        # Vector store for overflow memories
        self.vector_store = VectorStoreInterface()
        self.overflow_batch_size = overflow_batch_size
        self.overflow_buffer: List[MemoryEntry] = []
        
        # Meta-memory settings
        self.meta_memory_every = meta_memory_every
        self.meta_memory_prompt = meta_memory_prompt or self._default_meta_memory_prompt()
        self.meta_memories: List[str] = []
        self._entry_count = 0
        self._next_memory_id = 0
    
    def _default_meta_memory_prompt(self) -> str:
        """Default prompt for meta-memory generation"""
        return """Analyze the following memory entries and synthesize a generalized pattern or rule.
        Focus on spatial relationships, causal patterns, and modal relations (is/should/may/doesn't).
        Provide a concise abstraction that captures the underlying patterns."""
    
    def _generate_cache_key(self, X: Optional[str], Y: Optional[str], 
                           relation: Optional[str], context: Optional[str], top_k: int) -> str:
        """Generate cache key for query parameters"""
        params = [str(X), str(Y), str(relation), str(context), str(top_k)]
        return "|".join(params)
    
    def _remove_from_indexes(self, memory: MemoryEntry, position: int):
        """Remove memory from all hash indexes"""
        if memory is None:
            return
            
        # Remove from indexes
        self.x_index[memory.X.lower()].discard(position)
        self.y_index[memory.Y.lower()].discard(position)
        self.relation_index[memory.relation].discard(position)
        self.context_index[memory.context.lower()].discard(position)
        
        # Update counts
        self.context_counts[memory.context] -= 1
        self.relation_counts[memory.relation] -= 1
        if self.context_counts[memory.context] <= 0:
            del self.context_counts[memory.context]
        if self.relation_counts[memory.relation] <= 0:
            del self.relation_counts[memory.relation]
        
        self.total_active_memories -= 1
    
    def _add_to_indexes(self, memory: MemoryEntry, position: int):
        """Add memory to all hash indexes"""
        # Add to indexes
        self.x_index[memory.X.lower()].add(position)
        self.y_index[memory.Y.lower()].add(position)
        self.relation_index[memory.relation].add(position)
        self.context_index[memory.context.lower()].add(position)
        
        # Add to bloom filters
        self.x_bloom.add(memory.X)
        self.y_bloom.add(memory.Y)
        self.context_bloom.add(memory.context)
        
        # Update counts and most common tracking
        self.context_counts[memory.context] += 1
        self.relation_counts[memory.relation] += 1
        
        # Update most common (O(1) with simple comparison)
        if (self.most_common_context is None or 
            self.context_counts[memory.context] > self.context_counts.get(self.most_common_context, 0)):
            self.most_common_context = memory.context
            
        if (self.most_common_relation is None or 
            self.relation_counts[memory.relation] > self.relation_counts.get(self.most_common_relation, 0)):
            self.most_common_relation = memory.relation
        
        self.total_active_memories += 1
    
    def _handle_overflow(self, evicted_memory: MemoryEntry):
        """Handle memory overflow by batching to vector store"""
        self.overflow_buffer.append(evicted_memory)
        
        if len(self.overflow_buffer) >= self.overflow_batch_size:
            # Batch store to vector embeddings
            batch_id = f"batch_{datetime.now().isoformat()}_{len(self.overflow_buffer)}"
            success = self.vector_store.store_batch(self.overflow_buffer.copy(), batch_id)
            
            if success:
                print(f"Successfully moved {len(self.overflow_buffer)} memories to vector store")
                self.overflow_buffer.clear()
            else:
                print("Failed to store overflow batch to vector store")
    
    def add(self, X: str, relation: str, Y: str, context: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a new memory triplet with O(1) complexity using ring buffer.
        
        Args:
            X: Action, object, or event
            relation: Modal relation ("is", "should", "may", "doesn't")
            Y: Outcome or goal
            context: Spatial or environmental context
            metadata: Optional additional data
        """
        if relation not in self.VALID_RELATIONS:
            raise ValueError(f"Invalid relation '{relation}'. Must be one of: {self.VALID_RELATIONS}")
        
        # Create new memory entry
        memory_id = self._next_memory_id
        self._next_memory_id += 1
        entry = MemoryEntry(X=X, relation=relation, Y=Y, context=context, 
                          metadata=metadata, memory_id=memory_id)
        
        # Handle eviction if buffer position is occupied
        current_memory = self.ring_buffer[self.current_position]
        if current_memory is not None:
            # Remove from indexes before eviction
            self._remove_from_indexes(current_memory, self.current_position)
            # Handle overflow to vector store
            self._handle_overflow(current_memory)
        
        # Place new memory in ring buffer
        self.ring_buffer[self.current_position] = entry
        self._add_to_indexes(entry, self.current_position)
        
        # Advance ring buffer position
        self.current_position = (self.current_position + 1) % self.max_memories
        if not self.buffer_full and self.current_position == 0:
            self.buffer_full = True
        
        self._entry_count += 1
        
        # Invalidate query cache
        self.query_cache.invalidate()
        
        # Check if meta-memory generation should be triggered
        if self.should_generate_meta():
            meta = self.generate_meta_memory()
            if meta:
                self.meta_memories.append(meta)
    
    def query(self, X: Optional[str] = None, Y: Optional[str] = None, 
              relation: Optional[str] = None, context: Optional[str] = None, 
              top_k: int = 5, include_vector_search: bool = False) -> List[MemoryEntry]:
        """
        Retrieve relevant memories with O(1) hash-based lookups.
        
        Args:
            X: Filter by X component
            Y: Filter by Y component
            relation: Filter by relation type
            context: Filter by context
            top_k: Maximum number of results to return
            include_vector_search: Whether to search vector store for additional results
        
        Returns:
            List of matching memory entries, most recent first
        """
        # Check cache first
        cache_key = self._generate_cache_key(X, Y, relation, context, top_k)
        cached_result = self.query_cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Fast negative lookup with bloom filters
        if X is not None and not self.x_bloom.contains(X):
            result = []
            self.query_cache.put(cache_key, result)
            return result
        if Y is not None and not self.y_bloom.contains(Y):
            result = []
            self.query_cache.put(cache_key, result)
            return result
        if context is not None and not self.context_bloom.contains(context):
            result = []
            self.query_cache.put(cache_key, result)
            return result
        
        # Get candidate positions from hash indexes
        candidate_positions = None
        
        if X is not None:
            x_positions = self.x_index.get(X.lower(), set())
            candidate_positions = x_positions if candidate_positions is None else candidate_positions & x_positions
        
        if Y is not None:
            y_positions = self.y_index.get(Y.lower(), set())
            candidate_positions = y_positions if candidate_positions is None else candidate_positions & y_positions
        
        if relation is not None:
            rel_positions = self.relation_index.get(relation, set())
            candidate_positions = rel_positions if candidate_positions is None else candidate_positions & rel_positions
        
        if context is not None:
            ctx_positions = self.context_index.get(context.lower(), set())
            candidate_positions = ctx_positions if candidate_positions is None else candidate_positions & ctx_positions
        
        # If no filters provided, get all active memory positions
        if candidate_positions is None:
            if self.buffer_full:
                candidate_positions = set(range(self.max_memories))
            else:
                candidate_positions = set(range(self.current_position))
        
        # Collect matching memories and sort by recency (memory_id descending)
        matching_memories = []
        for pos in candidate_positions:
            memory = self.ring_buffer[pos]
            if memory is not None:
                matching_memories.append(memory)
        
        # Sort by memory_id (descending = most recent first) and limit to top_k
        matching_memories.sort(key=lambda m: m.memory_id, reverse=True)
        result = matching_memories[:top_k]
        
        # TODO: If include_vector_search and we need more results, search vector store
        if include_vector_search and len(result) < top_k:
            # Placeholder for vector similarity search
            query_text = f"X:{X} Y:{Y} relation:{relation} context:{context}"
            vector_results = self.vector_store.similarity_search(query_text, top_k - len(result))
            result.extend(vector_results)
        
        # Cache and return result
        self.query_cache.put(cache_key, result)
        return result
    
    def prune(self, max_memories: Optional[int] = None) -> None:
        """
        Prune is now O(1) - ring buffer auto-manages capacity.
        This method is kept for API compatibility but does nothing.
        """
        # Ring buffer automatically handles pruning via overflow to vector store
        pass
    
    def generate_meta_memory(self) -> Optional[str]:
        """
        Generate meta-memory using pre-computed statistics - O(1) complexity.
        
        Returns:
            Generated meta-memory string or None if insufficient data
        """
        if self.total_active_memories < self.meta_memory_every:
            return None
        
        # Use pre-computed statistics for O(1) meta-memory generation
        insights = []
        
        # Most common context (already tracked)
        if self.most_common_context:
            context_percentage = (self.context_counts[self.most_common_context] / self.total_active_memories) * 100
            insights.append(f"Most actions occur in context: {self.most_common_context} ({context_percentage:.1f}%)")
        
        # Dominant relation type (already tracked)
        if self.most_common_relation:
            relation_percentage = (self.relation_counts[self.most_common_relation] / self.total_active_memories) * 100
            insights.append(f"Dominant relation type: '{self.most_common_relation}' ({relation_percentage:.1f}% of actions)")
        
        # Context diversity
        unique_contexts = len(self.context_counts)
        if unique_contexts > 2:
            insights.append(f"Agent operates across {unique_contexts} different contexts")
        
        # Memory utilization
        if self.buffer_full:
            insights.append(f"Memory buffer at capacity ({self.max_memories} active memories)")
        
        return " | ".join(insights) if insights else "Insufficient pattern data for meta-memory generation"
    
    def should_generate_meta(self) -> bool:
        """Check if meta-memory generation should be triggered - O(1)"""
        return self._entry_count > 0 and self._entry_count % self.meta_memory_every == 0
    
    def reset(self, hard: bool = False) -> None:
        """
        Clear memory system - O(1) complexity.
        
        Args:
            hard: If True, clear everything including meta-memories and vector store
        """
        # Reset ring buffer
        self.ring_buffer = [None] * self.max_memories
        self.current_position = 0
        self.buffer_full = False
        
        # Reset indexes
        self.x_index.clear()
        self.y_index.clear()
        self.relation_index.clear()
        self.context_index.clear()
        
        # Reset statistics
        self.context_counts.clear()
        self.relation_counts.clear()
        self.total_active_memories = 0
        self.most_common_context = None
        self.most_common_relation = None
        
        # Reset bloom filters
        self.x_bloom = SimpleBloomFilter()
        self.y_bloom = SimpleBloomFilter()
        self.context_bloom = SimpleBloomFilter()
        
        # Reset cache
        self.query_cache.invalidate()
        
        # Reset counters
        self._entry_count = 0
        self._next_memory_id = 0
        
        # Clear overflow buffer
        self.overflow_buffer.clear()
        
        if hard:
            self.meta_memories.clear()
            # TODO: Clear vector store if needed
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize the memory system to a dictionary"""
        # Only serialize non-None memories from ring buffer
        active_memories = [memory for memory in self.ring_buffer if memory is not None]
        
        return {
            'memories': [asdict(memory) for memory in active_memories],
            'meta_memories': self.meta_memories,
            'meta_memory_every': self.meta_memory_every,
            'meta_memory_prompt': self.meta_memory_prompt,
            'max_memories': self.max_memories,
            'entry_count': self._entry_count,
            'next_memory_id': self._next_memory_id,
            'overflow_batch_size': self.overflow_batch_size,
            'current_position': self.current_position,
            'buffer_full': self.buffer_full
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CLIN_X2YMemory':
        """Deserialize the memory system from a dictionary"""
        instance = cls(
            meta_memory_every=data.get('meta_memory_every', 100),
            meta_memory_prompt=data.get('meta_memory_prompt'),
            max_memories=data.get('max_memories', 1000),
            overflow_batch_size=data.get('overflow_batch_size', 50)
        )
        
        # Restore state
        instance._entry_count = data.get('entry_count', 0)
        instance._next_memory_id = data.get('next_memory_id', 0)
        instance.current_position = data.get('current_position', 0)
        instance.buffer_full = data.get('buffer_full', False)
        instance.meta_memories = data.get('meta_memories', [])
        
        # Restore memories to ring buffer and rebuild indexes
        for memory_data in data.get('memories', []):
            memory = MemoryEntry(**memory_data)
            # Find position based on memory_id and current_position
            # This is a simplified restoration - in practice, you might want
            # to store position information or reconstruct the ring buffer order
            pos = memory.memory_id % instance.max_memories
            instance.ring_buffer[pos] = memory
            instance._add_to_indexes(memory, pos)
        
        return instance
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the memory system - O(1) complexity"""
        return {
            "total_active_memories": self.total_active_memories,
            "total_memories_processed": self._entry_count,
            "meta_memories": len(self.meta_memories),
            "unique_contexts": len(self.context_counts),
            "most_common_context": self.most_common_context,
            "most_common_relation": self.most_common_relation,
            "relation_distribution": dict(self.relation_counts),
            "context_distribution": dict(self.context_counts),
            "memory_capacity": self.max_memories,
            "buffer_utilization": (self.total_active_memories / self.max_memories) * 100,
            "buffer_full": self.buffer_full,
            "overflow_buffer_size": len(self.overflow_buffer),
            "entries_until_next_meta": self.meta_memory_every - (self._entry_count % self.meta_memory_every),
            "cache_stats": {
                "cached_queries": len(self.query_cache.cache),
                "cache_capacity": self.query_cache.capacity
            }
        }


class LogMessagesKani(Kani):
    """
    Enhanced Kani class with optimized CLIN_X2YMemory integration.
    """
    
    def __init__(self, *args, **kwargs):
        # Extract memory-specific kwargs
        memory_kwargs = {}
        for key in ['meta_memory_every', 'meta_memory_prompt', 'max_memories', 'overflow_batch_size']:
            if key in kwargs:
                memory_kwargs[key] = kwargs.pop(key)
        
        super().__init__(*args, **kwargs)
        self.log_file = open("kani-log.jsonl", "w")
        
        # Initialize optimized CLIN memory system
        self.memory = CLIN_X2YMemory(**memory_kwargs)
    
    async def meta_memory(self):
        """Generate and return current meta-memory state"""
        if self.memory.meta_memories:
            return self.memory.meta_memories[-1]  # Return most recent meta-memory
        return None
    
    async def add_to_history(self, message, *args, **kwargs):
        """Enhanced history logging with memory integration"""
        await super().add_to_history(message, *args, **kwargs)
        self.log_file.write(message.model_dump_json())
        self.log_file.write("\n")
    
    def add_memory(self, X: str, relation: str, Y: str, context: str, metadata: Optional[Dict[str, Any]] = None):
        """Convenience method to add memories to the agent's memory system"""
        self.memory.add(X, relation, Y, context, metadata)
    
    def query_memory(self, **kwargs) -> List[MemoryEntry]:
        """Convenience method to query the agent's memory system"""
        return self.memory.query(**kwargs)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get current memory system statistics"""
        return self.memory.get_stats()
    