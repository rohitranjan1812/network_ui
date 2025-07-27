"""
Comprehensive unit tests for the Graph Analytics module (Spec 3).
Tests all algorithms including edge cases and error conditions.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from src.network_ui.analytics.algorithms import (
    GraphAnalyzer, PathfindingAlgorithms, CentralityMeasures, AnalysisResult
)
from src.network_ui.analytics.community import CommunityDetection
from src.network_ui.analytics.connectivity import ConnectivityAnalyzer
from src.network_ui.core.models import GraphData, Node, Edge


class TestAnalysisResult:
    """Test the AnalysisResult data structure."""
    
    def test_analysis_result_creation(self):
        """Test creating AnalysisResult with all parameters."""
        result = AnalysisResult(
            algorithm="test_algorithm",
            results={"test": "data"},
            visual_mapping={"color": "red"},
            metadata={"version": "1.0"},
            success=True,
            error_message=None
        )
        
        assert result.algorithm == "test_algorithm"
        assert result.results == {"test": "data"}
        assert result.visual_mapping == {"color": "red"}
        assert result.metadata == {"version": "1.0"}
        assert result.success is True
        assert result.error_message is None
    
    def test_analysis_result_error(self):
        """Test creating AnalysisResult for failed analysis."""
        result = AnalysisResult(
            algorithm="test_algorithm",
            results=None,
            success=False,
            error_message="Test error"
        )
        
        assert result.success is False
        assert result.error_message == "Test error"
        assert result.results is None


class TestPathfindingAlgorithms:
    """Test pathfinding algorithms."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.pathfinding = PathfindingAlgorithms()
        
        # Create test graph
        self.test_graph = GraphData(
            nodes=[
                Node(id="A", name="Node A"),
                Node(id="B", name="Node B"),
                Node(id="C", name="Node C"),
                Node(id="D", name="Node D")
            ],
            edges=[
                Edge(id="1", source="A", target="B", weight=1.0),
                Edge(id="2", source="B", target="C", weight=2.0),
                Edge(id="3", source="A", target="C", weight=5.0),
                Edge(id="4", source="C", target="D", weight=1.0)
            ]
        )
    
    def test_shortest_path_success(self):
        """Test successful shortest path calculation."""
        result = self.pathfinding.shortest_path_dijkstra(
            self.test_graph, "A", "D", use_edge_weights=True
        )
        
        assert result.success is True
        assert result.algorithm == "shortest_path_dijkstra"
        assert "path" in result.results
        assert "distance" in result.results
        assert result.results["path"] == ["A", "B", "C", "D"]
        assert result.results["distance"] == 4.0
        assert "visual_mapping" in result.__dict__
    
    def test_shortest_path_no_path(self):
        """Test shortest path when no path exists."""
        # Create disconnected graph
        disconnected_graph = GraphData(
            nodes=[
                Node(id="A", name="Node A"),
                Node(id="B", name="Node B")
            ],
            edges=[]
        )
        
        result = self.pathfinding.shortest_path_dijkstra(
            disconnected_graph, "A", "B", use_edge_weights=True
        )
        
        assert result.success is True
        assert result.results["path"] == []
        assert result.results["distance"] == float('inf')
    
    def test_shortest_path_invalid_nodes(self):
        """Test shortest path with non-existent nodes."""
        result = self.pathfinding.shortest_path_dijkstra(
            self.test_graph, "X", "Y", use_edge_weights=True
        )
        
        assert result.success is False
        assert "not found" in result.error_message
    
    def test_all_paths_success(self):
        """Test finding all paths between nodes."""
        result = self.pathfinding.all_paths(
            self.test_graph, "A", "C", max_paths=10
        )
        
        assert result.success is True
        assert result.algorithm == "all_paths"
        assert "paths" in result.results
        assert len(result.results["paths"]) >= 1
        assert ["A", "B", "C"] in result.results["paths"]
        assert ["A", "C"] in result.results["paths"]
    
    def test_all_paths_max_limit(self):
        """Test all paths with maximum limit."""
        # Create a graph with multiple paths (diamond structure)
        complex_graph = GraphData(
            nodes=[Node(id=str(i), name=f"Node {i}") for i in range(4)],
            edges=[
                Edge(id="1", source="0", target="1"),
                Edge(id="2", source="0", target="2"),
                Edge(id="3", source="1", target="3"),
                Edge(id="4", source="2", target="3")
            ]
        )
        
        result = self.pathfinding.all_paths(
            complex_graph, "0", "3", max_paths=1  # Limit to 1 path
        )
        
        assert result.success is True
        assert len(result.results["paths"]) <= 1
        assert result.results["truncated"] is True
        assert "count" in result.results


