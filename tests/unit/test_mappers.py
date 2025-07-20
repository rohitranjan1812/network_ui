"""
Comprehensive tests for data mappers.
"""

import pandas as pd
import numpy as np
from network_ui.core.mappers import DataMapper


class TestDataMapper:
    """Test DataMapper functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mapper = DataMapper()

    def test_set_mapping_config(self):
        """Test setting mapping configuration."""
        mapping_config = {
            'node_id': 'id',
            'node_name': 'name',
            'attribute_category': 'category'
        }

        self.mapper.set_mapping_config(mapping_config)

        assert self.mapper.mapping_config == mapping_config

    def test_set_data_types(self):
        """Test setting data types."""
        data_types = {
            'id': 'integer',
            'name': 'string',
            'category': 'string'
        }

        self.mapper.set_data_types(data_types)

        assert self.mapper.data_types == data_types

    def test_create_default_mapping_with_id_name(self):
        """Test default mapping creation with ID and name columns."""
        columns = ['id', 'name', 'category', 'department']

        default_mapping = self.mapper.create_default_mapping(columns)

        assert 'node_id' in default_mapping
        assert 'node_name' in default_mapping
        assert default_mapping['node_id'] == 'id'
        assert default_mapping['node_name'] == 'name'

        # Check that remaining columns are mapped as attributes
        assert 'attribute_category' in default_mapping
        assert 'attribute_department' in default_mapping

    def test_create_default_mapping_without_id_name(self):
        """Test default mapping creation without ID and name columns."""
        columns = ['category', 'department', 'region']

        default_mapping = self.mapper.create_default_mapping(columns)

        # Should still have node_id and node_name mappings (empty)
        assert 'node_id' in default_mapping
        assert 'node_name' in default_mapping

        # All columns should be mapped as attributes
        assert 'attribute_category' in default_mapping
        assert 'attribute_department' in default_mapping
        assert 'attribute_region' in default_mapping

    def test_create_default_mapping_edge_columns(self):
        """Test default mapping creation with edge columns."""
        columns = ['source', 'target', 'weight', 'type']

        default_mapping = self.mapper.create_default_mapping(columns)

        assert 'edge_source' in default_mapping
        assert 'edge_target' in default_mapping
        assert default_mapping['edge_source'] == 'source'
        assert default_mapping['edge_target'] == 'target'

    def test_detect_data_types(self):
        """Test automatic data type detection."""
        data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['a', 'b', 'c'],
            'score': [1.5, 2.7, 3.1],
            'active': ['true', 'false', 'true'],
            'date': ['2024-01-01', '2024-01-02', '2024-01-03']
        })

        detected_types = self.mapper.detect_data_types(data)

        assert detected_types['id'] == 'integer'
        assert detected_types['name'] == 'string'
        assert detected_types['score'] == 'float'
        assert detected_types['active'] == 'boolean'
        assert detected_types['date'] == 'date'

    def test_transform_data_types(self):
        """Test data type transformation."""
        data = pd.DataFrame({
            'id': ['1', '2', '3'],
            'name': ['a', 'b', 'c'],
            'score': ['1.5', '2.7', '3.1'],
            'active': ['true', 'false', 'true']
        })

        data_types = {
            'id': 'integer',
            'name': 'string',
            'score': 'float',
            'active': 'boolean'
        }

        self.mapper.set_data_types(data_types)
        transformed_data = self.mapper.transform_data_types(data)

        assert transformed_data['id'].dtype == 'Int64'
        assert transformed_data['name'].dtype == 'object'
        assert transformed_data['score'].dtype == 'float64'
        # Boolean as object
        assert transformed_data['active'].dtype == 'object'

    def test_transform_data_types_with_errors(self):
        """Test data type transformation with conversion errors."""
        data = pd.DataFrame({
            'id': ['1', 'invalid', '3'],
            'score': ['1.5', 'not_a_number', '3.1']
        })

        data_types = {
            'id': 'integer',
            'score': 'float'
        }

        self.mapper.set_data_types(data_types)
        transformed_data = self.mapper.transform_data_types(data)

        # Should handle errors gracefully and continue
        assert 'id' in transformed_data.columns
        assert 'score' in transformed_data.columns

    def test_create_data_preview(self):
        """Test data preview creation."""
        data = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['a', 'b', 'c', 'd', 'e'],
            'category': ['A', 'B', 'A', 'B', 'A']
        })

        preview = self.mapper.create_data_preview(data, max_rows=3)

        assert preview['columns'] == ['id', 'name', 'category']
        assert preview['total_rows'] == 5
        assert preview['preview_rows'] == 3
        assert len(preview['data']) == 3

        # Check column info
        assert 'id' in preview['column_info']
        assert 'name' in preview['column_info']
        assert 'category' in preview['column_info']

        # Check data types in column info
        assert preview['column_info']['id']['data_type'] == 'integer'
        assert preview['column_info']['name']['data_type'] == 'string'
        assert preview['column_info']['category']['data_type'] == 'string'

    def test_validate_mapping_valid(self):
        """Test mapping validation with valid configuration."""
        data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['a', 'b', 'c'],
            'category': ['A', 'B', 'A']
        })

        self.mapper.set_mapping_config({
            'node_id': 'id',
            'node_name': 'name',
            'attribute_category': 'category'
        })

        is_valid, errors = self.mapper.validate_mapping(data)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_mapping_invalid(self):
        """Test mapping validation with invalid configuration."""
        data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['a', 'b', 'c']
        })

        self.mapper.set_mapping_config({
            'node_id': 'id',
            'node_name': 'nonexistent'  # Invalid mapping
        })

        is_valid, errors = self.mapper.validate_mapping(data)

        assert is_valid is False
        assert len(errors) > 0

    def test_get_mapping_suggestions(self):
        """Test mapping suggestions generation."""
        data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['a', 'b', 'c'],
            'source': [1, 2, 3],
            'target': [2, 3, 1],
            'category': ['A', 'B', 'A'],
            'department': ['Sales', 'Tech', 'HR']
        })

        suggestions = self.mapper.get_mapping_suggestions(data)

        # Check ID suggestions
        assert 'id' in suggestions['node_id']

        # Check name suggestions
        assert 'name' in suggestions['node_name']

        # Check source/target suggestions
        assert 'source' in suggestions['edge_source']
        assert 'target' in suggestions['edge_target']

        # Check attribute suggestions
        assert 'category' in suggestions['node_attributes']
        assert 'department' in suggestions['node_attributes']

    def test_create_mapping_ui_config(self):
        """Test mapping UI configuration creation."""
        data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['a', 'b', 'c'],
            'category': ['A', 'B', 'A'],
            'score': [1.5, 2.7, 3.1]
        })

        ui_config = self.mapper.create_mapping_ui_config(data)

        assert 'columns' in ui_config
        assert 'detected_types' in ui_config
        assert 'suggestions' in ui_config
        assert 'current_mapping' in ui_config
        assert 'supported_types' in ui_config
        assert 'data_preview' in ui_config

        assert ui_config['columns'] == ['id', 'name', 'category', 'score']
        assert 'id' in ui_config['detected_types']
        assert 'name' in ui_config['detected_types']
        assert 'category' in ui_config['detected_types']
        assert 'score' in ui_config['detected_types']

    def test_convert_to_boolean(self):
        """Test boolean conversion."""
        data = pd.Series(['true', 'false', 'yes', 'no',
                         '1', '0', 't', 'f', 'y', 'n'])
        converted = self.mapper._convert_to_boolean(data)

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
