"""
This file implements the act function for character agents.
"""

from typing import Any
from kani import ai_function

class ActMixin:
    """
    This class implements the act function for character agents.
    """
    @ai_function()
    def act(self, action_description: str, action_pronunciation: str, action_event: tuple[str, Any, Any]) -> None:
        