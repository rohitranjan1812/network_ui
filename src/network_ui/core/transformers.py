"""
Data transformation module for converting imported data to graph format.
"""

import pandas as pd
import uuid
from typing import Dict, List, Tuple, Any, Set
from network_ui.core.models import Node, Edge, GraphData


class GraphTransformer:
    """Transforms imported data into graph format."""

    def __init__(self):
        """Initialize the transformer."""
        pass

    def transform_to_graph(self, data: pd.DataFrame,
                           mapping_config: Dict[str, str],
                           data_types: Dict[str, str]) -> GraphData:
        """
        Transform data into graph format based on mapping configuration.

        Args:
            data: DataFrame containing the data
            mapping_config: Dictionary mapping data fields to graph elements
            data_types: Dictionary mapping column names to expected data types

        Returns:
            GraphData: Transformed graph data
        """
        # Convert data types first
        data = self._transform_data_types(data, data_types)

        # Determine if this is edge data or node data
        if self._is_edge_data(mapping_config):
            return self._transform_edge_data(data, mapping_config)
        else:
            return self._transform_node_data(data, mapping_config)

    def _is_edge_data(self, mapping_config: Dict[str, str]) -> bool:
        """Check if mapping config is for edge data."""
        return any(field.startswith('edge_')
                  for field in mapping_config.keys())

    def _transform_data_types(self, data: pd.DataFrame,
                              data_types: Dict[str, str]) -> pd.DataFrame:
        """
        Transform data types according to the specified data types.

        Args:
            data: DataFrame containing the data
            data_types: Dictionary mapping column names to expected data types

        Returns:
            pd.DataFrame: DataFrame with converted data types
        """
        transformed_data = data.copy()

        for column, data_type in data_types.items():
            if column not in transformed_data.columns:
                continue

            try:
                if data_type == 'integer':
                    transformed_data[column] = pd.to_numeric(
                        transformed_data[column], errors='coerce').astype('Int64')
                elif data_type == 'float':
                    transformed_data[column] = pd.to_numeric(
                        transformed_data[column], errors='coerce')
                elif data_type == 'boolean':
                    transformed_data[column] = self._convert_to_boolean(
                        transformed_data[column])
                elif data_type in ['date', 'datetime']:
                    transformed_data[column] = pd.to_datetime(
                        transformed_data[column], errors='coerce')
                elif data_type == 'string':
                    transformed_data[column] = transformed_data[column].astype(str)

            except (ValueError, TypeError):
                # Keep original data if conversion fails
                pass

        return transformed_data

    def _convert_to_boolean(self, data: pd.Series) -> pd.Series:
        """Convert data to boolean values."""
        bool_map = {
            'true': True, 'false': False,
            'yes': True, 'no': False,
            '1': True, '0': False,
            't': True, 'f': False,
            'y': True, 'n': False
        }
        return data.astype(str).str.lower().map(bool_map)

    def _transform_node_data(self, data: pd.DataFrame,
                             mapping_config: Dict[str, str]) -> GraphData:
        """
        Transform node data into graph format.

        Args:
            data: DataFrame containing node data
            mapping_config: Dictionary mapping data fields to node elements

        Returns:
            GraphData: Graph data with nodes
        """
        graph_data = GraphData()

        for _, row in data.iterrows():
            # Extract node ID and name
            node_id = str(row[mapping_config['node_id']])
            node_name = str(row[mapping_config['node_name']])

            # Create node
            node = Node(id=node_id, name=node_name)

            # Add attributes
            for field, column in mapping_config.items():
                if field.startswith('attribute_') and column in row:
                    attr_name = field.replace('attribute_', '')
                    node.attributes[attr_name] = row[column]

            # Add KPIs
            for field, column in mapping_config.items():
                if field.startswith('kpi_') and column in row:
                    kpi_name = field.replace('kpi_', '')
                    node.kpis[kpi_name] = row[column]

            # Set level if specified
            level_col = mapping_config.get('node_level')
            if level_col and level_col in row:
                try:
                    node.level = int(row[level_col])
                except (ValueError, TypeError):
                    pass

            graph_data.add_node(node)

        return graph_data

    def _transform_edge_data(self, data: pd.DataFrame,
                             mapping_config: Dict[str, str]) -> GraphData:
        """
        Transform edge data into graph format.

        Args:
            data: DataFrame containing edge data
            mapping_config: Dictionary mapping data fields to edge elements

        Returns:
            GraphData: Graph data with edges
        """
        graph_data = GraphData()

        for _, row in data.iterrows():
            # Extract source and target
            source_id = str(row[mapping_config['edge_source']])
            target_id = str(row[mapping_config['edge_target']])

            # Create edge
            edge = Edge(
                id=str(uuid.uuid4()),
                source=source_id,
                target=target_id,
                relationship_type="default"
            )

            # Add attributes
            for field, column in mapping_config.items():
                if field.startswith('attribute_') and column in row:
                    attr_name = field.replace('attribute_', '')
                    edge.attributes[attr_name] = row[column]

            # Add KPI components if specified
            for field, column in mapping_config.items():
                if field.startswith('kpi_') and column in row:
                    kpi_name = field.replace('kpi_', '')
                    edge.kpi_components[kpi_name] = row[column]

            # Set relationship type if specified
            rel_type_col = mapping_config.get('edge_type')
            if rel_type_col and rel_type_col in row:
                edge.relationship_type = str(row[rel_type_col])

            # Set level if specified
            level_col = mapping_config.get('edge_level')
            if level_col and level_col in row:
                try:
                    edge.level = int(row[level_col])
                except (ValueError, TypeError):
                    pass

            # Set weight if specified
            weight_col = mapping_config.get('edge_weight')
            if weight_col and weight_col in row:
                try:
                    edge.weight = float(row[weight_col])
                except (ValueError, TypeError):
                    pass

            graph_data.add_edge(edge)

            # Create nodes if they don't exist
            if not graph_data.get_node_by_id(source_id):
                source_node = Node(id=source_id, name=source_id)
                graph_data.add_node(source_node)

            if not graph_data.get_node_by_id(target_id):
                target_node = Node(id=target_id, name=target_id)
                graph_data.add_node(target_node)

        return graph_data

    def create_hierarchical_structure(
            self, graph_data: GraphData) -> GraphData:
        """
        Create hierarchical structure based on node attributes and relationships.

        Args:
            graph_data: GraphData object to process

        Returns:
            GraphData: GraphData with hierarchical structure
        """
        # Group nodes by common attributes to create levels
        node_groups: Dict[str, List[Node]] = {}

        for node in graph_data.nodes:
            # Create a key based on common attributes
            group_key = self._create_group_key(node)

            if group_key not in node_groups:
                node_groups[group_key] = []
            node_groups[group_key].append(node)

        # Assign levels based on group size and relationships
        for group_key, nodes in node_groups.items():
            if len(nodes) > 1:
                # This is a group that should be at a higher level
                level = 2
                for node in nodes:
                    node.level = level

        return graph_data

    def _create_group_key(self, node: Node) -> str:
        """Create a grouping key based on node attributes."""
        # Use common attributes for grouping
        group_attrs = []

        for attr_name, attr_value in node.attributes.items():
            if attr_name.lower() in [
                'category',
                'type',
                'group',
                'department',
                'region'
            ]:
                group_attrs.append(f"{attr_name}:{attr_value}")

        return "|".join(sorted(group_attrs)) if group_attrs else "default"

    def validate_graph_structure(
            self, graph_data: GraphData) -> Tuple[bool, List[str]]:
        """
        Validate the graph structure for consistency.

        Args:
            graph_data: GraphData object to validate

        Returns:
            Tuple[bool, List[str]]: (is_valid, error_messages)
        """
        errors = []

        # Check for duplicate node IDs
        node_ids = [node.id for node in graph_data.nodes]
        duplicate_ids = [node_id for node_id in set(
            node_ids) if node_ids.count(node_id) > 1]
        if duplicate_ids:
            errors.append(f"Duplicate node IDs found: {duplicate_ids}")

        # Check for edges with non-existent nodes
        existing_node_ids = set(node_ids)
        for edge in graph_data.edges:
            if edge.source not in existing_node_ids:
                errors.append(
                    f"Edge {edge.id} references non-existent source node: "
                    f"{edge.source}")
            if edge.target not in existing_node_ids:
                errors.append(
                    f"Edge {edge.id} references non-existent target node: "
                    f"{edge.target}")

        # Check for self-loops (if not allowed)
        for edge in graph_data.edges:
            if edge.source == edge.target:
                errors.append(f"Self-loop detected in edge {edge.id}")

        # Check for duplicate edges
        edge_keys = [(edge.source, edge.target, edge.relationship_type)
                     for edge in graph_data.edges]
        duplicate_edges = [key for key in set(
            edge_keys) if edge_keys.count(key) > 1]
        if duplicate_edges:
            errors.append(f"Duplicate edges found: {duplicate_edges}")

        return len(errors) == 0, errors

    def create_graph_summary(self, graph_data: GraphData) -> Dict[str, Any]:
        """
        Create a summary of the graph structure.

        Args:
            graph_data: GraphData object to summarize

        Returns:
            Dict[str, Any]: Graph summary
        """
        summary: Dict[str, Any] = {
            'total_nodes': len(graph_data.nodes),
            'total_edges': len(graph_data.edges),
            'node_levels': {},
            'edge_types': {},
            'attribute_summary': {},
            'kpi_summary': {}
        }

        # Count nodes by level
        for node in graph_data.nodes:
            level = node.level
            if level not in summary['node_levels']:
                summary['node_levels'][level] = 0
            summary['node_levels'][level] += 1

        # Count edges by type
        for edge in graph_data.edges:
            edge_type = edge.relationship_type
            if edge_type not in summary['edge_types']:
                summary['edge_types'][edge_type] = 0
            summary['edge_types'][edge_type] += 1

        # Analyze attributes
        all_node_attrs: Set[str] = set()
        all_edge_attrs: Set[str] = set()

        for node in graph_data.nodes:
            all_node_attrs.update(node.attributes.keys())
            all_node_attrs.update(node.kpis.keys())

        for edge in graph_data.edges:
            all_edge_attrs.update(edge.attributes.keys())
            all_edge_attrs.update(edge.kpi_components.keys())

        summary['attribute_summary'] = {
            'node_attributes': list(all_node_attrs),
            'edge_attributes': list(all_edge_attrs)
        }

        return summary
