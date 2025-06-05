"""
spatial
=======

.. module:: memory.spatial
   :synopsis: Module containing SpatialMemory.
"""

class SpatialMemory:
    """
    A spatial memory implementation using a graph structure.

    :ivar dict graph: The graph representation of spatial relationships.

    .. method:: add_nodes(nodes)

       Add multiple nodes to the spatial graph.

       :param list[str] nodes: A list of node identifiers to add.
       :returns: None

    .. method:: add_edge(edges)

       Add multiple edges between nodes in the spatial graph.

       :param list[tuple[str, str]] edges: A list of tuples containing (source_node, destination_node) pairs.
       :returns: None

    .. method:: convert_to_JSON()

       Convert the spatial graph to JSON format.

       :returns: The graph as a JSON-serializable dictionary.
       :rtype: dict

    **Example**

    .. code-block:: python

       memory = SpatialMemory()
       memory.add_nodes(["room1", "room2", "room3"])
       memory.add_edge([("room1", "room2"), ("room1", "room3")])
       json_data = memory.convert_to_JSON()
    """

    def __init__(self):
        """
        Initialize a new instance of :class:`SpatialMemory`.

        Creates an empty graph dictionary to store spatial relationships.
        """
        self.graph = dict()
    

    def add_nodes(self, nodes: list[str]):
        """
        Add multiple nodes to the spatial graph.

        :param list[str] nodes: A list of node identifiers to add.
        :returns: None
        """
        for node in nodes:
            self.graph[node] = list()
    

    def add_edges(self, edges: list[tuple[str, str]]):
        """
        Add multiple edges between nodes in the spatial graph.

        The edges are directed from source to destination nodes. If a source node 
        doesn't exist, that edge is not added.

        :param list[tuple[str, str]] edges: A list of tuples where each tuple contains (source_node, destination_node).
        :returns: None
        """
        for u, v in edges:
            if u in self.graph:
                self.graph[u].append(v)
    

    def add_edges(self, edges: list[tuple[str, list[str]]]):
        """
        Add multiple edges from nodes to their adjacency lists.

        Each tuple contains a source node and a list of destination nodes. 
        All edges are directed from the source to each destination in the list.
        If a source node doesn't exist, those edges are not added.

        :param list[tuple[str, list[str]]] edges: A list of tuples where each tuple contains (source_node, [destination_nodes]).
        :returns: None
        """
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
        def build_tree(node):
            """Recursively build tree structure for a node and its children."""
            children = self.graph.get(node, [])
            if not children:
                return {}
            
            tree = {}
            for child in children:
                tree[child] = build_tree(child)
            return tree
        
        # Find root nodes (nodes that are not contained by any other node)
        all_children = set()
        for connections in self.graph.values():
            all_children.update(connections)
        
        root_nodes = [node for node in self.graph.keys() if node not in all_children]
        
        # Build the complete tree structure
        result = {}
        for root in root_nodes:
            result[root] = build_tree(root)
        
        return result
