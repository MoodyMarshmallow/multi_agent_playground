# Chat Function Implementation Plan

## Overview

This document outlines the implementation plan for adding a chat function to the multi-agent simulation framework. The chat system will allow agents to send chat requests to other agents, with accept/reject functionality and message replies, all integrated with the existing turn-based architecture.

## Requirements Summary

1. **Chat Discovery**: When using 'look' action, agents can see who is in the room and have the option of chatting to them
2. **Chat Request**: Agents can send a CHAT REQUEST to another agent with a message explaining why they want to talk
3. **Chat Notification**: When the receiving agent's turn arrives, they are notified of pending chat requests
4. **Chat Response**: The receiving agent can accept or reject the chat request (this action does not end their turn)
5. **Chat Message**: If accepted, the agent can send a SINGLE message reply (this action ends their turn)
6. **Frontend Integration**: All chat messages are queued for display on the frontend via the existing schema system

## Current Architecture Analysis

### Key Components
- **Schema System**: Pydantic models in `backend/config/schema.py` with discriminated unions
- **Action System**: Generic actions in `backend/text_adventure_games/actions/generic.py`
- **Agent Management**: Turn-based execution via `backend/agent/manager.py`
- **Frontend Communication**: Event queue system through `AgentActionOutput` schema
- **LLM Integration**: Kani framework with function calling via `submit_command()`

### Existing Chat Infrastructure
- `ChatAction` schema already exists and will be used for frontend communication
- `Message` schema exists for chat data structures
- `AgentPerception` includes `chatable_agents` field
- Look action shows visible characters

## Implementation Plan

### Phase 1: Schema and Data Structure Updates

#### 1.1 Update Schema Definitions (`backend/config/schema.py`)

**Add internal action types for agent processing (not exposed to frontend):**
```python
class ChatRequestAction(BaseModel):
    """Internal: Send a chat request to another agent"""
    action_type: Literal["chat_request"]
    recipient: str
    message: str  # Explanation of why agent wants to chat

class ChatResponseAction(BaseModel):
    """Internal: Accept or reject a chat request"""
    action_type: Literal["chat_response"]
    request_id: str
    accepted: bool  # True for accept, False for reject
    response_message: Optional[str] = None  # Optional response message
```

**Update HouseAction union to include existing ChatAction:**
```python
HouseAction = Annotated[
    Union[
        # ... existing actions ...
        ChatAction,  # Use existing ChatAction for actual messages
        ChatRequestAction,  # Internal processing only
        ChatResponseAction,  # Internal processing only
        # ... rest of actions ...
    ],
    Field(discriminator="action_type")
]
```

**Frontend Communication Strategy:**
- Only `ChatAction` instances are added to the event queue for frontend
- Chat requests and responses are processed internally and converted to appropriate `ChatAction` events
- The frontend will receive clean chat messages via the existing `ChatAction` schema

**Add chat request data structure:**
```python
class ChatRequest(BaseModel):
    request_id: str
    sender_id: str
    recipient_id: str
    message: str
    timestamp: str
    status: Literal["pending", "accepted", "rejected", "expired"]
```

#### 1.2 Chat Manager (`backend/agent/chat_manager.py`)

**Create new ChatManager class:**
```python
class ChatManager:
    def __init__(self):
        self.pending_requests: Dict[str, List[ChatRequest]] = {}
        self.active_conversations: Dict[str, str] = {}  # agent_id -> conversation_id
        self.request_counter = 0
        
    def send_chat_request(self, sender_id: str, recipient_id: str, message: str) -> str:
        """Send a chat request and return request_id"""
        
    def get_pending_requests(self, agent_id: str) -> List[ChatRequest]:
        """Get all pending chat requests for an agent"""
        
    def process_chat_response(self, agent_id: str, request_id: str, accepted: bool) -> Optional[ChatRequest]:
        """Process accept/reject response"""
        
    def can_chat(self, sender_id: str, recipient_id: str, game) -> bool:
        """Check if two agents can chat (same room, both exist)"""
        
    def cleanup_expired_requests(self):
        """Remove old pending requests"""
```

### Phase 2: Agent Integration

#### 2.1 Update Agent Manager (`backend/agent/manager.py`)

