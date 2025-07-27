"""
Graph Layout Algorithms Module

Provides various layout algorithms for positioning nodes in graph visualizations: 
- Force - directed layouts (Fruchterman - Reingold, Spring - embedder)
- Hierarchical / Tree layouts
- Circular layouts
- Grid layouts
"""

import math
import random
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict, deque

from ..core.models import Node, Edge, GraphData

@dataclass
class LayoutParams: 
    """Parameters for layout algorithms."""
    width:   float = 800.0
    height:   float = 600.0
    iterations:   int = 100
    animate:   bool = True
    seed:   Optional[int] = None

class BaseLayout(ABC): 
    """Abstract base class for graph layout algorithms."""

    def __init__(self, params:   LayoutParams, **kwargs): 
        """Initialize the layout algorithm."""
        self.params = params
        self.logger = self._setup_logging()
        if params.seed is not None: 
            random.seed(params.seed)

  # Accept iterations parameter for API compatibility
        if 'iterations' in kwargs: 
            self.params.iterations = kwargs['iterations']

    def _setup_logging(self) -> logging.Logger:  
        """Setup logging for the layout."""
        logger = logging.getLogger(f'{self.__class__.__name__}')
        logger.setLevel(logging.INFO)

        if not logger.handlers:  
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    @abstractmethod
    def apply_layout(self, graph_data:   GraphData) -> GraphData: 
        """Apply the layout algorithm to the graph."""
        pass

    def _get_node_dict(self, nodes:   List[Node]) -> Dict[str, Node]: 
        """Create a dictionary mapping node IDs to nodes."""
        return {node.id:   node for node in nodes}

    def _get_adjacency_list(self, nodes:   List[Node], edges:   List[Edge]) -> Dict[str, List[str]]: 
        """Create an adjacency list representation of the graph."""
        adj_list = defaultdict(list)
        for edge in edges: 
            adj_list[edge.source].append(edge.target)
            if not edge.directed:  
                adj_list[edge.target].append(edge.source)
        return adj_list

