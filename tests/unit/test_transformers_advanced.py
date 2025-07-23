"""
Advanced Test Cases for Graph Transformer
Tests stress scenarios, large graphs, complex hierarchies, and performance.
"""

import pytest
import pandas as pd
import numpy as np
import time
from unittest.mock import patch
from network_ui.core.transformers import GraphTransformer
from network_ui.core.models import GraphData, Node, Edge


@pytest.mark.unit
class TestGraphTransformerAdvanced:
    """Advanced test cases for GraphTransformer with stress scenarios and performance tests."""

    def setup_method(self):
        """Set up test fixtures."""
        self.transformer = GraphTransformer()

    @pytest.mark.parametrize("graph_size", [100, 1000, 5000, 10000])
    def test_large_graph_transformation_performance(self, graph_size):
        """Test transformer performance with large graphs of varying sizes."""
        # Create large node dataset
        node_data = pd.DataFrame({
            'id': range(1, graph_size + 1),
            'name': [f'Node_{i}' for i in range(1, graph_size + 1)],
            'category': np.random.choice(['A', 'B', 'C', 'D'], graph_size),
            'value': np.random.uniform(0, 100, graph_size),
            'level': np.random.randint(1, 6, graph_size)
        })

        mapping_config = {
            'node_id': 'id',
            'node_name': 'name',
            'node_level': 'level',
            'attribute_category': 'category',
            'attribute_value': 'value'
        }

        # Create data types dictionary
        data_types = {
            'id': 'integer',
            'name': 'string',
            'category': 'string',
            'value': 'float',
            'level': 'integer'
        }

        # Time the transformation
        start_time = time.time()
        graph_data = self.transformer.transform_to_graph(node_data, mapping_config, data_types)
        end_time = time.time()

        # Verify results
        assert len(graph_data.nodes) == graph_size
        assert all(node.id == str(i) for i, node in enumerate(graph_data.nodes, 1))
        
        # Performance assertion (should scale reasonably)
        processing_time = end_time - start_time
        if graph_size <= 1000:
            assert processing_time < 2.0  # 2 seconds for up to 1k nodes
        elif graph_size <= 5000:
            assert processing_time < 10.0  # 10 seconds for up to 5k nodes
        else:
            assert processing_time < 30.0  # 30 seconds for up to 10k nodes

    def test_complex_hierarchical_structure_creation(self):
        """Test creation of complex multi-level hierarchical structures."""
        # Create nodes with complex hierarchy requirements
        # Ensure departments have multiple locations to create multiple levels
        departments = []
        locations = []
        for i in range(100):
            dept_idx = i // 25  # 4 departments with 25 nodes each
            dept = ['Engineering', 'Sales', 'Marketing', 'Support'][dept_idx]
            
            # Create overlapping department-location combinations
            if dept == 'Engineering':
                loc = ['US', 'EU'][i % 2]  # Engineering in US and EU
            elif dept == 'Sales':
                loc = ['EU', 'APAC'][i % 2]  # Sales in EU and APAC
            elif dept == 'Marketing':
                loc = ['APAC', 'LATAM'][i % 2]  # Marketing in APAC and LATAM
            else:  # Support
                loc = ['LATAM', 'US'][i % 2]  # Support in LATAM and US
                
            departments.append(dept)
            locations.append(loc)
        
        node_data = pd.DataFrame({
            'id': range(1, 101),
            'name': [f'Node_{i}' for i in range(1, 101)],
            'department': departments,
            'location': locations,
            'team_size': np.random.randint(1, 50, 100),
            'budget': np.random.uniform(10000, 500000, 100),
            'priority': np.random.choice(['High', 'Medium', 'Low'], 100)
        })

        mapping_config = {
            'node_id': 'id',
            'node_name': 'name',
            'attribute_department': 'department',
            'attribute_location': 'location',
            'attribute_team_size': 'team_size',
            'attribute_budget': 'budget',
            'attribute_priority': 'priority'
        }

        # Create data types dictionary
        data_types = {
            'id': 'integer',
            'name': 'string',
            'department': 'string',
            'location': 'string',
            'team_size': 'integer',
            'budget': 'float',
            'priority': 'string'
        }

        graph_data = self.transformer.transform_to_graph(node_data, mapping_config, data_types)
        
        # Apply hierarchical structure based on multiple attributes
        hierarchical_graph = self.transformer.create_hierarchical_structure(graph_data)
        
        # Verify hierarchical organization
        levels = {}
        for node in hierarchical_graph.nodes:
            if node.level not in levels:
                levels[node.level] = []
            levels[node.level].append(node)
        
        # Should have multiple levels
        assert len(levels) >= 2
        
        # Higher levels should have fewer nodes (hierarchy principle)
        level_counts = [len(nodes) for level, nodes in sorted(levels.items())]
        # Generally, higher levels should have same or fewer nodes
        for i in range(1, len(level_counts)):
            # Allow some flexibility in hierarchy
            assert level_counts[i] <= level_counts[i-1] * 2

    @pytest.mark.parametrize("edge_density", [0.1, 0.3, 0.5, 0.8, 1.0])
    def test_varying_edge_density_graphs(self, edge_density):
        """Test transformer with graphs of varying edge densities."""
        num_nodes = 100
        max_possible_edges = num_nodes * (num_nodes - 1)  # Directed graph
        num_edges = int(max_possible_edges * edge_density)
        
        # Create edge data with specified density
        edges = []
        edge_count = 0
        
        for source in range(1, num_nodes + 1):
            for target in range(1, num_nodes + 1):
                if source != target and edge_count < num_edges:
                    edges.append({
                        'source': source,
                        'target': target,
                        'weight': np.random.uniform(0.1, 1.0),
                        'type': np.random.choice(['connects', 'reports_to', 'collaborates'])
                    })
                    edge_count += 1
                if edge_count >= num_edges:
                    break
            if edge_count >= num_edges:
                break

        edge_data = pd.DataFrame(edges)

        mapping_config = {
            'edge_source': 'source',
            'edge_target': 'target',
            'attribute_weight': 'weight',
            'attribute_type': 'type'
        }

        # Create data types dictionary
        data_types = {
            'source': 'integer',
            'target': 'integer',
            'weight': 'float',
            'type': 'string'
        }

        graph_data = self.transformer.transform_to_graph(edge_data, mapping_config, data_types)
        
        # Verify edge density
        actual_edges = len(graph_data.edges)
        expected_edges = num_edges
        
        # Allow some tolerance due to random generation
        tolerance = max(1, int(expected_edges * 0.1))
        assert abs(actual_edges - expected_edges) <= tolerance
        
        # Verify edge properties
        for edge in graph_data.edges:
            assert edge.source in [str(i) for i in range(1, num_nodes + 1)]
            assert edge.target in [str(i) for i in range(1, num_nodes + 1)]
            assert edge.source != edge.target  # No self-loops
            assert hasattr(edge, 'attributes')
            assert 'weight' in edge.attributes
            assert 'type' in edge.attributes

    def test_memory_efficient_large_dataset_processing(self):
        """Test memory-efficient processing of very large datasets."""
        # Create a large dataset that would normally consume significant memory
        large_size = 50000
        
        def generate_node_data():
            """Generator to create node data in chunks."""
            chunk_size = 1000
            for i in range(0, large_size, chunk_size):
                chunk_data = pd.DataFrame({
                    'id': range(i + 1, min(i + chunk_size + 1, large_size + 1)),
                    'name': [f'Node_{j}' for j in range(i + 1, min(i + chunk_size + 1, large_size + 1))],
                    'category': np.random.choice(['A', 'B', 'C'], chunk_size),
                    'value': np.random.uniform(0, 100, chunk_size)
                })
                yield chunk_data

        mapping_config = {
            'node_id': 'id',
            'node_name': 'name',
            'attribute_category': 'category',
            'attribute_value': 'value'
        }

        # Create data types dictionary
        data_types = {
            'id': 'integer',
            'name': 'string',
            'category': 'string',
            'value': 'float'
        }

        # Process in chunks to test memory efficiency
        all_nodes = []
        for chunk in generate_node_data():
            graph_data = self.transformer.transform_to_graph(chunk, mapping_config, data_types)
            all_nodes.extend(graph_data.nodes)

        # Verify all nodes were processed
        assert len(all_nodes) == large_size
        
        # Verify node properties
        node_ids = [node.id for node in all_nodes]
        assert len(set(node_ids)) == large_size  # All unique IDs
        assert all(node.attributes for node in all_nodes)  # All have attributes

    def test_complex_data_type_transformations(self):
        """Test complex data type transformations and edge cases."""
        # Create data with mixed types and edge cases
        test_data = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Node_1', 'Node_2', 'Node_3', 'Node_4', 'Node_5'],
            'boolean_field': ['True', 'False', 'true', 'false', 'Yes'],
            'numeric_field': ['123', '456.78', '0', '-999', '3.14e5'],
            'date_field': ['2024-01-01', '2024-12-31', '2023-06-15', '2025-03-20', '2022-11-11'],
            'mixed_field': ['text', '123', 'True', '2024-01-01', 'mixed'],
            'null_field': [None, 'value', None, 'another', None]
        })

        mapping_config = {
            'node_id': 'id',
            'node_name': 'name',
            'attribute_boolean': 'boolean_field',
            'attribute_numeric': 'numeric_field',
            'attribute_date': 'date_field',
            'attribute_mixed': 'mixed_field',
            'attribute_null': 'null_field'
        }

        # Create data types dictionary
        data_types = {
            'id': 'integer',
            'name': 'string',
            'boolean_field': 'boolean',
            'numeric_field': 'float',
            'date_field': 'date',
            'mixed_field': 'string',
            'null_field': 'string'
        }

        graph_data = self.transformer.transform_to_graph(test_data, mapping_config, data_types)
        
        # Verify transformations
        assert len(graph_data.nodes) == 5
        
        # Check boolean transformation
        node = graph_data.nodes[0]
        assert node.attributes['boolean'] in [True, False]
        
        # Check numeric transformation
        assert isinstance(node.attributes['numeric'], (int, float))
        
        # Check date transformation
        assert hasattr(node.attributes['date'], 'date')  # Should be datetime-like
        
        # Check mixed field (should remain string)
        assert isinstance(node.attributes['mixed'], str)
        
        # Check null handling
        assert node.attributes['null'] is None or isinstance(node.attributes['null'], str)

    def test_circular_reference_resolution(self):
        """Test handling of circular references in edge data."""
        # Create edge data with potential circular references
        circular_edges = pd.DataFrame({
            'source': [1, 2, 3, 4, 5, 1, 2, 3],
            'target': [2, 3, 4, 5, 1, 3, 4, 5],
            'weight': [1.0, 1.0, 1.0, 1.0, 1.0, 0.5, 0.5, 0.5],
            'type': ['connects'] * 8
        })

        mapping_config = {
            'edge_source': 'source',
            'edge_target': 'target',
            'attribute_weight': 'weight',
            'attribute_type': 'type'
        }

        # Create data types dictionary
        data_types = {
            'source': 'integer',
            'target': 'integer',
            'weight': 'float',
            'type': 'string'
        }

        graph_data = self.transformer.transform_to_graph(circular_edges, mapping_config, data_types)
        
        # Verify all edges were processed
        assert len(graph_data.edges) == 8
        
        # Check for circular references
        source_target_pairs = [(edge.source, edge.target) for edge in graph_data.edges]
        
        # Should have some circular references (1->2->3->4->5->1)
        assert ('1', '2') in source_target_pairs
        assert ('2', '3') in source_target_pairs
        assert ('3', '4') in source_target_pairs
        assert ('4', '5') in source_target_pairs
        assert ('5', '1') in source_target_pairs
        
        # Verify edge properties
        for edge in graph_data.edges:
            assert edge.source != edge.target  # No self-loops
            assert 'weight' in edge.attributes
            assert 'type' in edge.attributes

    @pytest.mark.parametrize("attribute_count", [10, 50, 100, 500])
    def test_nodes_with_many_attributes(self, attribute_count):
        """Test nodes with a large number of attributes."""
        # Create node data with many attributes
        node_data = pd.DataFrame({
            'id': range(1, 11),
            'name': [f'Node_{i}' for i in range(1, 11)]
        })
        
        # Add many attribute columns
        for i in range(attribute_count):
            node_data[f'attr_{i}'] = [f'value_{i}_{j}' for j in range(1, 11)]

        # Create mapping config with many attributes
        mapping_config = {'node_id': 'id', 'node_name': 'name'}
        for i in range(attribute_count):
            mapping_config[f'attribute_attr_{i}'] = f'attr_{i}'

        # Create data types dictionary
        data_types = {'id': 'integer', 'name': 'string'}
        for i in range(attribute_count):
            data_types[f'attr_{i}'] = 'string'

        graph_data = self.transformer.transform_to_graph(node_data, mapping_config, data_types)
        
        # Verify all nodes have the expected number of attributes
        for node in graph_data.nodes:
            assert len(node.attributes) == attribute_count  # Just the attributes, id and name are separate fields
            
            # Check that all attributes are present
            for i in range(attribute_count):
                assert f'attr_{i}' in node.attributes
                assert node.attributes[f'attr_{i}'] == f'value_{i}_{int(node.id)}'

    def test_graph_validation_edge_cases(self):
        """Test graph validation with various edge cases."""
        # Test empty graph
        empty_data = pd.DataFrame(columns=['id', 'name'])
        empty_mapping = {'node_id': 'id', 'node_name': 'name'}
        empty_data_types = {'id': 'integer', 'name': 'string'}
        
        empty_graph = self.transformer.transform_to_graph(empty_data, empty_mapping, empty_data_types)
        is_valid, errors = self.transformer.validate_graph_structure(empty_graph)
        assert is_valid
        assert len(errors) == 0
        
        # Test single node graph
        single_node_data = pd.DataFrame({'id': [1], 'name': ['Single']})
        single_mapping = {'node_id': 'id', 'node_name': 'name'}
        single_data_types = {'id': 'integer', 'name': 'string'}
        
        single_graph = self.transformer.transform_to_graph(single_node_data, single_mapping, single_data_types)
        is_valid, errors = self.transformer.validate_graph_structure(single_graph)
        assert is_valid
        assert len(errors) == 0
        
        # Test graph with duplicate node IDs (should be handled gracefully)
        duplicate_data = pd.DataFrame({
            'id': [1, 2, 1, 3],  # Duplicate ID
            'name': ['Node_1', 'Node_2', 'Node_1_dup', 'Node_3']
        })
        duplicate_mapping = {'node_id': 'id', 'node_name': 'name'}
        duplicate_data_types = {'id': 'integer', 'name': 'string'}
        
        # This should raise an error or handle duplicates gracefully
        try:
            duplicate_graph = self.transformer.transform_to_graph(duplicate_data, duplicate_mapping, duplicate_data_types)
            # If no error, verify the graph structure
            is_valid, errors = self.transformer.validate_graph_structure(duplicate_graph)
            # Should have validation errors for duplicates
            assert not is_valid and len(errors) > 0
        except ValueError as e:
            # Expected behavior for duplicate IDs
            assert "duplicate" in str(e).lower() or "Duplicate" in str(e)
        
        # Test graph with orphaned edges (edges pointing to non-existent nodes)
        # Note: The transformer auto-creates missing nodes, so we need to test post-creation validation
        orphan_edges = pd.DataFrame({
            'source': [1, 2, 3, 4],
            'target': [2, 3, 999, 888],  # Non-existent targets
            'weight': [1.0, 1.0, 1.0, 1.0]
        })
        orphan_mapping = {
            'edge_source': 'source',
            'edge_target': 'target',
            'attribute_weight': 'weight'
        }
        orphan_data_types = {'source': 'integer', 'target': 'integer', 'weight': 'float'}
        
        orphan_graph = self.transformer.transform_to_graph(orphan_edges, orphan_mapping, orphan_data_types)
        
        # Since transformer auto-creates missing nodes, manually create an orphaned edge for testing
        from network_ui.core.models import Edge
        orphaned_edge = Edge(source="999", target="non_existent_node")
        orphan_graph.add_edge(orphaned_edge)
        
        is_valid, errors = self.transformer.validate_graph_structure(orphan_graph)
        # Should have validation errors for orphaned edges
        assert not is_valid and len(errors) > 0

    def test_graph_summary_with_complex_structures(self):
        """Test graph summary generation with complex hierarchical structures."""
        # Create a complex hierarchical structure
        node_data = pd.DataFrame({
            'id': range(1, 51),
            'name': [f'Node_{i}' for i in range(1, 51)],
            'level': [1] * 10 + [2] * 15 + [3] * 20 + [4] * 5,
            'category': ['A'] * 20 + ['B'] * 20 + ['C'] * 10,
            'value': np.random.uniform(0, 100, 50)
        })

        mapping_config = {
            'node_id': 'id',
            'node_name': 'name',
            'node_level': 'level',
            'attribute_category': 'category',
            'attribute_value': 'value'
        }

        # Create data types dictionary
        data_types = {
            'id': 'integer',
            'name': 'string',
            'level': 'integer',
            'category': 'string',
            'value': 'float'
        }

        graph_data = self.transformer.transform_to_graph(node_data, mapping_config, data_types)
        
        # Create hierarchical structure
        hierarchical_graph = self.transformer.create_hierarchical_structure(graph_data)
        
        # Generate summary
        summary = self.transformer.create_graph_summary(hierarchical_graph)
        
        # Verify summary structure
        assert 'total_nodes' in summary
        assert 'total_edges' in summary
        assert 'node_levels' in summary
        assert 'attribute_summary' in summary
        
        # Verify node count
        assert summary['total_nodes'] == 50
        
        # Verify level distribution
        assert '1' in summary['node_levels']
        assert '2' in summary['node_levels']
        assert '3' in summary['node_levels']
        assert '4' in summary['node_levels']
        
        # Verify level counts
        assert summary['node_levels']['1'] == 10
        assert summary['node_levels']['2'] == 15
        assert summary['node_levels']['3'] == 20
        assert summary['node_levels']['4'] == 5
        
        # Verify attribute summary
        assert 'category' in summary['attribute_summary']
        assert 'value' in summary['attribute_summary']
        
        # Check category distribution
        category_summary = summary['attribute_summary']['category']
        assert category_summary['A'] == 20
        assert category_summary['B'] == 20
        assert category_summary['C'] == 10
        
        # Check value statistics
        value_summary = summary['attribute_summary']['value']
        assert 'min' in value_summary
        assert 'max' in value_summary
        assert 'mean' in value_summary
        assert value_summary['min'] >= 0
        assert value_summary['max'] <= 100

    def test_concurrent_transformation_safety(self):
        """Test that transformer is thread-safe for concurrent operations."""
        import threading
        import queue
        
        # Create test data
        node_data = pd.DataFrame({
            'id': range(1, 101),
            'name': [f'Node_{i}' for i in range(1, 101)],
            'value': np.random.uniform(0, 100, 100)
        })

        mapping_config = {
            'node_id': 'id',
            'node_name': 'name',
            'attribute_value': 'value'
        }

        # Create data types dictionary
        data_types = {
            'id': 'integer',
            'name': 'string',
            'value': 'float'
        }

        results_queue = queue.Queue()
        errors_queue = queue.Queue()
        
        def transform_worker(worker_id):
            """Worker function for concurrent transformation."""
            try:
                transformer = GraphTransformer()
                graph_data = transformer.transform_to_graph(node_data, mapping_config, data_types)
                results_queue.put((worker_id, len(graph_data.nodes)))
            except Exception as e:
                errors_queue.put((worker_id, str(e)))
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=transform_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert errors_queue.empty(), f"Errors occurred: {[errors_queue.get() for _ in range(errors_queue.qsize())]}"
        
        # All workers should produce the same result
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        assert len(results) == 5
        for worker_id, node_count in results:
            assert node_count == 100, f"Worker {worker_id} produced {node_count} nodes, expected 100"

    def test_transformation_with_missing_values_handling(self):
        """Test transformation with various missing value scenarios."""
        # Create data with missing values
        data_with_nulls = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Node_1', None, 'Node_3', 'Node_4', 'Node_5'],
            'value': [10.5, 20.0, None, 40.0, 50.5],
            'category': ['A', 'B', 'C', None, 'E'],
            'boolean_field': ['True', None, 'False', 'true', None]
        })

        mapping_config = {
            'node_id': 'id',
            'node_name': 'name',
            'attribute_value': 'value',
            'attribute_category': 'category',
            'attribute_boolean': 'boolean_field'
        }

        # Create data types dictionary
        data_types = {
            'id': 'integer',
            'name': 'string',
            'value': 'float',
            'category': 'string',
            'boolean_field': 'boolean'
        }

        graph_data = self.transformer.transform_to_graph(data_with_nulls, mapping_config, data_types)
        
        # Verify all nodes were created
        assert len(graph_data.nodes) == 5
        
        # Check handling of missing values
        for node in graph_data.nodes:
            if node.id == '2':
                # Node with missing name - could be None, empty string, or 'None'
                assert node.name is None or node.name == '' or node.name == 'None'
            elif node.id == '3':
                # Node with missing value
                assert node.attributes['value'] is None or pd.isna(node.attributes['value'])
            elif node.id == '4':
                # Node with missing category - could be None, empty string, or 'None'
                assert node.attributes['category'] is None or node.attributes['category'] == '' or node.attributes['category'] == 'None'
            elif node.id in ['2', '5']:
                # Nodes with missing boolean values - could be None, 'None', or NaN
                assert (node.attributes['boolean'] is None or 
                       node.attributes['boolean'] == 'None' or
                       pd.isna(node.attributes['boolean']))

    def test_performance_with_complex_mappings(self):
        """Test performance with complex mapping configurations."""
        # Create large dataset with complex mapping
        large_size = 1000
        node_data = pd.DataFrame({
            'id': range(1, large_size + 1),
            'name': [f'Node_{i}' for i in range(1, large_size + 1)],
            'department': np.random.choice(['Engineering', 'Sales', 'Marketing', 'Support'], large_size),
            'location': np.random.choice(['US', 'EU', 'APAC', 'LATAM'], large_size),
            'team_size': np.random.randint(1, 50, large_size),
            'budget': np.random.uniform(10000, 500000, large_size),
            'priority': np.random.choice(['High', 'Medium', 'Low'], large_size),
            'status': np.random.choice(['Active', 'Inactive', 'Pending'], large_size),
            'created_date': pd.date_range('2020-01-01', periods=large_size, freq='D').strftime('%Y-%m-%d'),
            'score': np.random.uniform(0, 100, large_size),
            'is_verified': np.random.choice([True, False], large_size)
        })

        # Complex mapping with many attributes
        complex_mapping = {
            'node_id': 'id',
            'node_name': 'name',
            'attribute_department': 'department',
            'attribute_location': 'location',
            'attribute_team_size': 'team_size',
            'attribute_budget': 'budget',
            'attribute_priority': 'priority',
            'attribute_status': 'status',
            'attribute_created_date': 'created_date',
            'attribute_score': 'score',
            'attribute_is_verified': 'is_verified'
        }

        # Create data types dictionary
        data_types = {
            'id': 'integer',
            'name': 'string',
            'department': 'string',
            'location': 'string',
            'team_size': 'integer',
            'budget': 'float',
            'priority': 'string',
            'status': 'string',
            'created_date': 'date',
            'score': 'float',
            'is_verified': 'boolean'
        }

        # Time the transformation
        start_time = time.time()
        graph_data = self.transformer.transform_to_graph(node_data, complex_mapping, data_types)
        end_time = time.time()

        # Verify results
        assert len(graph_data.nodes) == large_size
        
        # Performance assertion
        processing_time = end_time - start_time
        assert processing_time < 5.0  # Should complete within 5 seconds
        
        # Verify all attributes are present
        for node in graph_data.nodes:
            assert len(node.attributes) == 9  # 9 attributes + id/name
            assert all(attr in node.attributes for attr in [
                'department', 'location', 'team_size', 'budget', 'priority',
                'status', 'created_date', 'score', 'is_verified'
            ]) 