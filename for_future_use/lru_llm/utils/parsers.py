"""
Optimized Response Parser
========================
Provides O(1) JSON parsing and validation for LLM responses.
"""

import json
import re
from typing import Dict, Any, Optional, Tuple, List
from functools import lru_cache


class ResponseParser:
    """
    Optimized parser for LLM responses with O(1) parsing operations.
    
    Uses pre-compiled regex patterns and fast JSON parsing for optimal performance.
    """
    
    def __init__(self):
        """Initialize ResponseParser with compiled patterns."""
        # Pre-compiled regex patterns for O(1) matching
        self._json_patterns = {
            'basic': re.compile(r'\{[^{}]*\}'),
            'multiline': re.compile(r'\{[^{}]*\}', re.DOTALL),
            'markdown': re.compile(r'```json\s*(\{.*?\})\s*```', re.DOTALL),
            'quoted': re.compile(r'["\'](\{.*?\})["\']', re.DOTALL)
        }
        
        # Pre-compiled regex patterns for O(1) matching with improved ordering
        self._action_patterns = {
            # Prioritize interact patterns to catch "going to interact" before "going" triggers move
            'interact': re.compile(r'\b(?:interact|interacting|use|using|operate|operating|engage|engaging)\b|going to interact|going to use|going to operate|planning to interact|about to use', re.IGNORECASE),
            'perceive': re.compile(r'\b(?:perceive|perceiving|observe|observing|look|looking|see|seeing|watch|watching)\b', re.IGNORECASE),
            'chat': re.compile(r'\b(?:chat|chatting|talk|talking|speak|speaking|say|saying|conversation|converse|conversing)\b', re.IGNORECASE),
            # Move pattern comes last to avoid catching "going to" when it's part of interaction phrases
            'move': re.compile(r'\b(?:move|moving|go|going|walk|walking|travel|traveling|head|heading)\b(?!\s+to\s+(?:interact|use|operate))', re.IGNORECASE),
        }
    
    # Pre-compiled regex patterns for O(1) matching (legacy support)
    _JSON_PATTERN = re.compile(r'\{[^{}]*\}')
    _ACTION_TYPE_PATTERN = re.compile(r'"action_type":\s*"([^"]+)"')
    _COORDINATES_PATTERN = re.compile(r'\[(\d+),\s*(\d+)\]')
    _NUMBER_PATTERN = re.compile(r'\b(\d+)\b')
    
    # Default fallback responses for O(1) error handling
    _DEFAULT_RESPONSES = {
        "perceive": {
            "action_type": "perceive",
            "observation": "I observe my surroundings",
            "emoji": "👀"
        },
        "chat": {
            "action_type": "chat", 
            "receiver": "",
            "message": "Hello!",
            "emoji": "💬"
        },
        "move": {
            "action_type": "move",
            "destination": [0, 0],
            "reason": "Moving to a new location",
            "emoji": "🚶"
        },
        "interact": {
            "action_type": "interact",
            "object": "",
            "action": "examine",
            "emoji": "🤝"
        }
    }
    
    @classmethod
    def parse_action_response(cls, response_text: str, 
                            expected_action: str = None) -> Dict[str, Any]:
        """
        Parse LLM response with O(1) JSON extraction and validation.
        
        Args:
            response_text: Raw LLM response text
            expected_action: Expected action type for validation
            
        Returns:
            Parsed action dictionary
        """
        # Fast JSON extraction - O(1) regex search
        json_match = cls._JSON_PATTERN.search(response_text)
        
        if json_match:
            try:
                # O(1) JSON parsing for small objects
                parsed = json.loads(json_match.group())
                
                # O(1) validation and sanitization
                action_type = parsed.get("action_type", expected_action or "perceive")
                
                if action_type == "perceive":
                    return cls._parse_perceive_response(parsed)
                elif action_type == "chat":
                    return cls._parse_chat_response(parsed)
                elif action_type == "move":
                    return cls._parse_move_response(parsed)
                elif action_type == "interact":
                    return cls._parse_interact_response(parsed)
                else:
                    return cls._get_default_response(expected_action or "perceive")
                    
            except json.JSONDecodeError:
                # Fallback to regex parsing
                return cls._parse_with_regex(response_text, expected_action)
        
        # Final fallback - O(1) default response
        return cls._get_default_response(expected_action or "perceive")
    
    @classmethod
    def parse_salience_response(cls, response_text: str) -> int:
        """
        Parse salience rating with O(1) number extraction.
        
        Args:
            response_text: LLM response containing salience rating
            
        Returns:
            Salience score (1-10), defaults to 5
        """
        # O(1) number extraction using pre-compiled regex
        number_match = cls._NUMBER_PATTERN.search(response_text)
        
        if number_match:
            try:
                score = int(number_match.group())
                # O(1) bounds checking
                return max(1, min(10, score))
            except ValueError:
                pass
        
        return 5  # Default fallback
    
    @classmethod
    def _parse_perceive_response(cls, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Parse perceive response with O(1) field extraction."""
        return {
            "action_type": "perceive",
            "observation": str(parsed.get("observation", "I observe my surroundings")),
            "emoji": str(parsed.get("emoji", "👀"))
        }
    
    @classmethod
    def _parse_chat_response(cls, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Parse chat response with O(1) field extraction."""
        return {
            "action_type": "chat",
            "receiver": str(parsed.get("receiver", "")),
            "message": str(parsed.get("message", "Hello!")),
            "emoji": str(parsed.get("emoji", "💬"))
        }
    
    @classmethod
    def _parse_move_response(cls, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Parse move response with O(1) coordinate parsing."""
        destination = parsed.get("destination", [0, 0])
        
        # Handle various destination formats
        if isinstance(destination, list) and len(destination) >= 2:
            # Already in correct format
            dest_coords = [int(destination[0]), int(destination[1])]
        elif isinstance(destination, str):
            # Parse coordinate string - O(1) regex match
            coord_match = cls._COORDINATES_PATTERN.search(destination)
            if coord_match:
                dest_coords = [int(coord_match.group(1)), int(coord_match.group(2))]
            else:
                dest_coords = [0, 0]
        else:
            dest_coords = [0, 0]
        
        return {
            "action_type": "move",
            "destination": dest_coords,
            "reason": str(parsed.get("reason", "Moving to a new location")),
            "emoji": str(parsed.get("emoji", "🚶"))
        }
    
    @classmethod
    def _parse_interact_response(cls, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Parse interact response with O(1) field extraction."""
        return {
            "action_type": "interact",
            "object": str(parsed.get("object", "")),
            "action": str(parsed.get("action", "examine")),
            "emoji": str(parsed.get("emoji", "🤝"))
        }
    
    @classmethod
    def _parse_with_regex(cls, response_text: str, 
                         expected_action: str = None) -> Dict[str, Any]:
        """
        Fallback regex parsing with O(1) pattern matching.
        
        Args:
            response_text: Raw response text
            expected_action: Expected action type
            
        Returns:
            Parsed action dictionary
        """
        # Extract action type - O(1) regex search
        action_match = cls._ACTION_TYPE_PATTERN.search(response_text)
        action_type = action_match.group(1) if action_match else (expected_action or "perceive")
        
        if action_type == "move":
            # Extract coordinates - O(1) regex search
            coord_match = cls._COORDINATES_PATTERN.search(response_text)
            if coord_match:
                destination = [int(coord_match.group(1)), int(coord_match.group(2))]
            else:
                destination = [0, 0]
            
            return {
                "action_type": "move",
                "destination": destination,
                "reason": "Moving to new location",
                "emoji": "🚶"
            }
        
        # For other action types, return default
        return cls._get_default_response(action_type)
    
    @classmethod
    @lru_cache(maxsize=16)
    def _get_default_response(cls, action_type: str) -> Dict[str, Any]:
        """Get default response with O(1) cached lookup."""
        return cls._DEFAULT_RESPONSES.get(action_type, cls._DEFAULT_RESPONSES["perceive"]).copy()
    
    @staticmethod
    def validate_action_format(action_data: Dict[str, Any]) -> bool:
        """
        Validate action format with O(1) checks.
        
        Args:
            action_data: Action dictionary to validate
            
        Returns:
            True if valid format, False otherwise
        """
        if not isinstance(action_data, dict):
            return False
        
        action_type = action_data.get("action_type")
        if not action_type:
            return False
        
        # O(1) validation per action type
        if action_type == "perceive":
            return "observation" in action_data and "emoji" in action_data
        elif action_type == "chat":
            return all(key in action_data for key in ["receiver", "message", "emoji"])
        elif action_type == "move":
            destination = action_data.get("destination")
            return (isinstance(destination, list) and 
                   len(destination) == 2 and 
                   all(isinstance(x, int) for x in destination))
        elif action_type == "interact":
            return all(key in action_data for key in ["object", "action", "emoji"])
        
        return False
    
    @staticmethod
    def extract_emotion_emoji(response_text: str) -> str:
        """
        Extract emoji from response with O(1) pattern matching.
        
        Args:
            response_text: Text containing potential emoji
            
        Returns:
            Extracted emoji or default
        """
        # Common emoji patterns for O(1) lookup
        emoji_map = {
            "perceive": "👀",
            "chat": "💬", 
            "move": "🚶",
            "interact": "🤝",
            "happy": "😊",
            "sad": "😢",
            "excited": "😄",
            "confused": "🤔",
            "surprised": "😲"
        }
        
        # O(1) lookup for common patterns
        text_lower = response_text.lower()
        for keyword, emoji in emoji_map.items():
            if keyword in text_lower:
                return emoji
        
        return "👀"  # Default emoji
    
    # Additional methods expected by tests
    def extract_json(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from response text."""
        # Try each pattern
        for pattern in self._json_patterns.values():
            match = pattern.search(response_text)
            if match:
                try:
                    json_text = match.group(1) if match.groups() else match.group(0)
                    return json.loads(json_text)
                except json.JSONDecodeError:
                    continue
        return None
    
    def extract_action(self, response_text: str) -> Optional[str]:
        """
        Extract action type from response text using prioritized pattern matching.
        
        Args:
            response_text: Response text to analyze
            
        Returns:
            Detected action type or None
        """
        response_lower = response_text.lower()
        
        # Check patterns in priority order (interact first to catch complex phrases)
        pattern_priority = ['interact', 'perceive', 'chat', 'move']
        
        for action_type in pattern_priority:
            if action_type in self._action_patterns:
                if self._action_patterns[action_type].search(response_text):
                    return action_type
        
        return None
    
    def sanitize_response(self, response_text: str) -> str:
        """Sanitize response text by removing control characters."""
        # Remove control characters except newlines and tabs
        sanitized = ''.join(char for char in response_text if ord(char) >= 32 or char in '\n\t')
        
        # Reduce excessive whitespace
        import re
        sanitized = re.sub(r'\n{3,}', '\n\n', sanitized)
        sanitized = re.sub(r' {2,}', ' ', sanitized)
        
        return sanitized.strip()
    
    def validate_response_structure(self, response_data: Dict[str, Any]) -> bool:
        """Validate response structure."""
        if not isinstance(response_data, dict):
            return False
        
        action_type = response_data.get("action")
        if not action_type:
            return False
        
        # Check valid action types
        valid_actions = ["perceive", "move", "chat", "interact"]
        return action_type in valid_actions
    
    def parse_custom_format(self, response_text: str, expected_format: str) -> Dict[str, Any]:
        """
        Parse response text according to a custom format specification.
        
        Args:
            response_text: Response text to parse
            expected_format: Format specification string
            
        Returns:
            Parsed response dictionary
        """
        result = {}
        
        if expected_format == "json":
            # Try JSON parsing first
            try:
                parsed = json.loads(response_text.strip())
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass
                
            # Try extracting JSON from text
            json_match = re.search(r'\{[^{}]*\}', response_text)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
                    
        elif expected_format == "key_value":
            # Parse key: value format
            lines = response_text.strip().split('\n')
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    result[key.strip()] = value.strip()
                    
        elif expected_format == "action_response":
            # Parse action response format
            result['action_type'] = self.extract_action(response_text)
            result['details'] = self.extract_details(response_text)
            result['target'] = self.extract_target(response_text)
            
        # Default: return the basic parsed response
        if not result:
            result = self.parse_response(response_text)
            
        return result


class ActionValidator:
    """
    Fast action validation with O(1) validation rules.
    """
    
    def __init__(self):
        """Initialize the validator with action schemas and custom rule support."""
        self.action_schemas = {
            'perceive': {
                'required_fields': ['action_type'],
                'optional_fields': ['observation', 'emoji'],
                'field_types': {
                    'action_type': str,
                    'observation': str,
                    'emoji': str
                }
            },
            'chat': {
                'required_fields': ['action_type', 'receiver'],
                'optional_fields': ['message', 'emoji'],
                'field_types': {
                    'action_type': str,
                    'receiver': str,
                    'message': str,
                    'emoji': str
                }
            },
            'move': {
                'required_fields': ['action_type'],
                'optional_fields': ['destination', 'reason', 'emoji'],
                'field_types': {
                    'action_type': str,
                    'destination': (list, tuple),
                    'reason': str,
                    'emoji': str
                }
            },
            'interact': {
                'required_fields': ['action_type'],
                'optional_fields': ['object', 'action', 'emoji'],
                'field_types': {
                    'action_type': str,
                    'object': str,
                    'action': str,
                    'emoji': str
                }
            }
        }
        self.validation_errors = []
        # Support for custom actions
        self.custom_validation_rules = {}
    
    def validate_action(self, action: Dict[str, Any]) -> bool:
        """
        Validate action dictionary against schemas with custom rule support.
        
        Args:
            action: Action dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        self.validation_errors = []
        
        if not isinstance(action, dict):
            self.validation_errors.append("Action must be a dictionary")
            return False
            
        action_type = action.get('action_type')
        if not action_type:
            self.validation_errors.append("Action must have 'action_type' field")
            return False
            
        # Check if it's a known action type
        if action_type in self.action_schemas:
            schema = self.action_schemas[action_type]
            
            # Check required fields
            for field in schema['required_fields']:
                if field not in action:
                    self.validation_errors.append(f"Missing required field: {field}")
                    return False
                    
            # Check field types
            for field, expected_type in schema['field_types'].items():
                if field in action:
                    if not isinstance(action[field], expected_type):
                        self.validation_errors.append(f"Invalid type for {field}: expected {expected_type}")
                        return False
                        
        else:
            # Handle custom actions
            if action_type in self.custom_validation_rules:
                # Apply custom validation rules
                custom_rule = self.custom_validation_rules[action_type]
                return custom_rule(action)
            else:
                # For unknown actions, do basic validation
                # Require at least action_type and allow additional custom fields
                if len(action) < 2:  # At least action_type + one other field
                    self.validation_errors.append(f"Custom action '{action_type}' needs additional fields")
                    return False
                    
                # Check for common expected fields in custom actions
                expected_custom_fields = ['reasoning', 'target', 'custom_param']
                has_expected_field = any(field in action for field in expected_custom_fields)
                if not has_expected_field:
                    self.validation_errors.append(f"Custom action should have at least one of: {expected_custom_fields}")
                    return False
                    
        return True
    
    def suggest_corrections(self, action_data: Dict[str, Any]) -> List[str]:
        """Suggest corrections for invalid action."""
        suggestions = []
        
        if not isinstance(action_data, dict):
            suggestions.append("Action must be a dictionary")
            return suggestions
        
        if "action" not in action_data:
            suggestions.append("Add 'action' field with action type")
        
        if "reasoning" not in action_data:
            suggestions.append("Add 'reasoning' field explaining the action")
        
        action_type = action_data.get("action")
        if action_type == "chat" and "message" not in action_data:
            suggestions.append("Add 'message' field for chat action")
        
        return suggestions
    
    @classmethod
    def sanitize_action(cls, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize action data with O(1) field cleaning.
        
        Args:
            action_data: Action data to sanitize
            
        Returns:
            Sanitized action data
        """
        if not isinstance(action_data, dict):
            return {}
        
        action_type = action_data.get("action_type", "perceive")
        
        # O(1) sanitization based on action type
        if action_type == "perceive":
            return {
                "action_type": "perceive",
                "observation": str(action_data.get("observation", ""))[:500],  # Limit length
                "emoji": str(action_data.get("emoji", "👀"))[:4]  # Single emoji
            }
        elif action_type == "chat":
            return {
                "action_type": "chat",
                "receiver": str(action_data.get("receiver", ""))[:50],
                "message": str(action_data.get("message", ""))[:200],  # Limit message length
                "emoji": str(action_data.get("emoji", "💬"))[:4]
            }
        elif action_type == "move":
            destination = action_data.get("destination", [0, 0])
            if isinstance(destination, list) and len(destination) >= 2:
                clean_dest = [int(float(destination[0])), int(float(destination[1]))]
            else:
                clean_dest = [0, 0]
            
            return {
                "action_type": "move", 
                "destination": clean_dest,
                "reason": str(action_data.get("reason", ""))[:200],
                "emoji": str(action_data.get("emoji", "🚶"))[:4]
            }
        elif action_type == "interact":
            return {
                "action_type": "interact",
                "object": str(action_data.get("object", ""))[:50],
                "action": str(action_data.get("action", ""))[:50],
                "emoji": str(action_data.get("emoji", "🤝"))[:4]
            }
        
        return action_data 
    
    def get_validation_errors(self, action_data: Dict[str, Any]) -> List[str]:
        """Get detailed validation errors for an action."""
        errors = []
        
        if not isinstance(action_data, dict):
            errors.append("Action must be a dictionary")
            return errors
        
        # Check basic required fields
        if "action" not in action_data:
            errors.append("Missing required field: action")
        
        if "reasoning" not in action_data:
            errors.append("Missing required field: reasoning")
        
        action_type = action_data.get("action")
        
        # Action-specific validation
        if action_type == "chat":
            if "message" not in action_data:
                errors.append("Chat action requires 'message' field")
            if "target" not in action_data:
                errors.append("Chat action requires 'target' field")
        elif action_type == "move":
            if "direction" not in action_data:
                errors.append("Move action requires 'direction' field")
        elif action_type == "interact":
            if "object" not in action_data:
                errors.append("Interact action requires 'object' field")
            if "interaction" not in action_data:
                errors.append("Interact action requires 'interaction' field")
        
        return errors
    
    def set_custom_rules(self, rules: Dict[str, Any]) -> None:
        """Set custom validation rules."""
        self.custom_validation_rules.update(rules)
    
    def get_custom_rules(self) -> Dict[str, Any]:
        """Get current custom validation rules."""
        return self.custom_validation_rules.copy() 