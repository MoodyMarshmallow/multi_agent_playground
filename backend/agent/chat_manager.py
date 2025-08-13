"""
Chat Manager for handling agent-to-agent chat requests and responses.
"""

from typing import Dict, List, Optional
from datetime import datetime
import uuid

from config.schema import ChatRequest


class ChatManager:
    """Manages chat requests and responses between agents"""
    
    def __init__(self):
        self.pending_requests: Dict[str, List[ChatRequest]] = {}  # recipient_id -> requests
        self.active_conversations: Dict[str, str] = {}  # agent_id -> conversation_id
        self.request_counter = 0
        
    def send_chat_request(self, sender_id: str, recipient_id: str, message: str) -> str:
        """
        Send a chat request from sender to recipient.
        Returns the request_id for tracking.
        """
        request_id = f"chat_req_{uuid.uuid4().hex[:8]}"
        
        chat_request = ChatRequest(
            request_id=request_id,
            sender_id=sender_id,
            recipient_id=recipient_id,
            message=message,
            timestamp=datetime.now().isoformat(),
            status="pending"
        )
        
        # Add to recipient's pending requests
        if recipient_id not in self.pending_requests:
            self.pending_requests[recipient_id] = []
            
        self.pending_requests[recipient_id].append(chat_request)
        
        return request_id
    
    def get_pending_requests(self, agent_id: str) -> List[ChatRequest]:
        """Get all pending chat requests for an agent"""
        return self.pending_requests.get(agent_id, [])
    
    def respond_to_request(self, agent_id: str, request_id: str, accepted: bool) -> Optional[ChatRequest]:
        """
        Agent responds to a chat request.
        Returns the request if found and updated, None otherwise.
        """
        agent_requests = self.pending_requests.get(agent_id, [])
        
        for request in agent_requests:
            if request.request_id == request_id:
                if accepted:
                    request.status = "accepted"
                    # Set up active conversation
                    conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
                    self.active_conversations[agent_id] = conversation_id
                    self.active_conversations[request.sender_id] = conversation_id
                else:
                    request.status = "rejected"
                
                # Remove from pending requests
                agent_requests.remove(request)
                if not agent_requests:
                    del self.pending_requests[agent_id]
                    
                return request
                
        return None
    
    def get_request_by_id(self, request_id: str) -> Optional[ChatRequest]:
        """Find a request by its ID across all pending requests"""
        for agent_requests in self.pending_requests.values():
            for request in agent_requests:
                if request.request_id == request_id:
                    return request
        return None
    
    def end_conversation(self, agent_id: str):
        """End active conversation for an agent"""
        if agent_id in self.active_conversations:
            conversation_id = self.active_conversations[agent_id]
            # Remove both participants from active conversations
            agents_to_remove = [
                aid for aid, cid in self.active_conversations.items() 
                if cid == conversation_id
            ]
            for aid in agents_to_remove:
                del self.active_conversations[aid]
    
    def is_in_conversation(self, agent_id: str) -> bool:
        """Check if agent is currently in an active conversation"""
        return agent_id in self.active_conversations
    
    def get_conversation_partner(self, agent_id: str) -> Optional[str]:
        """Get the conversation partner for an agent, if any"""
        if agent_id not in self.active_conversations:
            return None
            
        conversation_id = self.active_conversations[agent_id]
        for aid, cid in self.active_conversations.items():
            if cid == conversation_id and aid != agent_id:
                return aid
                
        return None
    
    def cleanup_expired_requests(self, max_age_minutes: int = 30):
        """Remove requests older than max_age_minutes"""
        current_time = datetime.now()
        
        for agent_id in list(self.pending_requests.keys()):
            requests = self.pending_requests[agent_id]
            valid_requests = []
            
            for request in requests:
                request_time = datetime.fromisoformat(request.timestamp)
                age_minutes = (current_time - request_time).total_seconds() / 60
                
                if age_minutes < max_age_minutes:
                    valid_requests.append(request)
                else:
                    request.status = "expired"
            
            if valid_requests:
                self.pending_requests[agent_id] = valid_requests
            else:
                del self.pending_requests[agent_id]