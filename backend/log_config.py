"""
Multi-Agent Playground - Logging Configuration
=============================================

This module provides comprehensive logging setup for the Multi-Agent Playground backend.
It includes:

1. **Centralized Logging Setup**: Configures root logger with file and console handlers
2. **Game Framework Integration**: Logs for text adventure games, game controller, agent manager
3. **Kani Library Integration**: Pretty-prints Kani LLM logs for better readability
4. **LRU LLM System Integration**: Logs for the optimized agent system
5. **Utility Functions**: Helper functions for logging game events, agent actions, etc.

Key Features:
- Debug logs go to debug.log file with detailed formatting
- Console shows only INFO and above for clean development experience
- Kani logs with long content are automatically pretty-printed
- Turn-based game system logging utilities
- Agent decision-making and action logging
- External library noise is filtered out

Usage:
    from backend.log_config import setup_logging, log_game_event, log_agent_decision
    
    # Set up logging (call once at startup)
    setup_logging()
    
    # Use utility functions for clean logging
    log_game_event("turn_start", {"agent": "alex_001", "turn": 42})
    log_agent_decision("alex_001", "go north", {"reasoning": "exploring"})
"""

import logging
import json
import pprint
from typing import Dict, Any, Optional, List
import re

def setup_logging(verbose: bool = False):
    """Set up comprehensive logging for the Multi-Agent Playground backend.
    
    Args:
        verbose: If True, console shows INFO+ messages. If False, only WARNING+ messages.
    """
    # Create formatters with clean spacing
    detailed_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s.%(funcName)s: %(message)s"
    )
    simple_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s"
    )
    
    # Create handlers
    # Debug file handler - captures ALL levels including DEBUG
    debug_file_handler = logging.FileHandler("debug.log")
    debug_file_handler.setLevel(logging.DEBUG)
    debug_file_handler.setFormatter(detailed_formatter)
    
    # Console handler - level depends on verbose flag
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO if verbose else logging.WARNING)
    console_handler.setFormatter(simple_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture everything
    root_logger.addHandler(debug_file_handler)
    root_logger.addHandler(console_handler)
    
    # Filter out external library noise (affects both console and debug.log)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    # Filter out kani library verbose logs
    logging.getLogger("kani.get_prompt").setLevel(logging.WARNING)
    
    # Configure backend module loggers
    logging.getLogger("backend.game_loop").setLevel(logging.INFO)
    logging.getLogger("backend.agent_manager").setLevel(logging.INFO)
    logging.getLogger("backend.infrastructure.game").setLevel(logging.INFO)
    logging.getLogger("backend.lru_llm").setLevel(logging.INFO)
    
    # Set up pretty-printing for Kani logs with long content
    _setup_kani_pretty_handlers()

def _setup_kani_pretty_handlers():
    """Set up custom handlers for pretty-printing Kani logs with long content."""
    
    # Handler for kani.messages logs (completion responses with long content)
    class KaniMessagesPrettyHandler(logging.Handler):
        def emit(self, record):
            msg = record.getMessage()
            # Only pretty-print if the message contains content with \n
            if 'content="' in msg and '\\n' in msg:
                match = re.search(r'role=(.*?) content="(.*?)"', msg)
                if match:
                    role = match.group(1)
                    content = match.group(2)
                    indented_content = "\n    ".join(content.split("\\n"))
                    indented_content = "    " + indented_content
                    # Create a new record with pretty content
                    pretty_record = logging.LogRecord(
                        name="kani.messages.pretty",
                        level=record.levelno,
                        pathname=record.pathname,
                        lineno=record.lineno,
                        msg=f"[KANI] role: {role}\ncontent:\n{indented_content}",
                        args=(),
                        exc_info=None
                    )
                    pretty_record.asctime = str(getattr(record, 'asctime', record.created))
                    # Let the root logger handle this record
                    logging.getLogger().handle(pretty_record)
                    return  # Don't let the original log through
            # For logs without \n, let them pass through normally
    
    # Handler for agent tool call messages (from KaniAgent loggers)
    class AgentToolCallPrettyHandler(logging.Handler):
        def emit(self, record):
            msg = record.getMessage()
            # Pretty-print tool call messages from agent code
            if 'Received message:' in msg and 'tool_calls=[' in msg and 'ToolCall(' in msg:
                # Extract the tool call information
                tool_call_match = re.search(r'tool_calls=\[(.*?)\]', msg)
                if tool_call_match:
                    tool_call_str = tool_call_match.group(1)
                    # Parse the tool call details
                    func_match = re.search(r"FunctionCall\(name='([^']+)', arguments='([^']+)'\)", tool_call_str)
                    if func_match:
                        func_name = func_match.group(1)
                        func_args = func_match.group(2)
                        try:
                            # Parse and pretty-print the arguments
                            args_dict = json.loads(func_args)
                            pretty_args = json.dumps(args_dict, indent=4, ensure_ascii=False)
                        except:
                            pretty_args = func_args
                        
                        # Create a new record with pretty content
                        pretty_record = logging.LogRecord(
                            name="agent.toolcall.pretty",
                            level=record.levelno,
                            pathname=record.pathname,
                            lineno=record.lineno,
                            msg=f"[AGENT TOOL CALL]\n  Function: {func_name}\n  Arguments:\n{pretty_args}",
                            args=(),
                            exc_info=None
                        )
                        pretty_record.asctime = str(getattr(record, 'asctime', record.created))
                        # Let the root logger handle this record
                        logging.getLogger().handle(pretty_record)
                        return  # Don't let the original log through
            # For logs without tool calls, let them pass through normally
    
    # Handler for kani tool call messages
    class KaniToolCallPrettyHandler(logging.Handler):
        def emit(self, record):
            msg = record.getMessage()
            # Pretty-print tool call messages
            if 'tool_calls=[' in msg and 'ToolCall(' in msg:
                # Extract the tool call information
                tool_call_match = re.search(r'tool_calls=\[(.*?)\]', msg)
                if tool_call_match:
                    tool_call_str = tool_call_match.group(1)
                    # Parse the tool call details
                    func_match = re.search(r"FunctionCall\(name='([^']+)', arguments='([^']+)'\)", tool_call_str)
                    if func_match:
                        func_name = func_match.group(1)
                        func_args = func_match.group(2)
                        try:
                            # Parse and pretty-print the arguments
                            args_dict = json.loads(func_args)
                            pretty_args = json.dumps(args_dict, indent=4, ensure_ascii=False)
                        except:
                            pretty_args = func_args
                        
                        # Create a new record with pretty content
                        pretty_record = logging.LogRecord(
                            name="kani.toolcall.pretty",
                            level=record.levelno,
                            pathname=record.pathname,
                            lineno=record.lineno,
                            msg=f"[KANI TOOL CALL]\n  Function: {func_name}\n  Arguments:\n{pretty_args}",
                            args=(),
                            exc_info=None
                        )
                        pretty_record.asctime = str(getattr(record, 'asctime', record.created))
                        # Let the root logger handle this record
                        logging.getLogger().handle(pretty_record)
                        return  # Don't let the original log through
            # For logs without tool calls, let them pass through normally
    
    # Configure kani.messages logger
    kani_messages_logger = logging.getLogger("kani.messages")
    kani_messages_logger.handlers = []
    kani_messages_logger.addHandler(KaniMessagesPrettyHandler())
    kani_messages_logger.propagate = False
    
    # Configure kani logger for tool calls
    kani_logger = logging.getLogger("kani")
    kani_logger.handlers = []
    kani_logger.addHandler(KaniToolCallPrettyHandler())
    kani_logger.propagate = False
    
    # Configure agent loggers for tool calls (covering both old and new systems)
    agent_logger = logging.getLogger("backend.agent_manager")
    agent_logger.handlers = []
    agent_logger.addHandler(AgentToolCallPrettyHandler())
    agent_logger.propagate = False

# ===== GAME SYSTEM LOGGING UTILITIES =====

def log_game_event(event_type: str, details: Dict[str, Any], game_id: Optional[str] = None):
    """Log game events like turn changes, game state changes, etc."""
    logger = logging.getLogger(__name__)
    prefix = f"[Game {game_id}] " if game_id else "[Game] "
    
    if event_type == "turn_start":
        agent = details.get('agent', 'unknown')
        turn = details.get('turn', 'unknown')
        logger.info(f"{prefix}Turn {turn}: Agent '{agent}' begins their turn")
    
    elif event_type == "turn_end":
        agent = details.get('agent', 'unknown')
        turn = details.get('turn', 'unknown')
        action = details.get('action', 'unknown')
        logger.info(f"{prefix}Turn {turn}: Agent '{agent}' completed action '{action}'")
    
    elif event_type == "game_start":
        logger.info(f"{prefix}Game started with {details.get('agent_count', 0)} agents")
    
    elif event_type == "game_end":
        reason = details.get('reason', 'unknown')
        total_turns = details.get('total_turns', 'unknown')
        logger.info(f"{prefix}Game ended after {total_turns} turns. Reason: {reason}")
    
    else:
        logger.info(f"{prefix}Event '{event_type}': {details}")

def log_agent_decision(agent_id: str, chosen_action: str, decision_context: Dict[str, Any]):
    """Log agent decision-making process with context"""
    logger = logging.getLogger(__name__)
    logger.info(f"[Agent {agent_id}] Decision: '{chosen_action}'")
    
    if decision_context.get('available_actions'):
        available = decision_context['available_actions']
        logger.debug(f"[Agent {agent_id}] Available actions: {available}")
    
    if decision_context.get('reasoning'):
        reasoning = decision_context['reasoning']
        logger.debug(f"[Agent {agent_id}] Reasoning: {reasoning}")
    
    if decision_context.get('world_state'):
        location = decision_context['world_state'].get('location', {}).get('name', 'unknown')
        logger.debug(f"[Agent {agent_id}] Current location: {location}")

def log_action_execution(agent_id: str, action: str, result: str, success: bool = True):
    """Log the execution of an action and its result"""
    logger = logging.getLogger(__name__)
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"[Agent {agent_id}] Action '{action}' {status}")
    logger.debug(f"[Agent {agent_id}] Action result: {result}")

