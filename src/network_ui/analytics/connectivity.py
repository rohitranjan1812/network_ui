"""
Connectivity analysis algorithms for graph analysis.
Implements connectivity and cycle detection requirements from Spec 3.
"""

import logging
from typing import Dict, List, Any, Set, Tuple
import networkx as nx
from collections import defaultdict, deque

from ..core.models import GraphData
from .algorithms import AnalysisResult

class ConnectivityAnalyzer: 
    """Connectivity analysis algorithms implementation."""

    def __init__(self): 
        self.logger = logging.getLogger(__name__)

    def connected_components(self, graph:   GraphData) -> AnalysisResult: 
        """
        Find connected components in the graph.

        Args: 
            graph:   Graph data structure

        Returns: 
            AnalysisResult containing connected components
        """
        try: 
  # Convert to NetworkX graph
            nx_graph = self._to_networkx(graph)

  # Find connected components
            if nx_graph.is_directed(): 
  # For directed graphs, use weakly connected components
                components = list(nx.weakly_connected_components(nx_graph))
                strongly_connected = list(nx.strongly_connected_components(nx_graph))

                component_analysis = {
                    "weakly_connected":  [list(comp) for comp in components],
                    "strongly_connected":  [list(comp) for comp in strongly_connected],
                    "num_weakly_connected":  len(components),
                    "num_strongly_connected":  len(strongly_connected)
                }
            else: 
  # For undirected graphs
                components = list(nx.connected_components(nx_graph))
                component_analysis = {
                    "connected_components":  [list(comp) for comp in components],
                    "num_components":  len(components)
                }

  # Assign colors to components
            component_colors = self._generate_component_colors(len(components))
            node_colors = {}

            for i, component in enumerate(components): 
                for node in component: 
                    node_colors[node] = component_colors[i]

  # Create visual mapping
            visual_mapping = {
                "node_colors":  node_colors,
                "components":  components,
                "color_scheme":  "connected_components"
            }

  # Additional metrics
            largest_component = max(components, key=len) if components else set()

            result = {
 **component_analysis,
                "largest_component":  list(largest_component),
                "largest_component_size":  len(largest_component),
                "is_connected":  len(components) == 1,
                "algorithm":  "connected_components"
            }

            return AnalysisResult(
                algorithm="connected_components",
                results=result,
                visual_mapping=visual_mapping,
                metadata={"library":  "networkx", "directed":  nx_graph.is_directed()}
            )

        except Exception as e: 
            self.logger.error(f"Error in connected components analysis:   {str(e)}")
            return AnalysisResult(
                algorithm="connected_components",
                results=None,
                success=False,
                error_message=str(e)
            )

    def cycle_detection(self, graph:   GraphData) -> AnalysisResult: 
        """
        Detect cycles in the graph.

        Args: 
            graph:   Graph data structure

        Returns: 
            AnalysisResult containing cycle information
        """
        try: 
            nx_graph = self._to_networkx(graph)

            cycles = []
            cycle_edges = set()

            if nx_graph.is_directed(): 
  # For directed graphs, find simple cycles
                try: 
  # NetworkX simple_cycles can be expensive, limit the search
                    cycle_generator = nx.simple_cycles(nx_graph)
                    for i, cycle in enumerate(cycle_generator): 
                        if i >= 100:  # Limit to first 100 cycles
                            break
                        cycles.append(cycle)
  # Add edges in cycle
                        for j in range(len(cycle)): 
                            source = cycle[j]
                            target = cycle[(j + 1) % len(cycle)]
                            cycle_edges.add((source, target))
                except Exception: 
  # Fallback to basic cycle detection
                    has_cycles = not nx.is_directed_acyclic_graph(nx_graph)
                    if has_cycles: 
                        cycles = ["Cycles detected but enumeration failed"]
            else: 
  # For undirected graphs, find cycle basis
                try: 
                    cycle_basis = nx.cycle_basis(nx_graph)
                    cycles = cycle_basis

  # Convert cycles to edges
                    for cycle in cycles: 
                        for i in range(len(cycle)): 
                            source = cycle[i]
                            target = cycle[(i + 1) % len(cycle)]
                            cycle_edges.add((min(source, target), max(source, target)))
                except Exception: 
  # Fallback:   check if any cycles exist
                    has_cycles = len(nx_graph.edges()) >= len(nx_graph.nodes())
                    if has_cycles: 
                        cycles = ["Cycles detected but enumeration failed"]

  # Create visual mapping
            cycle_nodes = set()
            for cycle in cycles: 
                if isinstance(cycle, list): 
                    cycle_nodes.update(cycle)

            visual_mapping = {
                "highlight_nodes":  list(cycle_nodes),
                "highlight_edges":  [f"{s}-{t}" for s, t in cycle_edges],
                "node_colors":  {node_id:   "#FF6B6B" for node_id in cycle_nodes},
                "edge_colors":  {f"{s}-{t}":  "#FF6B6B" for s, t in cycle_edges}
            }

            result = {
                "cycles":  cycles,
                "num_cycles":  len(cycles),
                "has_cycles":  len(cycles) > 0,
                "cycle_nodes":  list(cycle_nodes),
                "algorithm":  "cycle_detection"
            }

            return AnalysisResult(
                algorithm="cycle_detection",
                results=result,
                visual_mapping=visual_mapping,
                metadata={"library":  "networkx", "directed":  nx_graph.is_directed()}
            )

        except Exception as e: 
            self.logger.error(f"Error in cycle detection:   {str(e)}")
            return AnalysisResult(
                algorithm="cycle_detection",
                results=None,
                success=False,
                error_message=str(e)
            )

    def bridge_detection(self, graph:   GraphData) -> AnalysisResult: 
        """
        Detect bridge edges (edges whose removal increases connected components).

        Args: 
            graph:   Graph data structure

        Returns: 
            AnalysisResult containing bridge information
        """
        try: 
            nx_graph = self._to_networkx(graph)

  # Convert to undirected for bridge detection
            if nx_graph.is_directed(): 
                nx_graph = nx_graph.to_undirected()

  # Find bridges
            bridges = list(nx.bridges(nx_graph))

  # Create visual mapping
            visual_mapping = {
                "highlight_edges":  [f"{min(s, t)}-{max(s, t)}" for s, t in bridges],
                "edge_colors":  {f"{min(s, t)}-{max(s, t)}":  "#FF9800" for s, t in bridges},
                "edge_widths":  {f"{min(s, t)}-{max(s, t)}":  4 for s, t in bridges}
            }

            result = {
                "bridges":  bridges,
                "num_bridges":  len(bridges),
                "bridge_nodes":  list(set([node for bridge in bridges for node in bridge])),
                "algorithm":  "bridge_detection"
            }

            return AnalysisResult(
                algorithm="bridge_detection",
                results=result,
                visual_mapping=visual_mapping,
                metadata={"library":  "networkx"}
            )

        except Exception as e: 
            self.logger.error(f"Error in bridge detection:   {str(e)}")
            return AnalysisResult(
                algorithm="bridge_detection",
                results=None,
                success=False,
                error_message=str(e)
            )

    def articulation_points(self, graph:   GraphData) -> AnalysisResult: 
        """
        Find articulation points (nodes whose removal increases connected components).

        Args: 
            graph:   Graph data structure

        Returns: 
            AnalysisResult containing articulation points
        """
        try: 
            nx_graph = self._to_networkx(graph)

  # Convert to undirected for articulation point detection
            if nx_graph.is_directed(): 
                nx_graph = nx_graph.to_undirected()

  # Find articulation points
            articulation_points = list(nx.articulation_points(nx_graph))

  # Create visual mapping
            visual_mapping = {
                "highlight_nodes":  articulation_points,
                "node_colors":  {node_id:   "#E74C3C" for node_id in articulation_points},
                "node_sizes":  {node_id:   25 for node_id in articulation_points}
            }

            result = {
                "articulation_points":  articulation_points,
                "num_articulation_points":  len(articulation_points),
                "algorithm":  "articulation_points"
            }

            return AnalysisResult(
                algorithm="articulation_points",
                results=result,
                visual_mapping=visual_mapping,
                metadata={"library":  "networkx"}
            )

        except Exception as e: 
            self.logger.error(f"Error in articulation points detection:   {str(e)}")
            return AnalysisResult(
                algorithm="articulation_points",
                results=None,
                success=False,
                error_message=str(e)
            )

    def graph_density(self, graph:   GraphData) -> AnalysisResult: 
        """
        Calculate graph density and related metrics.

        Args: 
            graph:   Graph data structure

        Returns: 
            AnalysisResult containing density metrics
        """
        try: 
            nx_graph = self._to_networkx(graph)

  # Calculate basic metrics
            num_nodes = nx_graph.number_of_nodes()
            num_edges = nx_graph.number_of_edges()
            density = nx.density(nx_graph)

  # Calculate theoretical maximum edges
            if nx_graph.is_directed(): 
                max_edges = num_nodes * (num_nodes - 1)
            else: 
                max_edges = num_nodes * (num_nodes - 1) // 2

  # Additional metrics
            avg_degree = sum(dict(nx_graph.degree()).values()) / num_nodes if num_nodes > 0 else 0

            result = {
                "density":  density,
                "num_nodes":  num_nodes,
                "num_edges":  num_edges,
                "max_possible_edges":  max_edges,
                "average_degree":  avg_degree,
                "is_sparse":  density < 0.1,
                "is_dense":  density > 0.7,
                "algorithm":  "graph_density"
            }

  # No specific visual mapping for density
            visual_mapping = {}

            return AnalysisResult(
                algorithm="graph_density",
                results=result,
                visual_mapping=visual_mapping,
                metadata={"library":  "networkx", "directed":  nx_graph.is_directed()}
            )

        except Exception as e: 
            self.logger.error(f"Error in graph density calculation:   {str(e)}")
            return AnalysisResult(
                algorithm="graph_density",
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

    def _generate_component_colors(self, num_components:   int) -> List[str]: 
        """Generate distinct colors for connected components."""
        colors = [
            "#3498DB", "#E74C3C", "#2ECC71", "#F39C12", "#9B59B6",
            "#1ABC9C", "#E67E22", "#34495E", "#E91E63", "#FF5722",
            "#607D8B", "#795548", "#009688", "#FF9800", "#673AB7"
        ]

  # Extend colors if needed
        while len(colors) < num_components: 
            import random
            r = random.randint(50, 200)
            g = random.randint(50, 200)
            b = random.randint(50, 200)
            colors.append(f"#{r:02x}{g:02x}{b:02x}")

        return colors[: num_components]
