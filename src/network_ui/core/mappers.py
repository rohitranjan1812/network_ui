"""
Data Mapping Module
Handles the mapping of data columns to graph elements and data transformation.
"""

import pandas as pd
from typing import Dict, List, Any, Tuple
from .validators import DataValidator

class DataMapper: 
    """Maps data columns to graph elements and handles data transformation."""

    def __init__(self): 
        self.validator = DataValidator()
        self.mapping_config = {}
        self.data_types = {}

    def set_mapping_config(self, mapping_config:   Dict[str, str]) -> None: 
        """
        Set the mapping configuration for data transformation.

        Args: 
            mapping_config:   Dictionary mapping data fields to graph elements
        """
        self.mapping_config = mapping_config

    def set_data_types(self, data_types:   Dict[str, str]) -> None: 
        """
        Set the data types for columns.

        Args: 
            data_types:   Dictionary mapping column names to data types
        """
        self.data_types = data_types

    def create_default_mapping(self, columns:   List[str]) -> Dict[str, str]: 
        """
        Create a default mapping configuration based on available columns.

        Args: 
            columns:   List of available column names

        Returns: 
            Dict[str, str]:  Default mapping configuration
        """
        default_mapping = {}

  # Try to find ID column
        id_candidates = ['id', 'ID', 'Id', 'node_id', 'nodeid', 'identifier']
        for candidate in id_candidates: 
            if candidate in columns: 
                default_mapping['node_id'] = candidate
                break

  # Try to find name column
        name_candidates = [
            'name',
            'Name',
            'NAME',
            'node_name',
            'nodename',
            'title',
            'Title']
        for candidate in name_candidates: 
            if candidate in columns: 
                default_mapping['node_name'] = candidate
                break

  # Always include node_id and node_name (even if empty)
        if 'node_id' not in default_mapping: 
            default_mapping['node_id'] = ''
        if 'node_name' not in default_mapping: 
            default_mapping['node_name'] = ''

  # Try to find source and target for edges
        source_candidates = [
            'source',
            'Source',
            'SOURCE',
            'from',
            'From',
            'FROM',
            'start',
            'Start']
        target_candidates = [
            'target',
            'Target',
            'TARGET',
            'to',
            'To',
            'TO',
            'end',
            'End']

        for candidate in source_candidates: 
            if candidate in columns: 
                default_mapping['edge_source'] = candidate
                break

        for candidate in target_candidates: 
            if candidate in columns: 
                default_mapping['edge_target'] = candidate
                break

  # Map remaining columns as attributes
        mapped_columns = set(default_mapping.values())
        for column in columns: 
            if column not in mapped_columns: 
                default_mapping[f'attribute_{column}'] = column

        return default_mapping

    def detect_data_types(self, data:   pd.DataFrame) -> Dict[str, str]: 
        """
        Automatically detect data types for all columns.

        Args: 
            data:   DataFrame containing the data

        Returns: 
            Dict[str, str]:  Dictionary mapping column names to detected data types
        """
        detected_types = {}

        for column in data.columns:  
            detected_type = self.validator.detect_data_type(data[column])
            detected_types[column] = detected_type

        return detected_types

    def transform_data_types(self, data:   pd.DataFrame) -> pd.DataFrame:  
        """
        Transform data to the specified data types.

        Args: 
            data:   DataFrame containing the data

        Returns: 
            pd.DataFrame:   DataFrame with transformed data types
        """
        transformed_data = data.copy()

        for column, data_type in self.data_types.items(): 
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
                    transformed_data[column] = transformed_data[column].astype(
                        str)

            except Exception as e: 
                print(
                    f"Warning:   Could not convert column '{column}' to {data_type}:  {e}")

        return transformed_data

    def _convert_to_boolean(self, data:   pd.Series) -> pd.Series:  
        """Convert data to boolean values."""
        bool_map = {
            'true':  True, 'false':  False,
            'yes':  True, 'no':  False,
            '1':  True, '0':  False,
            't':  True, '':  False,
            'y':  True, 'n':  False
        }
        converted = data.astype(str).str.lower().map(bool_map)
  # Keep as object type to match test expectations
        return converted.astype('object')

    def create_data_preview(self, data:   pd.DataFrame,
                            max_rows:   int = 10) -> Dict[str, Any]: 
        """
        Create a preview of the data for the UI.

        Args: 
            data:   DataFrame containing the data
            max_rows:   Maximum number of rows to include in preview

        Returns: 
            Dict[str, Any]:  Data preview information
        """
        preview_data = data.head(max_rows)

        preview = {
            'columns':  list(data.columns),
            'total_rows':  len(data),
            'preview_rows':  len(preview_data),
            'data':  preview_data.to_dict('records'),
            'column_info':  {}
        }

  # Add column information
        for column in data.columns:  
            preview['column_info'][column] = {
                'data_type':  self.validator.detect_data_type(data[column]),
                'unique_count':  data[column].nunique(),
                'missing_count':  data[column].isnull().sum(),
                'sample_values':  data[column].dropna().head(5).tolist()
            }

        return preview

    def validate_mapping(self, data:   pd.DataFrame) -> Tuple[bool, List[str]]: 
        """
        Validate the current mapping configuration.

        Args: 
            data:   DataFrame containing the data

        Returns: 
            Tuple[bool, List[str]]:  (is_valid, error_messages)
        """
        return self.validator.validate_mapping_config(
            self.mapping_config, list(data.columns))

    def get_mapping_suggestions(
            self, data:   pd.DataFrame) -> Dict[str, List[str]]: 
        """
        Get suggestions for mapping based on column names and data content.

        Args: 
            data:   DataFrame containing the data

        Returns: 
            Dict[str, List[str]]:  Mapping suggestions
        """
        suggestions:   Dict[str, List[str]] = {
            'node_id':  [],
            'node_name':  [],
            'edge_source':  [],
            'edge_target':  [],
            'node_attributes':  [],
            'edge_attributes':  []
        }

        for column in data.columns:  
            column_lower = column.lower()

  # ID suggestions
            if any(
                keyword in column_lower for keyword in [
                    'id',
                    'identifier',
                    'key']): 
                suggestions['node_id'].append(column)

  # Name suggestions
            if any(
                keyword in column_lower for keyword in [
                    'name',
                    'title',
                    'label']): 
                suggestions['node_name'].append(column)

  # Source suggestions
            if any(
                keyword in column_lower for keyword in [
                    'source',
                    'from',
                    'start']): 
                suggestions['edge_source'].append(column)

  # Target suggestions
            if any(
                keyword in column_lower for keyword in [
                    'target',
                    'to',
                    'end']): 
                suggestions['edge_target'].append(column)

  # Attribute suggestions (exclude already suggested columns)
            if not any(
                column in suggestions[key] for key in [
                    'node_id',
                    'node_name',
                    'edge_source',
                    'edge_target']): 
                suggestions['node_attributes'].append(column)
                suggestions['edge_attributes'].append(column)

        return suggestions

    def create_mapping_ui_config(self, data:   pd.DataFrame) -> Dict[str, Any]: 
        """
        Create configuration for the mapping UI.

        Args: 
            data:   DataFrame containing the data

        Returns: 
            Dict[str, Any]:  UI configuration
        """
        detected_types = self.detect_data_types(data)
        suggestions = self.get_mapping_suggestions(data)

        config = {
            'columns':  list(data.columns),
            'detected_types':  detected_types,
            'suggestions':  suggestions,
            'current_mapping':  self.mapping_config,
            'supported_types':  list(self.validator.SUPPORTED_TYPES.keys()),
            'data_preview':  self.create_data_preview(data)
        }

        return config
