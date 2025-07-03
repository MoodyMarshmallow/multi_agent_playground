"""
Multi-Agent Playground - Logging Configuration
=============================================

This module provides comprehensive logging setup for the Multi-Agent Playground backend.
It includes:

1. **Centralized Logging Setup**: Configures root logger with file and console handlers
2. **Kani Library Integration**: Pretty-prints Kani LLM logs for better readability
3. **Utility Functions**: Helper functions for logging agent actions, perceptions, etc.

Key Features:
- Debug logs go to debug.log file with detailed formatting
- Console shows only INFO and above for clean development experience
- Kani logs with long content are automatically pretty-printed
- External library noise is filtered out
- Comprehensive utility functions for agent-specific logging

Usage:
    from backend.logging import setup_logging, log_agent_action
    
    # Set up logging (call once at startup)
    setup_logging()
    
    # Use utility functions for clean logging
    log_agent_action("agent_001", "move", {"from": [1,1], "to": [2,2]})
"""

import logging
import json
import pprint
from typing import Dict, Any, Optional
import re

def setup_logging():
    """Set up comprehensive logging for the Multi-Agent Playground backend."""
    # Create formatters with better spacing
    detailed_formatter = logging.Formatter(
        "\n%(asctime)s [%(levelname)s] %(name)s.%(funcName)s:\n%(message)s\n"
    )
    simple_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s"
    )
    
    # Create handlers
    # Debug file handler - captures ALL levels including DEBUG
    debug_file_handler = logging.FileHandler("debug.log")
    debug_file_handler.setLevel(logging.DEBUG)
    debug_file_handler.setFormatter(detailed_formatter)
    
    # Console handler - only shows INFO and above (no DEBUG noise)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
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
                    pretty_record.asctime = getattr(record, 'asctime', record.created)
                    # Let the root logger handle this record
                    logging.getLogger().handle(pretty_record)
                    return  # Don't let the original log through
            # For logs without \n, let them pass through normally
    
    # Handler for agent tool call messages (from character_agent loggers)
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
                        pretty_record.asctime = getattr(record, 'asctime', record.created)
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
                        pretty_record.asctime = getattr(record, 'asctime', record.created)
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
    
    # Configure character_agent loggers for tool calls
    character_agent_logger = logging.getLogger("character_agent")
    character_agent_logger.handlers = []
    character_agent_logger.addHandler(AgentToolCallPrettyHandler())
    character_agent_logger.propagate = False

def log_agent_action(agent_id: str, action_type: str, details: Dict[str, Any]):
    """Clean, readable logging for agent actions"""
    logger = logging.getLogger(__name__)
    logger.info(f"[Agent {agent_id}] Action: {action_type}")
    
    if action_type == "chat":
        message = details.get('message', '')
        receiver = details.get('receiver', 'unknown')
        logger.info(f"[Agent {agent_id}] Chat Details:\n  To: {receiver}\n  Message: '{message}'")
    elif action_type == "move":
        from_tile = details.get('from_tile', 'unknown')
        to_tile = details.get('to_tile', 'unknown')
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