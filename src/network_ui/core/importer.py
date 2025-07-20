"""
Data Importer Module
Main module that orchestrates the entire data import process.
"""

import logging
import pandas as pd
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Any, Optional
from .models import GraphData, ImportConfig, ImportResult
from .validators import DataValidator
from .mappers import DataMapper
from .transformers import GraphTransformer


class DataImporter:
    """Main class for importing and processing data files."""

    def __init__(self):
        self.validator = DataValidator()
        self.mapper = DataMapper()
        self.transformer = GraphTransformer()
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the import process."""
        logger = logging.getLogger('DataImporter')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def import_data(self, config: ImportConfig) -> ImportResult:
        """
        Main method to import data from a file.

        Args:
            config: ImportConfig object containing import parameters

        Returns:
            ImportResult: Result of the import process
        """
        result = ImportResult(success=False)

        try:
            self.logger.info(
                f"Starting import process for file: {
                    config.file_path}")

            # Validate file format
            is_valid, error_msg = self.validator.validate_file_format(
                config.file_path)
            if not is_valid:
                result.errors.append(error_msg)
                return result

            # Read data file
            data = self._read_file(config)
            if data is None:
                result.errors.append("Failed to read data file")
                return result

            result.total_rows = len(data)
            self.logger.info(f"Successfully read {len(data)} rows from file")

            # Create default mapping if not provided
            if not config.mapping_config:
                config.mapping_config = self.mapper.create_default_mapping(
                    list(data.columns))
                self.logger.info("Created default mapping configuration")

            # Detect data types if not provided
            if not config.data_types:
                config.data_types = self.mapper.detect_data_types(data)
                self.logger.info("Detected data types automatically")

            # Set mapping configuration
            self.mapper.set_mapping_config(config.mapping_config)
            self.mapper.set_data_types(config.data_types)

            # Validate mapping and data
            mapping_valid, mapping_errors = self.mapper.validate_mapping(data)
            if not mapping_valid:
                result.errors.extend(mapping_errors)
                return result

            # Create validation report
            validation_report = self.validator.create_validation_report(
                data, config.mapping_config, config.data_types
            )

            if not validation_report['is_valid']:
                result.errors.extend(validation_report['errors'])
                return result

            result.warnings.extend(validation_report['warnings'])

            # Transform data to graph format
            graph_data = self.transformer.transform_to_graph(
                data, config.mapping_config, config.data_types
            )

            # Validate graph structure
            graph_valid, graph_errors = self.transformer.validate_graph_structure(
                graph_data)
            if not graph_valid:
                result.errors.extend(graph_errors)
                return result

            # Create hierarchical structure
            graph_data = self.transformer.create_hierarchical_structure(
                graph_data)

            # Create import log
            import_log = self._create_import_log(
                config, validation_report, graph_data)

            # Set result
            result.success = True
            result.graph_data = graph_data
            result.import_log = import_log
            result.processed_rows = len(data)

            self.logger.info(
                f"Import completed successfully. Created {len(graph_data.nodes)} nodes and {len(graph_data.edges)} edges")

        except Exception as e:
            error_msg = f"Import failed with error: {str(e)}"
            result.errors.append(error_msg)
            self.logger.error(error_msg, exc_info=True)

        return result

    def _read_file(self, config: ImportConfig) -> Optional[pd.DataFrame]:
        """
        Read data from file based on file format.

        Args:
            config: ImportConfig object

        Returns:
            Optional[pd.DataFrame]: DataFrame containing the data
        """
        file_path = config.file_path
        file_extension = file_path.lower().split('.')[-1]

        try:
            if file_extension == 'csv':
                return pd.read_csv(
                    file_path,
                    encoding=config.file_encoding,
                    delimiter=config.delimiter,
                    skiprows=config.skip_rows,
                    nrows=config.max_rows
                )

            elif file_extension == 'json':
                with open(file_path, 'r', encoding=config.file_encoding) as f:
                    json_data = json.load(f)

                # Handle different JSON structures
                if isinstance(json_data, list):
                    return pd.DataFrame(json_data)
                elif isinstance(json_data, dict):
                    # Try to find a data array in the JSON
                    for key in ['data', 'records', 'items', 'nodes', 'edges']:
                        if key in json_data and isinstance(
                                json_data[key], list):
                            return pd.DataFrame(json_data[key])
                    # If no data array found, try to convert the dict to a
                    # single row
                    return pd.DataFrame([json_data])
                else:
                    raise ValueError("Unsupported JSON structure")

            elif file_extension == 'xml':
                return self._read_xml_file(file_path, config)

            else:
                raise ValueError(f"Unsupported file format: {file_extension}")

        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {str(e)}")
            return None

    def _read_xml_file(
            self,
            file_path: str,
            config: ImportConfig) -> pd.DataFrame:
        """
        Read data from XML file.

        Args:
            file_path: Path to XML file
            config: ImportConfig object

        Returns:
            pd.DataFrame: DataFrame containing the data
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Try to find data elements
            data_elements: List[ET.Element] = []

            # Look for common element names
            for element_name in [
                'record',
                'item',
                'node',
                'edge',
                'row',
                    'entry']:
                elements = root.findall(f'.//{element_name}')
                if elements:
                    data_elements = elements
                    break

            # If no specific elements found, use all child elements of root
            if not data_elements:
                data_elements = list(root)

            # Convert elements to dictionaries
            records = []
            for element in data_elements:
                record = {}
                for child in element:
                    record[child.tag] = child.text
                # Also include attributes
                for attr_name, attr_value in element.attrib.items():
                    record[f"@{attr_name}"] = attr_value
                records.append(record)

            return pd.DataFrame(records)

        except Exception as e:
            self.logger.error(f"Error reading XML file {file_path}: {str(e)}")
            raise

    def _create_import_log(self, config: ImportConfig,
                           validation_report: Dict[str, Any],
                           graph_data: GraphData) -> str:
        """
        Create a detailed import log.

        Args:
            config: ImportConfig object
            validation_report: Validation report
            graph_data: GraphData object

        Returns:
            str: Import log
        """
        log_lines = [
            f"Data Import Log - {datetime.now().isoformat()}",
            f"File: {config.file_path}",
            f"Encoding: {config.file_encoding}",
            f"Total rows processed: {len(graph_data.nodes) + len(graph_data.edges)}",
            f"Nodes created: {len(graph_data.nodes)}",
            f"Edges created: {len(graph_data.edges)}",
            "",
            "Mapping Configuration:",
        ]

        for field, column in config.mapping_config.items():
            log_lines.append(f"  {field}: {column}")

        log_lines.extend([
            "",
            "Data Types:",
        ])

        for column, data_type in config.data_types.items():
            log_lines.append(f"  {column}: {data_type}")

        log_lines.extend([
            "",
            "Validation Summary:",
            f"  Errors: {len(validation_report['errors'])}",
            f"  Warnings: {len(validation_report['warnings'])}",
        ])

        if validation_report['errors']:
            log_lines.extend([
                "",
                "Errors:",
            ])
            for error in validation_report['errors']:
                log_lines.append(f"  - {error}")

        if validation_report['warnings']:
            log_lines.extend([
                "",
                "Warnings:",
            ])
            for warning in validation_report['warnings']:
                log_lines.append(f"  - {warning}")

        # Add graph summary
        graph_summary = self.transformer.create_graph_summary(graph_data)
        log_lines.extend([
            "",
            "Graph Summary:",
            f"  Node levels: {graph_summary['node_levels']}",
            f"  Edge types: {graph_summary['edge_types']}",
            f"  Node attributes: {graph_summary['attribute_summary']['node_attributes']}",
            f"  Edge attributes: {graph_summary['attribute_summary']['edge_attributes']}",
        ])

        return "\n".join(log_lines)

    def get_data_preview(self, file_path: str,
                         encoding: str = "utf-8",
                         max_rows: int = 10) -> Optional[Dict[str, Any]]:
        """
        Get a preview of the data without full import.

        Args:
            file_path: Path to the data file
            encoding: File encoding
            max_rows: Maximum number of rows to preview

        Returns:
            Optional[Dict[str, Any]]: Data preview information
        """
        try:
            # Create a temporary config for reading
            config = ImportConfig(
                file_path=file_path,
                file_encoding=encoding,
                max_rows=max_rows
            )

            # Read data
            data = self._read_file(config)
            if data is None:
                return None

            # Create preview
            preview = self.mapper.create_data_preview(data, max_rows)

            # Add mapping suggestions
            preview['mapping_suggestions'] = self.mapper.get_mapping_suggestions(
                data)

            # Add detected types
            preview['detected_types'] = self.mapper.detect_data_types(data)

            return preview

        except Exception as e:
            self.logger.error(f"Error creating data preview: {str(e)}")
            return None

    def create_mapping_ui_config(
            self, file_path: str, encoding: str = "utf-8") -> Optional[Dict[str, Any]]:
        """
        Create configuration for the mapping UI.

        Args:
            file_path: Path to the data file
            encoding: File encoding

        Returns:
            Optional[Dict[str, Any]]: UI configuration
        """
        try:
            # Create a temporary config for reading
            config = ImportConfig(
                file_path=file_path,
                file_encoding=encoding,
                max_rows=100  # Read more rows for better analysis
            )

            # Read data
            data = self._read_file(config)
            if data is None:
                return None

            # Create UI configuration
            ui_config = self.mapper.create_mapping_ui_config(data)

            return ui_config

        except Exception as e:
            self.logger.error(f"Error creating mapping UI config: {str(e)}")
            return None
