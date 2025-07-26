import pytest
"""
import pytest
Spec 3 Integration Tests - Graph Visualization

This module contains comprehensive integration tests for Spec 3 (Graph Visualization)
ensuring seamless integration with Spec 1 (Data Import) and Spec 2 (Graph Engine).
"""

import json
import time
from datetime import datetime

# Import test fixtures and utilities
from ..conftest import sample_csv_data
from src.network_ui.api.app import create_app

# Import API instances
from src.network_ui.api.graph_engine import graph_engine_api
from src.network_ui.visualization.api.visualization import visualization_api

# Import visualization components for direct testing
from src.network_ui.visualization.config import get_default_config, get_performance_config
from src.network_ui.visualization.layouts import create_layout, LayoutParams
from src.network_ui.visualization.renderer import create_renderer
from src.network_ui.visualization.visual_mapping import VisualMappingEngine


@pytest.mark.integration
class TestSpec3Integration:
    """Test integration between all three specs: Data Import, Graph Engine, and Visualization."""

    @pytest.fixture
    def app(self):
        """Create test client."""
        return create_app()

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        # Clear graph storage before each test
        graph_engine_api.clear_graph()
        visualization_api._current_highlights.clear()
        visualization_api._current_filters = {}
        return app.test_client()

    def setup_method(self):
        """Setup for each test method."""
        # Clear graph storage before each test
        graph_engine_api.clear_graph()
        visualization_api._current_highlights.clear()
        visualization_api._current_filters = {}

    def test_full_pipeline_integration(self, client, sample_csv_data):
        """Test complete pipeline: Data Import → Graph Engine → Visualization."""

        # Step 1: Import data (Spec 1)
        import_data = {
            'filePath': 'data/test_data/test_data.csv',
            'mappingConfig': {
                'node_id': 'id',
                'node_name': 'name',
                'node_attributes': ['category', 'department', 'region']
            },
            'dataTypes': {
                'id': 'integer',
                'name': 'string',
                'category': 'string',
                'performance_score': 'float'
            }
        }

        response = client.post('/import',
                              data=json.dumps(import_data),
                              content_type='application/json')
        assert response.status_code == 200
        import_result = json.loads(response.data)
        assert import_result['success'] is True

        # Step 2: Verify graph creation (Spec 2)
        response = client.get('/api/v1/graph')
        assert response.status_code == 200
        graph_data = json.loads(response.data)
        assert len(graph_data['nodes']) > 0

                # Step 3: Apply layout and render (Spec 3)
        # First apply a layout
        layout_data = {
            'algorithm': 'force_directed',
            'graph_id': 'default',
            'parameters': {
                'iterations': 50,
                'animate': False
            }
        }

        response = client.post('/api/v1/visualization/layout',
                              data=json.dumps(layout_data),
                              content_type='application/json')
        assert response.status_code == 200

        # Then render the graph
        render_config = {
            'graph_id': 'default',
            'visual_mappings': {
                'nodes': {
                    'size': {
                        'attribute': 'performance_score',
                        'mapping_type': 'linear',
                        'scale_min': 8.0,
                        'scale_max': 20.0
                    },
                    'color': {
                        'attribute': 'category',
                        'mapping_type': 'categorical'
                    }
                }
            }
        }

        response = client.post('/api/v1/visualization/render',
                              data=json.dumps(render_config),
                              content_type='application/json')
        assert response.status_code == 200
        render_result = json.loads(response.data)
        assert render_result['status'] == 'rendered'
        assert 'stats' in render_result
        assert render_result['stats']['nodes_rendered'] > 0

    def test_layout_algorithm_switching(self, client, sample_csv_data):
        """Test switching between different layout algorithms."""

        # First import some data
        import_data = {
            'filePath': 'data/test_data/test_data.csv',
            'mappingConfig': {
                'node_id': 'id',
                'node_name': 'name'
            }
        }

        response = client.post('/import',
                              data=json.dumps(import_data),
                              content_type='application/json')
        assert response.status_code == 200

        # Test different layout algorithms
        algorithms = ['force_directed', 'circular', 'hierarchical', 'grid', 'random']

        for algorithm in algorithms:
            layout_data = {
                'algorithm': algorithm,
                'graph_id': 'default',
                'parameters': {
                    'iterations': 50,
                    'animate': False  # For faster testing
                }
            }

            response = client.post('/api/v1/visualization/layout',
                                  data=json.dumps(layout_data),
                                  content_type='application/json')
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['status'] == 'layout_applied'
            assert result['algorithm'] == algorithm

    def test_visual_mapping_configuration(self, client, sample_csv_data):
        """Test visual mapping configuration and application."""

        # Import data first
        import_data = {
            'filePath': 'data/test_data/test_data.csv',
            'mappingConfig': {
                'node_id': 'id',
                'node_name': 'name',
                'node_attributes': ['category', 'performance_score', 'revenue']
            }
        }

        response = client.post('/import',
                              data=json.dumps(import_data),
                              content_type='application/json')
        assert response.status_code == 200

        # Configure visual mappings
        mapping_data = {
            'mappings': {
                'nodes': {
                    'size': {
                        'attribute': 'revenue',
                        'mapping_type': 'linear',
                        'scale_min': 5.0,
                        'scale_max': 25.0
                    },
                    'color': {
                        'attribute': 'category',
                        'mapping_type': 'categorical',
                        'color_palette': ['#ff0000', '#00ff00', '#0000f', '#ffff00']
                    },
                    'opacity': {
                        'attribute': 'performance_score',
                        'mapping_type': 'linear',
                        'scale_min': 0.5,
                        'scale_max': 1.0
                    }
                }
            },
            'graph_id': 'default'
        }

        response = client.post('/api/v1/visualization/mapping',
                              data=json.dumps(mapping_data),
                              content_type='application/json')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['status'] == 'mappings_applied'

    def test_interaction_handling(self, client, sample_csv_data):
        """Test user interaction handling."""

        # Import and setup graph first
        import_data = {
            'filePath': 'data/test_data/test_data.csv',
            'mappingConfig': {'node_id': 'id', 'node_name': 'name'}
        }

        response = client.post('/import',
                              data=json.dumps(import_data),
                              content_type='application/json')
        assert response.status_code == 200

        # Test different interaction types
        interactions = [
            {
                'type': 'click',
                'coordinates': {'x': 100, 'y': 150},
                'target_id': 'node_1',
                'target_type': 'node'
            },
            {
                'type': 'hover',
                'coordinates': {'x': 200, 'y': 250},
                'target_id': 'node_2',
                'target_type': 'node'
            },
            {
                'type': 'zoom',
                'coordinates': {'x': 300, 'y': 350, 'delta': 1.2}
            },
            {
                'type': 'pan',
                'coordinates': {'deltaX': 50, 'deltaY': -30}
            }
        ]

        for interaction in interactions:
            response = client.post('/api/v1/visualization/interaction',
                                  data=json.dumps(interaction),
                                  content_type='application/json')
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['status'] == 'interaction_processed'

    def test_filtering_and_highlighting(self, client, sample_csv_data):
        """Test filtering and highlighting functionality."""

        # Import data
        import_data = {
            'filePath': 'data/test_data/test_data.csv',
            'mappingConfig': {
                'node_id': 'id',
                'node_name': 'name',
                'node_attributes': ['category', 'department']
            }
        }

        response = client.post('/import',
                              data=json.dumps(import_data),
                              content_type='application/json')
        assert response.status_code == 200

        # Apply filters
        filter_data = {
            'filters': {
                'nodes': {
                    'category': 'Engineering'
                }
            },
            'graph_id': 'default'
        }

        response = client.post('/api/v1/visualization/filter',
                              data=json.dumps(filter_data),
                              content_type='application/json')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['status'] == 'filters_applied'

        # Set highlights
        highlight_data = {
            'node_ids': ['1', '2'],
            'edge_ids': []
        }

        response = client.post('/api/v1/visualization/highlight',
                              data=json.dumps(highlight_data),
                              content_type='application/json')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['status'] == 'highlights_updated'

    def test_viewport_management(self, client):
        """Test viewport position and zoom management."""

        # Test viewport updates
        viewport_data = {
            'x': 100.0,
            'y': -50.0,
            'zoom': 1.5
        }

        response = client.post('/api/v1/visualization/viewport',
                              data=json.dumps(viewport_data),
                              content_type='application/json')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['status'] == 'viewport_updated'
        assert result['viewport']['x'] == 100.0
        assert result['viewport']['y'] == -50.0
        assert result['viewport']['zoom'] == 1.5

    def test_configuration_management(self, client):
        """Test visualization configuration management."""

        # Get current configuration
        response = client.get('/api/v1/visualization/config')
        assert response.status_code == 200
        config = json.loads(response.data)
        assert 'config' in config
        assert 'capabilities' in config
        assert 'available_layouts' in config

        # Update configuration
        new_config = {
            'rendering_engine': 'webgl',
            'canvas': {
                'width': 1200,
                'height': 800
            },
            'performance': {
                'max_nodes_full_render': 2000
            }
        }

        response = client.put('/api/v1/visualization/config',
                             data=json.dumps(new_config),
                             content_type='application/json')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['status'] == 'config_updated'

    def test_performance_with_large_dataset(self, client):
        """Test performance with larger datasets."""

        # This would typically use a larger test dataset
        # For now, we'll test the performance configuration
        performance_config = {
            'rendering_engine': 'webgl',
            'performance': {
                'enable_clustering': True,
                'level_of_detail': True,
                'batch_rendering': True,
                'max_nodes_full_render': 1000
            }
        }

        response = client.put('/api/v1/visualization/config',
                             data=json.dumps(performance_config),
                             content_type='application/json')
        assert response.status_code == 200

        # Verify performance optimizations are applied
        response = client.get('/api/v1/visualization/config')
        assert response.status_code == 200
        config = json.loads(response.data)
        assert config['config']['rendering_engine'] == 'webgl'
        assert config['config']['performance']['enable_clustering'] is True


