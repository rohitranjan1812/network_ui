"""
Data Models for Graph Structure
Defines the standardized data structures for nodes, edges, and graph objects.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid


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
    """Represents an edge/relationship between nodes."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source: str = ""
    target: str = ""
    relationship_type: str = "default"
    level: int = 1
    kpi_components: Dict[str, Any] = field(default_factory=dict)
    attributes: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class GraphData:
    """Standardized graph object containing nodes and edges."""
    nodes: List[Node] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def add_node(self, node: Node) -> None:
        """Add a node to the graph."""
        self.nodes.append(node)

    def add_edge(self, edge: Edge) -> None:
        """Add an edge to the graph."""
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


@dataclass
class ImportConfig:
    """Configuration for data import process."""
    file_path: str
    file_encoding: str = "utf-8"
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
