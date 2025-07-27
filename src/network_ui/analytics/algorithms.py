"""
Core graph analytics algorithms for pathfinding and centrality measures.
Implements Spec 3:   Graph Analytics requirements.
"""

import heapq
import logging
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
import networkx as nx
from collections import defaultdict, deque

from ..core.models import GraphData, Node, Edge

@dataclass
class AnalysisResult: 
    """Container for analysis results with visual mapping suggestions."""
    algorithm:   str
    results:   Any
    visual_mapping:   Optional[Dict[str, Any]] = None
    metadata:   Dict[str, Any] = None
    success:   bool = True
    error_message:   Optional[str] = None

class PathfindingAlgorithms: 
    """Pathfinding algorithms implementation."""

    def __init__(self): 
        self.logger = logging.getLogger(__name__)

    def shortest_path_dijkstra(self, graph:   GraphData, source_id:   str,
                              target_id:   str, use_edge_weights:   bool = True) -> AnalysisResult: 
        """
        Find shortest path using Dijkstra's algorithm.

        Args: 
            graph:   Graph data structure
            source_id:   Source node ID
            target_id:   Target node ID
            use_edge_weights:   Whether to use edge weights

        Returns: 
            AnalysisResult containing path and distance
        """
        try: 
  # Build adjacency list
            adjacency = self._build_adjacency_list(graph, use_edge_weights)

            if source_id not in adjacency or target_id not in adjacency: 
                return AnalysisResult(
                    algorithm="shortest_path_dijkstra",
                    results=None,
                    success=False,
                    error_message="Source or target node not found"
                )

  # Dijkstra's algorithm
            distances = {node_id:   float('inf') for node_id in adjacency}
            distances[source_id] = 0
            previous = {}
            heap = [(0, source_id)]
            visited = set()

            while heap: 
                current_distance, current = heapq.heappop(heap)

                if current in visited: 
                    continue

                visited.add(current)

                if current == target_id: 
                    break

                for neighbor, weight in adjacency[current]: 
                    distance = current_distance + weight

                    if distance < distances[neighbor]: 
                        distances[neighbor] = distance
                        previous[neighbor] = current
                        heapq.heappush(heap, (distance, neighbor))

  # Reconstruct path
            path = []
            if target_id in previous or source_id == target_id: 
                current = target_id
                while current is not None: 
                    path.append(current)
                    current = previous.get(current)
                path.reverse()

  # Create visual mapping
            visual_mapping = {
                "highlight_nodes":  path,
                "highlight_edges":  self._get_path_edges(graph, path),
                "node_colors":  {node_id:   "#FF6B6B" for node_id in path},
                "edge_colors":  {edge_id:   "#FF6B6B" for edge_id in self._get_path_edges(graph, path)}
            }

            result = {
                "path":  path,
                "distance":  distances.get(target_id, float('inf')),
                "path_length":  len(path) - 1 if len(path) > 1 else 0
            }

            return AnalysisResult(
                algorithm="shortest_path_dijkstra",
                results=result,
                visual_mapping=visual_mapping,
                metadata={"use_edge_weights":  use_edge_weights}
            )

        except Exception as e: 
            self.logger.error(f"Error in Dijkstra's algorithm:   {str(e)}")
            return AnalysisResult(
                algorithm="shortest_path_dijkstra",
                results=None,
                success=False,
                error_message=str(e)
            )

    def all_paths(self, graph:   GraphData, source_id:   str, target_id:   str,
                  max_paths:   int = 10) -> AnalysisResult: 
        """
        Find all paths between two nodes (limited to avoid exponential explosion).

        Args: 
            graph:   Graph data structure
            source_id:   Source node ID
            target_id:   Target node ID
            max_paths:   Maximum number of paths to find

        Returns: 
            AnalysisResult containing all found paths
        """
        try: 
            adjacency = self._build_adjacency_list(graph, use_weights=False)

            if source_id not in adjacency or target_id not in adjacency: 
                return AnalysisResult(
                    algorithm="all_paths",
                    results=None,
                    success=False,
                    error_message="Source or target node not found"
                )

            all_paths = []

            def dfs(current_path, visited): 
                if len(all_paths) >= max_paths: 
                    return

                current = current_path[-1]

                if current == target_id: 
                    all_paths.append(current_path.copy())
                    return

                for neighbor, _ in adjacency[current]: 
                    if neighbor not in visited: 
                        visited.add(neighbor)
                        current_path.append(neighbor)
                        dfs(current_path, visited)
                        current_path.pop()
                        visited.remove(neighbor)

            dfs([source_id], {source_id})

  # Create visual mapping for all paths
            all_nodes = set()
            all_edges = set()
            for path in all_paths: 
                all_nodes.update(path)
                all_edges.update(self._get_path_edges(graph, path))

            visual_mapping = {
                "highlight_nodes":  list(all_nodes),
                "highlight_edges":  list(all_edges),
                "node_colors":  {node_id:   "#4ECDC4" for node_id in all_nodes},
                "edge_colors":  {edge_id:   "#4ECDC4" for edge_id in all_edges}
            }

            result = {
                "paths":  all_paths,
                "count":  len(all_paths),
                "truncated":  len(all_paths) >= max_paths
            }

            return AnalysisResult(
                algorithm="all_paths",
                results=result,
                visual_mapping=visual_mapping,
                metadata={"max_paths":  max_paths}
            )

        except Exception as e: 
            self.logger.error(f"Error in all paths algorithm:   {str(e)}")
            return AnalysisResult(
                algorithm="all_paths",
                results=None,
                success=False,
                error_message=str(e)
            )

    def _build_adjacency_list(self, graph:   GraphData, use_weights:   bool = True) -> Dict[str, List[Tuple[str, float]]]: 
        """Build adjacency list from graph data."""
        adjacency = defaultdict(list)

  # Add all nodes to ensure they exist in adjacency list
        for node in graph.nodes:  
            adjacency[node.id] = []

  # Add edges
        for edge in graph.edges:  
            weight = edge.weight if use_weights else 1.0
            adjacency[edge.source].append((edge.target, weight))

  # Add reverse edge for undirected graphs
            if not edge.directed:  
                adjacency[edge.target].append((edge.source, weight))

        return dict(adjacency)

    def _get_path_edges(self, graph:   GraphData, path:   List[str]) -> List[str]: 
        """Get edge IDs that connect nodes in the path."""
        if len(path) < 2: 
            return []

        path_edges = []
        for i in range(len(path) - 1): 
            source, target = path[i], path[i + 1]
            for edge in graph.edges:  
                if (edge.source == source and edge.target == target) or \
                   (not edge.directed and edge.source == target and edge.target == source): 
                    path_edges.append(edge.id)
                    break

        return path_edges

