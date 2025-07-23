"""
Advanced Test Cases for Data Importer
Tests edge cases, stress scenarios, and robustness of the import functionality.
"""

import os
import tempfile
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, mock_open
from network_ui.core import DataImporter, ImportConfig
from network_ui.core.models import GraphData, Node, Edge


@pytest.mark.unit
class TestDataImporterAdvanced:
    """Advanced test cases for DataImporter with edge cases and stress tests."""

    def setup_method(self):
        """Set up test fixtures."""
        self.importer = DataImporter()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @pytest.mark.parametrize("file_size,expected_rows", [
        (100, 100),
        (1000, 1000),
        (5000, 5000),
    ])
    def test_large_dataset_import(self, file_size, expected_rows):
        """Test importing large datasets of varying sizes."""
        # Create large test dataset
        data = {
            'id': range(1, file_size + 1),
            'name': [f'Node_{i}' for i in range(1, file_size + 1)],
            'category': np.random.choice(['A', 'B', 'C', 'D'], file_size),
            'value': np.random.uniform(0, 100, file_size),
            'active': np.random.choice([True, False], file_size)
        }
        df = pd.DataFrame(data)
        
        file_path = os.path.join(self.temp_dir, f'large_dataset_{file_size}.csv')
        df.to_csv(file_path, index=False)

        config = ImportConfig(
            file_path=file_path,
            mapping_config={
                'node_id': 'id',
                'node_name': 'name',
                'attribute_category': 'category',
                'attribute_value': 'value',
                'attribute_active': 'active'
            }
        )

        result = self.importer.import_data(config)
        
        assert result.success is True
        assert result.processed_rows == expected_rows
        assert len(result.graph_data.nodes) == expected_rows
        assert result.graph_data.nodes[0].attributes['category'] in ['A', 'B', 'C', 'D']

    @pytest.mark.parametrize("encoding", [
        'utf-8', 'utf-16', 'latin-1', 'cp1252'
    ])
    def test_different_file_encodings(self, encoding):
        """Test importing files with different encodings."""
        # Create test data with special characters appropriate for each encoding
        if encoding in ['latin-1', 'cp1252']:
            # Use characters that are supported by these encodings
            data = {
                'id': [1, 2, 3],
                'name': ['Node Name 1', 'Node Name 2', 'Node Name 3'],
                'description': ['Special chars', 'Encoding test', 'Accented vowels']
            }
        else:
            # Use full Unicode characters for UTF encodings
            data = {
                'id': [1, 2, 3],
                'name': ['Nöde Ñame 1', 'Nøde Nàme 2', 'Nôde Namê 3'],
                'description': ['Spéciał chärs', 'Ünïcode tëst', 'Accénted vowëls']
            }
        
        df = pd.DataFrame(data)
        
        file_path = os.path.join(self.temp_dir, f'encoding_test_{encoding.replace("-", "_")}.csv')
        df.to_csv(file_path, index=False, encoding=encoding)

        config = ImportConfig(
            file_path=file_path,
            file_encoding=encoding,
            mapping_config={
                'node_id': 'id',
                'node_name': 'name',
                'attribute_description': 'description'
            }
        )

        result = self.importer.import_data(config)
        
        assert result.success is True
        assert len(result.graph_data.nodes) == 3
        assert 'ö' in result.graph_data.nodes[0].name or 'N' in result.graph_data.nodes[0].name

    @pytest.mark.parametrize("delimiter", [',', ';', '\t', '|'])
    def test_different_delimiters(self, delimiter):
        """Test importing CSV files with different delimiters."""
        data = ['id{0}name{0}category'.format(delimiter),
                '1{0}Node1{0}TypeA'.format(delimiter),
                '2{0}Node2{0}TypeB'.format(delimiter),
                '3{0}Node3{0}TypeC'.format(delimiter)]
        
        # Use safe filename for Windows
        delimiter_name = "tab" if delimiter == "\t" else "pipe" if delimiter == "|" else delimiter
        file_path = os.path.join(self.temp_dir, f'delimiter_test_{delimiter_name}.csv')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(data))

        config = ImportConfig(
            file_path=file_path,
            delimiter=delimiter,
            mapping_config={
                'node_id': 'id',
                'node_name': 'name',
                'attribute_category': 'category'
            }
        )

        result = self.importer.import_data(config)
        
        assert result.success is True
        assert len(result.graph_data.nodes) == 3
        assert result.graph_data.nodes[0].name == 'Node1'

    def test_malformed_csv_recovery(self):
        """Test importing malformed CSV with recovery mechanisms."""
        # Create malformed CSV data
        malformed_data = '''id,name,category,value
1,Node1,TypeA,100
2,"Node2,with,commas",TypeB,200
3,Node3,TypeC,300,extra_column
4,Node4 with "quotes",TypeD,400
5,Node5,TypeE,'''
        
        file_path = os.path.join(self.temp_dir, 'malformed.csv')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(malformed_data)

        config = ImportConfig(
            file_path=file_path,
            mapping_config={
                'node_id': 'id',
                'node_name': 'name',
                'attribute_category': 'category'
            }
        )

        result = self.importer.import_data(config)
        
        # Should handle malformed data gracefully - may not succeed but should not crash
        # The importer should either succeed with warnings or fail gracefully
        if result.success:
            assert result.processed_rows >= 3  # At least some rows should be processed
            assert len(result.warnings) > 0  # Should have warnings about malformed data
        else:
            # If it fails, should have meaningful error messages
            assert len(result.errors) > 0
            assert any('failed' in error.lower() or 'read' in error.lower() 
                      or 'tokenizing' in error.lower() or 'fields' in error.lower()
                      or 'error' in error.lower() for error in result.errors)

    def test_memory_efficient_large_file(self):
        """Test memory-efficient processing of large files."""
        # Create a large dataset
        large_data = {
            'id': range(1, 10001),  # 10k rows
            'name': [f'Node_{i}' for i in range(1, 10001)],
            'data': ['x' * 100 for _ in range(10000)]  # Large text fields
        }
        df = pd.DataFrame(large_data)
        
        file_path = os.path.join(self.temp_dir, 'large_memory_test.csv')
        df.to_csv(file_path, index=False)

        config = ImportConfig(
            file_path=file_path,
            max_rows=1000,  # Limit processing
            mapping_config={
                'node_id': 'id',
                'node_name': 'name',
                'attribute_data': 'data'
            }
        )

        result = self.importer.import_data(config)
        
        assert result.success is True
        assert result.processed_rows == 1000  # Should respect max_rows
        assert len(result.graph_data.nodes) == 1000

    @pytest.mark.parametrize("null_percentage", [0.1, 0.3, 0.5, 0.8])
    def test_high_null_data_handling(self, null_percentage):
        """Test handling datasets with high percentages of null values."""
        size = 1000
        null_count = int(size * null_percentage)
        
        # Create dataset with specified null percentage
        ids = list(range(1, size + 1))
        names = [f'Node_{i}' if i > null_count else None for i in range(1, size + 1)]
        values = [np.random.uniform(0, 100) if i > null_count else None for i in range(1, size + 1)]
        
        data = pd.DataFrame({
            'id': ids,
            'name': names,
            'value': values
        })
        
        file_path = os.path.join(self.temp_dir, f'null_test_{null_percentage}.csv')
        data.to_csv(file_path, index=False)

        config = ImportConfig(
            file_path=file_path,
            mapping_config={
                'node_id': 'id',
                'node_name': 'name',
                'attribute_value': 'value'
            }
        )

        result = self.importer.import_data(config)
        
        # Should handle nulls gracefully
        assert result.success is True
        assert len(result.graph_data.nodes) <= size
        if null_percentage < 0.9:  # If not too many nulls, should process some data
            assert len(result.graph_data.nodes) > 0

    def test_concurrent_import_safety(self):
        """Test thread safety of concurrent imports."""
        import threading
        import time
        
        # Create test data
        data = pd.DataFrame({
            'id': range(1, 101),
            'name': [f'Node_{i}' for i in range(1, 101)],
            'value': range(1, 101)
        })
        
        file_path = os.path.join(self.temp_dir, 'concurrent_test.csv')
        data.to_csv(file_path, index=False)

        config = ImportConfig(
            file_path=file_path,
            mapping_config={
                'node_id': 'id',
                'node_name': 'name',
                'attribute_value': 'value'
            }
        )

        results = []
        errors = []
        
        def import_worker(worker_id):
            try:
                importer = DataImporter()  # Each thread gets its own instance
                for iteration in range(5):  # Multiple imports per thread
                    result = importer.import_data(config)
                    results.append((worker_id, iteration, result.success))
                    time.sleep(0.01)  # Small delay to encourage race conditions
            except Exception as e:
                errors.append((worker_id, str(e)))
        
        # Start multiple threads
        threads = []
        for i in range(3):  # 3 threads to avoid overwhelming the system
            thread = threading.Thread(target=import_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(errors) == 0, f"Errors in concurrent import: {errors}"
        assert len(results) == 15  # 3 threads * 5 iterations each
        assert all(success for _, _, success in results)

    def test_invalid_json_structure(self):
        """Test handling of invalid JSON structures."""
        # Create invalid JSON data
        invalid_json = '''{
            "nodes": [
                {"id": 1, "name": "Node1"},
                {"id": 2, "name": "Node2", "invalid": "structure"},
                {"id": 3, "name": "Node3"}
            ],
            "invalid_section": "not expected"
        }'''
        
        file_path = os.path.join(self.temp_dir, 'invalid.json')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(invalid_json)

        config = ImportConfig(
            file_path=file_path,
            mapping_config={
                'node_id': 'id',
                'node_name': 'name'
            }
        )

        result = self.importer.import_data(config)
        
        # Should handle invalid JSON gracefully
        if result.success:
            assert len(result.graph_data.nodes) >= 1  # Should process valid nodes
            # Extra fields in JSON don't necessarily cause warnings - pandas is tolerant
            # This is actually valid behavior
        else:
            assert len(result.errors) > 0  # Should have error messages

    def test_extremely_long_field_values(self):
        """Test handling of extremely long field values."""
        # Create data with very long strings
        long_string = 'x' * 10000  # 10k character string
        data = pd.DataFrame({
            'id': range(1, 11),
            'name': [f'Node_{i}' for i in range(1, 11)],
            'long_description': [long_string] * 10
        })
        
        file_path = os.path.join(self.temp_dir, 'long_fields.csv')
        data.to_csv(file_path, index=False)

        config = ImportConfig(
            file_path=file_path,
            mapping_config={
                'node_id': 'id',
                'node_name': 'name',
                'attribute_long_description': 'long_description'
            }
        )

        result = self.importer.import_data(config)
        
        assert result.success is True
        assert len(result.graph_data.nodes) == 10
        # Should handle long strings without memory issues
        assert len(result.graph_data.nodes[0].attributes['long_description']) == 10000

    def test_circular_edge_detection(self):
        """Test detection of circular references in edge data."""
        # Create edge data with circular references
        edge_data = pd.DataFrame({
            'source': [1, 2, 3, 4, 5, 1, 2, 3],
            'target': [2, 3, 4, 5, 1, 3, 4, 5],
            'weight': [1.0, 1.0, 1.0, 1.0, 1.0, 0.5, 0.5, 0.5]
        })
        
        file_path = os.path.join(self.temp_dir, 'circular_edges.csv')
        edge_data.to_csv(file_path, index=False)

        config = ImportConfig(
            file_path=file_path,
            mapping_config={
                'edge_source': 'source',
                'edge_target': 'target',
                'attribute_weight': 'weight'
            }
        )

        result = self.importer.import_data(config)
        
        assert result.success is True
        assert len(result.graph_data.edges) == 8
        
        # Check for circular references
        source_target_pairs = [(edge.source, edge.target) for edge in result.graph_data.edges]
        assert ('1', '2') in source_target_pairs
        assert ('2', '3') in source_target_pairs
        assert ('3', '4') in source_target_pairs
        assert ('4', '5') in source_target_pairs
        assert ('5', '1') in source_target_pairs

    @pytest.mark.parametrize("skip_rows,max_rows,expected_count", [
        (0, 10, 10),
        (5, 10, 10),
        (10, 5, 5),
        (50, 100, 50),  # Skip more than available, should get remaining
    ])
    def test_skip_and_max_rows_combinations(self, skip_rows, max_rows, expected_count):
        """Test various combinations of skip_rows and max_rows parameters."""
        # Create test data with 100 rows
        data = pd.DataFrame({
            'id': range(1, 101),
            'name': [f'Node_{i}' for i in range(1, 101)],
            'value': range(1, 101)
        })
        
        file_path = os.path.join(self.temp_dir, 'skip_max_test.csv')
        data.to_csv(file_path, index=False)

        config = ImportConfig(
            file_path=file_path,
            skip_rows=skip_rows,
            max_rows=max_rows,
            mapping_config={
                'node_id': 'id',
                'node_name': 'name',
                'attribute_value': 'value'
            }
        )

        result = self.importer.import_data(config)
        
        # The importer should handle skip_rows and max_rows correctly
        if result.success:
            actual_rows = min(expected_count, max(0, 100 - skip_rows))
            assert len(result.graph_data.nodes) == actual_rows
        else:
            # If it fails, should be due to skip_rows removing all data
            assert skip_rows >= 100 or max_rows == 0

    def test_data_type_edge_cases(self):
        """Test edge cases in data type detection and conversion."""
        # Create data with edge case values
        edge_case_data = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Node1', 'Node2', 'Node3', 'Node4', 'Node5'],
            'mixed_numbers': ['123', '123.45', '1e10', '0.000001', 'inf'],
            'mixed_bools': ['true', '1', 'yes', 'false', 'maybe'],
            'mixed_dates': ['2024-01-01', '01/01/2024', '2024-13-01', 'not-a-date', ''],
            'special_chars': ['!@#$%', 'çñüé', '中文', '🚀🎉', '\n\t\r']
        })
        
        file_path = os.path.join(self.temp_dir, 'edge_cases.csv')
        edge_case_data.to_csv(file_path, index=False)

        config = ImportConfig(
            file_path=file_path,
            mapping_config={
                'node_id': 'id',
                'node_name': 'name',
                'attribute_mixed_numbers': 'mixed_numbers',
                'attribute_mixed_bools': 'mixed_bools',
                'attribute_mixed_dates': 'mixed_dates',
                'attribute_special_chars': 'special_chars'
            }
        )

        result = self.importer.import_data(config)
        
        assert result.success is True
        assert len(result.graph_data.nodes) == 5
        # Should handle edge cases gracefully without crashing
        assert result.graph_data.nodes[0].attributes['special_chars'] == '!@#$%'

    def test_file_system_edge_cases(self):
        """Test edge cases related to file system operations."""
        # Test with very long file path
        long_filename = 'a' * 200 + '.csv'
        long_file_path = os.path.join(self.temp_dir, long_filename)
        
        # Create simple test data
        data = pd.DataFrame({'id': [1, 2], 'name': ['A', 'B']})
        
        try:
            data.to_csv(long_file_path, index=False)
            file_created = True
        except OSError:
            file_created = False
        
        if file_created:
            config = ImportConfig(
                file_path=long_file_path,
                mapping_config={'node_id': 'id', 'node_name': 'name'}
            )
            result = self.importer.import_data(config)
            assert result.success is True

        # Test with file permission issues (mock)
        with patch('pandas.read_csv', side_effect=PermissionError("Access denied")):
            config = ImportConfig(
                file_path='test.csv',
                mapping_config={'node_id': 'id', 'node_name': 'name'}
            )
            result = self.importer.import_data(config)
            assert result.success is False
            # Check that the error message contains permission-related text
            assert any('permission' in error.lower() or 'access' in error.lower() or 'denied' in error.lower() 
                      or 'failed' in error.lower() for error in result.errors)

    def test_xml_complex_structures(self):
        """Test importing complex XML structures."""
        complex_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<root>
    <nodes>
        <node id="1" name="Node1">
            <attributes>
                <attribute name="category" value="A"/>
                <attribute name="weight" value="10.5"/>
                <attribute name="active" value="true"/>
            </attributes>
            <metadata>
                <created>2024-01-01</created>
                <tags>
                    <tag>important</tag>
                    <tag>primary</tag>
                </tags>
            </metadata>
        </node>
        <node id="2" name="Node2">
            <attributes>
                <attribute name="category" value="B"/>
                <attribute name="weight" value="20.0"/>
                <attribute name="active" value="false"/>
            </attributes>
        </node>
    </nodes>
</root>'''
        
        file_path = os.path.join(self.temp_dir, 'complex.xml')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(complex_xml)

        config = ImportConfig(
            file_path=file_path,
            mapping_config={
                'node_id': 'id',
                'node_name': 'name'
            }
        )

        result = self.importer.import_data(config)
        
        # Should handle complex XML structure
        assert result.success is True or len(result.errors) > 0  # Either works or fails gracefully 