"""
Module
=========

This package provides memory functionality for agents in the backend
of the JRPG simulation.

Features
--------
- :class:`.SpatialMemory` -- Spatial memory class in :mod:`spatial`.

Usage Example
-------------
.. code-block:: python

    from memory import SpatialMemory

    obj = SpatialMemory()
    obj.add_nodes(["room1", "room2"])
    obj.add_edges([("room1", ["room2"])])
    result = obj.convert_to_JSON()

Author
------
Arush Arora <arushar@seas.upenn.edu>

Version
-------
0.1.0
"""

from .spatial import SpatialMemory

__version__ = "0.1.0"