class ForceDirectedLayout(BaseLayout): 
    """Force - directed layout using Fruchterman - Reingold algorithm."""

    def __init__(self, params:   LayoutParams, spring_strength:   float = 0.1,
                 repulsion_strength:   float = 1000.0, damping:   float = 0.9, **kwargs): 
        """Initialize force - directed layout."""
        super().__init__(params)
        self.spring_strength = spring_strength
        self.repulsion_strength = repulsion_strength
        self.damping = damping
        self.temperature = 100.0  # Initial temperature for simulated annealing

  # Accept iterations parameter for API compatibility
        if 'iterations' in kwargs: 
            self.params.iterations = kwargs['iterations']

    def apply_layout(self, graph_data:   GraphData) -> GraphData: 
        """Apply force - directed layout to the graph."""
        if not graph_data.nodes:  
            return graph_data

        self.logger.info(f"Applying force - directed layout to {len(graph_data.nodes)} nodes")

  # Initialize random positions if not set
        self._initialize_positions(graph_data.nodes)

  # Create adjacency list for connected nodes
        adj_list = self._get_adjacency_list(graph_data.nodes, graph_data.edges)

  # Run force - directed simulation
        for iteration in range(self.params.iterations): 
            self._apply_forces(graph_data.nodes, adj_list)
            self._update_positions(graph_data.nodes)
            self._cool_temperature(iteration)

        self.logger.info("Force - directed layout completed")
        return graph_data

    def _initialize_positions(self, nodes:   List[Node]) -> None: 
        """Initialize node positions randomly within the layout area."""
        for node in nodes: 
            if node.position["x"] == 0 and node.position["y"] == 0: 
                node.position["x"] = random.uniform(-self.params.width / 2, self.params.width / 2)
                node.position["y"] = random.uniform(-self.params.height / 2, self.params.height / 2)

    def _apply_forces(self, nodes:   List[Node], adj_list:   Dict[str, List[str]]) -> None: 
        """Calculate and apply forces to all nodes."""
        forces = {}

  # Initialize forces
        for node in nodes: 
            forces[node.id] = {'x':  0.0, 'y':  0.0}

  # Repulsive forces between all pairs of nodes
        for i, node1 in enumerate(nodes): 
            for j, node2 in enumerate(nodes[i + 1:  ], i + 1): 
                dx = node2.position["x"] - node1.position["x"]
                dy = node2.position["y"] - node1.position["y"]
                distance = math.sqrt(dx * dx + dy * dy) + 0.01  # Avoid division by zero

  # Repulsive force
                force = self.repulsion_strength / (distance * distance)
                force_x = force * dx / distance
                force_y = force * dy / distance

                forces[node1.id]['x'] -= force_x
                forces[node1.id]['y'] -= force_y
                forces[node2.id]['x'] += force_x
                forces[node2.id]['y'] += force_y

  # Attractive forces between connected nodes
        for node_id, neighbors in adj_list.items(): 
            node = next((n for n in nodes if n.id == node_id), None)
            if not node: 
                continue

            for neighbor_id in neighbors: 
                neighbor = next((n for n in nodes if n.id == neighbor_id), None)
                if not neighbor: 
                    continue

                dx = neighbor.position["x"] - node.position["x"]
                dy = neighbor.position["y"] - node.position["y"]
                distance = math.sqrt(dx * dx + dy * dy) + 0.01

  # Attractive force (spring)
                force = self.spring_strength * distance
                force_x = force * dx / distance
                force_y = force * dy / distance

                forces[node.id]['x'] += force_x
                forces[node.id]['y'] += force_y

  # Store forces in node attributes
        for node in nodes: 
            node.attributes['force_x'] = forces[node.id]['x']
            node.attributes['force_y'] = forces[node.id]['y']

    def _update_positions(self, nodes:   List[Node]) -> None: 
        """Update node positions based on calculated forces."""
        for node in nodes: 
            force_x = node.attributes.get('force_x', 0.0)
            force_y = node.attributes.get('force_y', 0.0)

  # Limit displacement by temperature
            displacement = math.sqrt(force_x * force_x + force_y * force_y)
            if displacement > 0: 
                max_displacement = min(displacement, self.temperature)
                node.position["x"] += (force_x / displacement) * max_displacement
                node.position["y"] += (force_y / displacement) * max_displacement

  # Apply damping
            node.position["x"] *= self.damping
            node.position["y"] *= self.damping

  # Keep nodes within bounds
            node.position["x"] = max(-self.params.width / 2, min(self.params.width / 2, node.position["x"]))
            node.position["y"] = max(-self.params.height / 2, min(self.params.height / 2, node.position["y"]))

    def _cool_temperature(self, iteration:   int) -> None: 
        """Cool the temperature for simulated annealing."""
        self.temperature = max(1.0, 100.0 * (1.0 - iteration / self.params.iterations))

