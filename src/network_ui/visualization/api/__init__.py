"""
Visualization API Module

Provides REST API endpoints for graph visualization operations: 
- Render / update graph visualizations
- Change layout algorithms
- Configure visual mappings
- Apply filters and highlights
"""

from .visualization import visualization_api

__all__ = ['visualization_api']
