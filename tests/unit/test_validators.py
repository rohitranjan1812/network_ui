"""
Comprehensive tests for data validators.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from network_ui.core.validators import DataValidator


class TestDataValidator:
    """Test DataValidator functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = DataValidator()

    def test_detect_data_type_string(self):
        """Test string data type detection."""
        data = pd.Series(['a', 'b', 'c', 'd'])
        detected_type = self.validator.detect_data_type(data)
        assert detected_type == 'string'

    def test_detect_data_type_integer(self):
        """Test integer data type detection."""
        data = pd.Series([1, 2, 3, 4, 5])
        detected_type = self.validator.detect_data_type(data)
        assert detected_type == 'integer'

    def test_detect_data_type_float(self):
        """Test float data type detection."""
        data = pd.Series([1.5, 2.7, 3.1, 4.9])
        detected_type = self.validator.detect_data_type(data)
        assert detected_type == 'float'

    def test_detect_data_type_boolean(self):
        """Test boolean data type detection."""
        # Test various boolean representations
        boolean_data = [
            pd.Series(['true', 'false', 'true', 'false']),
            pd.Series(['yes', 'no', 'yes', 'no']),
            pd.Series(['1', '0', '1', '0']),
            pd.Series(['t', 'f', 't', 'f']),
            pd.Series(['y', 'n', 'y', 'n'])
        ]

        for data in boolean_data:
            detected_type = self.validator.detect_data_type(data)
            assert detected_type == 'boolean'

    def test_detect_data_type_datetime(self):
        """Test datetime data type detection."""
        data = pd.Series(['2024-01-01 10:00:00', '2024-01-02 11:30:00'])
        detected_type = self.validator.detect_data_type(data)
        assert detected_type == 'datetime'

    def test_detect_data_type_date(self):
        """Test date data type detection."""
        date_formats = [
            pd.Series(['2024-01-01', '2024-01-02']),
            pd.Series(['01/01/2024', '02/01/2024']),
            pd.Series(['2024/01/01', '2024/01/02'])
        ]

        for data in date_formats:
            detected_type = self.validator.detect_data_type(data)
            assert detected_type == 'date'

    def test_detect_data_type_empty_series(self):
        """Test data type detection with empty series."""
        data = pd.Series([])
        detected_type = self.validator.detect_data_type(data)
        assert detected_type == 'string'

    def test_detect_data_type_with_nulls(self):
        """Test data type detection with null values."""
        data = pd.Series([1, 2, np.nan, 4, 5])
        detected_type = self.validator.detect_data_type(data)
        assert detected_type == 'integer'

    def test_validate_mapping_config_valid(self):
        """Test valid mapping configuration."""
        mapping_config = {
            'node_id': 'id',
            'node_name': 'name',
            'attribute_category': 'category'
        }
        available_columns = ['id', 'name', 'category', 'department']

        is_valid, errors = self.validator.validate_mapping_config(
            mapping_config, available_columns)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_mapping_config_missing_required(self):
        """Test mapping configuration with missing required fields."""
        mapping_config = {
            'attribute_category': 'category'
        }
        available_columns = ['category', 'department']

        is_valid, errors = self.validator.validate_mapping_config(
            mapping_config, available_columns)

        assert is_valid is False
        assert len(errors) > 0
        assert any('node_id' in error for error in errors)
        assert any('node_name' in error for error in errors)

    def test_validate_mapping_config_missing_column(self):
        """Test mapping configuration with non-existent column."""
        mapping_config = {
            'node_id': 'id',
            'node_name': 'name',
            'attribute_category': 'nonexistent'
        }
        available_columns = ['id', 'name']

        is_valid, errors = self.validator.validate_mapping_config(
            mapping_config, available_columns)

        assert is_valid is False
        assert len(errors) > 0
        assert any('nonexistent' in error for error in errors)

    def test_validate_mapping_config_duplicate_mappings(self):
        """Test mapping configuration with duplicate column mappings."""
        mapping_config = {
            'node_id': 'id',
            'node_name': 'id',  # Duplicate mapping
            'attribute_category': 'category'
        }
        available_columns = ['id', 'category']

        is_valid, errors = self.validator.validate_mapping_config(
            mapping_config, available_columns)

        assert is_valid is False
        assert len(errors) > 0
        assert any('Duplicate' in error for error in errors)

    def test_validate_data_types_valid(self):
        """Test valid data type validation."""
        data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['a', 'b', 'c'],
            'score': [1.5, 2.7, 3.1],
            'active': ['true', 'false', 'true']
        })
        data_types = {
            'id': 'integer',
            'name': 'string',
            'score': 'float',
            'active': 'boolean'
        }

        is_valid, errors = self.validator.validate_data_types(data, data_types)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_data_types_invalid_conversion(self):
        """Test data type validation with invalid conversions."""
        data = pd.DataFrame({
            'id': [1, 2, 'invalid', 4],
            'score': [1.5, 'not_a_number', 3.1, 4.2]
        })
        data_types = {
            'id': 'integer',
            'score': 'float'
        }

        is_valid, errors = self.validator.validate_data_types(data, data_types)

        assert is_valid is False
        assert len(errors) > 0

    def test_validate_data_types_missing_column(self):
        """Test data type validation with missing column."""
        data = pd.DataFrame({
            'id': [1, 2, 3]
        })
        data_types = {
            'id': 'integer',
            'nonexistent': 'string'
        }

        is_valid, errors = self.validator.validate_data_types(data, data_types)

        assert is_valid is False
        assert len(errors) > 0
        assert any('not found' in error for error in errors)

    def test_validate_file_format_valid(self):
        """Test valid file format validation."""
        valid_files = ['test.csv', 'data.json', 'graph.xml']

        for file_path in valid_files:
            is_valid, error_msg = self.validator.validate_file_format(
                file_path)
            assert is_valid is True
            assert error_msg == ""

    def test_validate_file_format_invalid(self):
        """Test invalid file format validation."""
        invalid_files = ['test.txt', 'data.xlsx', 'graph.pdf']

        for file_path in invalid_files:
            is_valid, error_msg = self.validator.validate_file_format(
                file_path)
            assert is_valid is False
            assert len(error_msg) > 0
            assert 'Unsupported file format' in error_msg

    def test_create_validation_report(self):
        """Test validation report creation."""
        data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['a', 'b', 'c'],
            'score': [1.5, 2.7, 3.1],
            'category': ['A', 'B', 'A']
        })
        mapping_config = {
            'node_id': 'id',
            'node_name': 'name',
            'attribute_category': 'category'
        }
        data_types = {
            'id': 'integer',
            'name': 'string',
            'score': 'float',
            'category': 'string'
        }

        report = self.validator.create_validation_report(
            data, mapping_config, data_types)

        assert 'is_valid' in report
        assert 'errors' in report
        assert 'warnings' in report
        assert 'data_summary' in report
        assert 'type_detection' in report

        assert report['is_valid'] is True
        assert len(report['errors']) == 0
        assert 'total_rows' in report['data_summary']
        assert 'total_columns' in report['data_summary']

    def test_create_validation_report_with_errors(self):
        """Test validation report creation with errors."""
        data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['a', 'b', 'c']
        })
        mapping_config = {
            'node_id': 'id',
            'node_name': 'nonexistent'  # Invalid mapping
        }
        data_types = {
            'id': 'integer',
            'name': 'string'
        }

        report = self.validator.create_validation_report(
            data, mapping_config, data_types)

        assert report['is_valid'] is False
        assert len(report['errors']) > 0
        assert any('nonexistent' in error for error in report['errors'])

    def test_create_validation_report_empty_data(self):
        """Test validation report creation with empty data."""
        data = pd.DataFrame()
        mapping_config = {}
        data_types = {}

        report = self.validator.create_validation_report(
            data, mapping_config, data_types)

        assert report['is_valid'] is False
        assert len(report['warnings']) > 0
        assert any('empty' in warning.lower()
                   for warning in report['warnings'])

    def test_convert_to_boolean(self):
        """Test boolean conversion."""
        data = pd.Series(['true', 'false', 'yes', 'no',
                         '1', '0', 't', 'f', 'y', 'n'])
        converted = self.validator._convert_to_boolean(data)

        expected = [
            True,
            False,
            True,
            False,
            True,
            False,
            True,
            False,
            True,
            False]
        assert list(converted) == expected
