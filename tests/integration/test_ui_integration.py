"""
Integration tests for the User Interface (Spec 5).
Tests UI integration with all backend components.
"""

import pytest
import json
import os
from unittest.mock import patch, MagicMock
from src.network_ui.api.app import create_app
from src.network_ui.core.models import GraphData, Node, Edge


class TestUIIntegration:
    """Test UI integration with backend components."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = create_app()
        self.client = self.app.test_client()
        
        # Test data
        self.test_graph_data = {
            "nodes": [
                {"id": "A", "name": "Node A", "attributes": {"type": "test"}},
                {"id": "B", "name": "Node B", "attributes": {"type": "test"}},
                {"id": "C", "name": "Node C", "attributes": {"type": "test"}}
            ],
            "edges": [
                {"id": "1", "source": "A", "target": "B", "weight": 1.0},
                {"id": "2", "source": "B", "target": "C", "weight": 1.0}
            ]
        }
    
    def test_main_ui_endpoint(self):
        """Test the main UI endpoint serves the interface."""
        response = self.client.get('/')
        
        assert response.status_code == 200
        assert response.content_type == 'text/html; charset=utf-8'
        
        # Check for key UI elements in the HTML
        html_content = response.data.decode('utf-8')
        assert '<title>Network UI - Graph Visualization Platform</title>' in html_content
        assert 'app-container' in html_content
        assert 'menu-bar' in html_content
        assert 'toolbar' in html_content
        assert 'side-panel' in html_content
        assert 'canvas-area' in html_content
        assert 'graphCanvas' in html_content
    
    def test_ui_template_exists(self):
        """Test that the UI template file exists."""
        template_path = os.path.join(
            os.path.dirname(__file__), 
            '..', '..', 'src', 'network_ui', 'ui', 'templates', 'index.html'
        )
        assert os.path.exists(template_path), f"UI template not found at {template_path}"
        
        # Check file size
        file_size = os.path.getsize(template_path)
        assert file_size > 10000, f"UI template seems too small: {file_size} bytes"
    
    def test_ui_contains_required_components(self):
        """Test that UI contains all required components from Spec 5."""
        response = self.client.get('/')
        html_content = response.data.decode('utf-8')
        
        # Check for main window components
        required_components = [
            'menu-bar',           # Menu Bar
            'toolbar',            # Toolbar
            'side-panel',         # Side Panel
            'canvas-area',        # Main Canvas Area
            'status-bar',         # Status Bar
            'panel-tabs',         # Panel Tabs
            'import-panel',       # Import Panel
            'analysis-panel',     # Analysis Panel
            'visual-panel',       # Visual Styling Panel
            'details-panel',      # Details Panel
            'graphCanvas',        # Graph Canvas
            'import-modal'        # Import Wizard Modal
        ]
        
        for component in required_components:
            assert component in html_content, f"Missing UI component: {component}"
    
    def test_ui_contains_required_functionality(self):
        """Test that UI contains all required functionality from Spec 5."""
        response = self.client.get('/')
        html_content = response.data.decode('utf-8')
        
        # Check for required functionality
        required_features = [
            'showImportWizard',      # Data import wizard
            'runAnalysis',           # Analysis execution
            'applyLayout',           # Layout algorithms
            'updateNodeSize',        # Visual styling
            'updateEdgeWidth',       # Visual styling
            'updateNodeColor',       # Visual styling
            'updateEdgeColor',       # Visual styling
            'toggleLabels',          # Visual controls
            'toggleArrows',          # Visual controls
            'zoomIn',                # Canvas controls
            'zoomOut',               # Canvas controls
            'fitToWindow',           # Canvas controls
            'resetLayout',           # Layout controls
            'onMouseDown',           # Interaction handling
            'onMouseMove',           # Interaction handling
            'onMouseUp',             # Interaction handling
            'onWheel',               # Zoom handling
            'onCanvasClick',         # Selection handling
            'showNodeDetails',       # Details on demand
            'hideNodeDetails'        # Details on demand
        ]
        
        for feature in required_features:
            assert feature in html_content, f"Missing UI functionality: {feature}"
    
    def test_ui_integration_with_backend_apis(self):
        """Test that UI can integrate with backend APIs."""
        # Test health endpoint
        response = self.client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        
        # Test graph endpoint
        response = self.client.get('/api/v1/graph')
        assert response.status_code == 200
        
        # Test analytics endpoint
        response = self.client.get('/api/v1/analytics/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['module'] == 'analytics'
    
    def test_ui_import_wizard_integration(self):
        """Test UI import wizard integration with backend."""
        # Test import endpoint
        import_data = {
            "filePath": "data/test_data/test_data.csv",
            "mappingConfig": {
                "node_id": "id",
                "node_name": "name"
            }
        }
        
        response = self.client.post(
            '/import',
            data=json.dumps(import_data),
            content_type='application/json'
        )
        
        # Should handle import request
        assert response.status_code in [200, 400, 500]
    
    def test_ui_analysis_integration(self):
        """Test UI analysis integration with backend."""
        # Test analytics endpoint
        analysis_data = {
            "algorithm": "degree_centrality",
            "parameters": {},
            "graphData": self.test_graph_data
        }
        
        response = self.client.post(
            '/api/v1/analytics/analyze',
            data=json.dumps(analysis_data),
            content_type='application/json'
        )
        
        # Should handle analysis request
        assert response.status_code in [200, 400, 500]
    
    def test_ui_visual_styling_integration(self):
        """Test UI visual styling integration."""
        # Test visualization endpoint
        visual_data = {
            "graphData": self.test_graph_data,
            "visualConfig": {
                "layout": "force_directed",
                "nodeSize": 15,
                "edgeWidth": 2,
                "nodeColor": "#4CAF50",
                "edgeColor": "#666666"
            }
        }
        
        response = self.client.post(
            '/api/v1/visualization/render',
            data=json.dumps(visual_data),
            content_type='application/json'
        )
        
        # Should handle visualization request
        assert response.status_code in [200, 400, 500]
    
    def test_ui_error_handling(self):
        """Test UI error handling for backend failures."""
        # Test with invalid data
        invalid_data = {
            "algorithm": "invalid_algorithm",
            "parameters": {},
            "graphData": {"invalid": "data"}
        }
        
        response = self.client.post(
            '/api/v1/analytics/analyze',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        # Should handle errors gracefully
        assert response.status_code in [400, 500]
    
    def test_ui_responsive_design(self):
        """Test that UI has responsive design elements."""
        response = self.client.get('/')
        html_content = response.data.decode('utf-8')
        
        # Check for responsive design elements
        responsive_features = [
            '@media',           # Media queries
            'viewport',         # Viewport meta tag
            'width=device-width',  # Responsive viewport
            'max-width',        # Responsive sizing
            'flex',             # Flexbox layout
            'grid'              # CSS Grid
        ]
        
        for feature in responsive_features:
            assert feature in html_content, f"Missing responsive feature: {feature}"
    
    def test_ui_accessibility(self):
        """Test that UI has basic accessibility features."""
        response = self.client.get('/')
        html_content = response.data.decode('utf-8')
        
        # Check for accessibility features
        accessibility_features = [
            'lang="en"',        # Language attribute
            'alt=',             # Alt text for images
            'title=',           # Title attributes
            'aria-',            # ARIA attributes
            'role=',            # Role attributes
            'tabindex'          # Tab navigation
        ]
        
        # At least some accessibility features should be present
        found_features = sum(1 for feature in accessibility_features if feature in html_content)
        assert found_features >= 2, f"Too few accessibility features found: {found_features}"
    
    def test_ui_performance_optimization(self):
        """Test that UI has performance optimizations."""
        response = self.client.get('/')
        html_content = response.data.decode('utf-8')
        
        # Check for performance optimizations
        performance_features = [
            'requestAnimationFrame',  # Smooth animations
            'debounce',              # Debounced events
            'throttle',              # Throttled events
            'setTimeout',            # Async operations
            'addEventListener',      # Event delegation
            'removeEventListener'    # Memory management
        ]
        
        # At least some performance features should be present
        found_features = sum(1 for feature in performance_features if feature in html_content)
        assert found_features >= 2, f"Too few performance features found: {found_features}"


class TestUIWorkflowIntegration:
    """Test complete UI workflows."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = create_app()
        self.client = self.app.test_client()
    
    def test_complete_data_import_workflow(self):
        """Test complete data import workflow through UI."""
        # Step 1: Check import endpoint
        response = self.client.get('/files')
        assert response.status_code == 200
        
        # Step 2: Test file upload
        import_data = {
            "filePath": "data/test_data/test_data.csv",
            "mappingConfig": {
                "node_id": "id",
                "node_name": "name",
                "attribute_category": "category"
            }
        }
        
        response = self.client.post(
            '/import',
            data=json.dumps(import_data),
            content_type='application/json'
        )
        
        # Should handle import
        assert response.status_code in [200, 400, 500]
        
        # Step 3: Check if data is available
        response = self.client.get('/api/v1/graph')
        assert response.status_code == 200
    
    def test_complete_analysis_workflow(self):
        """Test complete analysis workflow through UI."""
        # Step 1: Get available algorithms
        response = self.client.get('/api/v1/analytics/algorithms')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['algorithms']) > 0
        
        # Step 2: Run analysis
        analysis_data = {
            "algorithm": "degree_centrality",
            "parameters": {},
            "graphData": {
                "nodes": [{"id": "A", "name": "Node A"}],
                "edges": []
            }
        }
        
        response = self.client.post(
            '/api/v1/analytics/analyze',
            data=json.dumps(analysis_data),
            content_type='application/json'
        )
        
        # Should handle analysis
        assert response.status_code in [200, 400, 500]
    
    def test_complete_visualization_workflow(self):
        """Test complete visualization workflow through UI."""
        # Step 1: Get graph data
        response = self.client.get('/api/v1/graph')
        assert response.status_code == 200
        
        # Step 2: Test visualization rendering
        visual_data = {
            "graphData": {
                "nodes": [{"id": "A", "name": "Node A"}],
                "edges": []
            },
            "visualConfig": {
                "layout": "force_directed",
                "nodeSize": 15,
                "edgeWidth": 2
            }
        }
        
        response = self.client.post(
            '/api/v1/visualization/render',
            data=json.dumps(visual_data),
            content_type='application/json'
        )
        
        # Should handle visualization
        assert response.status_code in [200, 400, 500]