class TestCentralityMeasures:
    """Test centrality measures."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.centrality = CentralityMeasures()
        
        # Create test graph
        self.test_graph = GraphData(
            nodes=[
                Node(id="A", name="Node A"),
                Node(id="B", name="Node B"),
                Node(id="C", name="Node C"),
                Node(id="D", name="Node D")
            ],
            edges=[
                Edge(id="1", source="A", target="B"),
                Edge(id="2", source="B", target="C"),
                Edge(id="3", source="A", target="C"),
                Edge(id="4", source="C", target="D")
            ]
        )
    
    def test_degree_centrality_success(self):
        """Test degree centrality calculation."""
        result = self.centrality.degree_centrality(self.test_graph)
        
        assert result.success is True
        assert result.algorithm == "degree_centrality"
        assert "centralities" in result.results
        assert "normalized_centralities" in result.results
        
        centralities = result.results["centralities"]
        assert centralities["A"] == 2  # Connected to B and C
        assert centralities["B"] == 2  # Connected to A and C
        assert centralities["C"] == 3  # Connected to A, B, and D
        assert centralities["D"] == 1  # Connected to C only
    
    def test_degree_centrality_empty_graph(self):
        """Test degree centrality with empty graph."""
        empty_graph = GraphData(nodes=[], edges=[])
        result = self.centrality.degree_centrality(empty_graph)
        
        assert result.success is True
        assert result.results["centralities"] == {}
        assert result.results["normalized_centralities"] == {}
    
    def test_degree_centrality_single_node(self):
        """Test degree centrality with single isolated node."""
        single_node_graph = GraphData(
            nodes=[Node(id="A", name="Node A")],
            edges=[]
        )
        
        result = self.centrality.degree_centrality(single_node_graph)
        
        assert result.success is True
        assert result.results["centralities"]["A"] == 0
        assert result.results["normalized_centralities"]["A"] == 0
    
    def test_degree_centrality_all_zero_degrees(self):
        """Test degree centrality when all nodes have degree 0."""
        isolated_graph = GraphData(
            nodes=[
                Node(id="A", name="Node A"),
                Node(id="B", name="Node B")
            ],
            edges=[]
        )
        
        result = self.centrality.degree_centrality(isolated_graph)
        
        assert result.success is True
        assert result.results["centralities"]["A"] == 0
        assert result.results["centralities"]["B"] == 0
        assert result.results["normalized_centralities"]["A"] == 0
        assert result.results["normalized_centralities"]["B"] == 0
    
    @patch('src.network_ui.analytics.algorithms.nx')
    def test_betweenness_centrality_success(self, mock_nx):
        """Test betweenness centrality calculation."""
        # Mock NetworkX response
        mock_nx.betweenness_centrality.return_value = {
            "A": 0.0, "B": 0.5, "C": 0.5, "D": 0.0
        }
        
        result = self.centrality.betweenness_centrality(self.test_graph)
        
        assert result.success is True
        assert result.algorithm == "betweenness_centrality"
        assert "centralities" in result.results
        mock_nx.betweenness_centrality.assert_called_once()
    
    @patch('src.network_ui.analytics.algorithms.nx')
    def test_closeness_centrality_success(self, mock_nx):
        """Test closeness centrality calculation."""
        # Mock NetworkX response
        mock_nx.closeness_centrality.return_value = {
            "A": 0.5, "B": 0.6, "C": 0.7, "D": 0.4
        }
        
        result = self.centrality.closeness_centrality(self.test_graph)
        
        assert result.success is True
        assert result.algorithm == "closeness_centrality"
        assert "centralities" in result.results
        mock_nx.closeness_centrality.assert_called_once()
    
    @patch('src.network_ui.analytics.algorithms.nx')
    def test_eigenvector_centrality_success(self, mock_nx):
        """Test eigenvector centrality calculation."""
        # Mock NetworkX response
        mock_nx.eigenvector_centrality.return_value = {
            "A": 0.3, "B": 0.4, "C": 0.5, "D": 0.2
        }
        mock_nx.is_connected.return_value = True
        
        result = self.centrality.eigenvector_centrality(self.test_graph)
        
        assert result.success is True
        assert result.algorithm == "eigenvector_centrality"
        assert "centralities" in result.results
        mock_nx.eigenvector_centrality.assert_called_once()
    
    def test_create_centrality_colors(self):
        """Test color mapping creation."""
        centralities = {"A": 0.0, "B": 0.5, "C": 1.0}
        colors = self.centrality._create_centrality_colors(centralities)
        
        assert len(colors) == 3
        assert all(color.startswith("#") for color in colors.values())
        assert all(len(color) == 7 for color in colors.values())  # #RRGGBB format
    
    def test_create_centrality_colors_empty(self):
        """Test color mapping with empty centralities."""
        colors = self.centrality._create_centrality_colors({})
        assert colors == {}
    
    def test_create_centrality_colors_single_value(self):
        """Test color mapping with single centrality value."""
        centralities = {"A": 0.5}
        colors = self.centrality._create_centrality_colors(centralities)
        
        assert len(colors) == 1
        assert colors["A"].startswith("#")


class TestCommunityDetection:
    """Test community detection algorithms."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.community = CommunityDetection()
        
        # Create test graph
        self.test_graph = GraphData(
            nodes=[
                Node(id="A", name="Node A"),
                Node(id="B", name="Node B"),
                Node(id="C", name="Node C"),
                Node(id="D", name="Node D")
            ],
            edges=[
                Edge(id="1", source="A", target="B"),
                Edge(id="2", source="B", target="C"),
                Edge(id="3", source="C", target="D")
            ]
        )
    
    @patch('src.network_ui.analytics.community.nx')
    def test_louvain_modularity_success(self, mock_nx):
        """Test Louvain community detection."""
        # Mock NetworkX response
        mock_communities = [{"A", "B"}, {"C", "D"}]
        mock_nx.community.louvain_communities.return_value = mock_communities
        mock_nx.community.modularity.return_value = 0.3
        
        result = self.community.louvain_modularity(self.test_graph)
        
        assert result.success is True
        assert result.algorithm == "louvain_modularity"
        assert "communities" in result.results
        assert "modularity" in result.results
        assert result.results["modularity"] == 0.3
    
    @patch('src.network_ui.analytics.community.nx')
    def test_girvan_newman_success(self, mock_nx):
        """Test Girvan-Newman community detection."""
        # Mock NetworkX response
        mock_communities = [{"A", "B"}, {"C", "D"}]
        mock_generator = iter([mock_communities])
        mock_nx.community.girvan_newman.return_value = mock_generator
        mock_nx.community.modularity.return_value = 0.4
        
        result = self.community.girvan_newman(self.test_graph, max_communities=5)
        
        assert result.success is True
        assert result.algorithm == "girvan_newman"
        assert "communities" in result.results
        assert "modularity" in result.results


