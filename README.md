# Network UI - Data Model Import Module

A comprehensive Python package for importing, validating, and transforming data into graph format for network visualization and analysis.

## Features

- **Multi-format Data Import**: Support for CSV, JSON, and XML files
- **Data Validation**: Automatic type detection and validation
- **Flexible Mapping**: Configurable field mapping for nodes and edges
- **Graph Transformation**: Convert data into standardized graph format
- **REST API**: Flask-based API for data import and preview
- **Comprehensive Testing**: Unit, integration, functional, and API tests

## Project Structure

```
network_ui/
├── src/network_ui/
│   ├── core/                 # Core data processing modules
│   │   ├── models.py         # Data models (Node, Edge, GraphData)
│   │   ├── importer.py       # Data import functionality
│   │   ├── validators.py     # Data validation and type detection
│   │   ├── mappers.py        # Data mapping and transformation
│   │   └── transformers.py   # Graph transformation utilities
│   ├── api/                  # REST API
│   │   └── app.py           # Flask application
│   └── config/              # Configuration management
├── tests/                   # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   ├── functional/         # Functional tests
│   └── api/               # API tests
├── specs/                  # Project specifications
└── requirements.txt        # Dependencies
```

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd network_ui
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Data Import

```python
from network_ui.core import DataImporter, ImportConfig

# Create importer
importer = DataImporter()

# Configure import
config = ImportConfig(
    file_path="data.csv",
    mapping_config={
        "node_id": "id",
        "node_name": "name",
        "attribute_category": "category",
        "kpi_performance": "performance_score"
    },
    data_types={
        "id": "integer",
        "name": "string",
        "category": "string",
        "performance_score": "float"
    }
)

# Import data
result = importer.import_data(config)

if result.success:
    print(f"Imported {len(result.graph_data.nodes)} nodes")
    print(f"Imported {len(result.graph_data.edges)} edges")
else:
    print("Import failed:", result.errors)
```

### Data Preview

```python
# Get data preview
preview = importer.get_data_preview("data.csv", max_rows=5)
print(f"Columns: {preview['columns']}")
print(f"Total rows: {preview['total_rows']}")
```

### REST API

Start the Flask API server:

```bash
python -m network_ui.api.app
```

Available endpoints:
- `GET /health` - Health check
- `POST /import` - Import data
- `POST /preview` - Preview data
- `POST /mapping-config` - Get mapping configuration
- `POST /upload` - Upload files

## Testing

Run the complete test suite:

```bash
python run_tests.py
```

Or run specific test categories:

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Functional tests
pytest tests/functional/ -v

# API tests
pytest tests/api/ -v
```

## Data Models

### Node
- `id`: Unique identifier
- `name`: Display name
- `level`: Hierarchical level
- `attributes`: Custom attributes
- `kpis`: Key performance indicators

### Edge
- `id`: Unique identifier
- `source`: Source node ID
- `target`: Target node ID
- `relationship_type`: Type of relationship
- `weight`: Edge weight
- `attributes`: Custom attributes
- `kpi_components`: KPI components

### GraphData
- `nodes`: List of nodes
- `edges`: List of edges
- `metadata`: Additional metadata

## Configuration

### ImportConfig
- `file_path`: Path to data file
- `file_encoding`: File encoding (default: utf-8)
- `mapping_config`: Field mapping configuration
- `data_types`: Expected data types
- `skip_rows`: Number of rows to skip

### Mapping Configuration

For node data:
```python
{
    "node_id": "id_column",
    "node_name": "name_column",
    "attribute_category": "category_column",
    "kpi_performance": "performance_column"
}
```

For edge data:
```python
{
    "edge_source": "source_column",
    "edge_target": "target_column",
    "edge_type": "type_column",
    "edge_weight": "weight_column"
}
```

## Supported Data Types

- `string`: Text data
- `integer`: Whole numbers
- `float`: Decimal numbers
- `boolean`: True/False values
- `date`: Date values (YYYY-MM-DD)
- `datetime`: Date and time values

## Development

### Code Quality

The project uses several tools for code quality:

- **Flake8**: Linting and style checking
- **MyPy**: Type checking
- **Pytest**: Testing framework
- **Coverage**: Test coverage reporting

Run code quality checks:

```bash
# Linting
flake8 src/ tests/

# Type checking
mypy src/

# Test coverage
pytest --cov=src/ tests/
```

### Adding New Features

1. Create feature branch
2. Implement feature with tests
3. Run test suite
4. Update documentation
5. Submit pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Support

For questions and support, please open an issue on GitHub. 