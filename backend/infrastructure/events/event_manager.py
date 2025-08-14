"""
Event generation and queuing system.
"""

from typing import Dict, List, Any


class EventManager:
    """
    Manages event generation and queuing for frontend consumption.
    """
    
    def __init__(self, game):
        self.game = game
        self.event_queue: List[Dict[str, Any]] = []
        self.event_id_counter = 0
    
    def add_event(self, event_type: str, data: Dict[str, Any]):
        """
        Add an event to the queue for frontend consumption.     
        Args:
            event_type: Type of event (e.g., 'move', 'get', 'drop')
            data: Event-specific data
        """
        self.event_id_counter += 1
        event = {
            'id': self.event_id_counter,
            'type': event_type,
            'timestamp': self.event_id_counter,  # Simple turn counter
            'data': data
        }
        self.event_queue.append(event)

    def get_events_since(self, last_event_id: int) -> List[Dict[str, Any]]:
        """
        Get all events after the given ID.
        
        Args:
            last_event_id: ID of last processed event
            
        Returns:
            List of new events
        """
        return [e for e in self.event_queue if e['id'] > last_event_id]
    
    def clear_events(self):
        """Clear all events from the queue."""
        self.event_queue.clear()
        self.event_id_counter = 0