class TestConnectivityAnalyzer:
    """Test connectivity analysis algorithms."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.connectivity = ConnectivityAnalyzer()
        
        # Create test graph
        self.test_graph = GraphData(
            nodes=[
                Node(id="A", name="Node A"),
                Node(id="B", name="Node B"),
                Node(id="C", name="Node C"),
                Node(id="D", name="Node D")
            ],
            edges=[
                Edge(id="1", source="A", target="B"),
                Edge(id="2", source="B", target="C"),
                Edge(id="3", source="C", target="D")
            ]
        )
    
    @patch('src.network_ui.analytics.connectivity.nx')
    def test_connected_components_success(self, mock_nx):
        """Test connected components analysis."""
        # Mock NetworkX response for directed graph
        mock_components = [{"A", "B", "C", "D"}]
        mock_nx.weakly_connected_components.return_value = mock_components
        mock_nx.strongly_connected_components.return_value = mock_components
        
        # Mock the graph creation
        mock_graph = MagicMock()
        mock_graph.is_directed.return_value = True
        mock_nx.DiGraph.return_value = mock_graph
        
        result = self.connectivity.connected_components(self.test_graph)
        
        assert result.success is True
        assert result.algorithm == "connected_components"
        assert "weakly_connected" in result.results  # For directed graphs (test graph has directed edges)
        assert result.results["is_connected"] is True
    
    @patch('src.network_ui.analytics.connectivity.nx')
    def test_cycle_detection_success(self, mock_nx):
        """Test cycle detection."""
        # Mock NetworkX response
        mock_nx.cycle_basis.return_value = []
        mock_nx.is_directed.return_value = False
        
        result = self.connectivity.cycle_detection(self.test_graph)
        
        assert result.success is True
        assert result.algorithm == "cycle_detection"
        assert "cycles" in result.results
        assert "has_cycles" in result.results
    
    @patch('src.network_ui.analytics.connectivity.nx')
    def test_bridge_detection_success(self, mock_nx):
        """Test bridge detection."""
        # Mock NetworkX response
        mock_nx.bridges.return_value = [("A", "B")]
        mock_nx.is_directed.return_value = False
        
        result = self.connectivity.bridge_detection(self.test_graph)
        
        assert result.success is True
        assert result.algorithm == "bridge_detection"
        assert "bridges" in result.results
        assert len(result.results["bridges"]) == 1
    
    @patch('src.network_ui.analytics.connectivity.nx')
    def test_articulation_points_success(self, mock_nx):
        """Test articulation points detection."""
        # Mock NetworkX response
        mock_nx.articulation_points.return_value = ["B"]
        mock_nx.is_directed.return_value = False
        
        result = self.connectivity.articulation_points(self.test_graph)
        
        assert result.success is True
        assert result.algorithm == "articulation_points"
        assert "articulation_points" in result.results
        assert "B" in result.results["articulation_points"]
    
    @patch('src.network_ui.analytics.connectivity.nx')
    def test_graph_density_success(self, mock_nx):
        """Test graph density calculation."""
        # Mock the graph creation and methods
        mock_graph = MagicMock()
        mock_graph.number_of_nodes.return_value = 4
        mock_graph.number_of_edges.return_value = 3
        mock_degree_dict = {"A": 2, "B": 2, "C": 2, "D": 1}
        mock_graph.degree.return_value = mock_degree_dict
        mock_graph.is_directed.return_value = False
        
        # Mock NetworkX functions
        mock_nx.Graph.return_value = mock_graph
        mock_nx.density.return_value = 0.5  # Return a real number
        
        # Mock the _to_networkx method to return our mock graph
        with patch.object(self.connectivity, '_to_networkx', return_value=mock_graph):
            # Mock the dict() call on degree result
            with patch('builtins.dict', return_value=mock_degree_dict):
                result = self.connectivity.graph_density(self.test_graph)
        
        assert result.success is True
        assert result.algorithm == "graph_density"
        assert "density" in result.results
        assert result.results["density"] == 0.5


class TestGraphAnalyzer:
    """Test the main graph analyzer orchestrator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = GraphAnalyzer()
        
        # Create test graph
        self.test_graph = GraphData(
            nodes=[
                Node(id="A", name="Node A"),
                Node(id="B", name="Node B")
            ],
            edges=[
                Edge(id="1", source="A", target="B")
            ]
        )
    
    def test_analyze_degree_centrality(self):
        """Test degree centrality analysis through analyzer."""
        result = self.analyzer.analyze(
            "degree_centrality", {}, self.test_graph
        )
        
        assert result.success is True
        assert result.algorithm == "degree_centrality"
        assert "centralities" in result.results
    
    def test_analyze_unknown_algorithm(self):
        """Test analysis with unknown algorithm."""
        result = self.analyzer.analyze(
            "unknown_algorithm", {}, self.test_graph
        )
        
        assert result.success is False
        assert "Unknown algorithm" in result.error_message
    
    def test_get_available_algorithms(self):
        """Test getting available algorithms list."""
        algorithms = self.analyzer.get_available_algorithms()
        
        assert isinstance(algorithms, dict)
        assert "shortest_path" in algorithms
        assert "degree_centrality" in algorithms
        assert "betweenness_centrality" in algorithms
        assert "closeness_centrality" in algorithms
        assert "eigenvector_centrality" in algorithms
        assert "all_paths" in algorithms
    
    def test_analyze_with_exception(self):
        """Test analyzer handles exceptions gracefully."""
        with patch.object(self.analyzer.centrality, 'degree_centrality', 
                         side_effect=Exception("Test error")):
            result = self.analyzer.analyze(
                "degree_centrality", {}, self.test_graph
            )
            
            assert result.success is False
            assert "Test error" in result.error_message


