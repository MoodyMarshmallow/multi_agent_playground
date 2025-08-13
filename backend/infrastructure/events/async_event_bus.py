"""
AsyncEventBus - Infrastructure Implementation
============================================
Asynchronous implementation of the EventBus interface using asyncio.
This provides the concrete event bus functionality for the simulation system.
"""

import asyncio
import logging
from typing import List, Dict, Callable, Optional, Set, DefaultDict
from datetime import datetime
from collections import defaultdict

from ...domain.events.event_bus import EventBus, EventSubscription
from ...domain.events.domain_event import DomainEvent

logger = logging.getLogger(__name__)


class AsyncEventBus(EventBus):
    """
    Asynchronous implementation of the EventBus interface.
    
    This implementation uses asyncio for non-blocking event publishing
    and maintains in-memory storage for events and subscriptions.
    """
    
    def __init__(self):
        # Event storage
        self._events: List[DomainEvent] = []
        self._event_queue: asyncio.Queue = asyncio.Queue()
        
        # Subscription management
        self._subscriptions: DefaultDict[str, List[Callable]] = defaultdict(list)
        
        # Consumer tracking for unserved events
        self._served_events: DefaultDict[str, Set[str]] = defaultdict(set)  # consumer_id -> set of event_ids
        
        # Background processing
        self._processing_task: Optional[asyncio.Task] = None
        self._running = False
        
        logger.info("AsyncEventBus initialized")
    
    async def start(self):
        """Start the background event processing."""
        if not self._running:
            self._running = True
            self._processing_task = asyncio.create_task(self._process_events())
            logger.info("AsyncEventBus started")
    
    async def stop(self):
        """Stop the background event processing."""
        if self._running:
            self._running = False
            if self._processing_task:
                self._processing_task.cancel()
                try:
                    await self._processing_task
                except asyncio.CancelledError:
                    pass
            logger.info("AsyncEventBus stopped")
    
    async def publish(self, event: DomainEvent) -> None:
        """Publish a domain event to the event bus."""
        # Add to queue for processing
        await self._event_queue.put(event)
        logger.debug(f"Event published: {event.event_type} ({event.event_id})")
    
    async def subscribe(self, event_type: str, handler: Callable[[DomainEvent], None]) -> None:
        """Subscribe to events of a specific type."""
        self._subscriptions[event_type].append(handler)
        logger.debug(f"Subscribed to event type: {event_type}")
    
    async def unsubscribe(self, event_type: str, handler: Callable[[DomainEvent], None]) -> None:
        """Unsubscribe from events of a specific type."""
        if handler in self._subscriptions[event_type]:
            self._subscriptions[event_type].remove(handler)
            logger.debug(f"Unsubscribed from event type: {event_type}")
    
    async def get_events_since(self, timestamp: str, event_type: Optional[str] = None) -> List[DomainEvent]:
        """Get all events that occurred after the specified timestamp."""
        try:
            target_time = datetime.fromisoformat(timestamp)
        except ValueError:
            logger.warning(f"Invalid timestamp format: {timestamp}")
            return []
        
        filtered_events = []
        for event in self._events:
            try:
                event_time = datetime.fromisoformat(event.timestamp)
                if event_time > target_time:
                    if event_type is None or event.event_type == event_type:
                        filtered_events.append(event)
            except ValueError:
                logger.warning(f"Event has invalid timestamp: {event.timestamp}")
                continue
        
        return filtered_events
    
    async def get_unserved_events(self, consumer_id: str = "frontend") -> List[DomainEvent]:
        """Get events that have not been served to the specified consumer."""
        served_for_consumer = self._served_events[consumer_id]
        unserved_events = [
            event for event in self._events 
            if event.event_id not in served_for_consumer
        ]
        
        logger.debug(f"Found {len(unserved_events)} unserved events for consumer: {consumer_id}")
        return unserved_events
    
    async def mark_events_served(self, event_ids: List[str], consumer_id: str = "frontend") -> None:
        """Mark events as served for a specific consumer."""
        self._served_events[consumer_id].update(event_ids)
        logger.debug(f"Marked {len(event_ids)} events as served for consumer: {consumer_id}")
    
    async def get_event_count(self, event_type: Optional[str] = None) -> int:
        """Get the total number of events in the bus."""
        if event_type is None:
            return len(self._events)
        
        return sum(1 for event in self._events if event.event_type == event_type)
    
    async def clear_events(self, event_type: Optional[str] = None) -> None:
        """Clear events from the bus (used for reset operations)."""
        if event_type is None:
            self._events.clear()
            self._served_events.clear()
            logger.info("All events cleared from event bus")
        else:
            # Remove events of specific type
            original_count = len(self._events)
            self._events = [event for event in self._events if event.event_type != event_type]
            
            # Clear served tracking for removed events
            for consumer_served in self._served_events.values():
                # We can't easily identify which event_ids correspond to the removed event_type
                # For now, we'll clear all served tracking when clearing specific types
                consumer_served.clear()
            
            removed_count = original_count - len(self._events)
            logger.info(f"Cleared {removed_count} events of type '{event_type}' from event bus")
    
    async def _process_events(self):
        """Background task to process events from the queue."""
        logger.info("Event processing started")
        
        while self._running:
            try:
                # Wait for an event with timeout to allow shutdown
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                
                # Store the event
                self._events.append(event)
                
                # Notify subscribers
                await self._notify_subscribers(event)
                
                # Mark task done
                self._event_queue.task_done()
                
            except asyncio.TimeoutError:
                # Normal timeout, continue loop
                continue
            except asyncio.CancelledError:
                logger.info("Event processing cancelled")
                break
            except Exception as e:
                logger.error(f"Error processing event: {e}")
                continue
        
        logger.info("Event processing stopped")
    
    async def _notify_subscribers(self, event: DomainEvent):
        """Notify all subscribers for this event type."""
        handlers = self._subscriptions.get(event.event_type, [])
        
        if handlers:
            logger.debug(f"Notifying {len(handlers)} subscribers for event type: {event.event_type}")
            
            # Call all handlers (they should be non-blocking)
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler for {event.event_type}: {e}")
    
    # Additional utility methods for debugging/monitoring
    
    def get_subscription_count(self) -> Dict[str, int]:
        """Get subscription counts by event type."""
        return {event_type: len(handlers) for event_type, handlers in self._subscriptions.items()}
    
    def get_consumer_status(self) -> Dict[str, Dict[str, int]]:
        """Get status information for all consumers."""
        status = {}
        for consumer_id, served_events in self._served_events.items():
            total_events = len(self._events)
            served_count = len(served_events)
            unserved_count = total_events - served_count
            
            status[consumer_id] = {
                'total_events': total_events,
                'served_events': served_count,
                'unserved_events': unserved_count
            }
        
        return status