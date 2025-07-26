"""
Graph Renderer Module
Implements high-performance 2D graph visualization with interactive features.
"""

import json
import math
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

from ..core.models import GraphData, Node, Edge

logger = logging.getLogger(__name__)


class LayoutAlgorithm(Enum):
    """Available layout algorithms."""
    FORCE_DIRECTED = "force_directed"
    HIERARCHICAL = "hierarchical"
    CIRCULAR = "circular"
    RANDOM = "random"


class VisualStyle(Enum):
    """Visual style options."""
    SOLID = "solid"
    DASHED = "dashed"
    DOTTED = "dotted"


@dataclass
class VisualConfig:
    """Configuration for visual properties."""
    # Node properties
    node_size: int = 20
    node_color: str = "#4A90E2"
    node_shape: str = "circle"
    show_node_labels: bool = True
    node_label_size: int = 12

    # Edge properties
    edge_width: int = 2
    edge_color: str = "#666666"
    edge_style: VisualStyle = VisualStyle.SOLID
    show_edge_labels: bool = False
    show_arrows: bool = True

    # Layout properties
    layout_algorithm: LayoutAlgorithm = LayoutAlgorithm.FORCE_DIRECTED
    force_strength: float = 0.1
    repulsion_strength: float = 100.0

    # Canvas properties
    canvas_width: int = 800
    canvas_height: int = 600
    background_color: str = "#FFFFFF"

    # Interaction properties
    enable_drag: bool = True
    enable_zoom: bool = True
    enable_pan: bool = True


@dataclass
class VisualMapping:
    """Data-driven visual mapping configuration."""
    node_size_mapping: Optional[str] = None  # Attribute name
    node_color_mapping: Optional[str] = None  # Attribute name
    edge_width_mapping: Optional[str] = None  # Attribute name
    edge_color_mapping: Optional[str] = None  # Attribute name

    # Color schemes
    color_scheme: str = "viridis"  # viridis, plasma, inferno, etc.

    # Size ranges
    min_node_size: int = 10
    max_node_size: int = 50
    min_edge_width: int = 1
    max_edge_width: int = 10


