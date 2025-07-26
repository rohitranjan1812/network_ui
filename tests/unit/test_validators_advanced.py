"""
Advanced Test Cases for Data Validator
Tests boundary conditions, complex validation scenarios, and edge cases.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, date
from network_ui.core.validators import DataValidator


@pytest.mark.unit
class TestDataValidatorAdvanced:
    """Advanced test cases for DataValidator with boundary conditions and edge cases."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = DataValidator()

    @pytest.mark.parametrize("data_values,expected_type", [
        # Integer edge cases
        ([0, 1, -1, 2147483647, -2147483648], 'integer'),
        (['0', '1', '-1', '999999999'], 'integer'),
        ([0.0, 1.0, 2.0], 'integer'),  # Floats that are actually integers
        
        # Float edge cases
        ([0.1, 1.5, -2.7, 3.14159], 'float'),
        ([1e10, 1e-10, float('inf'), -float('inf')], 'float'),
        (['1.5', '2.7', '3.14'], 'float'),
        ([np.nan, 1.5, 2.7], 'float'),  # NaN handling
        
        # Boolean edge cases
        (['True', 'False'], 'boolean'),
        (['true', 'false'], 'boolean'),
        (['YES', 'NO'], 'boolean'),
        (['1', '0'], 'boolean'),
        (['Yes', 'No'], 'boolean'),  # Changed from ['T', 'F'] to be less ambiguous
        (['y', 'n'], 'boolean'),
        
        # String edge cases
        (['', ' ', 'text'], 'string'),
        (['123abc', 'abc123', 'mixed'], 'string'),
        (['None', 'null', 'undefined'], 'string'),
        
        # Date edge cases
        (['2024-01-01', '2024-12-31'], 'date'),
        (['01/01/2024', '12/31/2024'], 'date'),
        (['2024/01/01', '2024/12/31'], 'date'),
        
        # Datetime edge cases
        (['2024-01-01 12:30:45', '2024-12-31 23:59:59'], 'datetime'),
        (['2024-01-01T12:30:45Z', '2024-12-31T00:00:00'], 'datetime'),
    ])
    def test_data_type_detection_boundary_cases(self, data_values, expected_type):
        """Test data type detection with boundary cases and edge values."""
        data = pd.Series(data_values)
        detected_type = self.validator.detect_data_type(data)
        
        # Allow either 'date' or 'datetime' for date-like data
        if expected_type == 'date':
            assert detected_type in ['date', 'datetime'], f"Expected date/datetime, got {detected_type}"
        else:
            assert detected_type == expected_type

    @pytest.mark.parametrize("mixed_data,expected_type", [
        # Mixed numeric types should default to most general
        (['1', '2.5', '3'], 'float'),
        ([1, 2.5, 3], 'float'),
        (['1', '2', 'abc'], 'string'),
        
        # Mixed boolean patterns
        (['true', 'false', 'maybe'], 'string'),  # Invalid boolean should become string
        (['1', '0', '2'], 'integer'),  # Not all 1/0 values are boolean
        
        # Mixed date patterns
        (['2024-01-01', '2024-13-01'], 'string'),  # Invalid date should become string
        (['2024-01-01', 'not-a-date'], 'string'),
    ])
    def test_mixed_data_type_resolution(self, mixed_data, expected_type):
        """Test data type detection with mixed data that should resolve to specific types."""
        data = pd.Series(mixed_data)
        detected_type = self.validator.detect_data_type(data)
        assert detected_type == expected_type

    def test_extremely_large_datasets(self):
        """Test validation performance with extremely large datasets."""
        # Create large dataset for performance testing
        large_size = 100000
        large_data = pd.Series(range(large_size))
        
        # Should complete in reasonable time
        import time
        start_time = time.time()
        data_type = self.validator.detect_data_type(large_data)
        end_time = time.time()
        
        assert data_type == 'integer'
        assert end_time - start_time < 5.0  # Should complete within 5 seconds

    @pytest.mark.parametrize("null_ratio", [0.0, 0.1, 0.5, 0.9, 0.99, 1.0])
    def test_high_null_ratio_datasets(self, null_ratio):
        """Test data type detection with various null ratios."""
        size = 1000
        null_count = int(size * null_ratio)
        
        # Create data with specified null ratio
        values = [1, 2, 3, 4, 5] * (size // 5 + 1)
        values = values[:size]
        
        # Replace with nulls
        for i in range(null_count):
            values[i] = None
        
        data = pd.Series(values)
        data_type = self.validator.detect_data_type(data)
        
        if null_ratio < 1.0:
            assert data_type == 'integer'
        else:
            assert data_type == 'string'  # All nulls default to string

    def test_unicode_and_special_characters(self):
        """Test data type detection with unicode and special characters."""
        unicode_data = pd.Series([
            '测试数据',  # Chinese
            'тест данных',  # Russian
            'テストデータ',  # Japanese
            '🚀🎉💻',  # Emojis
            'café résumé naïve',  # Accented characters
            '\n\t\r',  # Control characters
            '\\x00\\x01\\x02'  # Escape sequences
        ])
        
        data_type = self.validator.detect_data_type(unicode_data)
        assert data_type == 'string'

    @pytest.mark.parametrize("mapping_config,columns,should_be_valid", [
        # Valid node mappings
        ({'node_id': 'id', 'node_name': 'name'}, ['id', 'name', 'extra'], True),
        
        # Valid edge mappings
        ({'edge_source': 'from', 'edge_target': 'to'}, ['from', 'to', 'type'], True),
        
        # Missing required fields (node_name is now optional, so this should be valid)
        ({'node_id': 'id'}, ['id', 'name'], True),  # node_name is optional
        ({'edge_source': 'from'}, ['from', 'to'], False),  # Missing edge_target
        
        # Invalid column references
        ({'node_id': 'missing_col', 'node_name': 'name'}, ['id', 'name'], False),
        
        # Duplicate mappings
        ({'node_id': 'id', 'node_name': 'id'}, ['id', 'name'], False),
        
        # Complex valid mappings
        ({
            'node_id': 'id',
            'node_name': 'name',
            'node_level': 'level',
            'attribute_category': 'cat',
            'attribute_value': 'val',
            'kpi_performance': 'perf'
        }, ['id', 'name', 'level', 'cat', 'val', 'perf'], True),
        
        # Mixed node and edge (invalid)
        ({
            'node_id': 'id',
            'edge_source': 'from'
        }, ['id', 'from'], False),
    ])
    def test_complex_mapping_validation(self, mapping_config, columns, should_be_valid):
        """Test validation of complex mapping configurations."""
        is_valid, errors = self.validator.validate_mapping_config(mapping_config, columns)
        
        if should_be_valid:
            assert is_valid is True
            assert len(errors) == 0
        else:
            assert is_valid is False
            assert len(errors) > 0

    def test_boundary_value_data_types(self):
        """Test data type validation with boundary values."""
        boundary_cases = {
            'max_int': pd.Series([2147483647, 2147483646]),
            'min_int': pd.Series([-2147483648, -2147483647]),
            'max_float': pd.Series([1.7976931348623157e+308]),
            'min_float': pd.Series([2.2250738585072014e-308]),
            'zero_values': pd.Series([0, 0.0, '0']),
            'inf_values': pd.Series([float('inf'), -float('inf')]),
            'nan_values': pd.Series([np.nan, None, pd.NA]),
        }
        
        for case_name, data in boundary_cases.items():
            data_type = self.validator.detect_data_type(data)
            # Should not crash and should return a valid type
            assert data_type in ['integer', 'float', 'string', 'boolean', 'date', 'datetime']

    @pytest.mark.parametrize("data_types,columns,should_be_valid", [
        # Valid data type mappings
        ({'id': 'integer', 'name': 'string'}, ['id', 'name'], True),
        ({'value': 'float', 'active': 'boolean'}, ['value', 'active'], True),
        ({'created': 'date', 'updated': 'datetime'}, ['created', 'updated'], True),
        
        # Invalid data type names
        ({'id': 'invalid_type'}, ['id'], False),
        ({'value': 'number'}, ['value'], False),  # Should be 'float' or 'integer'
        
        # Missing columns
        ({'missing_col': 'string'}, ['id', 'name'], False),
        
        # Complex valid mappings
        ({
            'id': 'integer',
            'name': 'string',
            'value': 'float',
            'active': 'boolean',
            'created': 'date',
            'updated': 'datetime'
        }, ['id', 'name', 'value', 'active', 'created', 'updated'], True),
    ])
    def test_data_type_mapping_validation(self, data_types, columns, should_be_valid):
        """Test validation of data type mappings."""
        # Create test data based on the columns
        test_data = {}
        for col in columns:
            if 'id' in col:
                test_data[col] = [1, 2, 3]
            elif 'name' in col:
                test_data[col] = ['A', 'B', 'C']
            elif 'value' in col:
                test_data[col] = [1.5, 2.7, 3.1]
            elif 'active' in col:
                test_data[col] = [True, False, True]
            elif 'created' in col or 'updated' in col:
                test_data[col] = ['2024-01-01', '2024-02-01', '2024-03-01']
            else:
                test_data[col] = ['val1', 'val2', 'val3']
        
        df = pd.DataFrame(test_data)
        is_valid, errors = self.validator.validate_data_types(df, data_types)
        
        if should_be_valid:
            assert is_valid is True
            assert len(errors) == 0
        else:
            assert is_valid is False
            assert len(errors) > 0

    def test_circular_reference_detection(self):
        """Test detection of circular references in mappings."""
        # This would be handled at the transformer level, but we can test basic duplicate detection
        circular_mapping = {
            'node_id': 'col1',
            'node_name': 'col1',  # Same column mapped twice
            'attribute_type': 'col1'  # Same column mapped three times
        }
        
        is_valid, errors = self.validator.validate_mapping_config(
            circular_mapping, 
            ['col1', 'col2']
        )
        
        assert is_valid is False
        assert any('duplicate' in error.lower() for error in errors)

    def test_memory_stress_validation(self):
        """Test validator behavior under memory stress conditions."""
        # Create very large data with different patterns
        large_datasets = [
            # Large integer dataset
            pd.Series(range(50000)),
            
            # Large string dataset
            pd.Series([f'string_{i}' for i in range(50000)]),
            
            # Large mixed dataset
            pd.Series([i if i % 2 == 0 else f'str_{i}' for i in range(50000)]),
        ]
        
        for i, dataset in enumerate(large_datasets):
            data_type = self.validator.detect_data_type(dataset)
            # Should complete without memory errors
            assert data_type in ['integer', 'string']

    def test_malformed_date_detection(self):
        """Test detection of malformed dates and proper fallback."""
        malformed_dates = pd.Series([
            '2024-02-30',  # Invalid date (Feb 30th doesn't exist)
            '2024-13-01',  # Invalid month
            '2024-01-32',  # Invalid day
            '0000-01-01',  # Edge case year
            '9999-12-31',  # Edge case year
            '24-01-01',    # Ambiguous year format
            '2024/13/45',  # Invalid month and day
            '2024-1-1',    # Non-zero-padded (might be valid)
            'Jan 1, 2024', # Different format
            '1/1/24',      # Ambiguous format
        ])
        
        data_type = self.validator.detect_data_type(malformed_dates)
        # Should fall back to string for malformed dates
        assert data_type == 'string'

    def test_numeric_overflow_handling(self):
        """Test handling of numeric overflow conditions."""
        overflow_data = pd.Series([
            '999999999999999999999999999999999999999',  # Very large number
            '-999999999999999999999999999999999999999',  # Very large negative
            '1e1000',  # Scientific notation overflow
            '1e-1000',  # Scientific notation underflow
        ])
        
        data_type = self.validator.detect_data_type(overflow_data)
        # Should handle overflow gracefully
        assert data_type in ['float', 'string']

    @pytest.mark.parametrize("file_format,should_be_valid", [
        ('csv', True),
        ('json', True),
        ('xml', True),
        ('txt', False),
        ('xlsx', False),
        ('doc', False),
        ('pdf', False),
        ('', False),
        (None, False),
        ('CSV', True),  # Case insensitive
        ('JSON', True),
        ('file.csv', True),  # With filename
        ('path/to/file.json', True),
        ('/absolute/path/file.xml', True),
        ('file.unknown', False),
    ])
    def test_file_format_validation_edge_cases(self, file_format, should_be_valid):
        """Test file format validation with various edge cases."""
        is_valid, error = self.validator.validate_file_format(file_format)
        
        if should_be_valid:
            assert is_valid is True
            assert error == ""  # Empty string for valid cases
        else:
            assert is_valid is False
            assert error != ""  # Non-empty error message for invalid cases

    def test_validation_report_completeness(self):
        """Test that validation reports contain all required information."""
        test_data = pd.DataFrame({
            'id': [1, 2, 3, None, 5],
            'name': ['A', 'B', '', 'D', 'E'],
            'value': [1.5, 2.7, None, 4.2, 'invalid'],
            'active': [True, False, None, True, 'maybe'],
            'date': ['2024-01-01', '2024-02-01', 'invalid', None, '2024-05-01']
        })
        
        mapping_config = {
            'node_id': 'id',
            'node_name': 'name',
            'attribute_value': 'value',
            'attribute_active': 'active',
            'attribute_date': 'date'
        }

        # Create data types dictionary
        data_types = {
            'id': 'integer',
            'name': 'string',
            'value': 'float',
            'active': 'boolean',
            'date': 'date'
        }
        
        report = self.validator.create_validation_report(test_data, mapping_config, data_types)
        
        # Check report completeness
        assert 'data_quality' in report
        assert 'mapping_validation' in report
        assert 'recommendations' in report
        assert 'summary' in report
        
        # Check data quality metrics
        dq = report['data_quality']
        assert 'total_rows' in dq
        assert 'null_counts' in dq
        assert 'data_types' in dq
        assert 'duplicate_counts' in dq
        
        # Check mapping validation
        mv = report['mapping_validation']
        assert 'is_valid' in mv
        assert 'errors' in mv
        assert 'warnings' in mv

    def test_performance_with_wide_datasets(self):
        """Test validator performance with datasets having many columns."""
        # Create dataset with many columns
        num_cols = 1000
        num_rows = 100
        
        data = {}
        for i in range(num_cols):
            data[f'col_{i}'] = [f'value_{j}_{i}' for j in range(num_rows)]
        
        df = pd.DataFrame(data)
        
        # Test data type detection for each column
        import time
        start_time = time.time()
        
        detected_types = {}
        for col in df.columns:
            detected_types[col] = self.validator.detect_data_type(df[col])
        
        end_time = time.time()
        
        # Should complete within reasonable time
        assert end_time - start_time < 10.0  # 10 seconds for 1000 columns
        assert len(detected_types) == num_cols
        assert all(dtype == 'string' for dtype in detected_types.values())

    def test_concurrent_validation_safety(self):
        """Test thread safety of validation operations."""
        import threading
        import time
        
        # Create test data
        test_data = pd.Series([1, 2, 3, 4, 5] * 1000)
        
        results = []
        errors = []
        
        def validate_worker(worker_id):
            try:
                validator = DataValidator()  # Each thread gets its own instance
                for _ in range(10):  # Multiple validations per thread
                    result = validator.detect_data_type(test_data)
                    results.append((worker_id, result))
                    time.sleep(0.01)  # Small delay to encourage race conditions
            except Exception as e:
                errors.append((worker_id, str(e)))
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=validate_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(errors) == 0, f"Errors in concurrent validation: {errors}"
        assert len(results) == 50  # 5 threads * 10 validations each
        assert all(result == 'integer' for _, result in results) 