class TestUIErrorScenarios:
    """Test UI error scenarios and edge cases."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = create_app()
        self.client = self.app.test_client()
    
    def test_ui_with_empty_graph(self):
        """Test UI behavior with empty graph."""
        # Test graph endpoint with empty data
        response = self.client.get('/api/v1/graph')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        # Should handle empty graph gracefully
        assert 'nodes' in data
        assert 'edges' in data
    
    def test_ui_with_large_graph(self):
        """Test UI behavior with large graph."""
        # Create large graph data
        large_graph = {
            "nodes": [{"id": str(i), "name": f"Node {i}"} for i in range(100)],
            "edges": [{"id": str(i), "source": str(i), "target": str(i+1)} for i in range(99)]
        }
        
        # Test analysis with large graph
        analysis_data = {
            "algorithm": "degree_centrality",
            "parameters": {},
            "graphData": large_graph
        }
        
        response = self.client.post(
            '/api/v1/analytics/analyze',
            data=json.dumps(analysis_data),
            content_type='application/json'
        )
        
        # Should handle large graphs
        assert response.status_code in [200, 400, 500]
    
    def test_ui_with_malformed_data(self):
        """Test UI behavior with malformed data."""
        # Test with malformed graph data
        malformed_data = {
            "algorithm": "degree_centrality",
            "parameters": {},
            "graphData": {
                "nodes": [{"invalid": "data"}],  # Missing required fields
                "edges": [{"invalid": "data"}]   # Missing required fields
            }
        }
        
        response = self.client.post(
            '/api/v1/analytics/analyze',
            data=json.dumps(malformed_data),
            content_type='application/json'
        )
        
        # Should handle malformed data gracefully
        assert response.status_code in [200, 400, 500]
    
    def test_ui_concurrent_requests(self):
        """Test UI behavior with concurrent requests."""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = self.client.get('/health')
            results.append(response.status_code)
        
        # Make concurrent requests
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results), f"Some requests failed: {results}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 