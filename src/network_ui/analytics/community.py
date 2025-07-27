"""
Community detection algorithms for graph analysis.
Implements community detection requirements from Spec 3.
"""

import logging
from typing import Dict, List, Any, Set
import networkx as nx
from collections import defaultdict
import random

from ..core.models import GraphData
from .algorithms import AnalysisResult

class CommunityDetection: 
    """Community detection algorithms implementation."""

    def __init__(self): 
        self.logger = logging.getLogger(__name__)

    def louvain_modularity(self, graph:   GraphData) -> AnalysisResult: 
        """
        Detect communities using Louvain modularity optimization.

        Args: 
            graph:   Graph data structure

        Returns: 
            AnalysisResult containing community assignments
        """
        try: 
  # Convert to NetworkX graph
            nx_graph = self._to_networkx(graph)

  # Run Louvain community detection
            communities = nx.community.louvain_communities(nx_graph)

  # Convert to node -> community mapping
            node_communities = {}
            community_colors = self._generate_community_colors(len(communities))

            for i, community in enumerate(communities): 
                for node in community: 
                    node_communities[node] = i

  # Create visual mapping
            visual_mapping = {
                "node_colors":  {
                    node_id:   community_colors[community_id]
                    for node_id, community_id in node_communities.items()
                },
                "communities":  communities,
                "color_scheme":  "community_detection"
            }

  # Calculate modularity score
            modularity = nx.community.modularity(nx_graph, communities)

            result = {
                "communities":  [list(community) for community in communities],
                "node_communities":  node_communities,
                "num_communities":  len(communities),
                "modularity":  modularity,
                "algorithm":  "louvain_modularity"
            }

            return AnalysisResult(
                algorithm="louvain_modularity",
                results=result,
                visual_mapping=visual_mapping,
                metadata={"library":  "networkx", "modularity":  modularity}
            )

        except Exception as e: 
            self.logger.error(f"Error in Louvain modularity:   {str(e)}")
            return AnalysisResult(
                algorithm="louvain_modularity",
                results=None,
                success=False,
                error_message=str(e)
            )

    def girvan_newman(self, graph:   GraphData, max_communities:   int = 10) -> AnalysisResult: 
        """
        Detect communities using Girvan-Newman algorithm.

        Args: 
            graph:   Graph data structure
            max_communities:   Maximum number of communities to detect

        Returns: 
            AnalysisResult containing community assignments
        """
        try: 
            nx_graph = self._to_networkx(graph)

  # Run Girvan-Newman algorithm
            communities_generator = nx.community.girvan_newman(nx_graph)

  # Get communities at different levels
            all_levels = []
            for i, communities in enumerate(communities_generator): 
                if i >= max_communities: 
                    break
                all_levels.append(list(communities))

  # Use the last level (most communities)
            if all_levels: 
                communities = all_levels[-1]
            else: 
                communities = [set(nx_graph.nodes())]

  # Convert to node -> community mapping
            node_communities = {}
            community_colors = self._generate_community_colors(len(communities))

            for i, community in enumerate(communities): 
                for node in community: 
                    node_communities[node] = i

  # Create visual mapping
            visual_mapping = {
                "node_colors":  {
                    node_id:   community_colors[community_id]
                    for node_id, community_id in node_communities.items()
                },
                "communities":  communities,
                "color_scheme":  "community_detection"
            }

  # Calculate modularity score
            modularity = nx.community.modularity(nx_graph, communities)

            result = {
                "communities":  [list(community) for community in communities],
                "node_communities":  node_communities,
                "num_communities":  len(communities),
                "modularity":  modularity,
                "algorithm":  "girvan_newman",
                "all_levels":  [[list(c) for c in level] for level in all_levels]
            }

            return AnalysisResult(
                algorithm="girvan_newman",
                results=result,
                visual_mapping=visual_mapping,
                metadata={"library":  "networkx", "modularity":  modularity, "levels":  len(all_levels)}
            )

        except Exception as e: 
            self.logger.error(f"Error in Girvan-Newman:   {str(e)}")
            return AnalysisResult(
                algorithm="girvan_newman",
                results=None,
                success=False,
                error_message=str(e)
            )

    def label_propagation(self, graph:   GraphData) -> AnalysisResult: 
        """
        Detect communities using label propagation algorithm.

        Args: 
            graph:   Graph data structure

        Returns: 
            AnalysisResult containing community assignments
        """
        try: 
            nx_graph = self._to_networkx(graph)

  # Run label propagation
            communities = list(nx.community.label_propagation_communities(nx_graph))

  # Convert to node -> community mapping
            node_communities = {}
            community_colors = self._generate_community_colors(len(communities))

            for i, community in enumerate(communities): 
                for node in community: 
                    node_communities[node] = i

  # Create visual mapping
            visual_mapping = {
                "node_colors":  {
                    node_id:   community_colors[community_id]
                    for node_id, community_id in node_communities.items()
                },
                "communities":  communities,
                "color_scheme":  "community_detection"
            }

  # Calculate modularity score
            modularity = nx.community.modularity(nx_graph, communities)

            result = {
                "communities":  [list(community) for community in communities],
                "node_communities":  node_communities,
                "num_communities":  len(communities),
                "modularity":  modularity,
                "algorithm":  "label_propagation"
            }

            return AnalysisResult(
                algorithm="label_propagation",
                results=result,
                visual_mapping=visual_mapping,
                metadata={"library":  "networkx", "modularity":  modularity}
            )

        except Exception as e: 
            self.logger.error(f"Error in label propagation:   {str(e)}")
            return AnalysisResult(
                algorithm="label_propagation",
                results=None,
                success=False,
                error_message=str(e)
            )

    def _to_networkx(self, graph:   GraphData) -> nx.Graph:  
        """Convert GraphData to NetworkX graph."""
  # Use undirected graph for community detection
        nx_graph = nx.Graph()

  # Add nodes
        for node in graph.nodes:  
            nx_graph.add_node(node.id, **node.attributes)

  # Add edges
        for edge in graph.edges:  
            nx_graph.add_edge(edge.source, edge.target, weight=edge.weight, **edge.attributes)

        return nx_graph

    def _generate_community_colors(self, num_communities:   int) -> List[str]: 
        """Generate distinct colors for communities."""
        colors = [
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
            "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9",
            "#F8C471", "#82E0AA", "#F1948A", "#85C1E9", "#F4D03F",
            "#AED6F1", "#A9DFBF", "#F9E79F", "#D7BDE2", "#A3E4D7"
        ]

  # If we need more colors than predefined, generate random ones
        while len(colors) < num_communities: 
            r = random.randint(100, 255)
            g = random.randint(100, 255)
            b = random.randint(100, 255)
            colors.append(f"#{r:02x}{g:02x}{b:02x}")

        return colors[: num_communities]