**Integrate ChatManager:**
```python
class AgentManager:
    def __init__(self, game: Game):
        # ... existing code ...
        self.chat_manager = ChatManager()
        
    async def execute_agent_turn(self, agent: Character) -> tuple[Optional[AgentActionOutput], bool]:
        # ... existing code ...
        
        # Check for pending chat requests
        pending_requests = self.chat_manager.get_pending_requests(agent.name)
        if pending_requests:
            # Include chat notifications in previous_result
            previous_result += self._format_chat_notifications(pending_requests)
        
        # ... rest of method ...
        
    def _format_chat_notifications(self, requests: List[ChatRequest]) -> str:
        """Format chat requests for agent feedback"""
```

#### 2.2 Update Action Result Processing

**Modify action result feedback to include chat context:**
- Include pending chat requests in agent's turn feedback
- Format chat notifications clearly for LLM understanding
- Handle chat responses and message routing

### Phase 3: Action Implementation

#### 3.1 Chat Request Action (`backend/text_adventure_games/actions/generic.py`)

**Add ChatRequestAction implementation:**
```python
class GenericChatRequestAction(Action):
    ACTION_NAME = "chat_request"
    ACTION_DESCRIPTION = "Send a chat request to another agent"
    
    def check_preconditions(self) -> bool:
        # Verify recipient exists and is in same room
        # Check no pending request already exists
        
    def apply_effects(self):
        # Add request to chat manager
        # NO ChatAction event sent to frontend (internal only)
        # Return success message to requesting agent
```

#### 3.2 Chat Response Action

**Add ChatResponseAction implementation:**
```python
class GenericChatResponseAction(Action):
    ACTION_NAME = "chat_response"
    ACTION_DESCRIPTION = "Accept or reject a chat request"
    ends_turn = False  # This action does not end the turn
    
    def check_preconditions(self) -> bool:
        # Verify request exists and is pending
        
    def apply_effects(self):
        # Process accept/reject through chat manager
        # If accepted, enable follow-up chat message
        # NO ChatAction event sent to frontend (internal only)
        # Return success message to responding agent
```

#### 3.3 Chat Message Action (Uses existing ChatAction)

**Add GenericChatAction implementation:**
```python
class GenericChatAction(Action):
    ACTION_NAME = "chat"
    ACTION_DESCRIPTION = "Send a chat message"
    ends_turn = True  # This action ends the turn
    
    def check_preconditions(self) -> bool:
        # Verify recipient exists and is in same room
        # Verify conversation is active (request was accepted)
        
    def apply_effects(self):
        # Send message via ChatAction schema
        # CREATE ChatAction event for frontend display
        # Close conversation after message sent
        # Return success message
```

### Phase 4: Enhanced Look Action

#### 4.1 Update Look Action (`backend/text_adventure_games/actions/generic.py`)

**Modify `EnhancedLookAction._format_world_state()`:**
```python
def _format_world_state(self, state: dict) -> str:
    # ... existing code ...
    
    # Other characters (enhanced with chat info)
    visible_characters = state.get('visible_characters', [])
    if visible_characters:
        lines.append("\nOther characters here (you can send chat requests to them):")
        for char in visible_characters:
            lines.append(f"  - {char.get('name', 'character')}: {char.get('description', 'a character')}")
    
    # ... rest of method ...
```

#### 4.2 Update World State Building

**Modify world state manager to include chat-relevant information:**
- Mark which characters are available for chat
- Include any active conversation status

### Phase 5: LLM Integration

#### 5.1 Update Agent Function Calling

**Ensure new chat actions work with existing `submit_command()` function:**
- `"chat request [recipient] [message]"` - Send chat request
- `"accept chat [request_id]"` or `"reject chat [request_id]"` - Respond to request  
- `"chat message [recipient] [message]"` - Send chat message

#### 5.2 Agent Prompt Updates

**Update system prompts to include chat instructions:**
```python
system_prompt += """

CHAT SYSTEM:
- Use 'look' to see other characters you can chat with
- Send chat requests: "chat request [name] [reason]"
- Respond to requests: "accept chat [id]" or "reject chat [id]" 
- Send messages: "chat message [name] [message]"
- Chat responses don't end your turn, but messages do
"""
```

### Phase 6: Frontend Integration

#### 6.1 Event Queue Integration

**Frontend receives only ChatAction events:**
- Only actual chat messages generate `ChatAction` events for the frontend
- Chat requests and responses are processed internally without frontend events
- Frontend polls `/agent_act/next` for `ChatAction` events only
- Chat messages display in frontend chat interface using existing `ChatAction` schema

#### 6.2 Chat Action Schema Export

