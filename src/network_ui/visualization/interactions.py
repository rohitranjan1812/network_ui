"""
Graph Interactions Module
Handles user interactions with the graph visualization.
"""

import math
from typing import Dict, List, Any, Optional, Tuple, Callable, Set
from dataclasses import dataclass
from enum import Enum
import logging

from ..core.models import Node, Edge

logger = logging.getLogger(__name__)

class InteractionType(Enum): 
    """Types of user interactions."""
    NODE_CLICK = "node_click"
    EDGE_CLICK = "edge_click"
    NODE_DRAG = "node_drag"
    CANVAS_CLICK = "canvas_click"
    ZOOM = "zoom"
    PAN = "pan"
    SELECTION = "selection"
    CONTEXT_MENU = "context_menu"

@dataclass
class InteractionEvent: 
    """Represents a user interaction event."""
    type:   InteractionType
    element_id:   Optional[str] = None
    element_type:   Optional[str] = None  # "node" or "edge"
    position:   Optional[Tuple[float, float]] = None
    data:   Optional[Dict[str, Any]] = None

class InteractionManager: 
    """
    Manages user interactions with the graph visualization.
    Implements the Direct Manipulation functionality from the specification.
    """

    def __init__(self): 
        """Initialize the interaction manager."""
        self.selected_nodes:   Set[str] = set()
        self.selected_edges:   Set[str] = set()
        self.dragged_node:   Optional[str] = None
        self.drag_start_position:   Optional[Tuple[float, float]] = None

  # Event callbacks
        self.on_node_click:   Optional[Callable[[str, Dict[str, Any]], None]] = None
        self.on_edge_click:   Optional[Callable[[str, Dict[str, Any]], None]] = None
        self.on_canvas_click:   Optional[Callable[[Tuple[float, float]], None]] = None
        self.on_selection_change:   Optional[Callable[[Set[str], Set[str]], None]] = None
        self.on_node_drag_start:   Optional[Callable[[str, Tuple[float, float]], None]] = None
        self.on_node_drag:   Optional[Callable[[str, Tuple[float, float]], None]] = None
        self.on_node_drag_end:   Optional[Callable[[str, Tuple[float, float]], None]] = None

  # Interaction settings
        self.enable_drag = True
        self.enable_selection = True
        self.enable_context_menu = True
        self.selection_mode = "single"  # "single", "multiple", "additive"

        logger.info("InteractionManager initialized")

    def handle_interaction(self, interaction_data:   Dict[str, Any]) -> Dict[str, Any]: 
        """
        Handle a user interaction.

        Args: 
            interaction_data:   Dictionary containing interaction details

        Returns: 
            Dict containing the interaction result
        """
        try: 
            interaction_type = interaction_data.get('type', 'unknown')

            if interaction_type == 'click': 
                return self._handle_click(interaction_data)
            elif interaction_type == 'hover': 
                return self._handle_hover(interaction_data)
            elif interaction_type == 'zoom': 
                return self._handle_zoom(interaction_data)
            elif interaction_type == 'pan': 
                return self._handle_pan(interaction_data)
            else: 
                return {'success':  False, 'error':  f'Unknown interaction type:   {interaction_type}'}

        except Exception as e: 
            logger.error(f"Error handling interaction:   {e}")
            return {'success':  False, 'error':  str(e)}

    def _handle_click(self, data:   Dict[str, Any]) -> Dict[str, Any]: 
        """Handle click interaction."""
        return {'success':  True, 'type':  'click', 'result':  'Click handled'}

    def _handle_hover(self, data:   Dict[str, Any]) -> Dict[str, Any]: 
        """Handle hover interaction."""
        return {'success':  True, 'type':  'hover', 'result':  'Hover handled'}

    def _handle_zoom(self, data:   Dict[str, Any]) -> Dict[str, Any]: 
        """Handle zoom interaction."""
        return {'success':  True, 'type':  'zoom', 'result':  'Zoom handled'}

    def _handle_pan(self, data:   Dict[str, Any]) -> Dict[str, Any]: 
        """Handle pan interaction."""
        return {'success':  True, 'type':  'pan', 'result':  'Pan handled'}

    def handle_click(self, position:   Tuple[float, float],
                     nodes_data:   List[Dict[str, Any]],
                     edges_data:   List[Dict[str, Any]]) -> Optional[InteractionEvent]: 
        """
        Handle a click event and return the corresponding interaction event.
        """
  # Check if a node was clicked
        clicked_node = self._find_node_at_position(position, nodes_data)
        if clicked_node: 
            return self._handle_node_click(clicked_node, position)

  # Check if an edge was clicked
        clicked_edge = self._find_edge_at_position(position, edges_data)
        if clicked_edge: 
            return self._handle_edge_click(clicked_edge, position)

  # Canvas click
        return self._handle_canvas_click(position)

    def _find_node_at_position(self, position:   Tuple[float, float],
                               nodes_data:   List[Dict[str, Any]]) -> Optional[Dict[str, Any]]: 
        """Find a node at the given position."""
        x, y = position

        for node in nodes_data: 
            node_x, node_y = node["x"], node["y"]
            size = node["size"]

  # Check if click is within node bounds
            distance = math.sqrt((x - node_x) ** 2 + (y - node_y) ** 2)
            if distance <= size: 
                return node

        return None

    def _find_edge_at_position(self, position:   Tuple[float, float],
                               edges_data:   List[Dict[str, Any]]) -> Optional[Dict[str, Any]]: 
        """Find an edge at the given position."""
        x, y = position

        for edge in edges_data: 
            x1, y1 = edge["sourceX"], edge["sourceY"]
            x2, y2 = edge["targetX"], edge["targetY"]
            width = edge["width"]

  # Check if click is near the edge line
            if self._point_near_line((x, y), (x1, y1), (x2, y2), width + 5): 
                return edge

        return None

    def _point_near_line(self, point:   Tuple[float, float],
                         line_start:   Tuple[float, float],
                         line_end:   Tuple[float, float],
                         tolerance:   float) -> bool: 
        """Check if a point is near a line segment."""
        px, py = point
        x1, y1 = line_start
        x2, y2 = line_end

  # Calculate distance from point to line segment
        A = px - x1
        B = py - y1
        C = x2 - x1
        D = y2 - y1

        dot = A * C + B * D
        len_sq = C * C + D * D

        if len_sq == 0: 
  # Line segment is actually a point
            distance = math.sqrt(A * A + B * B)
        else: 
            param = dot / len_sq

            if param < 0: 
                xx, yy = x1, y1
            elif param > 1: 
                xx, yy = x2, y2
            else: 
                xx = x1 + param * C
                yy = y1 + param * D

            distance = math.sqrt((px - xx) ** 2 + (py - yy) ** 2)

        return distance <= tolerance

    def _handle_node_click(self, node:   Dict[str, Any],
                           position:   Tuple[float, float]) -> InteractionEvent: 
        """Handle a node click event."""
        node_id = node["id"]

  # Update selection
        if self.enable_selection:  
            if self.selection_mode == "single": 
                self.selected_nodes.clear()
                self.selected_edges.clear()
                self.selected_nodes.add(node_id)
            elif self.selection_mode == "multiple": 
                if node_id in self.selected_nodes:  
                    self.selected_nodes.remove(node_id)
                else: 
                    self.selected_nodes.add(node_id)
            elif self.selection_mode == "additive": 
                self.selected_nodes.add(node_id)

  # Call callback
        if self.on_node_click:  
            self.on_node_click(node_id, node)

  # Notify selection change
        if self.on_selection_change:  
            self.on_selection_change(self.selected_nodes, self.selected_edges)

        logger.info(f"Node clicked:   {node_id}")

        return InteractionEvent(
            type=InteractionType.NODE_CLICK,
            element_id=node_id,
            element_type="node",
            position=position,
            data=node
        )

    def _handle_edge_click(self, edge:   Dict[str, Any],
                           position:   Tuple[float, float]) -> InteractionEvent: 
        """Handle an edge click event."""
        edge_id = edge["id"]

  # Update selection
        if self.enable_selection:  
            if self.selection_mode == "single": 
                self.selected_nodes.clear()
                self.selected_edges.clear()
                self.selected_edges.add(edge_id)
            elif self.selection_mode == "multiple": 
                if edge_id in self.selected_edges:  
                    self.selected_edges.remove(edge_id)
                else: 
                    self.selected_edges.add(edge_id)
            elif self.selection_mode == "additive": 
                self.selected_edges.add(edge_id)

  # Call callback
        if self.on_edge_click:  
            self.on_edge_click(edge_id, edge)

  # Notify selection change
        if self.on_selection_change:  
            self.on_selection_change(self.selected_nodes, self.selected_edges)

        logger.info(f"Edge clicked:   {edge_id}")

        return InteractionEvent(
            type=InteractionType.EDGE_CLICK,
            element_id=edge_id,
            element_type="edge",
            position=position,
            data=edge
        )

    def _handle_canvas_click(self, position:   Tuple[float, float]) -> InteractionEvent: 
        """Handle a canvas click event."""
  # Clear selection if clicking on empty space
        if self.enable_selection and self.selection_mode == "single": 
            self.selected_nodes.clear()
            self.selected_edges.clear()

            if self.on_selection_change:  
                self.on_selection_change(self.selected_nodes, self.selected_edges)

  # Call callback
        if self.on_canvas_click:  
            self.on_canvas_click(position)

        logger.info(f"Canvas clicked at {position}")

        return InteractionEvent(
            type=InteractionType.CANVAS_CLICK,
            position=position
        )

    def handle_drag_start(self, node_id:   str, position:   Tuple[float, float]) -> Optional[InteractionEvent]: 
        """Handle the start of a drag operation."""
        if not self.enable_drag:  
            return None

        self.dragged_node = node_id
        self.drag_start_position = position

        if self.on_node_drag_start:  
            self.on_node_drag_start(node_id, position)

        logger.info(f"Drag started for node:   {node_id}")

        return InteractionEvent(
            type=InteractionType.NODE_DRAG,
            element_id=node_id,
            element_type="node",
            position=position,
            data={"drag_start":  True}
        )

    def handle_drag(self, position:   Tuple[float, float]) -> Optional[InteractionEvent]: 
        """Handle a drag operation."""
        if not self.enable_drag or not self.dragged_node:  
            return None

        if self.on_node_drag:  
            self.on_node_drag(self.dragged_node, position)

        return InteractionEvent(
            type=InteractionType.NODE_DRAG,
            element_id=self.dragged_node,
            element_type="node",
            position=position,
            data={"drag_start":  False}
        )

    def handle_drag_end(self, position:   Tuple[float, float]) -> Optional[InteractionEvent]: 
        """Handle the end of a drag operation."""
        if not self.enable_drag or not self.dragged_node:  
            return None

        node_id = self.dragged_node

        if self.on_node_drag_end:  
            self.on_node_drag_end(node_id, position)

        self.dragged_node = None
        self.drag_start_position = None

        logger.info(f"Drag ended for node:   {node_id}")

        return InteractionEvent(
            type=InteractionType.NODE_DRAG,
            element_id=node_id,
            element_type="node",
            position=position,
            data={"drag_end":  True}
        )

    def handle_zoom(self, delta:   float, center:   Tuple[float, float]) -> InteractionEvent: 
        """Handle a zoom event."""
        return InteractionEvent(
            type=InteractionType.ZOOM,
            position=center,
            data={"delta":  delta}
        )

    def handle_pan(self, delta:   Tuple[float, float]) -> InteractionEvent: 
        """Handle a pan event."""
        return InteractionEvent(
            type=InteractionType.PAN,
            data={"delta":  delta}
        )

    def select_nodes(self, node_ids:   List[str], mode:   str = "replace") -> None: 
        """Select multiple nodes."""
        if mode == "replace": 
            self.selected_nodes.clear()
            self.selected_edges.clear()
            self.selected_nodes.update(node_ids)
        elif mode == "add": 
            self.selected_nodes.update(node_ids)
        elif mode == "remove": 
            for node_id in node_ids: 
                self.selected_nodes.discard(node_id)

        if self.on_selection_change:  
            self.on_selection_change(self.selected_nodes, self.selected_edges)

    def select_edges(self, edge_ids:   List[str], mode:   str = "replace") -> None: 
        """Select multiple edges."""
        if mode == "replace": 
            self.selected_nodes.clear()
            self.selected_edges.clear()
            self.selected_edges.update(edge_ids)
        elif mode == "add": 
            self.selected_edges.update(edge_ids)
        elif mode == "remove": 
            for edge_id in edge_ids: 
                self.selected_edges.discard(edge_id)

        if self.on_selection_change:  
            self.on_selection_change(self.selected_nodes, self.selected_edges)

    def clear_selection(self) -> None: 
        """Clear all selections."""
        self.selected_nodes.clear()
        self.selected_edges.clear()

        if self.on_selection_change:  
            self.on_selection_change(self.selected_nodes, self.selected_edges)

    def get_selected_nodes(self) -> Set[str]: 
        """Get the set of selected node IDs."""
        return self.selected_nodes.copy()

    def get_selected_edges(self) -> Set[str]: 
        """Get the set of selected edge IDs."""
        return self.selected_edges.copy()

    def is_node_selected(self, node_id:   str) -> bool: 
        """Check if a node is selected."""
        return node_id in self.selected_nodes

    def is_edge_selected(self, edge_id:   str) -> bool: 
        """Check if an edge is selected."""
        return edge_id in self.selected_edges

    def set_selection_mode(self, mode:   str) -> None: 
        """Set the selection mode."""
        if mode in ["single", "multiple", "additive"]: 
            self.selection_mode = mode
        else: 
            raise ValueError(f"Invalid selection mode:   {mode}")

    def enable_interactions(self, drag:   bool = True, selection:   bool = True,
                            context_menu:   bool = True) -> None: 
        """Enable or disable specific interactions."""
        self.enable_drag = drag
        self.enable_selection = selection
        self.enable_context_menu = context_menu
