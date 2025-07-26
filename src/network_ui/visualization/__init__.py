"""
Network UI - Graph Visualization Module (Spec 3)

This module provides comprehensive graph visualization capabilities including:
- High - performance HTML5 Canvas / WebGL rendering
- Interactive layout algorithms (force - directed, hierarchical, circular)
- Direct manipulation (drag & drop, selection)
- Data - driven visual mapping
- Real - time filtering and highlighting

The visualization module integrates seamlessly with the Graph Engine (Spec 2)
and Data Import (Spec 1) modules.
"""

__version__ = "1.0.0"
__author__ = "Agentic AI Development"

# Core visualization components
from .renderer import GraphRenderer, VisualConfig, LayoutAlgorithm, VisualStyle
from .layouts import ForceDirectedLayout, HierarchicalLayout, CircularLayout, GridLayout, RandomLayout
from .interactions import InteractionManager
from .visual_mapping import VisualMapper, MappingConfig, ColorScheme
from .config import VisualizationConfig

# API components - imported separately to avoid circular imports

__all__ = [
    'GraphRenderer',
    'VisualConfig',
    'LayoutAlgorithm', 
    'VisualStyle',
    'ForceDirectedLayout',
    'HierarchicalLayout',
    'CircularLayout',
    'GridLayout',
    'RandomLayout',
    'InteractionManager',
    'VisualMapper',
    'MappingConfig',
    'ColorScheme',
    'VisualizationConfig'
]
