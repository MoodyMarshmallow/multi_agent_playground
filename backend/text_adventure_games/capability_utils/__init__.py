"""
Capability system utilities for the text adventure game.

This package contains modules for managing object capabilities:
- discovery: Capability discovery logic
"""

# Re-export capability protocols from the main capabilities module
from ..capabilities import (
    ActionResult,
    Activatable,
    Openable, 
    Lockable,
    Usable,
    Container,
    Recipient,
    Giver,
    Conversational,
    Consumable,
    Examinable
)