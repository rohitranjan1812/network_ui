"""
Comprehensive tests for graph transformers.
"""

import pandas as pd
import pytest
from network_ui.core.transformers import GraphTransformer
from network_ui.core.models import GraphData, Node, Edge


class TestGraphTransformer:
    """Test GraphTransformer functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.transformer = GraphTransformer()

    def test_is_edge_data_true(self):
        """Test edge data detection with edge columns."""
        mapping_config = {
            'edge_source': 'source',
            'edge_target': 'target',
            'node_id': 'id'
        }

        is_edge_data = self.transformer._is_edge_data(mapping_config)
        assert is_edge_data is True

    def test_is_edge_data_false(self):
        """Test edge data detection without edge columns."""
        mapping_config = {
            'node_id': 'id',
            'node_name': 'name',
            'attribute_category': 'category'
        }

        is_edge_data = self.transformer._is_edge_data(mapping_config)
        assert is_edge_data is False

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

        transformed_data = self.transformer._transform_data_types(
            data, data_types)

        assert transformed_data['id'].dtype == 'Int64'
        assert transformed_data['name'].dtype == 'object'
        assert transformed_data['score'].dtype == 'float64'
        assert transformed_data['active'].dtype == 'object'

    def test_transform_to_graph_node_data(self):
        """Test graph transformation with node data."""
        data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Node A', 'Node B', 'Node C'],
            'category': ['A', 'B', 'A'],
            'performance': [85.5, 92.3, 78.9]
        })

        mapping_config = {
            'node_id': 'id',
            'node_name': 'name',
            'attribute_category': 'category',
            'kpi_performance': 'performance'
        }

        data_types = {
            'id': 'integer',
            'name': 'string',
            'category': 'string',
            'performance': 'float'
        }

        graph_data = self.transformer.transform_to_graph(
            data, mapping_config, data_types)

        assert isinstance(graph_data, GraphData)
        assert len(graph_data.nodes) == 3
        assert len(graph_data.edges) == 0

        # Check first node
        node = graph_data.nodes[0]
        assert node.id == '1'
        assert node.name == 'Node A'
        assert node.attributes['category'] == 'A'
        assert node.kpis['performance'] == 85.5

    def test_transform_to_graph_edge_data(self):
        """Test graph transformation with edge data."""
        data = pd.DataFrame({
            'source': [1, 2, 3],
            'target': [2, 3, 1],
            'type': ['collaborates', 'reports_to', 'mentors'],
            'weight': [0.8, 0.9, 0.6],
            'collaboration': [75.5, 88.2, 65.3]
        })

        mapping_config = {
            'edge_source': 'source',
            'edge_target': 'target',
            'edge_type': 'type',
            'edge_weight': 'weight',
            'kpi_collaboration': 'collaboration'
        }

        data_types = {
            'source': 'integer',
            'target': 'integer',
            'type': 'string',
            'weight': 'float',
            'collaboration': 'float'
        }

        graph_data = self.transformer.transform_to_graph(
            data, mapping_config, data_types)

        assert isinstance(graph_data, GraphData)
        assert len(graph_data.nodes) == 3  # Auto-created nodes
        assert len(graph_data.edges) == 3

        # Check first edge
        edge = graph_data.edges[0]
        assert edge.source == '1'
        assert edge.target == '2'
        assert edge.relationship_type == 'collaborates'
        assert edge.weight == 0.8
        assert edge.kpi_components['collaboration'] == 75.5

    def test_transform_node_data(self):
        """Test node data transformation."""
        data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Node A', 'Node B', 'Node C'],
            'category': ['A', 'B', 'A'],
            'level': [1, 2, 1],
            'performance': [85.5, 92.3, 78.9]
        })

        mapping_config = {
            'node_id': 'id',
            'node_name': 'name',
            'node_level': 'level',
            'attribute_category': 'category',
            'kpi_performance': 'performance'
        }

        graph_data = self.transformer._transform_node_data(
            data, mapping_config)

        assert len(graph_data.nodes) == 3
        assert len(graph_data.edges) == 0

        # Check node with level
        node = graph_data.nodes[1]
        assert node.id == '2'
        assert node.name == 'Node B'
        assert node.level == 2
        assert node.attributes['category'] == 'B'
        assert node.kpis['performance'] == 92.3

    def test_transform_node_data_missing_required(self):
        """Test node data transformation with missing required fields."""
        data = pd.DataFrame({
            'id': [1, 2, 3],
            'category': ['A', 'B', 'A']
        })

        # Test missing node_id (should still raise error)
        mapping_config = {
            # Missing node_id
            'attribute_category': 'category'
        }

        with pytest.raises(ValueError, match="requires 'node_id'"):
            self.transformer._transform_node_data(data, mapping_config)
            
        # Test node_name optional (should work fine)
        valid_mapping_config = {
            'node_id': 'id',
            # node_name is optional, will be generated
            'attribute_category': 'category'
        }
        
        result = self.transformer.transform_to_graph(data, valid_mapping_config, {
            'id': 'integer',
            'category': 'string'
        })
        assert len(result.nodes) == 3
        assert result.nodes[0].name == "Node_1"  # Generated name

    def test_transform_edge_data(self):
        """Test edge data transformation."""
        data = pd.DataFrame({
            'source': [1, 2, 3],
            'target': [2, 3, 1],
            'type': ['collaborates', 'reports_to', 'mentors'],
            'level': [1, 2, 1],
            'weight': [0.8, 0.9, 0.6],
            'collaboration': [75.5, 88.2, 65.3],
            'frequency': ['weekly', 'daily', 'monthly']
        })

        mapping_config = {
            'edge_source': 'source',
            'edge_target': 'target',
            'edge_type': 'type',
            'edge_level': 'level',
            'edge_weight': 'weight',
            'kpi_collaboration': 'collaboration',
            'attribute_frequency': 'frequency'
        }

        graph_data = self.transformer._transform_edge_data(
            data, mapping_config)

        assert len(graph_data.nodes) == 3  # Auto-created nodes
        assert len(graph_data.edges) == 3

        # Check edge with all fields
        edge = graph_data.edges[1]
        assert edge.source == '2'
        assert edge.target == '3'
        assert edge.relationship_type == 'reports_to'
        assert edge.level == 2
        assert edge.weight == 0.9
        assert edge.kpi_components['collaboration'] == 88.2
        assert edge.attributes['frequency'] == 'daily'

    def test_transform_edge_data_missing_required(self):
        """Test edge data transformation with missing required fields."""
        data = pd.DataFrame({
            'source': [1, 2, 3],
            'type': ['collaborates', 'reports_to', 'mentors']
        })

        mapping_config = {
            'edge_source': 'source',
            # Missing edge_target
            'edge_type': 'type'
        }

        with pytest.raises(ValueError, match="requires both 'edge_source' and 'edge_target'"):
            self.transformer._transform_edge_data(data, mapping_config)

    def test_create_hierarchical_structure(self):
        """Test hierarchical structure creation."""
        graph_data = GraphData()

        # Create nodes with different attributes
        node1 = Node(
            id="1",
            name="Node 1",
            attributes={
                "category": "A",
                "department": "Sales"})
        node2 = Node(
            id="2",
            name="Node 2",
            attributes={
                "category": "A",
                "department": "Sales"})
        node3 = Node(
            id="3",
            name="Node 3",
            attributes={
                "category": "B",
                "department": "Tech"})

        graph_data.add_node(node1)
        graph_data.add_node(node2)
        graph_data.add_node(node3)

        # Create hierarchical structure
        result_graph = self.transformer.create_hierarchical_structure(
            graph_data)

        # Nodes with same attributes should be grouped at level 3
        assert node1.level == 3
        assert node2.level == 3
        assert node3.level == 1  # Different attributes, stays at level 1
        assert result_graph is not None  # Verify function returns a result

    def test_validate_graph_structure_valid(self):
        """Test graph structure validation with valid data."""
        graph_data = GraphData()

        # Add valid nodes
        node1 = Node(id="1", name="Node 1")
        node2 = Node(id="2", name="Node 2")
        node3 = Node(id="3", name="Node 3")

        graph_data.add_node(node1)
        graph_data.add_node(node2)
        graph_data.add_node(node3)

        # Add valid edges
        edge1 = Edge(source="1", target="2")
        edge2 = Edge(source="2", target="3")

        graph_data.add_edge(edge1)
        graph_data.add_edge(edge2)

        is_valid, errors = self.transformer.validate_graph_structure(
            graph_data)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_graph_structure_duplicate_nodes(self):
        """Test graph structure validation with duplicate node IDs."""
        graph_data = GraphData()

        # Add nodes with duplicate IDs
        node1 = Node(id="1", name="Node 1")
        node2 = Node(id="1", name="Node 2")  # Duplicate ID

        graph_data.add_node(node1)
        graph_data.add_node(node2)

        is_valid, errors = self.transformer.validate_graph_structure(
            graph_data)

        assert is_valid is False
        assert len(errors) > 0
        assert any('Duplicate node IDs' in error for error in errors)

    def test_validate_graph_structure_invalid_edges(self):
        """Test graph structure validation with invalid edges."""
        graph_data = GraphData()

        # Add nodes
        node1 = Node(id="1", name="Node 1")
        graph_data.add_node(node1)

        # Add edge with non-existent source
        edge1 = Edge(source="999", target="1")
        graph_data.add_edge(edge1)

        is_valid, errors = self.transformer.validate_graph_structure(
            graph_data)

        assert is_valid is False
        assert len(errors) > 0
        assert any('non-existent source node' in error for error in errors)

    def test_validate_graph_structure_self_loops(self):
        """Test graph structure validation with self-loops."""
        graph_data = GraphData()

        # Add node
        node1 = Node(id="1", name="Node 1")
        graph_data.add_node(node1)

        # Add self-loop
        edge1 = Edge(source="1", target="1")
        graph_data.add_edge(edge1)

        is_valid, errors = self.transformer.validate_graph_structure(
            graph_data)

        assert is_valid is False
        assert len(errors) > 0
        assert any('Self-loop' in error for error in errors)

    def test_validate_graph_structure_duplicate_edges(self):
        """Test graph structure validation with duplicate edges."""
        graph_data = GraphData()

        # Add nodes
        node1 = Node(id="1", name="Node 1")
        node2 = Node(id="2", name="Node 2")

        graph_data.add_node(node1)
        graph_data.add_node(node2)

        # Add duplicate edges
        edge1 = Edge(source="1", target="2", relationship_type="collaborates")
        edge2 = Edge(source="1", target="2", relationship_type="collaborates")

        graph_data.add_edge(edge1)
        graph_data.add_edge(edge2)

        is_valid, errors = self.transformer.validate_graph_structure(
            graph_data)

        assert is_valid is False
        assert len(errors) > 0
        assert any('Duplicate edges' in error for error in errors)

    def test_create_graph_summary(self):
        """Test graph summary creation."""
        graph_data = GraphData()

        # Add nodes with different levels
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

        graph_data.add_node(node1)
        graph_data.add_node(node2)
        graph_data.add_node(node3)

        # Add edges with different types
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

        graph_data.add_edge(edge1)
        graph_data.add_edge(edge2)
        graph_data.add_edge(edge3)

        summary = self.transformer.create_graph_summary(graph_data)

        assert summary['total_nodes'] == 3
        assert summary['total_edges'] == 3

        # Check node levels
        assert summary['node_levels']['1'] == 2
        assert summary['node_levels']['2'] == 1

        # Check edge types
        assert summary['edge_types']['collaborates'] == 2
        assert summary['edge_types']['reports_to'] == 1

        # Check attributes
        assert 'category' in summary['attribute_summary']['node_attributes']
        assert 'performance' in summary['attribute_summary']['node_attributes']
        assert 'collaboration' in summary['attribute_summary']['edge_attributes']

    def test_convert_to_boolean(self):
        """Test boolean conversion."""
        data = pd.Series(['true', 'false', 'yes', 'no',
                         '1', '0', 't', 'f', 'y', 'n'])
        converted = self.transformer._convert_to_boolean(data)

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
