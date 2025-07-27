"""
Network UI - Graph Analytics Module (Spec 3)

This module provides comprehensive graph analytics capabilities including: 
- Pathfinding algorithms (Dijkstra, A*, All Paths)
- Centrality measures (Degree, Betweenness, Closeness, Eigenvector)
- Community detection (Louvain, Girvan-Newman)
- Cycle detection and connectivity analysis
- Visual mapping suggestions for analysis results

The analytics module integrates with the Graph Engine (Spec 2) and provides
results that can be visualized through the Graph Visualization module (Spec 4).
"""

__version__ = "1.0.0"
__author__ = "Agentic AI Development"

# Core analytics components
from .algorithms import GraphAnalyzer, PathfindingAlgorithms, CentralityMeasures
from .community import CommunityDetection
from .connectivity import ConnectivityAnalyzer
from .api.analytics import AnalyticsAPI

__all__ = [
    'GraphAnalyzer',
    'PathfindingAlgorithms',
    'CentralityMeasures',
    'CommunityDetection',
    'ConnectivityAnalyzer',
    'AnalyticsAPI'
]
