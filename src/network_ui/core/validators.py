"""
Data validation and type detection for the Network UI platform.
"""

import pandas as pd
from typing import Dict, List, Tuple, Any

class DataValidator: 
    """Validates and detects data types for imported data."""

    SUPPORTED_TYPES = {
        'string':  'Text data',
        'integer':  'Whole numbers',
        'float':  'Decimal numbers',
        'boolean':  'True / False values',
        'date':  'Date values (YYYY - MM - DD)',
        'datetime':  'Date and time values'
    }

    def __init__(self): 
        """Initialize the validator."""
        pass

    def detect_data_type(self, column_data:   pd.Series) -> str: 
        """
        Automatically detect the data type of a column.

        Args: 
            column_data:   Pandas Series containing the column data

        Returns: 
            str:   Detected data type
        """
  # Remove NaN values for type detection
        clean_data = column_data.dropna()

        if len(clean_data) == 0: 
            return 'string'  # Default for empty columns

  # Check for boolean type first
        if self._is_boolean_column(clean_data): 
            return 'boolean'

  # Check for datetime / date types first (before numeric to avoid timestamp detection)
        if self._is_datetime_column(clean_data): 
            return 'datetime'

        if self._is_date_column(clean_data): 
            return 'date'

  # Check for numeric types (after datetime to avoid timestamp false positives)
        if self._is_numeric_column(clean_data): 
            if self._is_integer_column(clean_data): 
                return 'integer'
            else: 
                return 'float'

  # Default to string
        return 'string'

    def _is_boolean_column(self, data:   pd.Series) -> bool: 
        """Check if column contains boolean values."""
        bool_values = {'true', 'false', 'yes', 'no', '1', '0', 't', '', 'y', 'n'}
        string_data = data.astype(str).str.lower()
        return all(val in bool_values for val in string_data.unique())

    def _is_datetime_column(self, data:   pd.Series) -> bool: 
        """Check if column contains datetime values."""
  # Check if already datetime type
        if pd.api.types.is_datetime64_any_dtype(data): 
            return True

  # Don't try to parse purely numeric data as datetime
        if pd.api.types.is_numeric_dtype(data): 
            return False

        try: 
  # First try with default parsing
            pd.to_datetime(data, errors='raise')
            return True
        except (ValueError, TypeError): 
            try: 
  # Try with ISO8601 format specifically with UTC timezone handling
                pd.to_datetime(data, errors='raise', format='ISO8601', utc=True)
                return True
            except (ValueError, TypeError): 
                try: 
  # Try with mixed format parsing
                    pd.to_datetime(data, errors='raise', format='mixed')
                    return True
                except (ValueError, TypeError): 
                    return False

    def _is_date_column(self, data:   pd.Series) -> bool: 
        """Check if column contains date values."""
        try: 
  # Try to parse as datetime first
            parsed_dates = pd.to_datetime(data, errors='coerce')
            if not all(pd.notna(parsed_dates)): 
                return False

  # Check if all values are dates (no time component)
  # Convert to string and check if they match date patterns
            date_strings = data.astype(str)
            date_patterns = [
                r'^\d{4}-\d{2}-\d{2}$',  # YYYY - MM - DD
                r'^\d{2}/\d{2}/\d{4}$',  # MM / DD / YYYY
                r'^\d{4}/\d{2}/\d{2}$',  # YYYY / MM / DD
            ]

            import re
            for pattern in date_patterns: 
                if all(re.match(pattern, date_str) for date_str in date_strings): 
                    return True

            return False
        except (ValueError, TypeError): 
            return False

    def _is_numeric_column(self, data:   pd.Series) -> bool: 
        """Check if column contains numeric values."""
        try: 
            pd.to_numeric(data, errors='raise')
            return True
        except (ValueError, TypeError): 
            return False

    def _is_integer_column(self, data:   pd.Series) -> bool: 
        """Check if column contains integer values."""
        try: 
            numeric_data = pd.to_numeric(data, errors='raise')
            return all(numeric_data == numeric_data.astype(int))
        except (ValueError, TypeError): 
            return False

    def validate_mapping_config(self,
                                mapping_config:   Dict[str, Any],
                                available_columns:   List[str]) -> Tuple[bool,
                                                                       List[str]]: 
        """
        Validate the mapping configuration against available columns.

        Args: 
            mapping_config:   Dictionary mapping data fields to graph elements
            available_columns:   List of available column names

        Returns: 
            Tuple[bool, List[str]]:  (is_valid, error_messages)
        """
        errors = []

  # Determine if this is edge data or node data
        is_edge_data = any(field.startswith('edge_')
                           for field in mapping_config.keys())

        if is_edge_data: 
  # For edge data, require edge_source and edge_target
            required_mappings = ['edge_source', 'edge_target']
        else: 
  # For node data, require only node_id (node_name is optional)
            required_mappings = ['node_id']

        for required in required_mappings: 
            if required not in mapping_config: 
                errors.append(f"Missing required mapping:   {required}")

  # Check if mapped columns exist in data
        for field, column in mapping_config.items(): 
            if isinstance(column, list): 
  # Handle list of columns (e.g., node_attributes)
                for col in column: 
                    if col not in available_columns: 
                        errors.append(f"Mapped column '{col}' found not in data")
            else: 
  # Handle single column
                if column not in available_columns: 
                    errors.append(f"Mapped column '{column}' found not in data")

  # Check for duplicate mappings (only for single column mappings)
        column_mappings = []
        for field, column in mapping_config.items(): 
            if isinstance(column, list): 
                column_mappings.extend(column)
            else: 
                column_mappings.append(column)

        duplicates = [col for col in set(column_mappings)
                      if column_mappings.count(col) > 1]
        if duplicates: 
            errors.append(f"Duplicate column mappings:   {duplicates}")

        return len(errors) == 0, errors

    def validate_data_types(self,
                            data:   pd.DataFrame,
                            data_types:   Dict[str, str]) -> Tuple[bool,
                                                                 List[str]]: 
        """
        Validate that data conforms to specified data types.

        Args: 
            data:   DataFrame containing the data
            data_types:   Dictionary mapping column names to expected data types

        Returns: 
            Tuple[bool, List[str]]:  (is_valid, error_messages)
        """
        errors = []

        for column, expected_type in data_types.items(): 
            if column not in data.columns:  
                errors.append(f"Column '{column}' found not in data")
                continue

  # Validate that the expected_type is supported
            if expected_type not in self.SUPPORTED_TYPES:  
                errors.append(f"Unsupported data type '{expected_type}' for column '{column}'. "
                              f"Supported types:   {list(self.SUPPORTED_TYPES.keys())}")
                continue

            try: 
                if expected_type == 'integer': 
                    pd.to_numeric(data[column], errors='raise').astype(int)
                elif expected_type == 'float': 
                    pd.to_numeric(data[column], errors='raise')
                elif expected_type == 'boolean': 
                    self._convert_to_boolean(data[column])
                elif expected_type in ['date', 'datetime']: 
                    pd.to_datetime(data[column], errors='raise')
  # String type doesn't need validation

            except (ValueError, TypeError) as e: 
                errors.append(
                    f"Column '{column}' cannot be converted to {expected_type}:  "
                    f"{str(e)}")

        return len(errors) == 0, errors

    def _convert_to_boolean(self, data:   pd.Series) -> pd.Series:  
        """Convert data to boolean values."""
        bool_map = {
            'true':  True, 'false':  False,
            'yes':  True, 'no':  False,
            '1':  True, '0':  False,
            't':  True, '':  False,
            'y':  True, 'n':  False
        }
        return data.astype(str).str.lower().map(bool_map)

    def validate_file_format(self, file_path:   str) -> Tuple[bool, str]: 
        """
        Validate that the file format is supported.

        Args: 
            file_path:   Path to the file or file extension

        Returns: 
            Tuple[bool, str]:  (is_valid, error_message)
        """
        if file_path is None or file_path == '': 
            return False, "File path is empty or None"

        supported_extensions = ['.csv', '.json', '.xml']
        supported_formats = ['csv', 'json', 'xml']

  # Check if the input itself is a supported format (without dot)
        if file_path.lower() in supported_formats: 
            return True, ""

  # Handle case where file_path doesn't have an extension
        if '.' not in file_path: 
            return False, f"No file extension found. Supported formats:   {supported_formats}"

  # Extract the file extension
        file_extension = file_path.lower().split('.')[-1]

  # Check if it's a supported extension
        if f'.{file_extension}' in supported_extensions or file_extension in supported_formats: 
            return True, ""
        else: 
            return False, (f"Unsupported file format:   {file_extension}. "
                           f"Supported formats:   {supported_formats}")

        return True, ""

    def create_validation_report(self, data:   pd.DataFrame,
                                 mapping_config:   Dict[str, str],
                                 data_types:   Dict[str, str]) -> Dict[str, Any]: 
        """
        Create a comprehensive validation report.

        Args: 
            data:   DataFrame containing the data
            mapping_config:   Dictionary mapping data fields to graph elements
            data_types:   Dictionary mapping column names to expected data types

        Returns: 
            Dict[str, Any]:  Validation report
        """
        report:   Dict[str, Any] = {
            'is_valid':  True,
            'errors':  [],
            'warnings':  [],
            'data_quality':  {},
            'mapping_validation':  {},
            'recommendations':  [],
            'summary':  {},
            'type_detection':  {}
        }

  # Validate mapping configuration
        mapping_valid, mapping_errors = self.validate_mapping_config(
            mapping_config, list(data.columns)
        )
        report['errors'].extend(mapping_errors)

  # Validate data types
        type_valid, type_errors = self.validate_data_types(data, data_types)
        report['errors'].extend(type_errors)

  # Detect data types for all columns
        for column in data.columns:  
            detected_type = self.detect_data_type(data[column])
            report['type_detection'][column] = detected_type

  # Add warning if detected type differs from specified type
            if column in data_types and data_types[column] != detected_type: 
                report['warnings'].append(
                    f"Column '{column}':  detected type '{detected_type}' "
                    f"differs from specified type '{data_types[column]}'")

  # Create data quality metrics
        report['data_quality'] = {
            'total_rows':  len(data),
            'total_columns':  len(data.columns),
            'null_counts':  data.isnull().sum().to_dict(),
            'data_types':  report['type_detection'],
            'duplicate_counts':  {col:   data[col].duplicated().sum() for col in data.columns}
        }

  # Create mapping validation section
        report['mapping_validation'] = {
            'is_valid':  mapping_valid,
            'errors':  mapping_errors,
            'warnings':  []
        }

  # Create summary
        report['summary'] = {
            'total_rows':  len(data),
            'total_columns':  len(data.columns),
            'missing_values':  data.isnull().sum().to_dict(),
            'unique_values':  {col:   data[col].nunique() for col in data.columns}
        }

  # Generate recommendations and warnings
        if len(data) == 0: 
            report['recommendations'].append("Data file is empty")
            report['warnings'].append("Empty data file - no data to process")
        if len(data.columns) == 0: 
            report['recommendations'].append("Data file has no columns")
            report['warnings'].append("No columns found in data file")
        if len(report['errors']) > 0: 
            report['recommendations'].append("Fix validation errors before proceeding")
        if len(report['warnings']) > 0: 
            report['recommendations'].append("Review warnings for potential issues")

  # Set overall validity
        report['is_valid'] = len(report['errors']) == 0

        return report