class TestAnalyticsIntegration:
    """Test integration between analytics components."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = GraphAnalyzer()
        self.community = CommunityDetection()
        self.connectivity = ConnectivityAnalyzer()
        
        # Create complex test graph
        self.complex_graph = GraphData(
            nodes=[
                Node(id="A", name="Node A"),
                Node(id="B", name="Node B"),
                Node(id="C", name="Node C"),
                Node(id="D", name="Node D"),
                Node(id="E", name="Node E")
            ],
            edges=[
                Edge(id="1", source="A", target="B"),
                Edge(id="2", source="B", target="C"),
                Edge(id="3", source="C", target="D"),
                Edge(id="4", source="D", target="E"),
                Edge(id="5", source="E", target="A"),  # Creates cycle
                Edge(id="6", source="A", target="C")   # Shortcut
            ]
        )
    
    def test_multiple_analyses_same_graph(self):
        """Test running multiple analyses on the same graph."""
        # Test degree centrality
        degree_result = self.analyzer.analyze(
            "degree_centrality", {}, self.complex_graph
        )
        assert degree_result.success is True
        
        # Test shortest path
        path_result = self.analyzer.analyze(
            "shortest_path", 
            {"source_node_id": "A", "target_node_id": "E"}, 
            self.complex_graph
        )
        assert path_result.success is True
        
        # Both should work with the same graph data
        assert degree_result.results["centralities"]["A"] > 0
        assert len(path_result.results["path"]) > 0
    
    def test_analysis_result_serialization(self):
        """Test that analysis results can be JSON serialized."""
        result = self.analyzer.analyze(
            "degree_centrality", {}, self.complex_graph
        )
        
        # This should not raise an exception
        json_str = json.dumps(result.__dict__, default=str)
        assert isinstance(json_str, str)
        assert len(json_str) > 0
    
    def test_visual_mapping_consistency(self):
        """Test that visual mappings are consistent across analyses."""
        degree_result = self.analyzer.analyze(
            "degree_centrality", {}, self.complex_graph
        )
        
        assert degree_result.visual_mapping is not None
        assert "node_colors" in degree_result.visual_mapping
        assert "node_sizes" in degree_result.visual_mapping
        
        # All nodes should have colors and sizes
        node_ids = [node.id for node in self.complex_graph.nodes]
        for node_id in node_ids:
            assert node_id in degree_result.visual_mapping["node_colors"]
            assert node_id in degree_result.visual_mapping["node_sizes"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 