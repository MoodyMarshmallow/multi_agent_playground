import logging
import json
import pprint
from typing import Dict, Any, Optional

def setup_logging():
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
    logging.getLogger("kani.messages.get_model_completion").setLevel(logging.WARNING)
    logging.getLogger("kani.do_function_call").setLevel(logging.WARNING)

def log_agent_action(agent_id: str, action_type: str, details: Dict[str, Any]):
    """Clean, readable logging for agent actions"""
    logger = logging.getLogger(__name__)
    logger.info(f"[Agent {agent_id}] Action: {action_type}")
    
    if action_type == "chat":
        message = details.get('message', '')
        receiver = details.get('receiver', 'unknown')
        logger.info(f"[Agent {agent_id}] Chat Details:\n  To: {receiver}\n  Message: '{message[:50]}{'...' if len(message) > 50 else ''}'")
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

def log_tool_call(agent_id: str, tool_call: Any):
    """Log tool calls in readable format"""
    logger = logging.getLogger(__name__)
    
    try:
        args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
        logger.debug(f"[Agent {agent_id}] Tool Call:\n  Name: {tool_call.function.name}\n  Arguments:\n%s", json.dumps(args, indent=4))
    except Exception as e:
        logger.debug(f"[Agent {agent_id}] Tool Call:\n  Name: {tool_call.function.name}\n  Error parsing args: {e}")

def log_full_debug(obj: Any, context: str, agent_id: Optional[str] = None):
    """Full debug dump when needed"""
    logger = logging.getLogger(__name__)
    pp = pprint.PrettyPrinter(indent=2)
    
    prefix = f"[Agent {agent_id}] " if agent_id else ""
    logger.debug(f"{prefix}Full {context}:\n%s", pp.pformat(obj))

def log_conversation_flow(sender: str, receiver: str, message: str, conversation_id: str):
    """Log conversation flow in readable format"""
    logger = logging.getLogger(__name__)
    logger.info(f"[Chat] Flow Details:\n  From: {sender}\n  To: {receiver}\n  Message: '{message[:50]}{'...' if len(message) > 50 else ''}'\n  Conversation ID: {conversation_id[:8]}")

def log_queue_status(queue_size: int, operation: str):
    """Log message queue status"""
    logger = logging.getLogger(__name__)
    logger.debug(f"[Queue] Status:\n  Operation: {operation}\n  Size: {queue_size} messages")

def log_salience_evaluation(agent_id: str, event: str, salience: int):
    """Log salience evaluation results in a clean format"""
    logger = logging.getLogger(__name__)
    logger.debug(f"[Salience] Evaluation:\n  Agent: {agent_id}\n  Event: '{event[:80]}{'...' if len(event) > 80 else ''}'\n  Score: {salience}/10") 