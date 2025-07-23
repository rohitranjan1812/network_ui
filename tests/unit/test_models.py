"""
Comprehensive tests for data models.
"""

import uuid
from datetime import datetime
from network_ui.core.models import Node, Edge, GraphData, ImportConfig, ImportResult


class TestNode:
    """Test Node model functionality."""

    def test_node_creation(self):
        """Test basic node creation."""
        node = Node(id="1", name="Test Node")

        assert node.id == "1"
        assert node.name == "Test Node"
        assert node.level == 1
        assert node.kpis == {}
        assert node.attributes == {}
        assert node.position == {"x": 0.0, "y": 0.0}
        assert isinstance(node.created_at, datetime)
        assert isinstance(node.updated_at, datetime)

    def test_node_with_optional_fields(self):
        """Test node creation with all optional fields."""
        node = Node(
            id="2",
            name="Test Node 2",
            level=2,
            kpis={"performance": 85.5},
            attributes={"category": "Marketing"},
            position={"x": 100.0, "y": 200.0}
        )

        assert node.id == "2"
        assert node.name == "Test Node 2"
        assert node.level == 2
        assert node.kpis == {"performance": 85.5}
        assert node.attributes == {"category": "Marketing"}
        assert node.position == {"x": 100.0, "y": 200.0}

    def test_node_auto_id_generation(self):
        """Test automatic ID generation when not provided."""
        node = Node(name="Auto ID Node")

        assert node.id is not None
        assert len(node.id) > 0
        assert node.name == "Auto ID Node"

    def test_node_auto_position_generation(self):
        """Test automatic position generation when not provided."""
        node = Node(id="3", name="Auto Position Node")

        assert node.position == {"x": 0.0, "y": 0.0}


class TestEdge:
    """Test Edge model functionality."""

    def test_edge_creation(self):
        """Test basic edge creation."""
        edge = Edge(source="1", target="2")

        assert edge.source == "1"
        assert edge.target == "2"
        assert edge.relationship_type == "default"
        assert edge.level == 1
        assert edge.kpi_components == {}
        assert edge.attributes == {}
        assert edge.weight == 1.0
        assert isinstance(edge.created_at, datetime)

    def test_edge_with_optional_fields(self):
        """Test edge creation with all optional fields."""
        edge = Edge(
            id="edge1",
            source="1",
            target="2",
            relationship_type="collaborates",
            level=2,
            kpi_components={"collaboration": 75.5},
            attributes={"frequency": "weekly"},
            weight=0.8
        )

        assert edge.id == "edge1"
        assert edge.source == "1"
        assert edge.target == "2"
        assert edge.relationship_type == "collaborates"
        assert edge.level == 2
        assert edge.kpi_components == {"collaboration": 75.5}
        assert edge.attributes == {"frequency": "weekly"}
        assert edge.weight == 0.8

    def test_edge_auto_id_generation(self):
        """Test automatic ID generation when not provided."""
        edge = Edge(source="1", target="2")

        assert edge.id is not None
        assert len(edge.id) > 0


class TestGraphData:
    """Test GraphData model functionality."""

    def test_graph_data_creation(self):
        """Test basic graph data creation."""
        graph = GraphData()

        assert graph.nodes == []
        assert graph.edges == []
        assert graph.metadata == {}
        assert isinstance(graph.created_at, datetime)

    def test_add_node(self):
        """Test adding nodes to graph."""
        graph = GraphData()
        node1 = Node(id="1", name="Node 1")
        node2 = Node(id="2", name="Node 2")

        graph.add_node(node1)
        graph.add_node(node2)

        assert len(graph.nodes) == 2
        assert graph.nodes[0].id == "1"
        assert graph.nodes[1].id == "2"

    def test_add_edge(self):
        """Test adding edges to graph."""
        graph = GraphData()
        edge1 = Edge(source="1", target="2")
        edge2 = Edge(source="2", target="3")

        graph.add_edge(edge1)
        graph.add_edge(edge2)

        assert len(graph.edges) == 2
        assert graph.edges[0].source == "1"
        assert graph.edges[1].source == "2"

    def test_get_node_by_id(self):
        """Test retrieving node by ID."""
        graph = GraphData()
        node1 = Node(id="1", name="Node 1")
        node2 = Node(id="2", name="Node 2")

        graph.add_node(node1)
        graph.add_node(node2)

        found_node = graph.get_node_by_id("1")
        assert found_node is not None
        assert found_node.name == "Node 1"

        not_found = graph.get_node_by_id("999")
        assert not_found is None

    def test_get_edges_by_node(self):
        """Test retrieving edges connected to a node."""
        graph = GraphData()

        # Add nodes
        node1 = Node(id="1", name="Node 1")
        node2 = Node(id="2", name="Node 2")
        node3 = Node(id="3", name="Node 3")

        graph.add_node(node1)
        graph.add_node(node2)
        graph.add_node(node3)

        # Add edges
        edge1 = Edge(source="1", target="2")
        edge2 = Edge(source="2", target="3")
        edge3 = Edge(source="1", target="3")

        graph.add_edge(edge1)
        graph.add_edge(edge2)
        graph.add_edge(edge3)

        # Test edges for node 1
        node1_edges = graph.get_edges_by_node("1")
        assert len(node1_edges) == 2

        # Test edges for node 2
        node2_edges = graph.get_edges_by_node("2")
        assert len(node2_edges) == 2

        # Test edges for node 3
        node3_edges = graph.get_edges_by_node("3")
        assert len(node3_edges) == 2


class TestImportConfig:
    """Test ImportConfig model functionality."""

    def test_import_config_creation(self):
        """Test basic import config creation."""
        config = ImportConfig(file_path="test.csv")

        assert config.file_path == "test.csv"
        assert config.file_encoding == "utf-8"
        assert config.mapping_config == {}
        assert config.data_types == {}
        assert config.delimiter == ","
        assert config.skip_rows == 0
        assert config.max_rows is None

    def test_import_config_with_all_fields(self):
        """Test import config creation with all fields."""
        config = ImportConfig(
            file_path="test.csv",
            file_encoding="latin-1",
            mapping_config={"node_id": "id"},
            data_types={"id": "integer"},
            delimiter=";",
            skip_rows=2,
            max_rows=100
        )

        assert config.file_path == "test.csv"
        assert config.file_encoding == "latin-1"
        assert config.mapping_config == {"node_id": "id"}
        assert config.data_types == {"id": "integer"}
        assert config.delimiter == ";"
        assert config.skip_rows == 2
        assert config.max_rows == 100


class TestImportResult:
    """Test ImportResult model functionality."""

    def test_import_result_creation(self):
        """Test basic import result creation."""
        result = ImportResult(success=True)

        assert result.success is True
        assert result.graph_data is None
        assert result.import_log == ""
        assert result.errors == []
        assert result.warnings == []
        assert result.processed_rows == 0
        assert result.total_rows == 0

    def test_import_result_with_data(self):
        """Test import result creation with data."""
        graph_data = GraphData()
        result = ImportResult(
            success=True,
            graph_data=graph_data,
            import_log="Import completed",
            errors=["Error 1"],
            warnings=["Warning 1"],
            processed_rows=10,
            total_rows=10
        )

        assert result.success is True
        assert result.graph_data == graph_data
        assert result.import_log == "Import completed"
        assert result.errors == ["Error 1"]
        assert result.warnings == ["Warning 1"]
        assert result.processed_rows == 10
        assert result.total_rows == 10
