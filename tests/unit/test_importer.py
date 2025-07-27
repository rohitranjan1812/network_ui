"""
Comprehensive tests for the main data importer.
"""

import os
import tempfile
from network_ui.core import DataImporter, ImportConfig
from network_ui.core.models import GraphData, Node, Edge


class TestDataImporter:
    """Test DataImporter functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.importer = DataImporter()

    def test_csv_import_success(self):
        """Test successful CSV import."""
        config = ImportConfig(
            file_path="data/test_data/test_data.csv",
            mapping_config={
                "node_id": "id",
                "node_name": "name",
                "attribute_category": "category",
                "kpi_performance": "performance_score"
            },
            data_types={
                "id": "integer",
                "name": "string",
                "category": "string",
                "performance_score": "float"
            }
        )

        result = self.importer.import_data(config)

        assert result.success is True
        assert result.processed_rows == 8
        assert len(result.graph_data.nodes) == 8
        assert len(result.graph_data.edges) == 0
        assert len(result.errors) == 0

    def test_json_import_success(self):
        """Test successful JSON import."""
        config = ImportConfig(
            file_path="data/test_data/test_data_json.json",
            mapping_config={
                "node_id": "id",
                "node_name": "name",
                "attribute_category": "category",
                "kpi_performance": "performance_score"
            },
            data_types={
                "id": "integer",
                "name": "string",
                "category": "string",
                "performance_score": "float"
            }
        )

        result = self.importer.import_data(config)

        assert result.success is True
        assert result.processed_rows == 3
        assert len(result.graph_data.nodes) == 3
        assert len(result.graph_data.edges) == 0
        assert len(result.errors) == 0

    def test_xml_import_success(self):
        """Test successful XML import."""
        config = ImportConfig(
            file_path="data/test_data/test_data_xml.xml",
            mapping_config={
                "node_id": "id",
                "node_name": "name",
                "attribute_category": "category",
                "kpi_performance": "performance_score"
            },
            data_types={
                "id": "integer",
                "name": "string",
                "category": "string",
                "performance_score": "float"
            }
        )

        result = self.importer.import_data(config)

        assert result.success is True
        assert result.processed_rows == 3
        assert len(result.graph_data.nodes) == 3
        assert len(result.graph_data.edges) == 0
        assert len(result.errors) == 0

    def test_edge_import_success(self):
        """Test successful edge data import."""
        config = ImportConfig(
            file_path="data/test_data/test_edges.csv",
            mapping_config={
                "edge_source": "source",
                "edge_target": "target",
                "edge_type": "relationship_type",
                "edge_weight": "weight",
                "kpi_collaboration": "collaboration_score"
            },
            data_types={
                "source": "integer",
                "target": "integer",
                "relationship_type": "string",
                "weight": "float",
                "collaboration_score": "float"
            }
        )

        result = self.importer.import_data(config)

        assert result.success is True
        assert result.processed_rows == 8
        assert len(result.graph_data.nodes) == 8  # Auto - created nodes
        assert len(result.graph_data.edges) == 8
        assert len(result.errors) == 0

    def test_import_with_default_mapping(self):
        """Test import with automatic default mapping."""
        config = ImportConfig(
            file_path="data/test_data/test_data.csv"
            # No mapping_config provided, should use default
        )

        result = self.importer.import_data(config)

        assert result.success is True
        assert result.processed_rows == 8
        assert len(result.graph_data.nodes) == 8
        assert len(result.errors) == 0

    def test_import_with_automatic_data_types(self):
        """Test import with automatic data type detection."""
        config = ImportConfig(
            file_path="data/test_data/test_data.csv",
            mapping_config={
                "node_id": "id",
                "node_name": "name",
                "attribute_category": "category"
            }
            # No data_types provided, should auto - detect
        )

        result = self.importer.import_data(config)

        assert result.success is True
        assert result.processed_rows == 8
        assert len(result.graph_data.nodes) == 8
        assert len(result.errors) == 0

    def test_import_invalid_file_format(self):
        """Test import with invalid file format."""
        # Create a temporary file with invalid extension
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b"id,name\n1,test\n")
            temp_file = f.name

        try:
            config = ImportConfig(file_path=temp_file)
            result = self.importer.import_data(config)

            assert result.success is False
            assert len(result.errors) > 0
            assert any(
                'Unsupported file format' in error for error in result.errors)
        finally:
            os.unlink(temp_file)

    def test_import_nonexistent_file(self):
        """Test import with non - existent file."""
        config = ImportConfig(file_path="nonexistent_file.csv")
        result = self.importer.import_data(config)

        assert result.success is False
        assert len(result.errors) > 0
        assert any(
            'Failed to read data file' in error for error in result.errors)

    def test_import_invalid_mapping(self):
        """Test import with invalid mapping configuration."""
        config = ImportConfig(
            file_path="data/test_data/test_data.csv",
            mapping_config={
                "node_id": "id",
                "node_name": "nonexistent_column"  # Invalid column
            }
        )

        result = self.importer.import_data(config)

        assert result.success is False
        assert len(result.errors) > 0
        assert any('nonexistent_column' in error for error in result.errors)

    def test_import_invalid_data_types(self):
        """Test import with invalid data types."""
        config = ImportConfig(
            file_path="data/test_data/test_data_invalid.csv",
            mapping_config={
                "node_id": "id",
                "node_name": "name",
                "kpi_performance": "performance_score"
            },
            data_types={
                "id": "integer",
                "name": "string",
                "performance_score": "float"  # Will fail on invalid data
            }
        )

        result = self.importer.import_data(config)

        # Should fail due to invalid data types
        assert result.success is False
        assert len(result.errors) > 0
        assert any('performance_score' in error for error in result.errors)

    def test_import_empty_file(self):
        """Test import with empty file."""
        config = ImportConfig(
            file_path="data/test_data/test_data_empty.csv",
            mapping_config={
                "node_id": "id",
                "node_name": "name"
            }
        )

        result = self.importer.import_data(config)

        assert result.success is True
        assert result.processed_rows == 0
        assert len(result.graph_data.nodes) == 0
        assert len(result.warnings) > 0

    def test_import_with_duplicate_ids(self):
        """Test import with duplicate node IDs."""
        config = ImportConfig(
            file_path="data/test_data/test_data_duplicates.csv",
            mapping_config={
                "node_id": "id",
                "node_name": "name",
                "attribute_category": "category"
            }
        )

        result = self.importer.import_data(config)

        # Should fail due to duplicate IDs
        assert result.success is False
        assert len(result.errors) > 0
        assert any('Duplicate node IDs' in error for error in result.errors)

    def test_import_with_skip_rows(self):
        """Test import with skip rows configuration."""
        config = ImportConfig(
            file_path="data/test_data/test_data.csv",
            skip_rows=1,  # Skip header only
            mapping_config={
                "node_id": "id",  # Use actual column names
                "node_name": "name"
            }
        )

        result = self.importer.import_data(config)

        assert result.success is True
        assert result.processed_rows == 7  # 8 - 1 skipped row (header)
        assert len(result.graph_data.nodes) == 7

    def test_import_with_max_rows(self):
        """Test import with max rows configuration."""
        config = ImportConfig(
            file_path="data/test_data/test_data.csv",
            max_rows=3,
            mapping_config={
                "node_id": "id",
                "node_name": "name"
            }
        )

        result = self.importer.import_data(config)

        assert result.success is True
        assert result.processed_rows == 3
        assert len(result.graph_data.nodes) == 3

    def test_import_with_custom_delimiter(self):
        """Test import with custom delimiter."""
        # Create a CSV file with semicolon delimiter
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            f.write(b"id;name;category\n1;test1;A\n2;test2;B\n")
            temp_file = f.name

        try:
            config = ImportConfig(
                file_path=temp_file,
                delimiter=";",
                mapping_config={
                    "node_id": "id",
                    "node_name": "name",
                    "attribute_category": "category"
                }
            )

            result = self.importer.import_data(config)

            assert result.success is True
            assert result.processed_rows == 2
            assert len(result.graph_data.nodes) == 2
        finally:
            os.unlink(temp_file)

    def test_get_data_preview_success(self):
        """Test successful data preview."""
        preview = self.importer.get_data_preview(
            "data/test_data/test_data.csv", max_rows=3)

        assert preview is not None
        assert preview['total_rows'] == 3  # Limited by max_rows
        assert preview['preview_rows'] == 3  # Rows in preview
        assert len(preview['data']) == 3
        assert 'columns' in preview
        assert 'column_info' in preview
        assert 'mapping_suggestions' in preview
        assert 'detected_types' in preview

    def test_get_data_preview_nonexistent_file(self):
        """Test data preview with non - existent file."""
        preview = self.importer.get_data_preview("nonexistent_file.csv")

        assert preview is None

    def test_create_mapping_ui_config_success(self):
        """Test successful mapping UI configuration creation."""
        ui_config = self.importer.create_mapping_ui_config(
            "data/test_data/test_data.csv")

        assert ui_config is not None
        assert 'columns' in ui_config
        assert 'detected_types' in ui_config
        assert 'suggestions' in ui_config
        assert 'current_mapping' in ui_config
        assert 'supported_types' in ui_config
        assert 'data_preview' in ui_config

    def test_create_mapping_ui_config_nonexistent_file(self):
        """Test mapping UI configuration with non - existent file."""
        ui_config = self.importer.create_mapping_ui_config(
            "nonexistent_file.csv")

        assert ui_config is None

    def test_import_log_creation(self):
        """Test import log creation."""
        config = ImportConfig(
            file_path="data/test_data/test_data.csv",
            mapping_config={
                "node_id": "id",
                "node_name": "name"
            }
        )

        result = self.importer.import_data(config)

        assert result.success is True
        assert len(result.import_log) > 0
        assert "Data Import Log" in result.import_log
        assert "test_data.csv" in result.import_log
        assert "Nodes created: 8" in result.import_log
        assert "Edges created: 0" in result.import_log

    def test_import_with_encoding(self):
        """Test import with different encoding."""
        config = ImportConfig(
            file_path="data/test_data/test_data.csv",
            file_encoding="utf - 8",
            mapping_config={
                "node_id": "id",
                "node_name": "name"
            }
        )

        result = self.importer.import_data(config)

        assert result.success is True
        assert result.processed_rows == 8
        assert len(result.graph_data.nodes) == 8

    def test_import_with_complex_mapping(self):
        """Test import with complex mapping including KPIs and attributes."""
        config = ImportConfig(
            file_path="data/test_data/test_data.csv",
            mapping_config={
                "node_id": "id",
                "node_name": "name",
                "attribute_category": "category",
                "attribute_department": "department",
                "attribute_region": "region",
                "kpi_performance": "performance_score",
                "kpi_employees": "employee_count",
                "kpi_revenue": "revenue"
            }
        )

        result = self.importer.import_data(config)

        assert result.success is True
        assert result.processed_rows == 8
        assert len(result.graph_data.nodes) == 8

        # Check that nodes have attributes and KPIs
        first_node = result.graph_data.nodes[0]
        assert 'category' in first_node.attributes
        assert 'department' in first_node.attributes
        assert 'region' in first_node.attributes
        assert 'performance' in first_node.kpis
        assert 'employees' in first_node.kpis
        assert 'revenue' in first_node.kpis