def log_world_state_change(change_type: str, details: Dict[str, Any]):
    """Log changes to the world state"""
    logger = logging.getLogger(__name__)
    
    if change_type == "item_moved":
        item = details.get('item', 'unknown')
        from_loc = details.get('from_location', 'unknown')
        to_loc = details.get('to_location', 'unknown')
        logger.debug(f"[World] Item '{item}' moved: {from_loc} -> {to_loc}")
    
    elif change_type == "agent_moved":
        agent = details.get('agent', 'unknown')
        from_loc = details.get('from_location', 'unknown')
        to_loc = details.get('to_location', 'unknown')
        logger.debug(f"[World] Agent '{agent}' moved: {from_loc} -> {to_loc}")
    
    elif change_type == "object_state_change":
        obj = details.get('object', 'unknown')
        old_state = details.get('old_state', 'unknown')
        new_state = details.get('new_state', 'unknown')
        logger.debug(f"[World] Object '{obj}' state changed: {old_state} -> {new_state}")
    
    else:
        logger.debug(f"[World] {change_type}: {details}")

# ===== LEGACY COMPATIBILITY UTILITIES =====

def log_agent_action(agent_id: str, action_type: str, details: Dict[str, Any]):
    """Legacy compatibility - clean, readable logging for agent actions"""
    logger = logging.getLogger(__name__)
    logger.info(f"[Agent {agent_id}] Action: {action_type}")
    
    if action_type == "chat":
        message = details.get('message', '')
        receiver = details.get('receiver', 'unknown')
        logger.info(f"[Agent {agent_id}] Chat Details:\n  To: {receiver}\n  Message: '{message}'")
    elif action_type == "move":
        from_tile = details.get('from_tile', details.get('from_location', 'unknown'))
        to_tile = details.get('to_tile', details.get('to_location', 'unknown'))
        logger.info(f"[Agent {agent_id}] Move Details:\n  From: {from_tile}\n  To: {to_tile}")
    elif action_type == "interact":
        obj = details.get('object', 'unknown')
        current_state = details.get('current_state', 'unknown')
        new_state = details.get('new_state', 'unknown')
        logger.info(f"[Agent {agent_id}] Interact Details:\n  Object: {obj}\n  State Change: {current_state} -> {new_state}")
    elif action_type == "perceive":
        logger.info(f"[Agent {agent_id}] Perceive: looking around")