class CentralityMeasures: 
    """Centrality measures implementation."""

    def __init__(self): 
        self.logger = logging.getLogger(__name__)

    def degree_centrality(self, graph:   GraphData) -> AnalysisResult: 
        """Calculate degree centrality for all nodes."""
        try: 
            centralities = {}

  # Count connections for each node
            for node in graph.nodes:  
                degree = 0
                for edge in graph.edges:  
                    if edge.source == node.id or edge.target == node.id:  
                        degree += 1
                centralities[node.id] = degree

  # Normalize by maximum possible degree
            max_degree = max(centralities.values()) if centralities else 1
            normalized_centralities = {
                node_id:   degree / max_degree if max_degree > 0 else 0
                for node_id, degree in centralities.items()
            }

  # Create visual mapping
            visual_mapping = {
                "node_sizes":  {
                    node_id:   10 + (30 * centrality)  # Size between 10-40
                    for node_id, centrality in normalized_centralities.items()
                },
                "node_colors":  self._create_centrality_colors(normalized_centralities),
                "color_scheme":  "viridis"
            }

            result = {
                "centralities":  centralities,
                "normalized_centralities":  normalized_centralities,
                "max_centrality":  max(centralities.values()) if centralities else 0,
                "min_centrality":  min(centralities.values()) if centralities else 0,
                "algorithm":  "degree_centrality"
            }

            return AnalysisResult(
                algorithm="degree_centrality",
                results=result,
                visual_mapping=visual_mapping,
                metadata={"normalization":  "max_degree"}
            )

        except Exception as e: 
            self.logger.error(f"Error in degree centrality:   {str(e)}")
            return AnalysisResult(
                algorithm="degree_centrality",
                results=None,
                success=False,
                error_message=str(e)
            )

    def betweenness_centrality(self, graph:   GraphData) -> AnalysisResult: 
        """Calculate betweenness centrality using NetworkX for efficiency."""
        try: 
  # Convert to NetworkX graph
            nx_graph = self._to_networkx(graph)

  # Calculate betweenness centrality
            centralities = nx.betweenness_centrality(nx_graph)

  # Create visual mapping
            visual_mapping = {
                "node_sizes":  {
                    node_id:   10 + (30 * centrality)
                    for node_id, centrality in centralities.items()
                },
                "node_colors":  self._create_centrality_colors(centralities),
                "color_scheme":  "plasma"
            }

            result = {
                "centralities":  centralities,
                "max_centrality":  max(centralities.values()) if centralities else 0,
                "algorithm":  "betweenness_centrality"
            }

            return AnalysisResult(
                algorithm="betweenness_centrality",
                results=result,
                visual_mapping=visual_mapping,
                metadata={"library":  "networkx"}
            )

        except Exception as e: 
            self.logger.error(f"Error in betweenness centrality:   {str(e)}")
            return AnalysisResult(
                algorithm="betweenness_centrality",
                results=None,
                success=False,
                error_message=str(e)
            )

    def closeness_centrality(self, graph:   GraphData) -> AnalysisResult: 
        """Calculate closeness centrality."""
        try: 
            nx_graph = self._to_networkx(graph)
            centralities = nx.closeness_centrality(nx_graph)

            visual_mapping = {
                "node_sizes":  {
                    node_id:   10 + (30 * centrality)
                    for node_id, centrality in centralities.items()
                },
                "node_colors":  self._create_centrality_colors(centralities),
                "color_scheme":  "inferno"
            }

            result = {
                "centralities":  centralities,
                "max_centrality":  max(centralities.values()) if centralities else 0,
                "algorithm":  "closeness_centrality"
            }

            return AnalysisResult(
                algorithm="closeness_centrality",
                results=result,
                visual_mapping=visual_mapping,
                metadata={"library":  "networkx"}
            )

        except Exception as e: 
            self.logger.error(f"Error in closeness centrality:   {str(e)}")
            return AnalysisResult(
                algorithm="closeness_centrality",
                results=None,
                success=False,
                error_message=str(e)
            )

    def eigenvector_centrality(self, graph:   GraphData) -> AnalysisResult: 
        """Calculate eigenvector centrality."""
        try: 
            nx_graph = self._to_networkx(graph)

  # NetworkX eigenvector centrality may fail for disconnected graphs
            if not nx.is_connected(nx_graph.to_undirected()): 
  # Use the largest connected component
                largest_cc = max(nx.connected_components(nx_graph.to_undirected()), key=len)
                subgraph = nx_graph.subgraph(largest_cc)
                centralities = nx.eigenvector_centrality(subgraph)

  # Add zero centrality for nodes not in largest component
                for node in nx_graph.nodes(): 
                    if node not in centralities: 
                        centralities[node] = 0.0
            else: 
                centralities = nx.eigenvector_centrality(nx_graph)

            visual_mapping = {
                "node_sizes":  {
                    node_id:   10 + (30 * centrality)
                    for node_id, centrality in centralities.items()
                },
                "node_colors":  self._create_centrality_colors(centralities),
                "color_scheme":  "magma"
            }

            result = {
                "centralities":  centralities,
                "max_centrality":  max(centralities.values()) if centralities else 0,
                "algorithm":  "eigenvector_centrality"
            }

            return AnalysisResult(
                algorithm="eigenvector_centrality",
                results=result,
                visual_mapping=visual_mapping,
                metadata={"library":  "networkx"}
            )

        except Exception as e: 
            self.logger.error(f"Error in eigenvector centrality:   {str(e)}")
            return AnalysisResult(
                algorithm="eigenvector_centrality",
                results=None,
                success=False,
                error_message=str(e)
            )

    def _to_networkx(self, graph:   GraphData) -> nx.Graph:  
        """Convert GraphData to NetworkX graph."""
        if any(edge.directed for edge in graph.edges): 
            nx_graph = nx.DiGraph()
        else: 
            nx_graph = nx.Graph()

  # Add nodes
        for node in graph.nodes:  
            nx_graph.add_node(node.id, **node.attributes)

  # Add edges
        for edge in graph.edges:  
            nx_graph.add_edge(edge.source, edge.target, weight=edge.weight, **edge.attributes)

        return nx_graph

    def _create_centrality_colors(self, centralities:   Dict[str, float]) -> Dict[str, str]: 
        """Create color mapping based on centrality values."""
        if not centralities: 
            return {}

        max_centrality = max(centralities.values())
        min_centrality = min(centralities.values())
        range_centrality = max_centrality - min_centrality

        colors = {}
        for node_id, centrality in centralities.items(): 
            if range_centrality > 0: 
                normalized = (centrality - min_centrality) / range_centrality
            else: 
                normalized = 0.5

  # Create color gradient from blue (low) to red (high)
            red = int(255 * normalized)
            blue = int(255 * (1 - normalized))
            green = int(128 * (1 - abs(0.5 - normalized) * 2))

  # Ensure color values are within valid range
            red = max(0, min(255, red))
            blue = max(0, min(255, blue))
            green = max(0, min(255, green))

            colors[node_id] = f"#{red:02x}{green:02x}{blue:02x}"

        return colors

