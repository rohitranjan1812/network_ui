"""
Integration tests for the Network UI platform.

These tests verify that different components work together correctly.
"""

import pytest
import pandas as pd
from network_ui.core import DataImporter, ImportConfig
from network_ui.core.models import GraphData
from network_ui.core.validators import DataValidator
from network_ui.core.mappers import DataMapper
from network_ui.core.transformers import GraphTransformer


@pytest.mark.integration
class TestComponentIntegration:
    """Test integration between different components."""

    def test_importer_validator_integration(self):
        """Test that importer and validator work together."""
        # Create components
        validator = DataValidator()

        # Create test data
        data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Team A', 'Team B', 'Team C'],
            'category': ['Engineering', 'Sales', 'Marketing']
        })

        # Test validation integration
        mapping_config = {
            'node_id': 'id',
            'node_name': 'name',
            'node_attributes': ['category']
        }

        is_valid, errors = validator.validate_mapping_config(
            mapping_config, list(data.columns)
        )

        assert is_valid
        assert len(errors) == 0

    def test_importer_mapper_integration(self):
        """Test that importer and mapper work together."""
        # Create components
        mapper = DataMapper()

        # Create test data
        data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Team A', 'Team B', 'Team C'],
            'category': ['Engineering', 'Sales', 'Marketing']
        })

        # Test mapping integration
        mapper.set_mapping_config({
            'node_id': 'id',
            'node_name': 'name',
            'node_attributes': ['category']
        })

        preview = mapper.create_data_preview(data)

        assert 'columns' in preview
        assert 'data' in preview
        assert len(preview['data']) == 3

    def test_importer_transformer_integration(self):
        """Test that importer and transformer work together."""
        # Create components
        transformer = GraphTransformer()

        # Create test data
        data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Team A', 'Team B', 'Team C'],
            'category': ['Engineering', 'Sales', 'Marketing']
        })

        # Test transformation integration
        mapping_config = {
            'node_id': 'id',
            'node_name': 'name',
            'node_attributes': ['category']
        }

        data_types = {
            'id': 'integer',
            'name': 'string',
            'category': 'string'
        }

        graph_data = transformer.transform_to_graph(
            data, mapping_config, data_types
        )

        assert isinstance(graph_data, GraphData)
        assert len(graph_data.nodes) == 3
        assert len(graph_data.edges) == 0

    def test_full_pipeline_integration(self):
        """Test the complete data import pipeline."""
        # Create importer
        importer = DataImporter()

        # Create test data
        data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Team A', 'Team B', 'Team C'],
            'category': ['Engineering', 'Sales', 'Marketing'],
            'performance': [85.5, 92.3, 78.9]
        })

        # Test complete pipeline
        config = ImportConfig(
            file_path="test_data.csv",
            mapping_config={
                'node_id': 'id',
                'node_name': 'name',
                'node_attributes': ['category', 'performance']
            },
            data_types={
                'id': 'integer',
                'name': 'string',
                'category': 'string',
                'performance': 'float'
            }
        )

        # Mock the file reading to use our test data
        with pytest.MonkeyPatch().context() as m:
            m.setattr(importer, '_read_file', lambda x: data)
            result = importer.import_data(config)

        assert result.success
        assert result.graph_data is not None
        assert len(result.graph_data.nodes) == 3
        assert len(result.errors) == 0

    def test_edge_data_integration(self):
        """Test integration with edge data."""
        # Create components
        transformer = GraphTransformer()

        # Create edge data
        edge_data = pd.DataFrame({
            'source': [1, 2, 3],
            'target': [2, 3, 1],
            'relationship_type': ['collaborates', 'reports_to', 'mentors'],
            'weight': [0.8, 0.9, 0.6]
        })

        # Test edge transformation
        mapping_config = {
            'edge_source': 'source',
            'edge_target': 'target',
            'edge_type': 'relationship_type',
            'edge_weight': 'weight'
        }

        data_types = {
            'source': 'integer',
            'target': 'integer',
            'relationship_type': 'string',
            'weight': 'float'
        }

        graph_data = transformer.transform_to_graph(
            edge_data, mapping_config, data_types
        )

        assert isinstance(graph_data, GraphData)
        assert len(graph_data.edges) == 3
        assert len(graph_data.nodes) == 3  # Should create nodes for sources/targets

    def test_validation_pipeline_integration(self):
        """Test validation pipeline integration."""
        # Create components
        validator = DataValidator()
        mapper = DataMapper()

        # Create test data
        data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Team A', 'Team B', 'Team C'],
            'category': ['Engineering', 'Sales', 'Marketing']
        })

        # Test validation pipeline
        mapping_config = {
            'node_id': 'id',
            'node_name': 'name',
            'node_attributes': ['category']
        }

        # Validate mapping
        is_valid, errors = validator.validate_mapping_config(
            mapping_config, list(data.columns)
        )

        assert is_valid
        assert len(errors) == 0

        # Test mapping with validated config
        mapper.set_mapping_config(mapping_config)
        preview = mapper.create_data_preview(data)

        assert 'columns' in preview
        assert 'data' in preview

    def test_data_preview_integration(self):
        """Test data preview integration."""
        # Create importer
        importer = DataImporter()

        # Create test data
        data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Team A', 'Team B', 'Team C'],
            'category': ['Engineering', 'Sales', 'Marketing']
        })

        # Mock file reading
        with pytest.MonkeyPatch().context() as m:
            m.setattr(importer, '_read_file', lambda x: data)
            preview = importer.get_data_preview("test.csv", max_rows=2)

        assert preview is not None
        assert 'total_rows' in preview
        assert 'preview_rows' in preview
        assert 'columns' in preview
        assert 'data' in preview

    def test_mapping_ui_integration(self):
        """Test mapping UI configuration integration."""
        # Create importer
        importer = DataImporter()

        # Create test data
        data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Team A', 'Team B', 'Team C'],
            'category': ['Engineering', 'Sales', 'Marketing']
        })

        # Mock file reading
        with pytest.MonkeyPatch().context() as m:
            m.setattr(importer, '_read_file', lambda x: data)
            ui_config = importer.create_mapping_ui_config("test.csv")

        assert ui_config is not None
        assert 'columns' in ui_config
        assert 'detected_types' in ui_config
        assert 'suggestions' in ui_config
        assert 'supported_types' in ui_config 