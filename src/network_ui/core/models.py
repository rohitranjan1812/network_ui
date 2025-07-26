"""
Data Models for Graph Structure
Defines the standardized data structures for nodes, edges, and graph objects.
"""

import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime


@dataclass
class Node:
    """Represents a node in the graph with hierarchical KPI structure and visual properties."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    level: int = 1
    kpis: Dict[str, Any] = field(default_factory=dict)
    attributes: Dict[str, Any] = field(default_factory=dict)
    position: Optional[Dict[str, float]] = None
    # Spec 2 additions: Visual properties for graph visualization
    visual_properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.position:
            self.position = {"x": 0.0, "y": 0.0}

        # Initialize default visual properties if not set (Spec 2)
        if not self.visual_properties:
            self.visual_properties = {
                "size": 10.0,
                "color": "#3498db",
                "shape": "circle"
            }


@dataclass
class Edge:
    """Represents an edge / relationship between nodes with visual properties."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source: str = ""
    target: str = ""
    relationship_type: str = "default"
    level: int = 1
    kpi_components: Dict[str, Any] = field(default_factory=dict)
    attributes: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
    # Spec 2 additions: Direction control and visual properties
    directed: bool = True
    visual_properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        # Initialize default visual properties if not set (Spec 2)
        if not self.visual_properties:
            self.visual_properties = {
                "width": 2.0,
                "color": "#7f8c8d",
                "style": "solid"
            }


