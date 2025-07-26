"""
Visualization API for network graph rendering and interaction.
Implements REST endpoints for graph visualization features.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, Set
from dataclasses import dataclass
from flask import Blueprint, request, jsonify, send_file

# Import visualization components
from ..config import VisualizationConfig, get_default_config
from ..renderer import GraphRenderer, VisualConfig, create_renderer
from ..layouts import ForceDirectedLayout, HierarchicalLayout, CircularLayout, LayoutParams, create_layout
from ..visual_mapping import VisualMapper
from ..interactions import InteractionManager


def get_renderer_capabilities() -> Dict[str, Any]:
    """Get renderer capabilities information."""
    return {
        'supported_layouts': ['force_directed', 'circular', 'hierarchical', 'grid', 'random'],
        'supported_renderers': ['canvas', 'webgl'],
        'max_nodes': 10000,
        'max_edges': 50000,
        'features': {
            'clustering': True,
            'level_of_detail': True,
            'batch_rendering': True,
            'real_time_updates': True
        }
    }


class VisualizationAPI:
    """Visualization API class for managing graph visualization operations."""

    def __init__(self):
        """Initialize the Visualization API."""
        self.logger = self._setup_logging()
        self.config = get_default_config()
        self.renderer = None
        self.visual_mapping = VisualMapper()
        self.interaction_manager = InteractionManager()
        self.graph_engine = None  # Will be initialized lazily

        # Current visualization state
        self._current_highlights: Set[str] = set()
        self._current_filters: Dict[str, Any] = {}
        self._viewport_state = {
            'x': 0.0,
            'y': 0.0,
            'zoom': 1.0
        }

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the visualization API."""
        logger = logging.getLogger('VisualizationAPI')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _get_graph_engine(self):
        """Get graph engine instance (lazy loading to avoid circular import)."""
        if self.graph_engine is None:
            from ...api.graph_engine import graph_engine_api
            self.graph_engine = graph_engine_api
        return self.graph_engine

    def create_blueprint(self) -> Blueprint:
        """Create Flask blueprint with all visualization endpoints."""
        bp = Blueprint('visualization', __name__, url_prefix='/api/v1/visualization')

        @bp.route('/render', methods=['POST'])
        def render_graph():
            """Render or update the graph visualization."""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No data provided'}), 400

                graph_id = data.get('graph_id', 'default')
                config_data = data.get('config', {})
                highlights = set(data.get('highlights', []))

                # Update configuration if provided
                if config_data:
                    self.config = VisualizationConfig.from_dict(config_data)

                # Get graph data
                graph_data = self._get_graph_engine().get_graph(graph_id)
                if not graph_data:
                    return jsonify({'error': 'Graph not found'}), 404

                # Initialize renderer if needed
                if not self.renderer:
                    self.renderer = create_renderer(self.config)
                    if not self.renderer.initialize():
                        return jsonify({'error': 'Failed to initialize renderer'}), 500

                # Apply layout if requested
                layout_algorithm = data.get('layout_algorithm')
                if layout_algorithm:
                    layout_params = LayoutParams(
                        width=self.config.canvas.width,
                        height=self.config.canvas.height,
                        iterations=self.config.layout.iterations,
                        animate=self.config.layout.animate
                    )
                    layout = create_layout(layout_algorithm, layout_params)
                    graph_data = layout.apply_layout(graph_data)

                # Apply visual mappings
                if data.get('visual_mappings'):
                    self.visual_mapping.apply_mappings(graph_data, data['visual_mappings'])

                # Render the graph
                self._current_highlights = highlights
                stats = self.renderer.render_frame(graph_data, highlights)

                if not stats.get('success', False):
                    return jsonify({'error': stats.get('error', 'Render failed')}), 500

                return jsonify({
                    'status': 'rendered',
                    'timestamp': datetime.now().isoformat(),
                    'stats': {
                        'nodes_rendered': stats.get('node_count', 0),
                        'edges_rendered': stats.get('edge_count', 0),
                        'render_time_ms': 0,  # TODO: Add timing
                        'fps': 60,  # Default FPS
                        'culled_nodes': 0,  # TODO: Add culling stats
                        'culled_edges': 0   # TODO: Add culling stats
                    },
                    'viewport': self._viewport_state
                })

            except Exception as e:
                self.logger.error(f"Error rendering graph: {str(e)}")
                return jsonify({'error': 'Internal server error'}), 500

        @bp.route('/layout', methods=['POST'])
        def change_layout():
            """Change the layout algorithm for the graph."""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No data provided'}), 400

                algorithm = data.get('algorithm')
                if not algorithm:
                    return jsonify({'error': 'Algorithm not specified'}), 400

                graph_id = data.get('graph_id', 'default')
                parameters = data.get('parameters', {})

                # Get graph data
                graph_data = self._get_graph_engine().get_graph(graph_id)
                if not graph_data:
                    return jsonify({'error': 'Graph not found'}), 404

                # Create layout with parameters
                layout_params = LayoutParams(
                    width=self.config.canvas.width,
                    height=self.config.canvas.height,
                    iterations=parameters.get('iterations', 100),
                    animate=parameters.get('animate', True),
                    seed=parameters.get('seed')
                )

                layout = create_layout(algorithm, layout_params, **parameters)
                updated_graph = layout.apply_layout(graph_data)

                # Update the node positions in the graph engine
                for updated_node in updated_graph.nodes:
                    original_node = graph_data.get_node_by_id(updated_node.id)
                    if original_node:
                        original_node.position = updated_node.position.copy()

                return jsonify({
                    'status': 'layout_applied',
                    'algorithm': algorithm,
                    'timestamp': datetime.now().isoformat(),
                    'node_count': len(updated_graph.nodes),
                    'edge_count': len(updated_graph.edges),
                    'message': 'Applied layout'
                })

            except ValueError as e:
                return jsonify({'error': str(e)}), 400
            except Exception as e:
                self.logger.error(f"Error changing layout: {str(e)}")
                return jsonify({'error': 'Internal server error'}), 500

        @bp.route('/mapping', methods=['POST'])
        def configure_visual_mapping():
            """Configure visual mappings for nodes and edges."""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No data provided'}), 400

                mappings = data.get('mappings', {})
                graph_id = data.get('graph_id', 'default')

                # Validate mappings
                if not self.visual_mapping.validate_mappings(mappings):
                    return jsonify({'error': 'Invalid mapping configuration'}), 400

                # Get graph data
                graph_data = self._get_graph_engine().get_graph(graph_id)
                if not graph_data:
                    return jsonify({'error': 'Graph not found'}), 404

                # Apply mappings
                self.visual_mapping.apply_mappings(graph_data, mappings)

                return jsonify({
                    'status': 'mappings_applied',
                    'timestamp': datetime.now().isoformat(),
                    'mappings': mappings
                })

            except Exception as e:
                self.logger.error(f"Error configuring visual mapping: {str(e)}")
                return jsonify({'error': 'Internal server error'}), 500

        @bp.route('/filter', methods=['POST'])
        def apply_filter():
            """Apply filters to show / hide nodes and edges."""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No data provided'}), 400

                filters = data.get('filters', {})
                graph_id = data.get('graph_id', 'default')

                # Store current filters
                self._current_filters = filters

                # Get graph data
                graph_data = self._get_graph_engine().get_graph(graph_id)
                if not graph_data:
                    return jsonify({'error': 'Graph not found'}), 404

                # Apply filters (this would modify visibility properties)
                filtered_count = self._apply_filters(graph_data, filters)

                return jsonify({
                    'status': 'filters_applied',
                    'timestamp': datetime.now().isoformat(),
                    'filters': filters,
                    'visible_nodes': filtered_count['nodes'],
                    'visible_edges': filtered_count['edges']
                })

            except Exception as e:
                self.logger.error(f"Error applying filter: {str(e)}")
                return jsonify({'error': 'Internal server error'}), 500

        @bp.route('/highlight', methods=['POST'])
        def set_highlights():
            """Set highlighted nodes and edges."""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No data provided'}), 400

                node_ids = data.get('node_ids', [])
                edge_ids = data.get('edge_ids', [])

                # Update current highlights
                self._current_highlights = set(node_ids + edge_ids)

                return jsonify({
                    'status': 'highlights_updated',
                    'timestamp': datetime.now().isoformat(),
                    'highlighted_count': len(self._current_highlights)
                })

            except Exception as e:
                self.logger.error(f"Error setting highlights: {str(e)}")
                return jsonify({'error': 'Internal server error'}), 500

        @bp.route('/viewport', methods=['POST'])
        def update_viewport():
            """Update viewport position and zoom."""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No data provided'}), 400

                x = data.get('x', self._viewport_state['x'])
                y = data.get('y', self._viewport_state['y'])
                zoom = data.get('zoom', self._viewport_state['zoom'])

                # Update viewport
                self._viewport_state = {'x': x, 'y': y, 'zoom': zoom}

                if self.renderer:
                    self.renderer.set_viewport(x, y, zoom)

                return jsonify({
                    'status': 'viewport_updated',
                    'timestamp': datetime.now().isoformat(),
                    'viewport': self._viewport_state
                })

            except Exception as e:
                self.logger.error(f"Error updating viewport: {str(e)}")
                return jsonify({'error': 'Internal server error'}), 500

        @bp.route('/config', methods=['GET'])
        def get_configuration():
            """Get current visualization configuration."""
            try:
                return jsonify({
                    'config': self.config.to_dict(),
                    'capabilities': get_renderer_capabilities(),
                    'available_layouts': get_available_layouts(),
                    'viewport': self._viewport_state,
                    'current_highlights': list(self._current_highlights),
                    'current_filters': self._current_filters
                })

            except Exception as e:
                self.logger.error(f"Error getting configuration: {str(e)}")
                return jsonify({'error': 'Internal server error'}), 500

        @bp.route('/config', methods=['PUT'])
        def update_configuration():
            """Update visualization configuration."""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No data provided'}), 400

                # Update configuration
                self.config = VisualizationConfig.from_dict(data)

                # Reinitialize renderer if engine changed
                if self.renderer and data.get('rendering_engine'):
                    self.renderer = create_renderer(self.config)
                    self.renderer.initialize()

                return jsonify({
                    'status': 'config_updated',
                    'timestamp': datetime.now().isoformat(),
                    'config': self.config.to_dict()
                })

            except Exception as e:
                self.logger.error(f"Error updating configuration: {str(e)}")
                return jsonify({'error': 'Internal server error'}), 500

        @bp.route('/interaction', methods=['POST'])
        def handle_interaction():
            """Handle user interactions (click, drag, etc.)."""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No data provided'}), 400

                interaction_type = data.get('type')
                coordinates = data.get('coordinates', {})
                target_id = data.get('target_id')

                # Process interaction
                result = self.interaction_manager.handle_interaction(
                    interaction_type, coordinates, target_id
                )

                return jsonify({
                    'status': 'interaction_processed',
                    'timestamp': datetime.now().isoformat(),
                    'result': result
                })

            except Exception as e:
                self.logger.error(f"Error handling interaction: {str(e)}")
                return jsonify({'error': 'Internal server error'}), 500

        return bp

    def _apply_filters(self, graph_data, filters: Dict[str, Any]) -> Dict[str, int]:
        """Apply filters to graph data and return visible counts."""
        visible_nodes = 0
        visible_edges = 0

        # Apply node filters
        for node in graph_data.nodes:
            visible = True
            for filter_key, filter_value in filters.get('nodes', {}).items():
                if filter_key in node.attributes:
                    if node.attributes[filter_key] != filter_value:
                        visible = False
                        break

            # Store visibility in node attributes
            node.attributes['visible'] = visible
            if visible:
                visible_nodes += 1

        # Apply edge filters
        for edge in graph_data.edges:
            visible = True
            for filter_key, filter_value in filters.get('edges', {}).items():
                if filter_key in edge.attributes:
                    if edge.attributes[filter_key] != filter_value:
                        visible = False
                        break

            # Store visibility in edge attributes
            edge.attributes['visible'] = visible
            if visible:
                visible_edges += 1

        return {'nodes': visible_nodes, 'edges': visible_edges}


# Create global instance
visualization_api = VisualizationAPI()
