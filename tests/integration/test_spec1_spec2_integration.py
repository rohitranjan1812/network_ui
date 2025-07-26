import pytest
"""
import pytest
Integration Tests for Spec 1 + Spec 2
Tests the integration between Data Import (Spec 1) and Graph Engine (Spec 2).
"""

import tempfile
import os
import json
from datetime import datetime

from src.network_ui.core.models import Node, Edge, GraphData, ImportConfig
from src.network_ui.core.importer import DataImporter
from src.network_ui.api.app import create_app
from src.network_ui.api.graph_engine import graph_engine_api


@pytest.mark.integration
class TestSpec1Spec2Integration:
    """Test integration between Spec 1 (Data Import) and Spec 2 (Graph Engine)."""

    @pytest.fixture
    def app(self):
        """Create test Flask app."""
        app = create_app()
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        # Clear graph storage before each test
        graph_engine_api.clear_graph()
        return app.test_client()

    @pytest.fixture
    def sample_csv_data(self):
        """Sample CSV data for testing."""
        return """id,name,department,location,budget,team_size
1,Marketing Team,Marketing,New York,500000,25
2,Engineering Team,Engineering,San Francisco,800000,40
3,Sales Team,Sales,Chicago,300000,15
4,HR Team,HR,New York,200000,8
5,Finance Team,Finance,Boston,400000,12"""

    @pytest.fixture
    def sample_edge_data(self):
        """Sample edge CSV data for testing."""
        return """source,target,relationship,weight
1,2,collaborates,0.8
2,3,supports,0.6
3,4,reports_to,0.9
4,5,coordinates,0.7
1,5,manages,0.85"""

    def test_import_then_graph_engine_operations(self, client, sample_csv_data):
        """Test importing data via Spec 1 then manipulating via Spec 2 Graph Engine."""
        # Step 1: Import data using Spec 1
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_csv_data)
            temp_file_path = f.name

        try:
            # Import via Spec 1 API
            import_data = {
                'filePath': temp_file_path,
                'mappingConfig': {
                    'node_id': 'id',
                    'node_name': 'name',
                    'attribute_department': 'department',
                    'attribute_location': 'location',
                    'attribute_budget': 'budget',
                    'attribute_team_size': 'team_size'
                }
            }

            response = client.post('/import',
                                  data=json.dumps(import_data),
                                  content_type='application/json')
            assert response.status_code == 200
            import_result = json.loads(response.data)
            assert import_result['success'] is True
            assert import_result['nodesCreated'] == 5

            # Step 2: Verify nodes exist in Graph Engine
            response = client.get('/api/v1/graph')
            assert response.status_code == 200
            graph_data = json.loads(response.data)

            # Should have nodes from import
            assert len(graph_data['nodes']) >= 5
            assert graph_data['total_nodes'] >= 5

            # Step 3: Use Graph Engine to add new node
            new_node_data = {
                'id': 'new_node_1',
                'name': 'New Operations Team',
                'attributes': {
                    'department': 'Operations',
                    'location': 'Seattle',
                    'budget': 350000
                },
                'visual_properties': {
                    'color': '#ff6b6b',
                    'size': 15.0
                }
            }

            response = client.post('/api/v1/nodes',
                                  data=json.dumps(new_node_data),
                                  content_type='application/json')
            assert response.status_code == 201
            created_node = json.loads(response.data)
            assert created_node['success'] is True
            assert created_node['node']['id'] == 'new_node_1'

            # Step 4: Create edge between imported and new node
            edge_data = {
                'source': '1',  # From imported data
                'target': 'new_node_1',  # New node
                'relationship_type': 'coordinates_with',
                'weight': 0.75,
                'directed': True,
                'visual_properties': {
                    'color': '#2ecc71',
                    'width': 3.0
                }
            }

            response = client.post('/api/v1/edges',
                                  data=json.dumps(edge_data),
                                  content_type='application/json')
            assert response.status_code == 201
            created_edge = json.loads(response.data)
            assert created_edge['success'] is True

            # Step 5: Query nodes using Graph Engine
            query_data = {
                'filters': {
                    'department': 'Marketing'
                }
            }

            response = client.post('/api/v1/nodes/query',
                                  data=json.dumps(query_data),
                                  content_type='application/json')
            assert response.status_code == 200
            query_result = json.loads(response.data)
            assert query_result['count'] == 1
            assert query_result['results'][0]['name'] == 'Marketing Team'

            # Step 6: Test graph traversal
            response = client.get('/api/v1/nodes/1/neighbors?direction=outgoing')
            assert response.status_code == 200
            neighbors = json.loads(response.data)
            assert 'new_node_1' in neighbors['neighbors']

        finally:
            os.unlink(temp_file_path)

    def test_undo_redo_integration(self, client):
        """Test undo / redo functionality in Graph Engine."""
        # Create initial node
        node_data = {
            'id': 'test_node',
            'name': 'Test Node',
            'attributes': {'test': 'value'}
        }

        response = client.post('/api/v1/nodes',
                              data=json.dumps(node_data),
                              content_type='application/json')
        assert response.status_code == 201

        # Verify node exists
        response = client.get('/api/v1/nodes/test_node')
        assert response.status_code == 200

        # Undo node creation
        response = client.post('/api/v1/graph/undo')
        assert response.status_code == 200
        undo_result = json.loads(response.data)
        assert undo_result['success'] is True

        # Verify node is gone
        response = client.get('/api/v1/nodes/test_node')
        assert response.status_code == 404

        # Redo node creation
        response = client.post('/api/v1/graph/redo')
        assert response.status_code == 200
        redo_result = json.loads(response.data)
        assert redo_result['success'] is True

        # Verify node is back
        response = client.get('/api/v1/nodes/test_node')
        assert response.status_code == 200

    def test_visual_properties_persistence(self, client, sample_csv_data):
        """Test that visual properties are preserved through import and graph operations."""
        # Import data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_csv_data)
            temp_file_path = f.name

        try:
            import_data = {
                'filePath': temp_file_path,
                'mappingConfig': {
                    'node_id': 'id',
                    'node_name': 'name',
                    'attribute_department': 'department'
                }
            }

            response = client.post('/import',
                                  data=json.dumps(import_data),
                                  content_type='application/json')
            assert response.status_code == 200

            # Get imported node and check default visual properties
            response = client.get('/api/v1/nodes/1')
            assert response.status_code == 200
            node = json.loads(response.data)

            # Should have default visual properties from Spec 2
            assert 'visual_properties' in node
            assert node['visual_properties']['color'] == '#3498db'
            assert node['visual_properties']['size'] == 10.0
            assert node['visual_properties']['shape'] == 'circle'

            # Update visual properties
            update_data = {
                'visual_properties': {
                    'color': '#e74c3c',
                    'size': 20.0,
                    'shape': 'square'
                }
            }

            response = client.put('/api/v1/nodes/1',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
            assert response.status_code == 200

            # Verify visual properties updated
            response = client.get('/api/v1/nodes/1')
            assert response.status_code == 200
            updated_node = json.loads(response.data)
            assert updated_node['visual_properties']['color'] == '#e74c3c'
            assert updated_node['visual_properties']['size'] == 20.0
            assert updated_node['visual_properties']['shape'] == 'square'

        finally:
            os.unlink(temp_file_path)

    def test_edge_directionality_integration(self, client, sample_edge_data):
        """Test edge directionality features from Spec 2."""
        # First create some nodes
        for i in range(1, 6):
            node_data = {
                'id': str(i),
                'name': f'Node {i}'
            }
            response = client.post('/api/v1/nodes',
                                  data=json.dumps(node_data),
                                  content_type='application/json')
            assert response.status_code == 201

        # Import edges with directionality
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_edge_data)
            temp_file_path = f.name

        try:
            import_data = {
                'filePath': temp_file_path,
                'mappingConfig': {
                    'edge_source': 'source',
                    'edge_target': 'target',
                    'edge_type': 'relationship',
                    'edge_weight': 'weight'
                }
            }

            response = client.post('/import',
                                  data=json.dumps(import_data),
                                  content_type='application/json')
            assert response.status_code == 200

            # Query edges and verify directionality
            response = client.get('/api/v1/graph')
            assert response.status_code == 200
            graph_data = json.loads(response.data)

            # All edges should be directed by default (Spec 2)
            for edge in graph_data['edges']:
                assert edge['directed'] is True

            # Test creating undirected edge
            undirected_edge = {
                'source': '1',
                'target': '3',
                'directed': False,
                'relationship_type': 'mutual_connection'
            }

            response = client.post('/api/v1/edges',
                                  data=json.dumps(undirected_edge),
                                  content_type='application/json')
            assert response.status_code == 201
            created_edge = json.loads(response.data)
            assert created_edge['edge']['directed'] is False

        finally:
            os.unlink(temp_file_path)

    def test_complex_query_integration(self, client, sample_csv_data):
        """Test complex queries across imported and manually created data."""
        # Import initial data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_csv_data)
            temp_file_path = f.name

        try:
            import_data = {
                'filePath': temp_file_path,
                'mappingConfig': {
                    'node_id': 'id',
                    'node_name': 'name',
                    'attribute_department': 'department',
                    'attribute_location': 'location',
                    'attribute_budget': 'budget'
                }
            }

            response = client.post('/import',
                                  data=json.dumps(import_data),
                                  content_type='application/json')
            assert response.status_code == 200

            # Add additional nodes via Graph Engine
            additional_nodes = [
                {
                    'id': 'ops_1',
                    'name': 'Operations Team Alpha',
                    'attributes': {
                        'department': 'Operations',
                        'location': 'New York',
                        'budget': 450000
                    }
                },
                {
                    'id': 'ops_2',
                    'name': 'Operations Team Beta',
                    'attributes': {
                        'department': 'Operations',
                        'location': 'Chicago',
                        'budget': 380000
                    }
                }
            ]

            for node_data in additional_nodes:
                response = client.post('/api/v1/nodes',
                                      data=json.dumps(node_data),
                                      content_type='application/json')
                assert response.status_code == 201

            # Complex query: Find all teams in New York
            query_data = {
                'filters': {
                    'location': 'New York'
                }
            }

            response = client.post('/api/v1/nodes/query',
                                  data=json.dumps(query_data),
                                  content_type='application/json')
            assert response.status_code == 200
            query_result = json.loads(response.data)

            # Should find Marketing, HR (from import) + Operations Alpha (manually added)
            assert query_result['count'] == 3
            ny_teams = [node['name'] for node in query_result['results']]
            assert 'Marketing Team' in ny_teams
            assert 'HR Team' in ny_teams
            assert 'Operations Team Alpha' in ny_teams

            # Query by department
            query_data = {
                'filters': {
                    'department': 'Operations'
                }
            }

            response = client.post('/api/v1/nodes/query',
                                  data=json.dumps(query_data),
                                  content_type='application/json')
            assert response.status_code == 200
            query_result = json.loads(response.data)
            assert query_result['count'] == 2

        finally:
            os.unlink(temp_file_path)

    def test_backward_compatibility(self, client, sample_csv_data):
        """Test that Spec 1 functionality still works exactly as before."""
        # This test ensures that all existing Spec 1 functionality is preserved
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_csv_data)
            temp_file_path = f.name

        try:
            # Test original Spec 1 import workflow
            import_data = {
                'filePath': temp_file_path,
                'mappingConfig': {
                    'node_id': 'id',
                    'node_name': 'name',
                    'attribute_department': 'department',
                    'kpi_budget': 'budget',
                    'kpi_team_size': 'team_size'
                }
            }

            response = client.post('/import',
                                  data=json.dumps(import_data),
                                  content_type='application/json')
            assert response.status_code == 200

            result = json.loads(response.data)

            # All original Spec 1 assertions should still pass
            assert result['success'] is True
            assert result['nodesCreated'] == 5
            assert result['edgesCreated'] == 0
            assert result['processedRows'] == 5
            assert result['totalRows'] == 5
            assert 'importLog' in result
            assert 'graphSummary' in result

            # Graph summary should work as before
            assert result['graphSummary']['totalNodes'] == 5
            assert result['graphSummary']['totalEdges'] == 0

            # Test preview functionality (Spec 1)
            preview_data = {
                'filePath': temp_file_path,
                'maxRows': 3
            }

            response = client.post('/preview',
                                  data=json.dumps(preview_data),
                                  content_type='application/json')
            assert response.status_code == 200

            preview_result = json.loads(response.data)
            assert 'columns' in preview_result
            assert 'data' in preview_result
            assert len(preview_result['data']) <= 3

            # Test mapping config endpoint (Spec 1)
            mapping_data = {
                'filePath': temp_file_path
            }

            response = client.post('/mapping-config',
                                  data=json.dumps(mapping_data),
                                  content_type='application/json')
            assert response.status_code == 200

            mapping_result = json.loads(response.data)
            assert 'suggestions' in mapping_result
            assert 'detected_types' in mapping_result

        finally:
            os.unlink(temp_file_path)

    def test_performance_with_integration(self, client):
        """Test performance when using both Spec 1 and Spec 2 features together."""
        import time

        # Create a moderately sized dataset
        csv_data = "id,name,department\n"
        for i in range(100):
            csv_data += f"{i},Node_{i},Dept_{i % 5}\n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_data)
            temp_file_path = f.name

        try:
            # Time the import process
            start_time = time.time()

            import_data = {
                'filePath': temp_file_path,
                'mappingConfig': {
                    'node_id': 'id',
                    'node_name': 'name',
                    'attribute_department': 'department'
                }
            }

            response = client.post('/import',
                                  data=json.dumps(import_data),
                                  content_type='application/json')
            assert response.status_code == 200

            import_time = time.time() - start_time
            assert import_time < 5.0  # Should complete within 5 seconds

            # Time graph operations
            start_time = time.time()

            # Query operations
            query_data = {'filters': {'department': 'Dept_0'}}
            response = client.post('/api/v1/nodes/query',
                                  data=json.dumps(query_data),
                                  content_type='application/json')
            assert response.status_code == 200

            # Graph retrieval
            response = client.get('/api/v1/graph')
            assert response.status_code == 200

            graph_ops_time = time.time() - start_time
            assert graph_ops_time < 2.0  # Graph operations should be fast

            print(f"Import time: {import_time:.2f}s, Graph ops time: {graph_ops_time:.2f}s")

        finally:
            os.unlink(temp_file_path)