class GraphAnalyzer: 
    """Main graph analyzer that orchestrates all analysis algorithms."""

    def __init__(self): 
        self.logger = logging.getLogger(__name__)
        self.pathfinding = PathfindingAlgorithms()
        self.centrality = CentralityMeasures()

    def analyze(self, algorithm:   str, parameters:   Dict[str, Any],
                graph_data:   GraphData) -> AnalysisResult: 
        """
        Execute specified analysis algorithm.

        Args: 
            algorithm:   Name of algorithm to run
            parameters:   Algorithm parameters
            graph_data:   Graph to analyze

        Returns: 
            AnalysisResult with results and visual mapping
        """
        try: 
  # Pathfinding algorithms
            if algorithm == "shortest_path": 
                return self.pathfinding.shortest_path_dijkstra(
                    graph_data,
                    parameters.get("source_node_id"),
                    parameters.get("target_node_id"),
                    parameters.get("use_edge_weights", True)
                )

            elif algorithm == "all_paths": 
                return self.pathfinding.all_paths(
                    graph_data,
                    parameters.get("source_node_id"),
                    parameters.get("target_node_id"),
                    parameters.get("max_paths", 10)
                )

  # Centrality algorithms
            elif algorithm == "degree_centrality": 
                return self.centrality.degree_centrality(graph_data)

            elif algorithm == "betweenness_centrality": 
                return self.centrality.betweenness_centrality(graph_data)

            elif algorithm == "closeness_centrality": 
                return self.centrality.closeness_centrality(graph_data)

            elif algorithm == "eigenvector_centrality": 
                return self.centrality.eigenvector_centrality(graph_data)

            else: 
                return AnalysisResult(
                    algorithm=algorithm,
                    results=None,
                    success=False,
                    error_message=f"Unknown algorithm:   {algorithm}"
                )

        except Exception as e: 
            self.logger.error(f"Error in analysis:   {str(e)}")
            return AnalysisResult(
                algorithm=algorithm,
                results=None,
                success=False,
                error_message=str(e)
            )

    def get_available_algorithms(self) -> Dict[str, Dict[str, Any]]: 
        """Get list of available algorithms and their parameters."""
        return {
            "shortest_path":  {
                "description":  "Find shortest path between two nodes",
                "parameters":  {
                    "source_node_id":  {"type":  "string", "required":  True},
                    "target_node_id":  {"type":  "string", "required":  True},
                    "use_edge_weights":  {"type":  "boolean", "required":  False, "default":  True}
                }
            },
            "all_paths":  {
                "description":  "Find all paths between two nodes",
                "parameters":  {
                    "source_node_id":  {"type":  "string", "required":  True},
                    "target_node_id":  {"type":  "string", "required":  True},
                    "max_paths":  {"type":  "integer", "required":  False, "default":  10}
                }
            },
            "degree_centrality":  {
                "description":  "Calculate degree centrality for all nodes",
                "parameters":  {}
            },
            "betweenness_centrality":  {
                "description":  "Calculate betweenness centrality for all nodes",
                "parameters":  {}
            },
            "closeness_centrality":  {
                "description":  "Calculate closeness centrality for all nodes",
                "parameters":  {}
            },
            "eigenvector_centrality":  {
                "description":  "Calculate eigenvector centrality for all nodes",
                "parameters":  {}
            }
        }