**Simplified schema export:**
- Only `ChatAction` instances are added to the event queue
- Chat requests/responses are converted to action results for agents
- Maintain backward compatibility with existing `ChatAction` handling
- Frontend receives clean, displayable chat messages only

## Implementation Details

### Turn Flow Example

1. **Agent A's Turn**: 
   - Receives: "Welcome to the game! This is your first turn."
   - Executes: `look` 
   - Sees: "Other characters here: Agent B (you can send chat requests to them)"
   - Executes: `chat request Agent B I want to discuss the weather`
   - Result: "Chat request sent to Agent B" (NO frontend event)

2. **Agent B's Turn**:
   - Receives: "You have a chat request from Agent A: 'I want to discuss the weather' (ID: req_001)"
   - Executes: `accept chat req_001` (turn continues, NO frontend event)
   - Result: "Chat request accepted. You can now send a message."
   - Executes: `chat Agent A The weather is lovely today!` (turn ends)
   - Result: Creates `ChatAction` event for frontend display

3. **Agent A's Next Turn**:
   - Receives: "Agent B accepted your chat request and sent: 'The weather is lovely today!'"

### Data Flow

```
Agent A -> ChatRequestAction -> ChatManager (internal) -> No frontend event
Agent B -> ChatResponseAction -> ChatManager (internal) -> No frontend event  
Agent B -> ChatAction -> Frontend event queue -> Display message
```

### Frontend Event Strategy

**Only ChatAction events reach the frontend:**
- Chat requests: Internal processing only, no frontend visibility
- Chat responses: Internal processing only, no frontend visibility
- Chat messages: Generate `ChatAction` events for frontend display
- This keeps the frontend simple and focused on displayable messages

### Error Handling

- **Invalid recipient**: Return error message to requesting agent
- **Not in same room**: Reject chat request with appropriate message
- **Expired requests**: Clean up automatically, notify sender
- **Invalid request ID**: Handle gracefully in chat responses

### Security Considerations

- Validate all agent IDs exist and are active
- Prevent spam by limiting requests per agent per turn
- Clean up expired requests to prevent memory leaks
- Validate room proximity for all chat actions

## Testing Plan

### Unit Tests
- Test ChatManager request/response cycle
- Test chat action preconditions and effects
- Test schema validation for all chat action types

### Integration Tests
- Test complete chat flow between two agents
- Test chat notifications in agent feedback
- Test frontend event generation
- Test error handling and edge cases

### Agent Goal Tests
- Create goal-based tests for social interaction
- Test agent decision-making around chat acceptance
- Verify agents can accomplish goals through chat

## Rollout Strategy

### Phase 1: Infrastructure (No User Impact)
- Implement schema updates and ChatManager
- Deploy without enabling chat actions
- Test infrastructure with unit tests

### Phase 2: Basic Chat (Limited Testing)
- Enable chat request/response actions
- Test with manual agents first
- Validate event queue integration

### Phase 3: Full Chat (Beta)
- Enable chat messages and full flow
- Test with AI agents
- Monitor for any performance issues

### Phase 4: Production Release
- Full deployment with monitoring
- Documentation updates
- Performance optimization if needed

## Future Enhancements

### Short Term
- Chat history persistence
- Multi-turn conversations
- Group chat support

### Long Term  
- Private messaging (agents not in same room)
- Chat commands and formatting
- Chat-based collaborative goals
- Agent reputation system based on chat interactions

## Risk Mitigation

### Performance Risks
- **Memory usage**: Implement request cleanup and limits
- **Event queue growth**: Monitor queue size and implement cleanup
- **LLM token usage**: Optimize chat notification formatting

### Functional Risks
- **Chat spam**: Limit requests per agent per time period
- **Infinite loops**: Prevent agents from endless chat cycles
- **Turn deadlock**: Ensure chat responses don't break turn progression

### Integration Risks
- **Schema breaking changes**: Maintain backward compatibility
- **Frontend compatibility**: Test all chat events display correctly
- **Agent confusion**: Clear prompts and error messages for LLMs

## Success Metrics

- Agents successfully discover and initiate chat
- Chat request acceptance rate > 50%
- No performance degradation in turn processing
- Frontend correctly displays all chat events
- Zero chat-related crashes or errors in production

---

This implementation plan provides a comprehensive roadmap for adding robust chat functionality to the multi-agent simulation framework while maintaining compatibility with existing systems and ensuring reliable operation.