@pytest.mark.integration
class TestSpec3Components:
    """Test individual Spec 3 components in isolation."""

    def test_layout_algorithms(self):
        """Test layout algorithm implementations."""
        from src.network_ui.core.models import Node, GraphData

        # Create test graph
        nodes = []
        for i in range(5):
            node = Node()
            node.id = str(i)
            node.name = f"Node {i}"
            node.position = {"x": 0.0, "y": 0.0}
            nodes.append(node)

        graph_data = GraphData()
        graph_data.nodes = nodes

        # Test different layouts
        layout_params = LayoutParams(width=400, height=300, iterations=10)

        algorithms = ['force_directed', 'circular', 'hierarchical', 'grid', 'random']
        for algorithm in algorithms:
            layout = create_layout(algorithm, layout_params)
            result_graph = layout.apply_layout(graph_data)

            # Verify positions were updated
            for node in result_graph.nodes:
                assert node.position["x"] != 0.0 or node.position["y"] != 0.0

    def test_visual_mapping_engine(self):
        """Test visual mapping engine functionality."""
        from src.network_ui.core.models import Node, GraphData

        # Create test nodes with attributes
        nodes = []
        categories = ['A', 'B', 'C']
        scores = [10, 20, 30, 15, 25]

        for i in range(5):
            node = Node()
            node.id = str(i)
            node.attributes = {
                'category': categories[i % len(categories)],
                'score': scores[i]
            }
            node.visual_properties = {'size': 10.0, 'color': '#000000'}
            nodes.append(node)

        graph_data = GraphData()
        graph_data.nodes = nodes

        # Test visual mapping
        mapping_engine = VisualMappingEngine()

        mappings = {
            'nodes': {
                'size': {
                    'attribute': 'score',
                    'mapping_type': 'linear',
                    'scale_min': 5.0,
                    'scale_max': 20.0
                },
                'color': {
                    'attribute': 'category',
                    'mapping_type': 'categorical'
                }
            }
        }

        # Apply mappings
        mapping_engine.apply_mappings(graph_data, mappings)

        # Verify mappings were applied
        for node in nodes:
            # Size should be mapped from score
            assert node.visual_properties['size'] >= 5.0
            assert node.visual_properties['size'] <= 20.0

            # Color should be mapped from category
            assert 'color' in node.visual_properties

    def test_renderer_initialization(self):
        """Test renderer initialization and basic functionality."""
        config = get_default_config()

        # Test Canvas renderer
        canvas_renderer = create_renderer(config)
        assert canvas_renderer.initialize() is True
        assert canvas_renderer.config == config

        # Test WebGL renderer
        config.rendering_engine = config.rendering_engine.__class__.WEBGL
        webgl_renderer = create_renderer(config)
        assert webgl_renderer.initialize() is True

    def test_configuration_system(self):
        """Test the configuration system."""
        # Test default configuration
        default_config = get_default_config()
        assert default_config.canvas.width == 800
        assert default_config.canvas.height == 600

        # Test performance configuration
        perf_config = get_performance_config()
        assert perf_config.performance.enable_clustering is True
        assert perf_config.performance.level_of_detail is True

        # Test configuration serialization
        config_dict = default_config.to_dict()
        assert isinstance(config_dict, dict)
        assert 'canvas' in config_dict
        assert 'rendering_engine' in config_dict

        # Test configuration deserialization
        restored_config = default_config.__class__.from_dict(config_dict)
        assert restored_config.canvas.width == default_config.canvas.width


