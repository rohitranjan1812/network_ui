"""
Pytest configuration and fixtures for Network UI tests.
"""

import pytest
from network_ui.core.models import GraphData, Node, Edge
from network_ui.core import DataImporter, ImportConfig
import os
import sys
import tempfile
import pandas as pd
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def sample_csv_data():
    """Create sample CSV data for testing."""
    data = {
        'id': [1, 2, 3, 4, 5],
        'name': ['Team A', 'Team B', 'Team C', 'Team D', 'Team E'],
        'category': ['Marketing', 'Engineering', 'Sales', 'HR', 'Finance'],
        'department': ['Sales', 'Technology', 'Sales', 'Admin', 'Admin'],
        'region': ['North', 'South', 'East', 'West', 'North'],
        'performance_score': [85.5, 92.3, 78.9, 88.2, 91.7],
        'employee_count': [12, 18, 8, 5, 6],
        'revenue': [1250000, 2100000, 980000, 450000, 890000]
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_edge_data():
    """Create sample edge data for testing."""
    data = {
        'source': [
            1, 2, 3, 4, 5], 'target': [
            2, 3, 4, 5, 1], 'relationship_type': [
                'collaborates', 'reports_to', 'mentors', 'partners', 'advises'], 'weight': [
                    0.8, 0.9, 0.6, 0.7, 0.5], 'collaboration_score': [
                        75.5, 88.2, 65.3, 72.1, 58.9], 'communication_frequency': [
                            'weekly', 'daily', 'monthly', 'weekly', 'quarterly']}
    return pd.DataFrame(data)


@pytest.fixture
def temp_csv_file(sample_csv_data):
    """Create a temporary CSV file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
        sample_csv_data.to_csv(f, index=False)
        temp_file = f.name

    yield temp_file

    # Cleanup
    if os.path.exists(temp_file):
        os.unlink(temp_file)


@pytest.fixture
def temp_edge_csv_file(sample_edge_data):
    """Create a temporary edge CSV file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
        sample_edge_data.to_csv(f, index=False)
        temp_file = f.name

    yield temp_file

    # Cleanup
    if os.path.exists(temp_file):
        os.unlink(temp_file)


@pytest.fixture
def temp_json_file(sample_csv_data):
    """Create a temporary JSON file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w') as f:
        sample_csv_data.to_json(f, orient='records', indent=2)
        temp_file = f.name

    yield temp_file

    # Cleanup
    if os.path.exists(temp_file):
        os.unlink(temp_file)


@pytest.fixture
def temp_xml_file(sample_csv_data):
    """Create a temporary XML file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.xml', delete=False, mode='w') as f:
        f.write('<?xml version="1.0" encoding="UTF - 8"?>\n')
        f.write('<data>\n')

        for _, row in sample_csv_data.iterrows():
            f.write('  <record>\n')
            for col, val in row.items():
                f.write(f'    <{col}>{val}</{col}>\n')
            f.write('  </record>\n')

        f.write('</data>\n')
        temp_file = f.name

    yield temp_file

    # Cleanup
    if os.path.exists(temp_file):
        os.unlink(temp_file)


@pytest.fixture
def sample_graph_data():
    """Create sample graph data for testing."""
    graph = GraphData()

    # Add nodes
    node1 = Node(
        id="1", name="Node 1", level=1, attributes={
            "category": "A"}, kpis={
            "performance": 85.5})
    node2 = Node(
        id="2", name="Node 2", level=2, attributes={
            "category": "B"}, kpis={
            "performance": 92.3})
    node3 = Node(
        id="3", name="Node 3", level=1, attributes={
            "category": "A"}, kpis={
            "performance": 78.9})

    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)

    # Add edges
    edge1 = Edge(
        source="1",
        target="2",
        relationship_type="collaborates",
        kpi_components={
            "collaboration": 75.5})
    edge2 = Edge(
        source="2",
        target="3",
        relationship_type="reports_to",
        kpi_components={
            "collaboration": 88.2})
    edge3 = Edge(
        source="1",
        target="3",
        relationship_type="collaborates",
        kpi_components={
            "collaboration": 65.3})

    graph.add_edge(edge1)
    graph.add_edge(edge2)
    graph.add_edge(edge3)

    return graph


@pytest.fixture
def basic_import_config():
    """Create a basic import configuration for testing."""
    return ImportConfig(
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


@pytest.fixture
def edge_import_config():
    """Create an edge import configuration for testing."""
    return ImportConfig(
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


@pytest.fixture
def data_importer():
    """Create a DataImporter instance for testing."""
    return DataImporter()


# Test data for different scenarios
@pytest.fixture
def invalid_data_csv():
    """Create CSV data with invalid values for testing error handling."""
    data = {
        'id': [1, 2, 3, 4, 5],
        'name': ['Team A', 'Team B', 'Team C', 'Team D', 'Team E'],
        'performance_score': [85.5, 'invalid_number', 78.9, 'missing_value', 91.7]
    }
    return pd.DataFrame(data)


@pytest.fixture
def duplicate_ids_csv():
    """Create CSV data with duplicate IDs for testing validation."""
    data = {
        'id': [1, 1, 2, 3, 4],  # Duplicate ID
        'name': ['Team A', 'Team B', 'Team C', 'Team D', 'Team E'],
        'category': ['Marketing', 'Engineering', 'Sales', 'HR', 'Finance']
    }
    return pd.DataFrame(data)


@pytest.fixture
def empty_csv():
    """Create empty CSV data for testing edge cases."""
    return pd.DataFrame()


@pytest.fixture
def boolean_data_csv():
    """Create CSV data with boolean values for testing type detection."""
    data = {
        'id': [1, 2, 3, 4, 5],
        'name': ['Team A', 'Team B', 'Team C', 'Team D', 'Team E'],
        'is_active': ['true', 'false', 'yes', 'no', '1'],
        'has_permission': ['t', '', 'y', 'n', '0']
    }
    return pd.DataFrame(data)


@pytest.fixture
def date_data_csv():
    """Create CSV data with date values for testing type detection."""
    data = {
        'id': [
            1,
            2,
            3,
            4,
            5],
        'name': [
            'Team A',
            'Team B',
            'Team C',
            'Team D',
            'Team E'],
        'created_date': [
            '2024 - 01 - 01',
            '2024 - 01 - 02',
            '2024 - 01 - 03',
            '2024 - 01 - 04',
            '2024 - 01 - 05'],
        'updated_date': [
            '2024 - 01 - 15 10:00:00',
            '2024 - 01 - 16 11:30:00',
            '2024 - 01 - 17 09:15:00',
            '2024 - 01 - 18 14:45:00',
            '2024 - 01 - 19 16:20:00']}
    return pd.DataFrame(data)
