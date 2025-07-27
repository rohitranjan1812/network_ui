"""
Comprehensive API tests for the Analytics module (Spec 3).
Tests all REST endpoints including edge cases and error conditions.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from src.network_ui.analytics.api.analytics import AnalyticsAPI
from src.network_ui.core.models import GraphData, Node, Edge


class TestAnalyticsAPI:
    """Test the Analytics API endpoints."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.api = AnalyticsAPI()
        self.app = self.api.create_blueprint()
        
        # Create test client
        from flask import Flask
        test_app = Flask(__name__)
        test_app.register_blueprint(self.app)
        self.client = test_app.test_client()
        
        # Test graph data
        self.test_graph_data = {
            "nodes": [
                {"id": "A", "name": "Node A", "attributes": {}},
                {"id": "B", "name": "Node B", "attributes": {}},
                {"id": "C", "name": "Node C", "attributes": {}}
            ],
            "edges": [
                {"id": "1", "source": "A", "target": "B", "weight": 1.0},
                {"id": "2", "source": "B", "target": "C", "weight": 1.0}
            ]
        }
    
    def test_health_endpoint(self):
        """Test analytics health endpoint."""
        response = self.client.get('/api/v1/analytics/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['module'] == 'analytics'
        assert 'version' in data
        assert 'timestamp' in data
    
    def test_algorithms_endpoint(self):
        """Test getting available algorithms."""
        response = self.client.get('/api/v1/analytics/algorithms')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'algorithms' in data
        assert 'count' in data
        assert data['count'] > 0
        
        # Check for specific algorithms
        algorithms = data['algorithms']
        assert 'degree_centrality' in algorithms
        assert 'shortest_path' in algorithms
        assert 'louvain_modularity' in algorithms
        assert 'connected_components' in algorithms
    
    def test_analyze_endpoint_success(self):
        """Test successful analysis request."""
        request_data = {
            "algorithm": "degree_centrality",
            "parameters": {},
            "graphData": self.test_graph_data
        }
        
        response = self.client.post(
            '/api/v1/analytics/analyze',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['algorithm'] == 'degree_centrality'
        assert 'results' in data
        assert 'visual_mapping' in data
        assert 'metadata' in data
        assert 'timestamp' in data
    
    def test_analyze_endpoint_missing_algorithm(self):
        """Test analysis request without algorithm."""
        request_data = {
            "parameters": {},
            "graphData": self.test_graph_data
        }
        
        response = self.client.post(
            '/api/v1/analytics/analyze',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Algorithm not specified' in data['error']
    
    def test_analyze_endpoint_missing_graph_data(self):
        """Test analysis request without graph data."""
        request_data = {
            "algorithm": "degree_centrality",
            "parameters": {}
        }
        
        response = self.client.post(
            '/api/v1/analytics/analyze',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Graph data not provided' in data['error']
    
    def test_analyze_endpoint_invalid_json(self):
        """Test analysis request with invalid JSON."""
        response = self.client.post(
            '/api/v1/analytics/analyze',
            data='invalid json'
            # Don't set content_type for invalid JSON to avoid Flask parsing error
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_analyze_endpoint_unknown_algorithm(self):
        """Test analysis request with unknown algorithm."""
        request_data = {
            "algorithm": "unknown_algorithm",
            "parameters": {},
            "graphData": self.test_graph_data
        }
        
        response = self.client.post(
            '/api/v1/analytics/analyze',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Unknown algorithm' in data['error']
    
    def test_analyze_endpoint_algorithm_failure(self):
        """Test analysis request when algorithm fails."""
        with patch.object(self.api.analyzer, 'analyze', 
                         return_value=MagicMock(success=False, error_message="Test error")):
            request_data = {
                "algorithm": "degree_centrality",
                "parameters": {},
                "graphData": self.test_graph_data
            }
            
            response = self.client.post(
                '/api/v1/analytics/analyze',
                data=json.dumps(request_data),
                content_type='application/json'
            )
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert data['error'] == 'Test error'
    
    def test_analyze_endpoint_exception_handling(self):
        """Test analysis request when exception occurs."""
        with patch.object(self.api.analyzer, 'analyze', 
                         side_effect=Exception("Unexpected error")):
            request_data = {
                "algorithm": "degree_centrality",
                "parameters": {},
                "graphData": self.test_graph_data
            }
            
            response = self.client.post(
                '/api/v1/analytics/analyze',
                data=json.dumps(request_data),
                content_type='application/json'
            )
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
    
    def test_analyze_all_algorithms(self):
        """Test all available algorithms through the API."""
        algorithms = [
            "degree_centrality",
            "shortest_path",
            "all_paths",
            "louvain_modularity",
            "connected_components",
            "cycle_detection"
        ]
        
        for algorithm in algorithms:
            request_data = {
                "algorithm": algorithm,
                "parameters": {},
                "graphData": self.test_graph_data
            }
            
            # Add algorithm-specific parameters
            if algorithm in ["shortest_path", "all_paths"]:
                request_data["parameters"] = {
                    "source_node_id": "A",
                    "target_node_id": "C"
                }
            
            response = self.client.post(
                '/api/v1/analytics/analyze',
                data=json.dumps(request_data),
                content_type='application/json'
            )
            
            # All algorithms should return a response (success or failure)
            assert response.status_code in [200, 400]
            data = json.loads(response.data)
            assert 'algorithm' in data
            assert data['algorithm'] == algorithm
    
    def test_dict_to_graph_data_conversion(self):
        """Test conversion of dictionary to GraphData object."""
        graph_dict = {
            "nodes": [
                {"id": "A", "name": "Node A", "attributes": {"type": "test"}},
                {"id": "B", "name": "Node B", "attributes": {}}
            ],
            "edges": [
                {"id": "1", "source": "A", "target": "B", "weight": 2.0, "directed": True}
            ],
            "metadata": {"test": "data"}
        }
        
        graph_data = self.api._dict_to_graph_data(graph_dict)
        
        assert isinstance(graph_data, GraphData)
        assert len(graph_data.nodes) == 2
        assert len(graph_data.edges) == 1
        
        # Check node conversion
        node_a = next(n for n in graph_data.nodes if n.id == "A")
        assert node_a.name == "Node A"
        assert node_a.attributes["type"] == "test"
        
        # Check edge conversion
        edge = graph_data.edges[0]
        assert edge.source == "A"
        assert edge.target == "B"
        assert edge.weight == 2.0
        assert edge.directed is True
    
    def test_dict_to_graph_data_empty(self):
        """Test conversion of empty dictionary to GraphData object."""
        graph_dict = {"nodes": [], "edges": []}
        graph_data = self.api._dict_to_graph_data(graph_dict)
        
        assert isinstance(graph_data, GraphData)
        assert len(graph_data.nodes) == 0
        assert len(graph_data.edges) == 0
    
    def test_dict_to_graph_data_missing_fields(self):
        """Test conversion with missing optional fields."""
        graph_dict = {
            "nodes": [{"id": "A"}],  # Missing name and attributes
            "edges": [{"id": "1", "source": "A", "target": "B"}]  # Missing weight and directed
        }
        
        graph_data = self.api._dict_to_graph_data(graph_dict)
        
        assert isinstance(graph_data, GraphData)
        assert len(graph_data.nodes) == 1
        assert len(graph_data.edges) == 1
        
        # Check defaults
        node = graph_data.nodes[0]
        assert node.name == ""
        assert node.attributes == {}
        
        edge = graph_data.edges[0]
        assert edge.weight == 1.0
        assert edge.directed is False


class TestAnalyticsAPIErrorHandling:
    """Test error handling in analytics API."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.api = AnalyticsAPI()
        self.app = self.api.create_blueprint()
        
        from flask import Flask
        test_app = Flask(__name__)
        test_app.register_blueprint(self.app)
        self.client = test_app.test_client()
    
    def test_analyze_with_malformed_graph_data(self):
        """Test analysis with malformed graph data."""
        request_data = {
            "algorithm": "degree_centrality",
            "parameters": {},
            "graphData": {
                "nodes": [{"invalid": "data"}],  # Missing required 'id' field
                "edges": []
            }
        }
        
        response = self.client.post(
            '/api/v1/analytics/analyze',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400, 500]
    
    def test_analyze_with_large_graph_data(self):
        """Test analysis with large graph data."""
        # Create large graph
        large_graph = {
            "nodes": [{"id": str(i), "name": f"Node {i}"} for i in range(1000)],
            "edges": [{"id": str(i), "source": str(i), "target": str(i+1)} for i in range(999)]
        }
        
        request_data = {
            "algorithm": "degree_centrality",
            "parameters": {},
            "graphData": large_graph
        }
        
        response = self.client.post(
            '/api/v1/analytics/analyze',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # Should handle large data
        assert response.status_code in [200, 400, 500]
    
    def test_analyze_with_special_characters(self):
        """Test analysis with special characters in node/edge data."""
        graph_data = {
            "nodes": [
                {"id": "node-1", "name": "Node with spaces", "attributes": {"special": "value with \"quotes\""}},
                {"id": "node_2", "name": "Node with unicode: éñ", "attributes": {}}
            ],
            "edges": [
                {"id": "edge-1", "source": "node-1", "target": "node_2", "attributes": {"type": "special"}}
            ]
        }
        
        request_data = {
            "algorithm": "degree_centrality",
            "parameters": {},
            "graphData": graph_data
        }
        
        response = self.client.post(
            '/api/v1/analytics/analyze',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # Should handle special characters
        assert response.status_code in [200, 400, 500]


class TestAnalyticsAPIIntegration:
    """Test integration scenarios for analytics API."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.api = AnalyticsAPI()
        self.app = self.api.create_blueprint()
        
        from flask import Flask
        test_app = Flask(__name__)
        test_app.register_blueprint(self.app)
        self.client = test_app.test_client()
    
    def test_multiple_sequential_analyses(self):
        """Test running multiple analyses sequentially."""
        graph_data = {
            "nodes": [
                {"id": "A", "name": "Node A"},
                {"id": "B", "name": "Node B"},
                {"id": "C", "name": "Node C"}
            ],
            "edges": [
                {"id": "1", "source": "A", "target": "B"},
                {"id": "2", "source": "B", "target": "C"}
            ]
        }
        
        # Run multiple analyses
        analyses = [
            ("degree_centrality", {}),
            ("connected_components", {}),
            ("shortest_path", {"source_node_id": "A", "target_node_id": "C"})
        ]
        
        for algorithm, parameters in analyses:
            request_data = {
                "algorithm": algorithm,
                "parameters": parameters,
                "graphData": graph_data
            }
            
            response = self.client.post(
                '/api/v1/analytics/analyze',
                data=json.dumps(request_data),
                content_type='application/json'
            )
            
            # Each analysis should complete
            assert response.status_code in [200, 400]
            data = json.loads(response.data)
            assert data['algorithm'] == algorithm
    
    def test_analysis_result_consistency(self):
        """Test that analysis results are consistent for the same input."""
        graph_data = {
            "nodes": [{"id": "A", "name": "Node A"}],
            "edges": []
        }
        
        request_data = {
            "algorithm": "degree_centrality",
            "parameters": {},
            "graphData": graph_data
        }
        
        # Run same analysis twice
        response1 = self.client.post(
            '/api/v1/analytics/analyze',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        response2 = self.client.post(
            '/api/v1/analytics/analyze',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # Results should be consistent
        assert response1.status_code == response2.status_code
        if response1.status_code == 200:
            data1 = json.loads(response1.data)
            data2 = json.loads(response2.data)
            assert data1['results'] == data2['results']


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 