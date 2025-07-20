# Data Model Import Module

A robust data import and parsing module that supports various file formats and transforms raw data into a standardized graph format for network visualization.

## Overview

This module implements the first YAML requirement specification (`01_data_model_import.yaml`) and provides:

- **File-based data import** for CSV, JSON, and XML formats
- **Data mapping UI** for mapping columns/keys to graph properties
- **Qualitative and quantitative data handling** with automatic type detection
- **Real-time data preview** with error highlighting
- **Comprehensive error handling and logging**
- **REST API endpoints** for integration with other modules

## Features

### Core Functionality

1. **Multi-format Support**
   - CSV files with configurable delimiters and encodings
   - JSON files with flexible structure handling
   - XML files with automatic element detection

2. **Intelligent Data Mapping**
   - Automatic column detection and suggestions
   - Support for node and edge data mapping
   - KPI and attribute mapping for hierarchical structures
   - Data type detection and validation

3. **Graph Transformation**
   - Converts data to standardized Node/Edge format
   - Supports hierarchical levels (Level 1, Level 2, etc.)
   - KPI components for performance metrics
   - Relationship types and weights for edges

4. **Validation & Error Handling**
   - Comprehensive data validation
   - Detailed error messages and warnings
   - Import logs for debugging
   - Graph structure validation

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. The module is ready to use!

## Usage

### Basic Import Example

```python
from data_model_import import DataImporter, ImportConfig

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
    print(f"Created {len(result.graph_data.nodes)} nodes")
    print(f"Created {len(result.graph_data.edges)} edges")
else:
    print("Import failed:", result.errors)
```

### API Usage

Start the Flask server:
```bash
python app.py
```

The server provides these endpoints:

- `POST /import` - Import data and transform to graph format
- `POST /preview` - Get data preview without full import
- `POST /mapping-config` - Get mapping configuration suggestions
- `POST /upload` - Upload a file to the server
- `GET /health` - Health check endpoint

### Example API Request

```bash
curl -X POST http://localhost:5000/import \
  -H "Content-Type: application/json" \
  -d '{
    "filePath": "test_data.csv",
    "mappingConfig": {
      "node_id": "id",
      "node_name": "name",
      "attribute_category": "category"
    },
    "dataTypes": {
      "id": "integer",
      "name": "string",
      "category": "string"
    }
  }'
```

## Data Structure

### Node Structure
```python
Node(
    id="unique_id",
    name="Node Name",
    level=1,  # Hierarchical level
    kpis={
        "performance": 85.5,
        "revenue": 1250000
    },
    attributes={
        "category": "Marketing",
        "department": "Sales"
    },
    position={"x": 0.0, "y": 0.0}
)
```

### Edge Structure
```python
Edge(
    id="edge_id",
    source="node1_id",
    target="node2_id",
    relationship_type="collaborates",
    level=1,
    kpi_components={
        "collaboration_score": 75.5
    },
    attributes={
        "frequency": "weekly"
    },
    weight=0.8
)
```

## File Formats

### CSV Format
```csv
id,name,category,performance_score
1,Team A,Marketing,85.5
2,Team B,Engineering,92.3
```

### JSON Format
```json
[
  {
    "id": 1,
    "name": "Team A",
    "category": "Marketing",
    "performance_score": 85.5
  }
]
```

### XML Format
```xml
<data>
  <record>
    <id>1</id>
    <name>Team A</name>
    <category>Marketing</category>
    <performance_score>85.5</performance_score>
  </record>
</data>
```

## Mapping Configuration

### Node Mapping
- `node_id` - Unique identifier for the node
- `node_name` - Display name for the node
- `node_level` - Hierarchical level (optional)
- `attribute_*` - Node attributes
- `kpi_*` - Key Performance Indicators

### Edge Mapping
- `edge_source` - Source node ID
- `edge_target` - Target node ID
- `edge_type` - Relationship type
- `edge_weight` - Edge weight
- `edge_level` - Hierarchical level
- `attribute_*` - Edge attributes
- `kpi_*` - KPI components

## Data Types

Supported data types:
- `string` - Text data
- `integer` - Whole numbers
- `float` - Decimal numbers
- `boolean` - True/False values
- `date` - Date values
- `datetime` - Date and time values

## Testing

Run the test suite:
```bash
python test_import.py
```

This will test:
- Data preview functionality
- Mapping UI configuration
- Node data import
- Edge data import

## Project Structure

```
network_ui/
├── data_model_import/
│   ├── __init__.py          # Package initialization
│   ├── models.py            # Data models (Node, Edge, GraphData)
│   ├── validators.py        # Data validation and type detection
│   ├── mappers.py           # Data mapping and transformation
│   ├── transformers.py      # Graph transformation logic
│   └── importer.py          # Main import orchestration
├── app.py                   # Flask API server
├── requirements.txt         # Python dependencies
├── test_import.py           # Test suite
├── test_data.csv            # Sample node data
├── test_edges.csv           # Sample edge data
└── README.md               # This file
```

## API Documentation

### POST /import
Import data from file and transform to graph format.

**Request Body:**
```json
{
  "filePath": "path/to/file.csv",
  "mappingConfig": {
    "node_id": "id_column",
    "node_name": "name_column"
  },
  "dataTypes": {
    "id_column": "integer",
    "name_column": "string"
  },
  "encoding": "utf-8",
  "delimiter": ",",
  "skipRows": 0,
  "maxRows": null
}
```

**Response:**
```json
{
  "success": true,
  "processedRows": 8,
  "totalRows": 8,
  "errors": [],
  "warnings": [],
  "importLog": "...",
  "graphData": {
    "nodes": [...],
    "edges": [...],
    "metadata": {...}
  }
}
```

### POST /preview
Get data preview without full import.

**Request Body:**
```json
{
  "filePath": "path/to/file.csv",
  "encoding": "utf-8",
  "maxRows": 10
}
```

### POST /mapping-config
Get mapping configuration suggestions.

**Request Body:**
```json
{
  "filePath": "path/to/file.csv",
  "encoding": "utf-8"
}
```

## Error Handling

The module provides comprehensive error handling:

- **File format validation** - Checks supported formats
- **Data type validation** - Ensures data conforms to specified types
- **Mapping validation** - Validates column mappings
- **Graph structure validation** - Checks for consistency
- **Detailed error messages** - Provides specific error information
- **Import logs** - Tracks the entire import process

## Logging

The module includes detailed logging:
- Import process tracking
- Error and warning messages
- Data validation results
- Graph transformation details

## Future Enhancements

- Support for additional file formats (Excel, Parquet)
- Advanced data transformation rules
- Real-time data streaming
- Integration with external data sources
- Enhanced visualization preview

## Contributing

1. Follow the existing code structure
2. Add comprehensive tests for new features
3. Update documentation for API changes
4. Ensure all imports work correctly
5. Follow PEP 8 style guidelines

## License

This module is part of the Network UI project and follows the project's licensing terms. 