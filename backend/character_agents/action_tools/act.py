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
    def act(self, ) -> None:
        