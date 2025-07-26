"""
Visual Mapping Module
Handles data-driven visual properties for graph visualization.
"""

import math
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MappingType(Enum):
    """Types of visual mappings."""
    LINEAR = "linear"
    LOGARITHMIC = "logarithmic"
    CATEGORICAL = "categorical"
    ORDINAL = "ordinal"


class ColorScheme(Enum):
    """Available color schemes."""
    VIRIDIS = "viridis"
    PLASMA = "plasma"
    INFERNO = "inferno"
    MAGMA = "magma"
    BLUES = "blues"
    GREENS = "greens"
    REDS = "reds"
    PURPLES = "purples"
    ORANGES = "oranges"
    GRAYS = "grays"


@dataclass
class MappingConfig:
    """Configuration for a visual mapping."""
    attribute: str
    mapping_type: MappingType
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    categories: Optional[List[str]] = None
    color_scheme: ColorScheme = ColorScheme.VIRIDIS
    custom_colors: Optional[List[str]] = None


class VisualMapper:
    """
    Handles data-driven visual mapping for graph elements.
    Implements the Data-driven Visualization functionality from the specification.
    """

    def __init__(self):
        """Initialize the visual mapper."""
        self.node_mappings: Dict[str, MappingConfig] = {}
        self.edge_mappings: Dict[str, MappingConfig] = {}
        self.color_palettes = self._initialize_color_palettes()

        logger.info("VisualMapper initialized")

    def _initialize_color_palettes(self) -> Dict[ColorScheme, List[str]]:
        """Initialize color palettes for different schemes."""
        return {
            ColorScheme.VIRIDIS: [
                "#440154", "#482878", "#3E4989", "#31688E", "#26828E",
                "#1F9E89", "#35B779", "#6DCD59", "#B4DE2C", "#FDE725"
            ],
            ColorScheme.PLASMA: [
                "#0D0887", "#46039F", "#7201A8", "#9C179E", "#BD3786",
                "#D8576B", "#ED7953", "#FA9E3B", "#FDC926", "#F0F921"
            ],
            ColorScheme.INFERNO: [
                "#000004", "#1B0C41", "#4A0C6B", "#781C6D", "#A52C60",
                "#CF4446", "#ED6925", "#FB9B06", "#F7D03C", "#FCFFA4"
            ],
            ColorScheme.MAGMA: [
                "#000004", "#180F3E", "#451077", "#721F81", "#9F2F7F",
                "#CD4071", "#F1605D", "#F98C5A", "#FBB954", "#FCFDBF"
            ],
            ColorScheme.BLUES: [
                "#F7FBFF", "#DEEBF7", "#C6DBEF", "#9ECAE1", "#6BAED6",
                "#4292C6", "#2171B5", "#08519C", "#08306B"
            ],
            ColorScheme.GREENS: [
                "#F7FCF5", "#E5F5E0", "#C7E9C0", "#A1D99B", "#74C476",
                "#41AB5D", "#238B45", "#006D2C", "#00441B"
            ],
            ColorScheme.REDS: [
                "#FFF5F0", "#FEE0D2", "#FCBBA1", "#FC9272", "#FB6A4A",
                "#EF4538", "#D7301F", "#B30000", "#7F0000"
            ],
            ColorScheme.PURPLES: [
                "#FCFBFD", "#EFEDF5", "#DADAEB", "#BCBDDC", "#9E9AC8",
                "#807DBA", "#6A51A3", "#54278F", "#3F007D"
            ],
            ColorScheme.ORANGES: [
                "#FFF5EB", "#FEE6CE", "#FDD0A2", "#FDAE6B", "#FD8D3C",
                "#F16913", "#D94801", "#A63603", "#7F2704"
            ],
            ColorScheme.GRAYS: [
                "#FFFFFF", "#F7F7F7", "#E6E6E6", "#D9D9D9", "#BDBDBD",
                "#969696", "#737373", "#525252", "#252525", "#000000"
            ]
        }

    def add_node_mapping(self, property_name: str, config: MappingConfig) -> None:
        """Add a visual mapping for node properties."""
        self.node_mappings[property_name] = config
        logger.info(f"Added node mapping for {property_name}")

    def add_edge_mapping(self, property_name: str, config: MappingConfig) -> None:
        """Add a visual mapping for edge properties."""
        self.edge_mappings[property_name] = config
        logger.info(f"Added edge mapping for {property_name}")

    def remove_node_mapping(self, property_name: str) -> None:
        """Remove a node visual mapping."""
        if property_name in self.node_mappings:
            del self.node_mappings[property_name]
            logger.info(f"Removed node mapping for {property_name}")

    def remove_edge_mapping(self, property_name: str) -> None:
        """Remove an edge visual mapping."""
        if property_name in self.edge_mappings:
            del self.edge_mappings[property_name]
            logger.info(f"Removed edge mapping for {property_name}")

    def get_node_color(self, node: Dict[str, Any], default_color: str = "#4A90E2") -> str:
        """Get the color for a node based on its attributes and mappings."""
        if "color" not in self.node_mappings:
            return default_color

        config = self.node_mappings["color"]
        value = node.get("attributes", {}).get(config.attribute)

        if value is None:
            return default_color

        return self._map_value_to_color(value, config)

    def get_node_size(self, node: Dict[str, Any], default_size: int = 20) -> int:
        """Get the size for a node based on its attributes and mappings."""
        if "size" not in self.node_mappings:
            return default_size

        config = self.node_mappings["size"]
        value = node.get("attributes", {}).get(config.attribute)

        if value is None:
            return default_size

        return self._map_value_to_size(value, config, default_size)

    def get_edge_color(self, edge: Dict[str, Any], default_color: str = "#666666") -> str:
        """Get the color for an edge based on its attributes and mappings."""
        if "color" not in self.edge_mappings:
            return default_color

        config = self.edge_mappings["color"]
        value = edge.get("attributes", {}).get(config.attribute)

        if value is None:
            return default_color

        return self._map_value_to_color(value, config)

    def get_edge_width(self, edge: Dict[str, Any], default_width: int = 2) -> int:
        """Get the width for an edge based on its attributes and mappings."""
        if "width" not in self.edge_mappings:
            return default_width

        config = self.edge_mappings["width"]
        value = edge.get("attributes", {}).get(config.attribute)

        if value is None:
            return default_width

        return self._map_value_to_width(value, config, default_width)

    def _map_value_to_color(self, value: Any, config: MappingConfig) -> str:
        """Map a value to a color based on the mapping configuration."""
        if config.mapping_type == MappingType.CATEGORICAL:
            return self._map_categorical_to_color(value, config)
        else:
            return self._map_numeric_to_color(value, config)

    def _map_categorical_to_color(self, value: Any, config: MappingConfig) -> str:
        """Map a categorical value to a color."""
        if config.categories is None:
            # Auto-generate categories if not provided
            return self._get_color_from_palette(0, config.color_scheme)

        try:
            index = config.categories.index(str(value))
            return self._get_color_from_palette(index, config.color_scheme)
        except ValueError:
            # Value not in categories, use default
            return self._get_color_from_palette(0, config.color_scheme)

    def _map_numeric_to_color(self, value: float, config: MappingConfig) -> str:
        """Map a numeric value to a color."""
        if not isinstance(value, (int, float)):
            return self._get_color_from_palette(0, config.color_scheme)

        # Normalize value
        if config.min_value is None or config.max_value is None:
            # Use 0-100 as default range
            normalized = max(0, min(1, value / 100))
        else:
            normalized = max(0, min(1, (value - config.min_value) / (config.max_value - config.min_value)))

        if config.mapping_type == MappingType.LOGARITHMIC:
            normalized = math.log(1 + normalized * 9) / math.log(10)

        # Map to color palette
        palette = self.color_palettes[config.color_scheme]
        index = int(normalized * (len(palette) - 1))
        return self._get_color_from_palette(index, config.color_scheme)

    def _map_value_to_size(self, value: float, config: MappingConfig, default_size: int) -> int:
        """Map a value to a size."""
        if not isinstance(value, (int, float)):
            return default_size

        # Normalize value
        if config.min_value is None or config.max_value is None:
            # Use 0-100 as default range
            normalized = max(0, min(1, value / 100))
        else:
            normalized = max(0, min(1, (value - config.min_value) / (config.max_value - config.min_value)))

        if config.mapping_type == MappingType.LOGARITHMIC:
            normalized = math.log(1 + normalized * 9) / math.log(10)

        # Map to size range (10-50 for nodes)
        min_size = 10
        max_size = 50
        size = min_size + normalized * (max_size - min_size)
        return int(size)

    def _map_value_to_width(self, value: float, config: MappingConfig, default_width: int) -> int:
        """Map a value to a width."""
        if not isinstance(value, (int, float)):
            return default_width

        # Normalize value
        if config.min_value is None or config.max_value is None:
            # Use 0-100 as default range
            normalized = max(0, min(1, value / 100))
        else:
            normalized = max(0, min(1, (value - config.min_value) / (config.max_value - config.min_value)))

        if config.mapping_type == MappingType.LOGARITHMIC:
            normalized = math.log(1 + normalized * 9) / math.log(10)

        # Map to width range (1-10 for edges)
        min_width = 1
        max_width = 10
        width = min_width + normalized * (max_width - min_width)
        return int(width)

    def _get_color_from_palette(self, index: int, color_scheme: ColorScheme) -> str:
        """Get a color from the specified palette."""
        palette = self.color_palettes[color_scheme]
        index = max(0, min(len(palette) - 1, index))
        return palette[index]

    def get_mapping_summary(self) -> Dict[str, Any]:
        """Get a summary of all current mappings."""
        return {
            "node_mappings": {
                prop: {
                    "attribute": config.attribute,
                    "type": config.mapping_type.value,
                    "color_scheme": config.color_scheme.value
                }
                for prop, config in self.node_mappings.items()
            },
            "edge_mappings": {
                prop: {
                    "attribute": config.attribute,
                    "type": config.mapping_type.value,
                    "color_scheme": config.color_scheme.value
                }
                for prop, config in self.edge_mappings.items()
            }
        }

    def clear_mappings(self) -> None:
        """Clear all visual mappings."""
        self.node_mappings.clear()
        self.edge_mappings.clear()
        logger.info("All visual mappings cleared")

    def export_mappings(self) -> Dict[str, Any]:
        """Export current mappings as a configuration."""
        return {
            "node_mappings": {
                prop: {
                    "attribute": config.attribute,
                    "mapping_type": config.mapping_type.value,
                    "min_value": config.min_value,
                    "max_value": config.max_value,
                    "categories": config.categories,
                    "color_scheme": config.color_scheme.value,
                    "custom_colors": config.custom_colors
                }
                for prop, config in self.node_mappings.items()
            },
            "edge_mappings": {
                prop: {
                    "attribute": config.attribute,
                    "mapping_type": config.mapping_type.value,
                    "min_value": config.min_value,
                    "max_value": config.max_value,
                    "categories": config.categories,
                    "color_scheme": config.color_scheme.value,
                    "custom_colors": config.custom_colors
                }
                for prop, config in self.edge_mappings.items()
            }
        }

    def import_mappings(self, config: Dict[str, Any]) -> None:
        """Import mappings from a configuration."""
        self.clear_mappings()

        # Import node mappings
        for prop, mapping_config in config.get("node_mappings", {}).items():
            config_obj = MappingConfig(
                attribute=mapping_config["attribute"],
                mapping_type=MappingType(mapping_config["mapping_type"]),
                min_value=mapping_config.get("min_value"),
                max_value=mapping_config.get("max_value"),
                categories=mapping_config.get("categories"),
                color_scheme=ColorScheme(mapping_config["color_scheme"]),
                custom_colors=mapping_config.get("custom_colors")
            )
            self.add_node_mapping(prop, config_obj)

        # Import edge mappings
        for prop, mapping_config in config.get("edge_mappings", {}).items():
            config_obj = MappingConfig(
                attribute=mapping_config["attribute"],
                mapping_type=MappingType(mapping_config["mapping_type"]),
                min_value=mapping_config.get("min_value"),
                max_value=mapping_config.get("max_value"),
                categories=mapping_config.get("categories"),
                color_scheme=ColorScheme(mapping_config["color_scheme"]),
                custom_colors=mapping_config.get("custom_colors")
            )
            self.add_edge_mapping(prop, config_obj)

        logger.info("Visual mappings imported from configuration")

    def apply_mappings(self, graph_data, mappings: Dict[str, MappingConfig]) -> None:
        """
        Apply visual mappings to graph data.
        
        Args:
            graph_data: Graph data to apply mappings to
            mappings: Dictionary of mappings to apply
        """
        for mapping_name, config in mappings.items():
            if 'node' in mapping_name:
                self.node_mappings[mapping_name] = config
            elif 'edge' in mapping_name:
                self.edge_mappings[mapping_name] = config
        
        logger.info(f"Applied {len(mappings)} visual mappings")

    def validate_mappings(self, mappings: Dict[str, MappingConfig]) -> bool:
        """
        Validate visual mappings configuration.
        
        Args:
            mappings: Dictionary of mappings to validate
            
        Returns:
            bool: True if all mappings are valid
        """
        try:
            for mapping_name, config in mappings.items():
                if not isinstance(config, dict):
                    return False
                    
                # Validate required fields
                required_fields = ['attribute', 'mapping_type']
                for field in required_fields:
                    if field not in config:
                        return False
                        
                # Validate mapping type
                valid_types = ['linear', 'categorical', 'logarithmic', 'discrete']
                if config['mapping_type'] not in valid_types:
                    return False
                    
            logger.info(f"Validated {len(mappings)} visual mappings")
            return True
        except Exception as e:
            logger.error(f"Error validating mappings: {e}")
            return False

# Alias for backward compatibility
VisualMappingEngine = VisualMapper