def log_perception(agent_id: str, perception: Dict[str, Any]):
    """Log perception data in readable format"""
    logger = logging.getLogger(__name__)
    logger.debug(f"[Agent {agent_id}] Perception:")
    
    if perception.get('visible_objects'):
        logger.debug("  Visible objects:\n%s", json.dumps(perception.get('visible_objects', {}), indent=4))
    if perception.get('visible_agents'):
        logger.debug("  Visible agents:\n    %s", "\n    ".join(perception.get('visible_agents', [])))
    if perception.get('current_tile'):
        logger.debug("  Current tile: %s", perception.get('current_tile'))
    if perception.get('heard_messages'):
        logger.debug("  Heard messages:\n%s", json.dumps(perception.get('heard_messages', []), indent=4))

def log_full_debug(obj: Any, context: str, agent_id: Optional[str] = None):
    """Full debug dump when needed"""
    logger = logging.getLogger(__name__)
    pp = pprint.PrettyPrinter(indent=2)
    
    prefix = f"[Agent {agent_id}] " if agent_id else ""
    logger.debug(f"{prefix}Full {context}:\n%s", pp.pformat(obj))

def log_conversation_flow(sender: str, receiver: str, message: str, conversation_id: str):
    """Log conversation flow in readable format"""
    logger = logging.getLogger(__name__)
    logger.info(f"[Chat] Flow Details:\n  From: {sender}\n  To: {receiver}\n  Message: '{message}'\n  Conversation ID: {conversation_id[:8]}")

def log_queue_status(queue_size: int, operation: str):
    """Log message queue status"""
    logger = logging.getLogger(__name__)
    logger.debug(f"[Queue] Status:\n  Operation: {operation}\n  Size: {queue_size} messages")

def log_salience_evaluation(agent_id: str, event: str, salience: int):
    """Log salience evaluation results in a clean format"""
    logger = logging.getLogger(__name__)
    logger.debug(f"[Salience] Evaluation:\n  Agent: {agent_id}\n  Event: '{event}'\n  Score: {salience}/10")