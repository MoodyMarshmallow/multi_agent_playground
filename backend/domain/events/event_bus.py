"""
EventBus Interface - Domain Layer
=================================
Defines the abstract interface for the event bus system.
This interface is implemented by infrastructure layer components.
"""

from abc import ABC, abstractmethod
from typing import List, Callable, Optional, Any, Dict
from .domain_event import DomainEvent


class EventBus(ABC):
    """
    Abstract interface for the event bus system.
    
    The event bus handles publishing, subscribing, and querying domain events
    throughout the simulation system. This interface ensures the domain layer
    has no dependencies on infrastructure implementations.
    """
    
    @abstractmethod
    async def start(self) -> None:
        """Start the event bus (initialize background processing if needed)."""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop the event bus (cleanup background processing if needed)."""
        pass
    
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """
        Publish a domain event to the event bus.
        
        Args:
            event: The domain event to publish
        """
        pass
    
    @abstractmethod
    async def subscribe(self, event_type: str, handler: Callable[[DomainEvent], None]) -> None:
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: The type of events to subscribe to
            handler: Callable that will be invoked when events of this type are published
        """
        pass
    
    @abstractmethod
    async def unsubscribe(self, event_type: str, handler: Callable[[DomainEvent], None]) -> None:
        """
        Unsubscribe from events of a specific type.
        
        Args:
            event_type: The type of events to unsubscribe from
            handler: The handler to remove from subscriptions
        """
        pass
    
    @abstractmethod
    async def get_events_since(self, timestamp: str, event_type: Optional[str] = None) -> List[DomainEvent]:
        """
        Get all events that occurred after the specified timestamp.
        
        Args:
            timestamp: ISO timestamp string to get events after
            event_type: Optional filter for specific event types
            
        Returns:
            List of domain events that occurred after the timestamp
        """
        pass
    
    @abstractmethod
    async def get_unserved_events(self, consumer_id: str = "frontend") -> List[DomainEvent]:
        """
        Get events that have not been served to the specified consumer.
        
        This is primarily used by the frontend polling mechanism to get
        new events that haven't been delivered yet.
        
        Args:
            consumer_id: Identifier for the consumer requesting events
            
        Returns:
            List of unserved domain events for this consumer
        """
        pass
    
    @abstractmethod
    async def mark_events_served(self, event_ids: List[str], consumer_id: str = "frontend") -> None:
        """
        Mark events as served for a specific consumer.
        
        Args:
            event_ids: List of event IDs that have been served
            consumer_id: Identifier for the consumer that received the events
        """
        pass
    
    @abstractmethod
    async def get_event_count(self, event_type: Optional[str] = None) -> int:
        """
        Get the total number of events in the bus.
        
        Args:
            event_type: Optional filter for specific event types
            
        Returns:
            Count of events matching the criteria
        """
        pass
    
    @abstractmethod
    async def clear_events(self, event_type: Optional[str] = None) -> None:
        """
        Clear events from the bus (used for reset operations).
        
        Args:
            event_type: Optional filter to only clear specific event types
        """
        pass


class EventSubscription:
    """
    Represents an event subscription for management purposes.
    """
    
    def __init__(self, event_type: str, handler: Callable[[DomainEvent], None], subscriber_id: str):
        self.event_type = event_type
        self.handler = handler
        self.subscriber_id = subscriber_id
    
    def __eq__(self, other):
        if not isinstance(other, EventSubscription):
            return False
        return (self.event_type == other.event_type and 
                self.handler == other.handler and 
                self.subscriber_id == other.subscriber_id)
    
    def __hash__(self):
        return hash((self.event_type, id(self.handler), self.subscriber_id))