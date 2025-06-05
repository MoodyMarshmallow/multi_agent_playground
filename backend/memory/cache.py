"""
cache
=======

.. module:: memory.cache
   :synopsis: Module containing CachedMemory.
"""

from typing import Dict, List, Tuple

from backend.memory.spatial import SpatialMemory

class CachedMemory:
    """
    A spatial memory implementation using a graph structure.

    :ivar dict graph: The graph representation of spatial relationships.

    .. method:: add(data)

       Add nodes and edges to the spatial graph from a dictionary.

       :param dict data: A dictionary containing "nodes" (list of node 
                         identifiers) and "edges" (list of tuples with source 
                         nodes and their destination lists).
       :returns: None

    .. method:: convert_to_JSON()

       Convert the spatial graph to JSON format.

       :returns: The graph as a JSON-serializable dictionary.
       :rtype: dict

    **Example**

    .. code-block:: python

       memory = SpatialMemory()
       memory.add({
           "nodes": ["room1", "room2", "room3"],
           "edges": [("room1", ["room2"]), ("room1", ["room3"])]
       })
       json_data = memory.convert_to_JSON()
    """

    def __init__(self, env: Dict[str, List] = None):
        """
        Initialize a new instance of :class:`SpatialMemory`.

        Creates an empty graph dictionary to store spatial relationships.
        """
        pass

