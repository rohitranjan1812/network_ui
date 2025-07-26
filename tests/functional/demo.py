"""
Demo script for the Data Model Import Module.
Shows how to use the module to import and transform data.
"""

from network_ui.core import DataImporter, ImportConfig


def demo_node_import():
    """Demonstrate node data import."""
    print("Demo: Node Data Import")
    print("-" * 40)

    # Create importer
    importer = DataImporter()

    # Configure import for team data
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

    # Import data
    result = importer.import_data(config)

    if result.success:
        print(f"Successfully imported {len(result.graph_data.nodes)} teams")

        # Show sample data
        print("\nSample Teams:")
        for i, node in enumerate(result.graph_data.nodes[:3]):
            print(f"   {i + 1}. {node.name}")
            print(f"      Category: {node.attributes.get('category', 'N / A')}")
            print(f"      Performance: {node.kpis.get('performance', 'N / A')}")
            print(f"      Revenue: ${node.kpis.get('revenue', 'N / A'):,}")
            print()

        return result.graph_data
    else:
        print("Import failed:")
        for error in result.errors:
            print(f"   - {error}")
        return None


def demo_edge_import():
    """Demonstrate edge data import."""
    print("Demo: Edge Data Import")
    print("-" * 40)

    # Create importer
    importer = DataImporter()

    # Configure import for relationship data
    config = ImportConfig(
        file_path="data/test_data/test_edges.csv",
        mapping_config={
            "edge_source": "source",
            "edge_target": "target",
            "edge_type": "relationship_type",
            "edge_weight": "weight",
            "kpi_collaboration": "collaboration_score",
            "attribute_frequency": "communication_frequency"
        }
    )

    # Import data
    result = importer.import_data(config)

    if result.success:
        print(f"Successfully imported {len(result.graph_data.edges)} "
              "relationships")

        # Show sample data
        print("\nSample Relationships:")
        for i, edge in enumerate(result.graph_data.edges[:3]):
            print(f"   {i + 1}. Team {edge.source} -> Team {edge.target}")
            print(f"      Type: {edge.relationship_type}")
            print(f"      Weight: {edge.weight}")
            print("      Collaboration: "
                  f"{edge.kpi_components.get('collaboration', 'N / A')}")
            print()

        return result.graph_data
    else:
        print("Import failed:")
        for error in result.errors:
            print(f"   - {error}")
        return None


def demo_data_preview():
    """Demonstrate data preview functionality."""
    print("Demo: Data Preview")
    print("-" * 40)

    # Create importer
    importer = DataImporter()

    # Get preview
    preview = importer.get_data_preview(
        "data/test_data/test_data.csv", max_rows=3)

    if preview:
        print(f"Preview generated for {preview['total_rows']} rows")
        print(f"Showing {preview['preview_rows']} sample rows")

        print("\nData Preview:")
        for i, row in enumerate(preview['data']):
            print(f"   Row {i + 1}: {row}")

        print("\nColumn Analysis:")
        for column, info in preview['column_info'].items():
            print(f"   {column}: {info['data_type']} "
                  f"({info['unique_count']} unique)")

        print("\nMapping Suggestions:")
        for field, suggestions in preview['mapping_suggestions'].items():
            if suggestions:
                print(f"   {field}: {suggestions}")
    else:
        print("Preview failed!")


def demo_mapping_suggestions():
    """Demonstrate mapping suggestions."""
    print("Demo: Mapping Suggestions")
    print("-" * 40)

    # Create importer
    importer = DataImporter()

    # Get mapping configuration
    ui_config = importer.create_mapping_ui_config(
        "data/test_data/test_data.csv")

    if ui_config:
        print("Mapping suggestions generated")

        print(f"\nAvailable Columns: {ui_config['columns']}")

        print("\nDetected Data Types:")
        for column, data_type in ui_config['detected_types'].items():
            print(f"   {column}: {data_type}")

        print("\nSmart Suggestions:")
        for field, suggestions in ui_config['suggestions'].items():
            if suggestions:
                print(f"   {field}: {suggestions}")
    else:
        print("Mapping suggestions failed!")


def demo_graph_summary(graph_data):
    """Demonstrate graph summary functionality."""
    if not graph_data:
        return

    print("Demo: Graph Summary")
    print("-" * 40)

    from network_ui.core.transformers import GraphTransformer

    transformer = GraphTransformer()
    summary = transformer.create_graph_summary(graph_data)

    print("Graph Statistics:")
    print(f"   Total Nodes: {summary['total_nodes']}")
    print(f"   Total Edges: {summary['total_edges']}")

    print("\nNode Levels:")
    for level, count in summary['node_levels'].items():
        print(f"   Level {level}: {count} nodes")

    print("\nEdge Types:")
    for edge_type, count in summary['edge_types'].items():
        print(f"   {edge_type}: {count} edges")

    print("\nAttributes:")
    print("   Node Attributes: "
          f"{summary['attribute_summary']['node_attributes']}")
    print("   Edge Attributes: "
          f"{summary['attribute_summary']['edge_attributes']}")


def main():
    """Run the demo."""
    print("Data Model Import Demo")
    print("=" * 50)

    # Run demos
    node_graph = demo_node_import()
    edge_graph = demo_edge_import()
    demo_data_preview()
    demo_mapping_suggestions()

    if node_graph:
        demo_graph_summary(node_graph)
    if edge_graph:
        demo_graph_summary(edge_graph)

    print("\n" + "=" * 50)
    print("Demo completed!")


if __name__ == "__main__":
    main()