@pytest.mark.integration
class TestSpec3ErrorHandling:
    """Test error handling and edge cases for Spec 3."""

    @pytest.fixture
    def app(self):
        """Create test client."""
        return create_app()

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        # Clear graph storage before each test
        graph_engine_api.clear_graph()
        visualization_api._current_highlights.clear()
        visualization_api._current_filters = {}
        return app.test_client()

    def test_invalid_layout_algorithm(self, client):
        """Test handling of invalid layout algorithm."""
        layout_data = {
            'algorithm': 'invalid_algorithm',
            'graph_id': 'default'
        }

        response = client.post('/api/v1/visualization/layout',
                              data=json.dumps(layout_data),
                              content_type='application/json')
        assert response.status_code == 400
        result = json.loads(response.data)
        assert 'error' in result

    def test_invalid_visual_mapping(self, client):
        """Test handling of invalid visual mapping configuration."""
        mapping_data = {
            'mappings': {
                'nodes': {
                    'size': {
                        'attribute': 'nonexistent_attr',
                        'mapping_type': 'invalid_type'
                    }
                }
            }
        }

        response = client.post('/api/v1/visualization/mapping',
                              data=json.dumps(mapping_data),
                              content_type='application/json')
        assert response.status_code == 400

    def test_missing_graph_data(self, client):
        """Test handling when graph data doesn't exist."""
        render_data = {
            'graph_id': 'nonexistent_graph'
        }

        response = client.post('/api/v1/visualization/render',
                              data=json.dumps(render_data),
                              content_type='application/json')
        assert response.status_code == 404
        result = json.loads(response.data)
        assert result['error'] == 'Graph not found'