class HierarchicalLayout(BaseLayout): 
    """Hierarchical layout for tree - like structures."""

    def __init__(self, params:   LayoutParams, level_separation:   float = 100.0,
                 node_separation:   float = 50.0, root_node:   Optional[str] = None, **kwargs): 
        """Initialize hierarchical layout."""
        super().__init__(params)
        self.level_separation = level_separation
        self.node_separation = node_separation
        self.root_node = root_node

  # Accept iterations parameter for API compatibility
        if 'iterations' in kwargs: 
            self.params.iterations = kwargs['iterations']

    def apply_layout(self, graph_data:   GraphData) -> GraphData: 
        """Apply hierarchical layout to the graph."""
        if not graph_data.nodes:  
            return graph_data

        self.logger.info(f"Applying hierarchical layout to {len(graph_data.nodes)} nodes")

  # Find root node or use the first node
        root = self._find_root_node(graph_data.nodes, graph_data.edges)
        if not root: 
            return graph_data

  # Build tree structure
        tree = self._build_tree(graph_data.nodes, graph_data.edges, root)

  # Calculate levels
        levels = self._calculate_levels(tree, root)

  # Position nodes
        self._position_nodes(graph_data.nodes, levels)

        self.logger.info("Hierarchical layout completed")
        return graph_data

    def _find_root_node(self, nodes:   List[Node], edges:   List[Edge]) -> Optional[str]: 
        """Find the root node for the hierarchy."""
        if self.root_node:  
            return self.root_node

  # Find node with no incoming edges (or least incoming edges)
        in_degree = defaultdict(int)
        for edge in edges: 
            in_degree[edge.target] += 1

  # Find node with minimum in - degree
        min_in_degree = float('inf')
        root = None
        for node in nodes: 
            degree = in_degree[node.id]
            if degree < min_in_degree: 
                min_in_degree = degree
                root = node.id

        return root

    def _build_tree(self, nodes:   List[Node], edges:   List[Edge], root:   str) -> Dict[str, List[str]]: 
        """Build tree structure from the graph."""
        adj_list = defaultdict(list)
        for edge in edges: 
            adj_list[edge.source].append(edge.target)

  # Perform BFS to build tree and avoid cycles
        tree = defaultdict(list)
        visited = set()
        queue = deque([root])
        visited.add(root)

        while queue: 
            current = queue.popleft()
            for neighbor in adj_list[current]: 
                if neighbor not in visited: 
                    tree[current].append(neighbor)
                    visited.add(neighbor)
                    queue.append(neighbor)

        return tree

    def _calculate_levels(self, tree:   Dict[str, List[str]], root:   str) -> Dict[str, int]: 
        """Calculate the level of each node in the tree."""
        levels = {root:   0}
        queue = deque([root])

        while queue: 
            current = queue.popleft()
            current_level = levels[current]

            for child in tree[current]: 
                levels[child] = current_level + 1
                queue.append(child)

        return levels

    def _position_nodes(self, nodes:   List[Node], levels:   Dict[str, int]) -> None: 
        """Position nodes based on their levels."""
  # Group nodes by level
        level_groups = defaultdict(list)
        max_level = 0
        for node_id, level in levels.items(): 
            level_groups[level].append(node_id)
            max_level = max(max_level, level)

  # Position nodes
        node_dict = self._get_node_dict(nodes)

        for level, node_ids in level_groups.items(): 
  # Handle single level case
            if max_level == 0: 
                y = 0
            else: 
                y = -self.params.height / 2 + (level / max_level) * self.params.height

  # Distribute nodes horizontally at this level
            total_width = len(node_ids) * self.node_separation
            start_x = -total_width / 2

            for i, node_id in enumerate(node_ids): 
                if node_id in node_dict: 
                    node = node_dict[node_id]
                    node.position["x"] = start_x + i * self.node_separation
                    node.position["y"] = y

class CircularLayout(BaseLayout): 
    """Circular layout that arranges nodes in a circle."""

    def __init__(self, params:   LayoutParams, radius:   Optional[float] = None, **kwargs): 
        """Initialize circular layout."""
        super().__init__(params)
        self.radius = radius or min(params.width, params.height) / 3

  # Accept iterations parameter for API compatibility
        if 'iterations' in kwargs: 
            self.params.iterations = kwargs['iterations']

    def apply_layout(self, graph_data:   GraphData) -> GraphData: 
        """Apply circular layout to the graph."""
        if not graph_data.nodes:  
            return graph_data

        self.logger.info(f"Applying circular layout to {len(graph_data.nodes)} nodes")

        num_nodes = len(graph_data.nodes)
        angle_step = 2 * math.pi / num_nodes

        for i, node in enumerate(graph_data.nodes): 
            angle = i * angle_step
            node.position["x"] = self.radius * math.cos(angle)
            node.position["y"] = self.radius * math.sin(angle)

        self.logger.info("Circular layout completed")
        return graph_data

