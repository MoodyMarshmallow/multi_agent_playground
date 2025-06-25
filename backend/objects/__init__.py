"""
Multi-Agent Playground - Objects Package
========================================
Objects package containing interactive object definitions and registry.

This package provides:
- Interactive object definitions
- Object registry for world state management

Author: Multi-Agent Playground Team
Version: 1.0.0
"""

from .interactive_object import InteractiveObject
from .object_registry import object_registry

__version__ = "1.0.0"

__all__ = [
    "InteractiveObject",
    "object_registry",
]
