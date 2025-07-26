"""
Visualization Configuration Module

Manages all configuration settings for graph visualization including:
- Rendering settings (canvas size, anti - aliasing, performance)
- Layout algorithm parameters
- Visual styling defaults
- Interaction behavior settings
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple
from enum import Enum


class RenderingEngine(Enum):
    """Available rendering engines."""
    CANVAS = "canvas"
    WEBGL = "webgl"


class LayoutAlgorithm(Enum):
    """Available layout algorithms."""
    FORCE_DIRECTED = "force_directed"
    HIERARCHICAL = "hierarchical"
    CIRCULAR = "circular"
    GRID = "grid"
    RANDOM = "random"


@dataclass
class NodeStyle:
    """Default node visual styling."""
    size: float = 10.0
    color: str = "#1f77b4"
    border_color: str = "#fffff"
    border_width: float = 1.0
    shape: str = "circle"  # circle, square, triangle
    opacity: float = 1.0
    label_size: float = 12.0
    label_color: str = "#000000"
    label_font: str = "Arial, sans - seri"


@dataclass
class EdgeStyle:
    """Default edge visual styling."""
    width: float = 2.0
    color: str = "#999999"
    opacity: float = 0.8
    style: str = "solid"  # solid, dashed, dotted
    arrow_size: float = 8.0
    arrow_color: str = "#666666"
    curved: bool = False
    curve_strength: float = 0.1


@dataclass
class CanvasSettings:
    """Canvas rendering settings."""
    width: int = 800
    height: int = 600
    background_color: str = "#fffff"
    anti_aliasing: bool = True
    high_dpi: bool = True
    fps_limit: int = 60


@dataclass
class InteractionSettings:
    """User interaction settings."""
    enable_zoom: bool = True
    enable_pan: bool = True
    enable_drag: bool = True
    enable_selection: bool = True
    enable_hover: bool = True
    zoom_speed: float = 0.1
    pan_speed: float = 1.0
    double_click_zoom: bool = True
    context_menu: bool = True


@dataclass
class LayoutSettings:
    """Layout algorithm settings."""
    algorithm: LayoutAlgorithm = LayoutAlgorithm.FORCE_DIRECTED
    iterations: int = 100
    animate: bool = True
    animation_duration: float = 1.0
    spring_strength: float = 0.1
    repulsion_strength: float = 1000.0
    center_force: float = 0.01
    damping: float = 0.9


@dataclass
class PerformanceSettings:
    """Performance optimization settings."""
    max_nodes_full_render: int = 1000
    max_edges_full_render: int = 5000
    enable_clustering: bool = True
    cluster_threshold: int = 500
    level_of_detail: bool = True
    frustum_culling: bool = True
    batch_rendering: bool = True


@dataclass
class VisualizationConfig:
    """Complete visualization configuration."""
    rendering_engine: RenderingEngine = RenderingEngine.CANVAS
    canvas: CanvasSettings = field(default_factory=CanvasSettings)
    node_style: NodeStyle = field(default_factory=NodeStyle)
    edge_style: EdgeStyle = field(default_factory=EdgeStyle)
    layout: LayoutSettings = field(default_factory=LayoutSettings)
    interactions: InteractionSettings = field(default_factory=InteractionSettings)
    performance: PerformanceSettings = field(default_factory=PerformanceSettings)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'rendering_engine': self.rendering_engine.value,
            'canvas': {
                'width': self.canvas.width,
                'height': self.canvas.height,
                'background_color': self.canvas.background_color,
                'anti_aliasing': self.canvas.anti_aliasing,
                'high_dpi': self.canvas.high_dpi,
                'fps_limit': self.canvas.fps_limit
            },
            'node_style': {
                'size': self.node_style.size,
                'color': self.node_style.color,
                'border_color': self.node_style.border_color,
                'border_width': self.node_style.border_width,
                'shape': self.node_style.shape,
                'opacity': self.node_style.opacity,
                'label_size': self.node_style.label_size,
                'label_color': self.node_style.label_color,
                'label_font': self.node_style.label_font
            },
            'edge_style': {
                'width': self.edge_style.width,
                'color': self.edge_style.color,
                'opacity': self.edge_style.opacity,
                'style': self.edge_style.style,
                'arrow_size': self.edge_style.arrow_size,
                'arrow_color': self.edge_style.arrow_color,
                'curved': self.edge_style.curved,
                'curve_strength': self.edge_style.curve_strength
            },
            'layout': {
                'algorithm': self.layout.algorithm.value,
                'iterations': self.layout.iterations,
                'animate': self.layout.animate,
                'animation_duration': self.layout.animation_duration,
                'spring_strength': self.layout.spring_strength,
                'repulsion_strength': self.layout.repulsion_strength,
                'center_force': self.layout.center_force,
                'damping': self.layout.damping
            },
            'interactions': {
                'enable_zoom': self.interactions.enable_zoom,
                'enable_pan': self.interactions.enable_pan,
                'enable_drag': self.interactions.enable_drag,
                'enable_selection': self.interactions.enable_selection,
                'enable_hover': self.interactions.enable_hover,
                'zoom_speed': self.interactions.zoom_speed,
                'pan_speed': self.interactions.pan_speed,
                'double_click_zoom': self.interactions.double_click_zoom,
                'context_menu': self.interactions.context_menu
            },
            'performance': {
                'max_nodes_full_render': self.performance.max_nodes_full_render,
                'max_edges_full_render': self.performance.max_edges_full_render,
                'enable_clustering': self.performance.enable_clustering,
                'cluster_threshold': self.performance.cluster_threshold,
                'level_of_detail': self.performance.level_of_detail,
                'frustum_culling': self.performance.frustum_culling,
                'batch_rendering': self.performance.batch_rendering
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VisualizationConfig':
        """Create configuration from dictionary."""
        config = cls()

        if 'rendering_engine' in data:
            config.rendering_engine = RenderingEngine(data['rendering_engine'])

        if 'canvas' in data:
            canvas_data = data['canvas']
            config.canvas = CanvasSettings(
                width=canvas_data.get('width', config.canvas.width),
                height=canvas_data.get('height', config.canvas.height),
                background_color=canvas_data.get('background_color', config.canvas.background_color),
                anti_aliasing=canvas_data.get('anti_aliasing', config.canvas.anti_aliasing),
                high_dpi=canvas_data.get('high_dpi', config.canvas.high_dpi),
                fps_limit=canvas_data.get('fps_limit', config.canvas.fps_limit)
            )

        if 'layout' in data:
            layout_data = data['layout']
            config.layout.algorithm = LayoutAlgorithm(layout_data.get('algorithm', config.layout.algorithm.value))
            config.layout.iterations = layout_data.get('iterations', config.layout.iterations)
            config.layout.animate = layout_data.get('animate', config.layout.animate)
            config.layout.animation_duration = layout_data.get('animation_duration', config.layout.animation_duration)

        return config


def get_default_config() -> VisualizationConfig:
    """Get default visualization configuration."""
    return VisualizationConfig()


def get_performance_config() -> VisualizationConfig:
    """Get performance - optimized configuration for large graphs."""
    config = VisualizationConfig()
    config.rendering_engine = RenderingEngine.WEBGL
    config.performance.enable_clustering = True
    config.performance.level_of_detail = True
    config.performance.batch_rendering = True
    config.layout.animate = False
    config.interactions.enable_hover = False
    return config


def get_high_quality_config() -> VisualizationConfig:
    """Get high - quality configuration for presentation."""
    config = VisualizationConfig()
    config.canvas.anti_aliasing = True
    config.canvas.high_dpi = True
    config.node_style.border_width = 2.0
    config.edge_style.width = 3.0
    config.layout.animate = True
    config.layout.animation_duration = 2.0
    return config
