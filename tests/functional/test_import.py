"""
Test script for the Data Model Import functionality.
Demonstrates how to use the import module to process data files.
"""

import pytest
import os
from network_ui.core import DataImporter, ImportConfig


@pytest.mark.functional
class TestFunctionalImport:
    """Functional tests for the Data Importer."""

    def test_node_import(self):
        """Test importing node data from CSV."""
        print("=== Testing Node Data Import ===")

        # Create importer
        importer = DataImporter()

        # Create import configuration for nodes
        config = ImportConfig(
            file_path="test_data.csv",
            file_encoding="utf - 8",
            mapping_config={
                "node_id": "id",
                "node_name": "name",
                "attribute_category": "category",
                "attribute_department": "department",
                "attribute_region": "region",
                "kpi_performance": "performance_score",
                "kpi_employees": "employee_count",
                "kpi_revenue": "revenue"
            },
            data_types={
                "id": "integer",
                "name": "string",
                "category": "string",
                "department": "string",
                "region": "string",
                "performance_score": "float",
                "employee_count": "integer",
                "revenue": "integer"
            }
        )

        # Import data
        result = importer.import_data(config)

        if result.success:
            print("✅ Node import successful!")
            print(f"   - Processed {result.processed_rows} rows")
            print(f"   - Created {len(result.graph_data.nodes)} nodes")
            print(f"   - Created {len(result.graph_data.edges)} edges")

            # Display first few nodes
            print("\nSample nodes:")
            for i, node in enumerate(result.graph_data.nodes[:3]):
                print(f"   Node {i + 1}: {node.name} (ID: {node.id})")
                print(f"     - Level: {node.level}")
                print(f"     - Category: {node.attributes.get('category', 'N / A')}")
                print(f"     - Performance: {node.kpis.get('performance', 'N / A')}")

            return result.graph_data
        else:
            print("❌ Node import failed!")
            for error in result.errors:
                print(f"   Error: {error}")
            return None

    def test_edge_import(self):
        """Test importing edge data from CSV."""
        print("\n=== Testing Edge Data Import ===")

        # Create importer
        importer = DataImporter()

        # Create import configuration for edges
        config = ImportConfig(
            file_path="test_edges.csv",
            file_encoding="utf - 8",
            mapping_config={
                "edge_source": "source",
                "edge_target": "target",
                "edge_type": "relationship_type",
                "edge_weight": "weight",
                "kpi_collaboration": "collaboration_score",
                "attribute_frequency": "communication_frequency"
            },
            data_types={
                "source": "integer",
                "target": "integer",
                "relationship_type": "string",
                "weight": "float",
                "collaboration_score": "float",
                "communication_frequency": "string"
            }
        )

        # Import data
        result = importer.import_data(config)

        if result.success:
            print("✅ Edge import successful!")
            print(f"   - Processed {result.processed_rows} rows")
            print(f"   - Created {len(result.graph_data.nodes)} nodes")
            print(f"   - Created {len(result.graph_data.edges)} edges")

            # Display first few edges
            print("\nSample edges:")
            for i, edge in enumerate(result.graph_data.edges[:3]):
                print(f"   Edge {i + 1}: {edge.source} -> {edge.target}")
                print(f"     - Type: {edge.relationship_type}")
                print(f"     - Weight: {edge.weight}")
                print("     - Collaboration: "
                      f"{edge.kpi_components.get('collaboration', 'N / A')}")

            return result.graph_data
        else:
            print("❌ Edge import failed!")
            for error in result.errors:
                print(f"   Error: {error}")
            return None

    def test_data_preview(self):
        """Test data preview functionality."""
        print("\n=== Testing Data Preview ===")

        # Create importer
        importer = DataImporter()

        # Get preview
        preview = importer.get_data_preview("test_data.csv", max_rows=5)

        if preview:
            print("✅ Data preview successful!")
            print(f"   - Total rows: {preview['total_rows']}")
            print(f"   - Preview rows: {preview['preview_rows']}")
            print(f"   - Columns: {preview['columns']}")

            print("\nColumn information:")
            for column, info in preview['column_info'].items():
                print(f"   {column}: {info['data_type']} "
                      f"({info['unique_count']} unique values)")

            print("\nMapping suggestions:")
            for field, suggestions in preview['mapping_suggestions'].items():
                if suggestions:
                    print(f"   {field}: {suggestions}")
        else:
            print("❌ Data preview failed!")

    def test_mapping_ui_config(self):
        """Test mapping UI configuration."""
        print("\n=== Testing Mapping UI Configuration ===")

        # Create importer
        importer = DataImporter()

        # Get UI configuration
        ui_config = importer.create_mapping_ui_config("test_data.csv")

        if ui_config:
            print("✅ Mapping UI configuration successful!")
            print(f"   - Columns: {ui_config['columns']}")
            print(f"   - Supported types: {ui_config['supported_types']}")

            print("\nDetected types:")
            for column, data_type in ui_config['detected_types'].items():
                print(f"   {column}: {data_type}")

            print("\nMapping suggestions:")
            for field, suggestions in ui_config['suggestions'].items():
                if suggestions:
                    print(f"   {field}: {suggestions}")
        else:
            print("❌ Mapping UI configuration failed!")


def main():
    """Run all tests."""
    print("Data Model Import Test Suite")
    print("=" * 50)

    # Check if test files exist
    if not os.path.exists("test_data.csv"):
        print("❌ test_data.csv not found!")
        return

    if not os.path.exists("test_edges.csv"):
        print("❌ test_edges.csv not found!")
        return

    # Create test instance and run tests
    test_instance = TestFunctionalImport()
    test_instance.test_data_preview()
    test_instance.test_mapping_ui_config()
    node_graph = test_instance.test_node_import()
    edge_graph = test_instance.test_edge_import()

    print("\n" + "=" * 50)
    print("Test suite completed!")

    if node_graph and edge_graph:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")


if __name__ == "__main__":
    main()