class GraphRenderer:
    """
    High-performance graph renderer with interactive features.
    Implements the Graph Visualization specification.
    """

    def __init__(self, config: Optional[VisualConfig] = None):
        """Initialize the renderer with configuration."""
        self.config = config or VisualConfig()
        self.visual_mapping = VisualMapping()
        self.graph_data: Optional[GraphData] = None
        self.node_positions: Dict[str, Tuple[float, float]] = {}
        self.selected_elements: set = set()
        self.highlighted_elements: set = set()
        self.filtered_elements: set = set()

        # Event callbacks
        self.on_node_click: Optional[Callable[[str], None]] = None
        self.on_edge_click: Optional[Callable[[str], None]] = None
        self.on_selection_change: Optional[Callable[[set], None]] = None

        logger.info("GraphRenderer initialized")

    def initialize(self) -> bool:
        """
        Initialize the renderer.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            # Reset all state
            self.node_positions.clear()
            self.selected_elements.clear()
            self.highlighted_elements.clear()
            self.filtered_elements.clear()
            
            logger.info("GraphRenderer initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize renderer: {e}")
            return False

    def set_graph_data(self, graph_data: GraphData) -> None:
        """Set the graph data to render."""
        self.graph_data = graph_data
        self._initialize_positions()
        logger.info(f"Graph data set with {len(graph_data.nodes)} nodes and {len(graph_data.edges)} edges")

    def _initialize_positions(self) -> None:
        """Initialize node positions based on layout algorithm."""
        if not self.graph_data:
            return

        if self.config.layout_algorithm == LayoutAlgorithm.RANDOM:
            self._random_layout()
        elif self.config.layout_algorithm == LayoutAlgorithm.CIRCULAR:
            self._circular_layout()
        elif self.config.layout_algorithm == LayoutAlgorithm.HIERARCHICAL:
            self._hierarchical_layout()
        else:  # Force-directed as default
            self._force_directed_layout()

    def _random_layout(self) -> None:
        """Random layout for initial positioning."""
        import random

        if not self.graph_data or not self.graph_data.nodes:
            return

        for node in self.graph_data.nodes:
            x = random.uniform(50, self.config.canvas_width - 50)
            y = random.uniform(50, self.config.canvas_height - 50)
            self.node_positions[node.id] = (x, y)

    def _circular_layout(self) -> None:
        """Circular layout positioning."""
        if not self.graph_data or not self.graph_data.nodes:
            return

        center_x = self.config.canvas_width / 2
        center_y = self.config.canvas_height / 2
        radius = min(self.config.canvas_width, self.config.canvas_height) / 3

        angle_step = 2 * math.pi / len(self.graph_data.nodes)

        for i, node in enumerate(self.graph_data.nodes):
            angle = i * angle_step
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.node_positions[node.id] = (x, y)

    def _hierarchical_layout(self) -> None:
        """Hierarchical layout positioning."""
        if not self.graph_data or not self.graph_data.nodes:
            return

        # Simple hierarchical layout - can be enhanced
        levels = self._calculate_hierarchy_levels()

        for level, nodes in levels.items():
            y = 50 + level * 100
            x_step = self.config.canvas_width / (len(nodes) + 1)

            for i, node in enumerate(nodes):
                x = x_step * (i + 1)
                self.node_positions[node.id] = (x, y)

    def _calculate_hierarchy_levels(self) -> Dict[int, List[Node]]:
        """Calculate hierarchy levels for nodes."""
        # Simple implementation - can be enhanced with proper graph analysis
        if not self.graph_data or not self.graph_data.nodes:
            return {0: []}

        levels: Dict[int, List[Node]] = {0: []}
        processed = set()

        # Start with nodes that have no incoming edges
        for node in self.graph_data.nodes:
            incoming_edges = [e for e in self.graph_data.edges if e.target == node.id]
            if not incoming_edges:
                levels[0].append(node)
                processed.add(node.id)

        # Assign remaining nodes to levels
        current_level = 1
        while len(processed) < len(self.graph_data.nodes):
            if current_level not in levels:
                levels[current_level] = []

            for node in self.graph_data.nodes:
                if node.id in processed:
                    continue

                incoming_edges = [e for e in self.graph_data.edges if e.target == node.id]
                if all(e.source in processed for e in incoming_edges):
                    levels[current_level].append(node)
                    processed.add(node.id)

            current_level += 1
            if current_level > 10:  # Prevent infinite loop
                break

        return levels

    def _force_directed_layout(self) -> None:
        """Force-directed layout using Fruchterman-Reingold algorithm."""
        if not self.graph_data or not self.graph_data.nodes:
            return

        # Initialize random positions
        self._random_layout()

        # Simple force-directed layout iteration
        iterations = 50
        for _ in range(iterations):
            self._apply_force_directed_forces()

    def _apply_force_directed_forces(self) -> None:
        """Apply force-directed layout forces."""
        if not self.graph_data:
            return

        # Calculate repulsive forces between all nodes
        forces = {node.id: (0.0, 0.0) for node in self.graph_data.nodes}

        # Repulsive forces
        for i, node1 in enumerate(self.graph_data.nodes):
            for j, node2 in enumerate(self.graph_data.nodes):
                if i >= j:
                    continue

                pos1 = self.node_positions[node1.id]
                pos2 = self.node_positions[node2.id]

                dx = pos2[0] - pos1[0]
                dy = pos2[1] - pos1[1]
                distance = math.sqrt(dx * dx + dy * dy)

                if distance > 0:
                    # Repulsive force
                    force = self.config.repulsion_strength / (distance * distance)
                    fx = (dx / distance) * force
                    fy = (dy / distance) * force

                    forces[node1.id] = (forces[node1.id][0] - fx, forces[node1.id][1] - fy)
                    forces[node2.id] = (forces[node2.id][0] + fx, forces[node2.id][1] + fy)

        # Attractive forces for connected nodes
        for edge in self.graph_data.edges:
            if edge.source in self.node_positions and edge.target in self.node_positions:
                pos1 = self.node_positions[edge.source]
                pos2 = self.node_positions[edge.target]

                dx = pos2[0] - pos1[0]
                dy = pos2[1] - pos1[1]
                distance = math.sqrt(dx * dx + dy * dy)

                if distance > 0:
                    # Attractive force
                    force = self.config.force_strength * distance
                    fx = (dx / distance) * force
                    fy = (dy / distance) * force

                    forces[edge.source] = (forces[edge.source][0] + fx, forces[edge.source][1] + fy)
                    forces[edge.target] = (forces[edge.target][0] - fx, forces[edge.target][1] - fy)

        # Apply forces with damping
        damping = 0.1
        for node_id, (fx, fy) in forces.items():
            if node_id in self.node_positions:
                x, y = self.node_positions[node_id]
                new_x = x + fx * damping
                new_y = y + fy * damping

                # Keep nodes within canvas bounds
                new_x = max(50, min(self.config.canvas_width - 50, new_x))
                new_y = max(50, min(self.config.canvas_height - 50, new_y))

                self.node_positions[node_id] = (new_x, new_y)

    def set_layout_algorithm(self, algorithm: LayoutAlgorithm) -> None:
        """Change the layout algorithm and recalculate positions."""
        self.config.layout_algorithm = algorithm
        self._initialize_positions()
        logger.info(f"Layout algorithm changed to {algorithm.value}")

    def set_visual_mapping(self, mapping: VisualMapping) -> None:
        """Set data-driven visual mapping configuration."""
        self.visual_mapping = mapping
        logger.info("Visual mapping configuration updated")

    def select_element(self, element_id: str, element_type: str = "node") -> None:
        """Select a node or edge."""
        element_key = f"{element_type}:{element_id}"
        self.selected_elements.add(element_key)

        if self.on_selection_change:
            self.on_selection_change(self.selected_elements)

        logger.info(f"Selected {element_type}: {element_id}")

    def deselect_element(self, element_id: str, element_type: str = "node") -> None:
        """Deselect a node or edge."""
        element_key = f"{element_type}:{element_id}"
        self.selected_elements.discard(element_key)

        if self.on_selection_change:
            self.on_selection_change(self.selected_elements)

    def clear_selection(self) -> None:
        """Clear all selections."""
        self.selected_elements.clear()

        if self.on_selection_change:
            self.on_selection_change(self.selected_elements)

    def highlight_elements(self, element_ids: List[str], element_type: str = "node") -> None:
        """Highlight specific elements."""
        for element_id in element_ids:
            element_key = f"{element_type}:{element_id}"
            self.highlighted_elements.add(element_key)

    def clear_highlights(self) -> None:
        """Clear all highlights."""
        self.highlighted_elements.clear()

    def filter_elements(self, filter_func: Callable[[Any], bool], element_type: str = "node") -> None:
        """Filter elements based on a function."""
        if not self.graph_data:
            return

        if element_type == "node":
            elements: List[Node] = self.graph_data.nodes
        else:
            elements: List[Edge] = self.graph_data.edges

        self.filtered_elements = {
            f"{element_type}:{elem.id}" for elem in elements if filter_func(elem)
        }

    def clear_filters(self) -> None:
        """Clear all filters."""
        self.filtered_elements.clear()

    def get_node_position(self, node_id: str) -> Optional[Tuple[float, float]]:
        """Get the position of a specific node."""
        return self.node_positions.get(node_id)

    def set_node_position(self, node_id: str, x: float, y: float) -> None:
        """Set the position of a specific node (for drag and drop)."""
        self.node_positions[node_id] = (x, y)

    def render(self) -> Dict[str, Any]:
        """
        Render the graph and return visualization data.
        This would typically return data for a frontend renderer.
        """
        if not self.graph_data:
            return {"error": "No graph data available"}

        # Prepare rendering data
        nodes_data = []
        for node in self.graph_data.nodes:
            if f"node:{node.id}" in self.filtered_elements:
                continue

            pos = self.node_positions.get(node.id, (0, 0))

            # Apply visual mapping
            size = self._get_mapped_node_size(node)
            color = self._get_mapped_node_color(node)

            node_data = {
                "id": node.id,
                "x": pos[0],
                "y": pos[1],
                "size": size,
                "color": color,
                "shape": self.config.node_shape,
                "label": node.name if self.config.show_node_labels else "",
                "attributes": node.attributes,
                "selected": f"node:{node.id}" in self.selected_elements,
                "highlighted": f"node:{node.id}" in self.highlighted_elements
            }
            nodes_data.append(node_data)

        edges_data = []
        for edge in self.graph_data.edges:
            if f"edge:{edge.id}" in self.filtered_elements:
                continue

            source_pos = self.node_positions.get(edge.source)
            target_pos = self.node_positions.get(edge.target)

            if not source_pos or not target_pos:
                continue

            # Apply visual mapping
            width = self._get_mapped_edge_width(edge)
            color = self._get_mapped_edge_color(edge)

            edge_data = {
                "id": edge.id,
                "source": edge.source,
                "target": edge.target,
                "sourceX": source_pos[0],
                "sourceY": source_pos[1],
                "targetX": target_pos[0],
                "targetY": target_pos[1],
                "width": width,
                "color": color,
                "style": self.config.edge_style.value,
                "label": edge.relationship_type if self.config.show_edge_labels else "",
                "attributes": edge.attributes,
                "selected": f"edge:{edge.id}" in self.selected_elements,
                "highlighted": f"edge:{edge.id}" in self.highlighted_elements,
                "showArrow": self.config.show_arrows
            }
            edges_data.append(edge_data)

        return {
            "nodes": nodes_data,
            "edges": edges_data,
            "config": {
                "canvasWidth": self.config.canvas_width,
                "canvasHeight": self.config.canvas_height,
                "backgroundColor": self.config.background_color,
                "enableDrag": self.config.enable_drag,
                "enableZoom": self.config.enable_zoom,
                "enablePan": self.config.enable_pan
            }
        }

    def render_frame(self, graph_data, highlights=None) -> Dict[str, Any]:
        """
        Render a frame of the graph visualization.
        
        Args:
            graph_data: Graph data to render
            highlights: Optional highlight information
            
        Returns:
            Dict containing render statistics and data
        """
        try:
            if graph_data:
                self.set_graph_data(graph_data)
            
            if highlights:
                for highlight_id in highlights:
                    self.highlighted_elements.add(highlight_id)
            
            # Generate the render data
            render_data = self.render()
            
            return {
                'success': True,
                'frame_data': render_data,
                'node_count': len(graph_data.nodes) if graph_data else 0,
                'edge_count': len(graph_data.edges) if graph_data else 0,
                'highlights_count': len(highlights) if highlights else 0,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error rendering frame: {e}")
            return {
                'success': False,
                'error': str(e),
                'node_count': 0,
                'edge_count': 0
            }

    def _get_mapped_node_size(self, node: Node) -> int:
        """Get node size based on visual mapping."""
        if not self.visual_mapping.node_size_mapping:
            return self.config.node_size

        value = node.attributes.get(self.visual_mapping.node_size_mapping, 0)
        if isinstance(value, (int, float)):
            # Normalize to size range
            normalized = (value - 0) / (100 - 0)  # Assuming 0-100 range
            size = self.visual_mapping.min_node_size + normalized * (
                self.visual_mapping.max_node_size - self.visual_mapping.min_node_size
            )
            return int(size)

        return self.config.node_size

    def _get_mapped_node_color(self, node: Node) -> str:
        """Get node color based on visual mapping."""
        if not self.visual_mapping.node_color_mapping:
            return self.config.node_color

        value = node.attributes.get(self.visual_mapping.node_color_mapping, 0)
        # Simple color mapping - can be enhanced with proper color schemes
        if isinstance(value, (int, float)):
            normalized = (value - 0) / (100 - 0)
            # Simple color interpolation
            r = int(74 + normalized * 181)  # 4A to FF
            g = int(144 + normalized * 111)  # 90 to FF
            b = int(226 + normalized * 29)   # E2 to FF
            return f"#{r:02x}{g:02x}{b:02x}"

        return self.config.node_color

    def _get_mapped_edge_width(self, edge: Edge) -> int:
        """Get edge width based on visual mapping."""
        if not self.visual_mapping.edge_width_mapping:
            return self.config.edge_width

        value = edge.attributes.get(self.visual_mapping.edge_width_mapping, 0)
        if isinstance(value, (int, float)):
            normalized = (value - 0) / (100 - 0)
            width = self.visual_mapping.min_edge_width + normalized * (
                self.visual_mapping.max_edge_width - self.visual_mapping.min_edge_width
            )
            return int(width)

        return self.config.edge_width

    def _get_mapped_edge_color(self, edge: Edge) -> str:
        """Get edge color based on visual mapping."""
        if not self.visual_mapping.edge_color_mapping:
            return self.config.edge_color

        value = edge.attributes.get(self.visual_mapping.edge_color_mapping, 0)
        if isinstance(value, (int, float)):
            normalized = (value - 0) / (100 - 0)
            # Simple color interpolation
            r = int(102 + normalized * 153)  # 66 to FF
            g = int(102 + normalized * 153)  # 66 to FF
            b = int(102 + normalized * 153)  # 66 to FF
            return f"#{r:02x}{g:02x}{b:02x}"

        return self.config.edge_color

    def export_visualization(self, format: str = "json") -> str:
        """Export visualization data in specified format."""
        render_data = self.render()

        if format == "json":
            return json.dumps(render_data, indent=2)
        elif format == "svg":
            return self._generate_svg(render_data)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _generate_svg(self, render_data: Dict[str, Any]) -> str:
        """Generate SVG representation of the graph."""
        svg_parts = [
            f'<svg width="{self.config.canvas_width}" height="{self.config.canvas_height}" xmlns="http://www.w3.org/2000/svg">',
            f'<rect width="100%" height="100%" fill="{self.config.background_color}"/>'
        ]

        # Add edges
        for edge in render_data["edges"]:
            svg_parts.append(
                f'<line x1="{edge["sourceX"]}" y1="{edge["sourceY"]}" '
                f'x2="{edge["targetX"]}" y2="{edge["targetY"]}" '
                f'stroke="{edge["color"]}" stroke-width="{edge["width"]}"/>'
            )

        # Add nodes
        for node in render_data["nodes"]:
            if node["shape"] == "circle":
                svg_parts.append(
                    f'<circle cx="{node["x"]}" cy="{node["y"]}" r="{node["size"]}" '
                    f'fill="{node["color"]}" stroke="#000000" stroke-width="1"/>'
                )
            else:  # square
                size = node["size"]
                svg_parts.append(
                    f'<rect x="{node["x"] - size}" y="{node["y"] - size}" '
                    f'width="{size * 2}" height="{size * 2}" '
                    f'fill="{node["color"]}" stroke="#000000" stroke-width="1"/>'
                )

            # Add label
            if node["label"]:
                svg_parts.append(
                    f'<text x="{node["x"]}" y="{node["y"] + node["size"] + 15}" '
                    f'text-anchor="middle" font-size="{self.config.node_label_size}">{node["label"]}</text>'
                )

        svg_parts.append('</svg>')
        return '\n'.join(svg_parts)


def create_renderer(config: Optional[VisualConfig] = None) -> GraphRenderer:
    """
    Factory function to create a graph renderer instance.
    
    Args:
        config: Optional visual configuration
        
    Returns:
        GraphRenderer: Configured renderer instance
    """
    return GraphRenderer(config)
