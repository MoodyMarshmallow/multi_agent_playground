"""
spatial
=======

.. module:: memory.spatial
   :synopsis: Module containing SpatialMemory.
"""

from typing import Dict, List, Tuple

class SpatialMemory:
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

    def __init__(self, data: Dict[str, List] = None):
        """
        Initialize a new instance of :class:`SpatialMemory`.

        Creates an empty graph dictionary to store spatial relationships.
        """
        self.graph = dict()
        if data is not None:
            self.add(data)
    

    def add(self, data: Dict[str, List]) -> None:
        """
        Add nodes and edges to the spatial graph from a dictionary.

        The dictionary must contain "nodes" and "edges" keys. Nodes are added 
        first, then edges are created between them. Edges are directed from 
        source to destination nodes.

        :param Dict[str, List] data: A dictionary with "nodes" (List[str]) and 
                                     "edges" (List[Tuple[str, List[str]]]) keys.
        :returns: None
        :raises KeyError: If required keys "nodes" or "edges" are missing from 
                          data.
        :raises TypeError: If data types don't match expected format.
        """
        # Type checking for required keys
        if "nodes" not in data or "edges" not in data:
            raise KeyError("Dictionary must contain both 'nodes' and 'edges' "
                          "keys")
        
        nodes: List[str] = data["nodes"]
        edges: List[Tuple[str, List[str]]] = data["edges"]
        
        # Add nodes first
        for node in nodes:
            self.graph[node] = list()
        
        # Add edges
        for u, adj_u in edges:
            if u in self.graph:
                self.graph[u].extend(adj_u)

    def convert_to_JSON(self):
        """
        Convert the spatial graph to JSON format as a nested tree structure.

        Creates a JSON structure that describes spatial relationships as a 
        hierarchical tree where each location contains its sub-locations.

        :returns: The graph as a nested tree structure.
        :rtype: dict
        """
        # Find root nodes (nodes that are not referenced by any other node)
        all_children = set()
        for node, children in self.graph.items():
            all_children.update(children)
        
        # Root nodes are those that exist in the graph but are not children of 
        # any other node
        root_nodes = [node for node in self.graph.keys() 
                      if node not in all_children]
        
        def build_tree(node):
            """Recursively build the tree structure for a given node."""
            children = self.graph.get(node, [])
            if not children:
                return {}
            
            result = {}
            for child in children:
                result[child] = build_tree(child)
            return result
        
        # Build the final tree structure
        result = {}
        for root in root_nodes:
            result[root] = build_tree(root)
        
        return result

