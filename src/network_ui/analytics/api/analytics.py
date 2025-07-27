"""
Analytics API for graph analysis endpoints.
Implements REST API for Spec 3:   Graph Analytics.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Blueprint, request, jsonify

from ...core.models import GraphData, Node, Edge
from ..algorithms import GraphAnalyzer
from ..community import CommunityDetection
from ..connectivity import ConnectivityAnalyzer

class AnalyticsAPI: 
    """Analytics API class for graph analysis endpoints."""

    def __init__(self): 
        self.logger = logging.getLogger(__name__)
        self.analyzer = GraphAnalyzer()
        self.community_detector = CommunityDetection()
        self.connectivity_analyzer = ConnectivityAnalyzer()

    def create_blueprint(self) -> Blueprint: 
        """Create Flask blueprint for analytics endpoints."""
        bp = Blueprint('analytics', __name__, url_prefix='/api/v1/analytics')

        @bp.route('/analyze', methods=['POST'])
        def analyze(): 
            """Execute specified graph analysis algorithm."""
            try: 
  # Check content type
                if not request.is_json:  
                    return jsonify({'error':  'Content-Type must be application/json'}), 400

                data = request.get_json()

                if not data: 
  # Check if the request has content but failed to parse
                    if request.data:  
                        return jsonify({'error':  'Invalid JSON format'}), 400
                    else: 
                        return jsonify({'error':  'No data provided'}), 400

                algorithm = data.get('algorithm')
                parameters = data.get('parameters', {})
                graph_data_dict = data.get('graphData')

                if not algorithm: 
                    return jsonify({'error':  'Algorithm not specified'}), 400

                if not graph_data_dict: 
                    return jsonify({'error':  'Graph data not provided'}), 400

  # Convert dict to GraphData object
                graph_data = self._dict_to_graph_data(graph_data_dict)

  # Execute analysis
                result = self._execute_analysis(algorithm, parameters, graph_data)

                if not result.success:  
                    return jsonify({
                        'success':  False,
                        'error':  result.error_message,
                        'algorithm':  algorithm
                    }), 400

  # Ensure results are JSON serializable
                serializable_results = self._make_json_serializable(result.results)
                serializable_visual_mapping = self._make_json_serializable(result.visual_mapping)
                serializable_metadata = self._make_json_serializable(result.metadata)

                response = {
                    'success':  True,
                    'algorithm':  algorithm,  # Use the requested algorithm name, not the internal one
                    'results':  serializable_results,
                    'visual_mapping':  serializable_visual_mapping,
                    'metadata':  serializable_metadata,
                    'timestamp':  datetime.now().isoformat()
                }

                return jsonify(response)

            except Exception as e: 
                self.logger.error(f"Error in analyze endpoint:   {str(e)}")
                return jsonify({'error':  str(e)}), 500

        @bp.route('/algorithms', methods=['GET'])
        def get_algorithms(): 
            """Get available analysis algorithms."""
            try: 
                algorithms = self.analyzer.get_available_algorithms()

  # Add community detection algorithms
                algorithms.update({
                    "louvain_modularity":  {
                        "description":  "Detect communities using Louvain modularity optimization",
                        "parameters":  {}
                    },
                    "girvan_newman":  {
                        "description":  "Detect communities using Girvan-Newman algorithm",
                        "parameters":  {
                            "max_communities":  {"type":  "integer", "required":  False, "default":  10}
                        }
                    },
                    "label_propagation":  {
                        "description":  "Detect communities using label propagation",
                        "parameters":  {}
                    }
                })

  # Add connectivity algorithms
                algorithms.update({
                    "connected_components":  {
                        "description":  "Find connected components in the graph",
                        "parameters":  {}
                    },
                    "cycle_detection":  {
                        "description":  "Detect cycles in the graph",
                        "parameters":  {}
                    },
                    "bridge_detection":  {
                        "description":  "Find bridge edges in the graph",
                        "parameters":  {}
                    },
                    "articulation_points":  {
                        "description":  "Find articulation points in the graph",
                        "parameters":  {}
                    },
                    "graph_density":  {
                        "description":  "Calculate graph density and metrics",
                        "parameters":  {}
                    }
                })

                return jsonify({
                    'algorithms':  algorithms,
                    'count':  len(algorithms)
                })

            except Exception as e: 
                self.logger.error(f"Error in get_algorithms endpoint:   {str(e)}")
                return jsonify({'error':  str(e)}), 500

        @bp.route('/health', methods=['GET'])
        def health(): 
            """Analytics API health check."""
            return jsonify({
                'status':  'healthy',
                'module':  'analytics',
                'version':  '1.0.0',
                'timestamp':  datetime.now().isoformat()
            })

        return bp

    def _execute_analysis(self, algorithm:   str, parameters:   Dict[str, Any],
                         graph_data:   GraphData): 
        """Execute the specified analysis algorithm."""
  # Core algorithms (pathfinding, centrality)
        if algorithm in ['shortest_path', 'all_paths', 'degree_centrality',
                        'betweenness_centrality', 'closeness_centrality', 'eigenvector_centrality']: 
            return self.analyzer.analyze(algorithm, parameters, graph_data)

  # Community detection algorithms
        elif algorithm == 'louvain_modularity': 
            return self.community_detector.louvain_modularity(graph_data)

        elif algorithm == 'girvan_newman': 
            max_communities = parameters.get('max_communities', 10)
            return self.community_detector.girvan_newman(graph_data, max_communities)

        elif algorithm == 'label_propagation': 
            return self.community_detector.label_propagation(graph_data)

  # Connectivity algorithms
        elif algorithm == 'connected_components': 
            return self.connectivity_analyzer.connected_components(graph_data)

        elif algorithm == 'cycle_detection': 
            return self.connectivity_analyzer.cycle_detection(graph_data)

        elif algorithm == 'bridge_detection': 
            return self.connectivity_analyzer.bridge_detection(graph_data)

        elif algorithm == 'articulation_points': 
            return self.connectivity_analyzer.articulation_points(graph_data)

        elif algorithm == 'graph_density': 
            return self.connectivity_analyzer.graph_density(graph_data)

        else: 
            from ..algorithms import AnalysisResult
            return AnalysisResult(
                algorithm=algorithm,
                results=None,
                success=False,
                error_message=f"Unknown algorithm:   {algorithm}"
            )

    def _dict_to_graph_data(self, graph_dict:   Dict[str, Any]) -> GraphData: 
        """Convert dictionary to GraphData object."""
        graph_data = GraphData()

  # Add nodes
        for node_dict in graph_dict.get('nodes', []): 
            node = Node(
                id=node_dict.get('id', ''),
                name=node_dict.get('name', ''),
                attributes=node_dict.get('attributes', {})
            )
            graph_data.add_node(node)

  # Add edges
        for edge_dict in graph_dict.get('edges', []): 
            edge = Edge(
                id=edge_dict.get('id', ''),
                source=edge_dict.get('source', ''),
                target=edge_dict.get('target', ''),
                weight=edge_dict.get('weight', 1.0),
                directed=edge_dict.get('directed', False),
                attributes=edge_dict.get('attributes', {})
            )
            graph_data.add_edge(edge)

        return graph_data

    def _make_json_serializable(self, obj): 
        """Convert objects to JSON serializable format."""
        if obj is None: 
            return None
        elif isinstance(obj, (str, int, float, bool)): 
            return obj
        elif isinstance(obj, (list, tuple)): 
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, dict): 
            return {str(k):  self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, set): 
            return list(obj)
        elif hasattr(obj, '__dict__'): 
            return self._make_json_serializable(obj.__dict__)
        else: 
            return str(obj)
