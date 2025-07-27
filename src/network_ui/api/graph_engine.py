"""
Graph Engine API for managing graph data structures and operations.
Spec 2:   Graph Engine Implementation
"""

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from flask import Flask, request, jsonify, current_app, Blueprint
from ..core.models import GraphData, Node, Edge
from ..core.importer import DataImporter

class GraphEngineAPI: 
    """Graph Engine API class for managing graph operations."""

    def __init__(self): 
        """Initialize the Graph Engine API."""
        self.logger = self._setup_logging()
  # Global graph storage (in production, this would be a database)
        self._graph_storage:   Dict[str, GraphData] = {}
        self._default_graph_id = "default"

  # Create default graph
        self._graph_storage[self._default_graph_id] = GraphData()

    def _setup_logging(self) -> logging.Logger:  
        """Setup logging for the graph engine."""
        logger = logging.getLogger('GraphEngineAPI')
        logger.setLevel(logging.INFO)

        if not logger.handlers:  
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def get_graph(self, graph_id:   str = None) -> Optional[GraphData]: 
        """Get graph by ID or default graph."""
        graph_id = graph_id or self._default_graph_id
        return self._graph_storage.get(graph_id)

    def clear_graph(self, graph_id:   str = None) -> None: 
        """Clear graph storage (for testing)."""
        graph_id = graph_id or self._default_graph_id
        self._graph_storage[graph_id] = GraphData()

    def create_blueprint(self) -> Blueprint: 
        """Create Flask blueprint with all graph engine endpoints."""
        bp = Blueprint('graph_engine', __name__, url_prefix='/api/v1')

        @bp.route('/graph', methods=['GET'])
        def get_graph(): 
            """Retrieve the entire graph structure."""
            try: 
                graph_id = request.args.get('graph_id', self._default_graph_id)
                graph = self.get_graph(graph_id)

                if not graph: 
                    return jsonify({'error':  'Graph not found'}), 404

                return jsonify({
                    'nodes':  [self._serialize_node(node) for node in graph.nodes],
                    'edges':  [self._serialize_edge(edge) for edge in graph.edges],
                    'metadata':  graph.metadata,
                    'created_at':  graph.created_at.isoformat(),
                    'total_nodes':  len(graph.nodes),
                    'total_edges':  len(graph.edges)
                })

            except Exception as e: 
                self.logger.error(f"Error retrieving graph:   {str(e)}")
                return jsonify({'error':  'Internal server error'}), 500

        @bp.route('/nodes', methods=['POST'])
        def create_node(): 
            """Add a new node to the graph."""
            try: 
                data = request.get_json()
                if not data: 
                    return jsonify({'error':  'No data provided'}), 400

                graph_id = data.get('graph_id', self._default_graph_id)
                graph = self.get_graph(graph_id)

                if not graph: 
                    return jsonify({'error':  'Graph not found'}), 404

  # Create node from data
                node_kwargs = {
                    'name':  data.get('name', ''),
                    'level':  data.get('level', 1),
                    'attributes':  data.get('attributes', {}),
                    'position':  data.get('position', {"x":  0.0, "y":  0.0}),
                    'visual_properties':  data.get('visual_properties', {})
                }

  # Only set ID if provided, otherwise let default factory generate it
                if 'id' in data and data['id']: 
                    node_kwargs['id'] = data['id']

                node = Node(**node_kwargs)

  # Check for duplicate ID
                if graph.get_node_by_id(node.id): 
                    return jsonify({'error':  f'Node with ID {node.id} already exists'}), 409

                graph.add_node(node)
                self.logger.info(f"Created node {node.id}")

                return jsonify({
                    'success':  True,
                    'node':  self._serialize_node(node)
                }), 201

            except Exception as e: 
                self.logger.error(f"Error creating node:   {str(e)}")
                return jsonify({'error':  'Internal server error'}), 500

        @bp.route('/nodes/<node_id>', methods=['GET'])
        def get_node(node_id:   str): 
            """Get a specific node by ID."""
            try: 
                graph_id = request.args.get('graph_id', self._default_graph_id)
                graph = self.get_graph(graph_id)

                if not graph: 
                    return jsonify({'error':  'Graph not found'}), 404

                node = graph.get_node_by_id(node_id)
                if not node: 
                    return jsonify({'error':  'Node not found'}), 404

                return jsonify(self._serialize_node(node))

            except Exception as e: 
                self.logger.error(f"Error retrieving node {node_id}:  {str(e)}")
                return jsonify({'error':  'Internal server error'}), 500

        @bp.route('/nodes/<node_id>', methods=['PUT'])
        def update_node(node_id:   str): 
            """Update a node's properties."""
            try: 
                data = request.get_json()
                if not data: 
                    return jsonify({'error':  'No data provided'}), 400

                graph_id = data.get('graph_id', self._default_graph_id)
                graph = self.get_graph(graph_id)

                if not graph: 
                    return jsonify({'error':  'Graph not found'}), 404

                if not graph.update_node(node_id, data): 
                    return jsonify({'error':  'Node not found'}), 404

                updated_node = graph.get_node_by_id(node_id)
                self.logger.info(f"Updated node {node_id}")

                return jsonify({
                    'success':  True,
                    'node':  self._serialize_node(updated_node)
                })

            except Exception as e: 
                self.logger.error(f"Error updating node {node_id}:  {str(e)}")
                return jsonify({'error':  'Internal server error'}), 500

        @bp.route('/nodes/<node_id>', methods=['DELETE'])
        def delete_node(node_id:   str): 
            """Delete a node and its connected edges."""
            try: 
                graph_id = request.args.get('graph_id', self._default_graph_id)
                graph = self.get_graph(graph_id)

                if not graph: 
                    return jsonify({'error':  'Graph not found'}), 404

                if not graph.remove_node(node_id): 
                    return jsonify({'error':  'Node not found'}), 404

                self.logger.info(f"Deleted node {node_id}")

                return jsonify({'success':  True, 'message':  f'Node {node_id} deleted'})

            except Exception as e: 
                self.logger.error(f"Error deleting node {node_id}:  {str(e)}")
                return jsonify({'error':  'Internal server error'}), 500

        @bp.route('/edges', methods=['POST'])
        def create_edge(): 
            """Add a new edge to the graph."""
            try: 
                data = request.get_json()
                if not data: 
                    return jsonify({'error':  'No data provided'}), 400

                graph_id = data.get('graph_id', self._default_graph_id)
                graph = self.get_graph(graph_id)

                if not graph: 
                    return jsonify({'error':  'Graph not found'}), 404

  # Validate source and target nodes exist
                source_id = data.get('source')
                target_id = data.get('target')

                if not source_id or not target_id: 
                    return jsonify({'error':  'Source and target are required'}), 400

                if not graph.get_node_by_id(source_id): 
                    return jsonify({'error':  f'Source node {source_id} not found'}), 404

                if not graph.get_node_by_id(target_id): 
                    return jsonify({'error':  f'Target node {target_id} not found'}), 404

  # Create edge from data
                edge_kwargs = {
                    'source':  source_id,
                    'target':  target_id,
                    'relationship_type':  data.get('relationship_type', 'default'),
                    'weight':  data.get('weight', 1.0),
                    'directed':  data.get('directed', True),
                    'attributes':  data.get('attributes', {}),
                    'visual_properties':  data.get('visual_properties', {})
                }

  # Only set ID if provided, otherwise let default factory generate it
                if 'id' in data and data['id']: 
                    edge_kwargs['id'] = data['id']

                edge = Edge(**edge_kwargs)

  # Check for duplicate ID
                if graph.get_edge_by_id(edge.id): 
                    return jsonify({'error':  f'Edge with ID {edge.id} already exists'}), 409

                graph.add_edge(edge)
                self.logger.info(f"Created edge {edge.id}")

                return jsonify({
                    'success':  True,
                    'edge':  self._serialize_edge(edge)
                }), 201

            except Exception as e: 
                self.logger.error(f"Error creating edge:   {str(e)}")
                return jsonify({'error':  'Internal server error'}), 500

        @bp.route('/edges/<edge_id>', methods=['GET'])
        def get_edge(edge_id:   str): 
            """Get a specific edge by ID."""
            try: 
                graph_id = request.args.get('graph_id', self._default_graph_id)
                graph = self.get_graph(graph_id)

                if not graph: 
                    return jsonify({'error':  'Graph not found'}), 404

                edge = graph.get_edge_by_id(edge_id)
                if not edge: 
                    return jsonify({'error':  'Edge not found'}), 404

                return jsonify(self._serialize_edge(edge))

            except Exception as e: 
                self.logger.error(f"Error retrieving edge {edge_id}:  {str(e)}")
                return jsonify({'error':  'Internal server error'}), 500

        @bp.route('/edges/<edge_id>', methods=['PUT'])
        def update_edge(edge_id:   str): 
            """Update an edge's properties."""
            try: 
                data = request.get_json()
                if not data: 
                    return jsonify({'error':  'No data provided'}), 400

                graph_id = data.get('graph_id', self._default_graph_id)
                graph = self.get_graph(graph_id)

                if not graph: 
                    return jsonify({'error':  'Graph not found'}), 404

                if not graph.update_edge(edge_id, data): 
                    return jsonify({'error':  'Edge not found'}), 404

                updated_edge = graph.get_edge_by_id(edge_id)
                self.logger.info(f"Updated edge {edge_id}")

                return jsonify({
                    'success':  True,
                    'edge':  self._serialize_edge(updated_edge)
                })

            except Exception as e: 
                self.logger.error(f"Error updating edge {edge_id}:  {str(e)}")
                return jsonify({'error':  'Internal server error'}), 500

        @bp.route('/edges/<edge_id>', methods=['DELETE'])
        def delete_edge(edge_id:   str): 
            """Delete an edge."""
            try: 
                graph_id = request.args.get('graph_id', self._default_graph_id)
                graph = self.get_graph(graph_id)

                if not graph: 
                    return jsonify({'error':  'Graph not found'}), 404

                if not graph.remove_edge(edge_id): 
                    return jsonify({'error':  'Edge not found'}), 404

                self.logger.info(f"Deleted edge {edge_id}")

                return jsonify({'success':  True, 'message':  f'Edge {edge_id} deleted'})

            except Exception as e: 
                self.logger.error(f"Error deleting edge {edge_id}:  {str(e)}")
                return jsonify({'error':  'Internal server error'}), 500

        @bp.route('/nodes/<node_id>/neighbors', methods=['GET'])
        def get_neighbors(node_id:   str): 
            """Get neighbors of a node."""
            try: 
                graph_id = request.args.get('graph_id', self._default_graph_id)
                direction = request.args.get('direction', 'all')

                graph = self.get_graph(graph_id)

                if not graph: 
                    return jsonify({'error':  'Graph not found'}), 404

                if not graph.get_node_by_id(node_id): 
                    return jsonify({'error':  'Node not found'}), 404

                neighbors = graph.get_neighbors(node_id, direction)

                return jsonify({
                    'node_id':  node_id,
                    'direction':  direction,
                    'neighbors':  neighbors,
                    'count':  len(neighbors)
                })

            except Exception as e: 
                self.logger.error(f"Error getting neighbors for node {node_id}:  {str(e)}")
                return jsonify({'error':  'Internal server error'}), 500

        @bp.route('/nodes/query', methods=['POST'])
        def query_nodes(): 
            """Query nodes based on filters."""
            try: 
                data = request.get_json()
                if not data: 
                    return jsonify({'error':  'No query filters provided'}), 400

                graph_id = data.get('graph_id', self._default_graph_id)
                filters = data.get('filters', {})

                graph = self.get_graph(graph_id)

                if not graph: 
                    return jsonify({'error':  'Graph not found'}), 404

                matching_nodes = graph.query_nodes(**filters)

                return jsonify({
                    'filters':  filters,
                    'results':  [self._serialize_node(node) for node in matching_nodes],
                    'count':  len(matching_nodes)
                })

            except Exception as e: 
                self.logger.error(f"Error querying nodes:   {str(e)}")
                return jsonify({'error':  'Internal server error'}), 500

        @bp.route('/edges/query', methods=['POST'])
        def query_edges(): 
            """Query edges based on filters."""
            try: 
                data = request.get_json()
                if not data: 
                    return jsonify({'error':  'No query filters provided'}), 400

                graph_id = data.get('graph_id', self._default_graph_id)
                filters = data.get('filters', {})

                graph = self.get_graph(graph_id)

                if not graph: 
                    return jsonify({'error':  'Graph not found'}), 404

                matching_edges = graph.query_edges(**filters)

                return jsonify({
                    'filters':  filters,
                    'results':  [self._serialize_edge(edge) for edge in matching_edges],
                    'count':  len(matching_edges)
                })

            except Exception as e: 
                self.logger.error(f"Error querying edges:   {str(e)}")
                return jsonify({'error':  'Internal server error'}), 500

        @bp.route('/graph/undo', methods=['POST'])
        def undo_action(): 
            """Undo the last graph modification."""
            try: 
  # Handle both JSON and empty requests
                if request.content_type == 'application / json': 
                    data = request.get_json() or {}
                else: 
                    data = {}
                graph_id = data.get('graph_id', self._default_graph_id)

                graph = self.get_graph(graph_id)

                if not graph: 
                    return jsonify({'error':  'Graph not found'}), 404

                if graph.undo(): 
                    self.logger.info("Undo operation successful")
                    return jsonify({
                        'success':  True,
                        'message':  'Action undone successfully',
                        'can_undo':  graph.can_undo(),
                        'can_redo':  graph.can_redo()
                    })
                else: 
                    return jsonify({
                        'success':  False,
                        'message':  'Nothing to undo',
                        'can_undo':  False,
                        'can_redo':  graph.can_redo()
                    })

            except Exception as e: 
                self.logger.error(f"Error during undo:   {str(e)}")
                return jsonify({'error':  'Internal server error'}), 500

        @bp.route('/graph/redo', methods=['POST'])
        def redo_action(): 
            """Redo the next graph modification."""
            try: 
  # Handle both JSON and empty requests
                if request.content_type == 'application / json': 
                    data = request.get_json() or {}
                else: 
                    data = {}
                graph_id = data.get('graph_id', self._default_graph_id)

                graph = self.get_graph(graph_id)

                if not graph: 
                    return jsonify({'error':  'Graph not found'}), 404

                if graph.redo(): 
                    self.logger.info("Redo operation successful")
                    return jsonify({
                        'success':  True,
                        'message':  'Action redone successfully',
                        'can_undo':  graph.can_undo(),
                        'can_redo':  graph.can_redo()
                    })
                else: 
                    return jsonify({
                        'success':  False,
                        'message':  'Nothing to redo',
                        'can_undo':  graph.can_undo(),
                        'can_redo':  False
                    })

            except Exception as e: 
                self.logger.error(f"Error during redo:   {str(e)}")
                return jsonify({'error':  'Internal server error'}), 500

        return bp

    def _serialize_node(self, node:   Node) -> Dict[str, Any]: 
        """Serialize a node for JSON response."""
        return {
            'id':  node.id,
            'name':  node.name,
            'level':  node.level,
            'attributes':  node.attributes,
            'kpis':  node.kpis,
            'position':  node.position,
            'visual_properties':  node.visual_properties,
            'created_at':  node.created_at.isoformat(),
            'updated_at':  node.updated_at.isoformat()
        }

    def _serialize_edge(self, edge:   Edge) -> Dict[str, Any]: 
        """Serialize an edge for JSON response."""
        return {
            'id':  edge.id,
            'source':  edge.source,
            'target':  edge.target,
            'relationship_type':  edge.relationship_type,
            'level':  edge.level,
            'weight':  edge.weight,
            'directed':  edge.directed,
            'attributes':  edge.attributes,
            'kpi_components':  edge.kpi_components,
            'visual_properties':  edge.visual_properties,
            'created_at':  edge.created_at.isoformat()
        }

# Global instance for the API
graph_engine_api = GraphEngineAPI()