class GridLayout(BaseLayout): 
    """Grid layout that arranges nodes in a regular grid."""

    def __init__(self, params:   LayoutParams, cols:   Optional[int] = None, **kwargs): 
        """Initialize grid layout."""
        super().__init__(params)
        self.cols = cols

  # Accept iterations parameter for API compatibility
        if 'iterations' in kwargs: 
            self.params.iterations = kwargs['iterations']

    def apply_layout(self, graph_data:   GraphData) -> GraphData: 
        """Apply grid layout to the graph."""
        if not graph_data.nodes:  
            return graph_data

        self.logger.info(f"Applying grid layout to {len(graph_data.nodes)} nodes")

        num_nodes = len(graph_data.nodes)
        cols = self.cols or math.ceil(math.sqrt(num_nodes))
        rows = math.ceil(num_nodes / cols)

        cell_width = self.params.width / cols
        cell_height = self.params.height / rows

        for i, node in enumerate(graph_data.nodes): 
            row = i // cols
            col = i % cols

            node.position["x"] = -self.params.width / 2 + col * cell_width + cell_width / 2
            node.position["y"] = -self.params.height / 2 + row * cell_height + cell_height / 2

        self.logger.info("Grid layout completed")
        return graph_data

class RandomLayout(BaseLayout): 
    """Random layout that places nodes randomly."""

    def apply_layout(self, graph_data:   GraphData) -> GraphData: 
        """Apply random layout to the graph."""
        if not graph_data.nodes:  
            return graph_data

        self.logger.info(f"Applying random layout to {len(graph_data.nodes)} nodes")

        for node in graph_data.nodes:  
            node.position["x"] = random.uniform(-self.params.width / 2, self.params.width / 2)
            node.position["y"] = random.uniform(-self.params.height / 2, self.params.height / 2)

        self.logger.info("Random layout completed")
        return graph_data

def create_layout(algorithm:   str, params:   LayoutParams, **kwargs) -> BaseLayout: 
    """Factory function to create layout algorithms."""
    algorithm = algorithm.lower()

    if algorithm == "force_directed": 
        return ForceDirectedLayout(params, **kwargs)
    elif algorithm == "hierarchical": 
        return HierarchicalLayout(params, **kwargs)
    elif algorithm == "circular": 
        return CircularLayout(params, **kwargs)
    elif algorithm == "grid": 
        return GridLayout(params, **kwargs)
    elif algorithm == "random": 
        return RandomLayout(params, **kwargs)
    else: 
        raise ValueError(f"Unknown layout algorithm:   {algorithm}")

def get_available_layouts() -> Dict[str, Dict[str, Any]]: 
    """Get information about available layout algorithms."""
    return {
        "force_directed":  {
            "name":  "Force - Directed",
            "description":  "Physics - based layout using attractive and repulsive forces",
            "parameters":  ["spring_strength", "repulsion_strength", "damping"],
            "best_for":  ["general graphs", "social networks", "small to medium graphs"]
        },
        "hierarchical":  {
            "name":  "Hierarchical",
            "description":  "Tree - like layout with clear hierarchy levels",
            "parameters":  ["level_separation", "node_separation", "root_node"],
            "best_for":  ["trees", "organizational charts", "directed acyclic graphs"]
        },
        "circular":  {
            "name":  "Circular",
            "description":  "Arranges nodes in a circle",
            "parameters":  ["radius"],
            "best_for":  ["small graphs", "showcasing connectivity", "aesthetic purposes"]
        },
        "grid":  {
            "name":  "Grid",
            "description":  "Regular grid arrangement",
            "parameters":  ["cols"],
            "best_for":  ["uniform display", "comparison purposes", "regular structures"]
        },
        "random":  {
            "name":  "Random",
            "description":  "Random positioning",
            "parameters":  [],
            "best_for":  ["initial positioning", "testing purposes"]
        }
    }