@dataclass
class GraphData:
    """Standardized graph object containing nodes and edges with advanced graph engine capabilities."""
    nodes: List[Node] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    # Spec 2 additions: Undo / Redo functionality
    _history: List[Dict[str, Any]] = field(default_factory=list, init=False)
    _history_index: int = field(default=-1, init=False)

    def add_node(self, node: Node) -> None:
        """Add a node to the graph."""
        self._save_state_for_undo("add_node", {"node": node})
        self.nodes.append(node)

    def add_edge(self, edge: Edge) -> None:
        """Add an edge to the graph."""
        self._save_state_for_undo("add_edge", {"edge": edge})
        self.edges.append(edge)

    def get_node_by_id(self, node_id: str) -> Optional[Node]:
        """Get a node by its ID."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def get_edges_by_node(self, node_id: str) -> List[Edge]:
        """Get all edges connected to a specific node."""
        return [edge for edge in self.edges
                if edge.source == node_id or edge.target == node_id]

    # Spec 2: Advanced Graph Engine Methods

    def remove_node(self, node_id: str) -> bool:
        """Remove a node and its connected edges."""
        node = self.get_node_by_id(node_id)
        if not node:
            return False

        # Get connected edges before removal for undo functionality
        connected_edges = self.get_edges_by_node(node_id)

        self._save_state_for_undo("remove_node", {
            "node": node,
            "connected_edges": connected_edges
        })

        # Remove connected edges
        self.edges = [edge for edge in self.edges
                      if edge.source != node_id and edge.target != node_id]

        # Remove node
        self.nodes = [n for n in self.nodes if n.id != node_id]
        return True

    def remove_edge(self, edge_id: str) -> bool:
        """Remove an edge by its ID."""
        edge = self.get_edge_by_id(edge_id)
        if not edge:
            return False

        self._save_state_for_undo("remove_edge", {"edge": edge})
        self.edges = [e for e in self.edges if e.id != edge_id]
        return True

    def update_node(self, node_id: str, updates: Dict[str, Any]) -> bool:
        """Update a node's properties."""
        node = self.get_node_by_id(node_id)
        if not node:
            return False

        # Save old state for undo
        old_state = {
            "name": node.name,
            "attributes": node.attributes.copy(),
            "visual_properties": node.visual_properties.copy(),
            "position": node.position.copy() if node.position else None
        }
        self._save_state_for_undo("update_node", {
            "node_id": node_id,
            "old_state": old_state
        })

        # Apply updates
        if "name" in updates:
            node.name = updates["name"]
        if "attributes" in updates:
            node.attributes.update(updates["attributes"])
        if "visual_properties" in updates:
            node.visual_properties.update(updates["visual_properties"])
        if "position" in updates:
            node.position = updates["position"]

        node.updated_at = datetime.now()
        return True

    def update_edge(self, edge_id: str, updates: Dict[str, Any]) -> bool:
        """Update an edge's properties."""
        edge = self.get_edge_by_id(edge_id)
        if not edge:
            return False

        # Save old state for undo
        old_state = {
            "weight": edge.weight,
            "directed": edge.directed,
            "attributes": edge.attributes.copy(),
            "visual_properties": edge.visual_properties.copy()
        }
        self._save_state_for_undo("update_edge", {
            "edge_id": edge_id,
            "old_state": old_state
        })

        # Apply updates
        if "weight" in updates:
            edge.weight = updates["weight"]
        if "directed" in updates:
            edge.directed = updates["directed"]
        if "attributes" in updates:
            edge.attributes.update(updates["attributes"])
        if "visual_properties" in updates:
            edge.visual_properties.update(updates["visual_properties"])

        return True

    def get_edge_by_id(self, edge_id: str) -> Optional[Edge]:
        """Get an edge by its ID."""
        for edge in self.edges:
            if edge.id == edge_id:
                return edge
        return None

    def get_neighbors(self, node_id: str, direction: str = "all") -> List[str]:
        """Get neighbors of a node.

        Args:
            node_id: ID of the node
            direction: "incoming", "outgoing", or "all"

        Returns:
            List of neighbor node IDs
        """
        neighbors = []

        for edge in self.edges:
            if direction in ["outgoing", "all"] and edge.source == node_id:
                neighbors.append(edge.target)
            if direction in ["incoming", "all"] and edge.target == node_id:
                neighbors.append(edge.source)

        return list(set(neighbors))  # Remove duplicates

    def query_nodes(self, **filters) -> List[Node]:
        """Query nodes based on attributes."""
        result = []

        for node in self.nodes:
            match = True

            for key, value in filters.items():
                if key == "id" and node.id != value:
                    match = False
                    break
                elif key == "name" and node.name != value:
                    match = False
                    break
                elif key == "level" and node.level != value:
                    match = False
                    break
                elif key in node.attributes and node.attributes[key] != value:
                    match = False
                    break
                elif key not in ["id", "name", "level"] and key not in node.attributes:
                    match = False
                    break

            if match:
                result.append(node)

        return result

    def query_edges(self, **filters) -> List[Edge]:
        """Query edges based on attributes."""
        result = []

        for edge in self.edges:
            match = True

            for key, value in filters.items():
                if key == "id" and edge.id != value:
                    match = False
                    break
                elif key == "source" and edge.source != value:
                    match = False
                    break
                elif key == "target" and edge.target != value:
                    match = False
                    break
                elif key == "directed" and edge.directed != value:
                    match = False
                    break
                elif key == "weight" and edge.weight != value:
                    match = False
                    break
                elif key in edge.attributes and edge.attributes[key] != value:
                    match = False
                    break
                elif key not in ["id", "source", "target", "directed", "weight"] and key not in edge.attributes:
                    match = False
                    break

            if match:
                result.append(edge)

        return result

    # Spec 2: Undo / Redo functionality

    def _save_state_for_undo(self, action: str, data: Dict[str, Any]) -> None:
        """Save current state for undo functionality."""
        # Remove any redo history when new action is performed
        if self._history_index < len(self._history) - 1:
            self._history = self._history[:self._history_index + 1]

        # Add new state
        state = {
            "action": action,
            "data": data,
            "timestamp": datetime.now()
        }
        self._history.append(state)
        self._history_index += 1

        # Limit history size to prevent memory issues
        if len(self._history) > 100:
            self._history = self._history[-100:]
            self._history_index = len(self._history) - 1

    def undo(self) -> bool:
        """Undo the last action."""
        if self._history_index < 0:
            return False

        state = self._history[self._history_index]
        action = state["action"]
        data = state["data"]

        # Reverse the action
        if action == "add_node":
            node = data["node"]
            self.nodes = [n for n in self.nodes if n.id != node.id]
        elif action == "add_edge":
            edge = data["edge"]
            self.edges = [e for e in self.edges if e.id != edge.id]
        elif action == "remove_node":
            self.nodes.append(data["node"])
            self.edges.extend(data["connected_edges"])
        elif action == "remove_edge":
            self.edges.append(data["edge"])
        elif action == "update_node":
            node = self.get_node_by_id(data["node_id"])
            if node:
                old_state = data["old_state"]
                node.name = old_state["name"]
                node.attributes = old_state["attributes"]
                node.visual_properties = old_state["visual_properties"]
                if old_state["position"]:
                    node.position = old_state["position"]
        elif action == "update_edge":
            edge = self.get_edge_by_id(data["edge_id"])
            if edge:
                old_state = data["old_state"]
                edge.weight = old_state["weight"]
                edge.directed = old_state["directed"]
                edge.attributes = old_state["attributes"]
                edge.visual_properties = old_state["visual_properties"]

        self._history_index -= 1
        return True

    def redo(self) -> bool:
        """Redo the next action."""
        if self._history_index >= len(self._history) - 1:
            return False

        self._history_index += 1
        state = self._history[self._history_index]
        action = state["action"]
        data = state["data"]

        # Re - apply the action
        if action == "add_node":
            self.nodes.append(data["node"])
        elif action == "add_edge":
            self.edges.append(data["edge"])
        elif action == "remove_node":
            node_id = data["node"].id
            self.nodes = [n for n in self.nodes if n.id != node_id]
            self.edges = [e for e in self.edges
                         if e.source != node_id and e.target != node_id]
        elif action == "remove_edge":
            edge_id = data["edge"].id
            self.edges = [e for e in self.edges if e.id != edge_id]
        # Note: update actions would need the new state stored to properly redo

        return True

    def can_undo(self) -> bool:
        """Check if undo is possible."""
        return self._history_index >= 0

    def can_redo(self) -> bool:
        """Check if redo is possible."""
        return self._history_index < len(self._history) - 1


@dataclass
class ImportConfig:
    """Configuration for data import process."""
    file_path: str
    file_encoding: str = "utf - 8"
    mapping_config: Dict[str, str] = field(default_factory=dict)
    data_types: Dict[str, str] = field(default_factory=dict)
    delimiter: str = ","
    skip_rows: int = 0
    max_rows: Optional[int] = None


@dataclass
class ImportResult:
    """Result of the import process."""
    success: bool
    graph_data: Optional[GraphData] = None
    import_log: str = ""
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    processed_rows: int = 0
    total_rows: int = 0