@pytest.mark.integration
class TestSpec2StandaloneFeatures:
    """Test Spec 2 features that don't require Spec 1 integration."""

    @pytest.fixture
    def app(self):
        """Create test Flask app."""
        app = create_app()
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        # Clear graph storage before each test
        graph_engine_api.clear_graph()
        return app.test_client()

    def test_graph_engine_crud_operations(self, client):
        """Test basic CRUD operations in Graph Engine."""
        # Create node
        node_data = {
            'id': 'test_node',
            'name': 'Test Node',
            'attributes': {'category': 'test'},
            'visual_properties': {'color': '#ff0000'}
        }

        response = client.post('/api/v1/nodes',
                              data=json.dumps(node_data),
                              content_type='application/json')
        assert response.status_code == 201

        # Read node
        response = client.get('/api/v1/nodes/test_node')
        assert response.status_code == 200
        node = json.loads(response.data)
        assert node['id'] == 'test_node'
        assert node['visual_properties']['color'] == '#ff0000'

        # Update node
        update_data = {
            'name': 'Updated Test Node',
            'attributes': {'category': 'updated'}
        }

        response = client.put('/api/v1/nodes/test_node',
                             data=json.dumps(update_data),
                             content_type='application/json')
        assert response.status_code == 200

        # Verify update
        response = client.get('/api/v1/nodes/test_node')
        assert response.status_code == 200
        updated_node = json.loads(response.data)
        assert updated_node['name'] == 'Updated Test Node'
        assert updated_node['attributes']['category'] == 'updated'

        # Delete node
        response = client.delete('/api/v1/nodes/test_node')
        assert response.status_code == 200

        # Verify deletion
        response = client.get('/api/v1/nodes/test_node')
        assert response.status_code == 404

    def test_graph_traversal_features(self, client):
        """Test graph traversal and neighbor functionality."""
        # Create nodes
        nodes = [
            {'id': 'A', 'name': 'Node A'},
            {'id': 'B', 'name': 'Node B'},
            {'id': 'C', 'name': 'Node C'}
        ]

        for node_data in nodes:
            response = client.post('/api/v1/nodes',
                                  data=json.dumps(node_data),
                                  content_type='application/json')
            assert response.status_code == 201

        # Create edges: A -> B, B -> C
        edges = [
            {'source': 'A', 'target': 'B', 'directed': True},
            {'source': 'B', 'target': 'C', 'directed': True}
        ]

        for edge_data in edges:
            response = client.post('/api/v1/edges',
                                  data=json.dumps(edge_data),
                                  content_type='application/json')
            assert response.status_code == 201

        # Test outgoing neighbors
        response = client.get('/api/v1/nodes/A/neighbors?direction=outgoing')
        assert response.status_code == 200
        neighbors = json.loads(response.data)
        assert 'B' in neighbors['neighbors']
        assert len(neighbors['neighbors']) == 1

        # Test incoming neighbors
        response = client.get('/api/v1/nodes/C/neighbors?direction=incoming')
        assert response.status_code == 200
        neighbors = json.loads(response.data)
        assert 'B' in neighbors['neighbors']
        assert len(neighbors['neighbors']) == 1

        # Test all neighbors
        response = client.get('/api/v1/nodes/B/neighbors?direction=all')
        assert response.status_code == 200
        neighbors = json.loads(response.data)
        assert 'A' in neighbors['neighbors']
        assert 'C' in neighbors['neighbors']
        assert len(neighbors['neighbors']) == 2
