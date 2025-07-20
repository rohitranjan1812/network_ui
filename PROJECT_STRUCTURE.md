# Network UI - Project Structure

This document outlines the refactored, modular project structure for the Network UI platform.

## 📁 Directory Structure

```
network_ui/
├── src/                          # Source code
│   └── network_ui/              # Main package
│       ├── __init__.py          # Package initialization
│       ├── core/                # Core functionality
│       │   ├── __init__.py
│       │   ├── models.py        # Data models
│       │   ├── validators.py    # Data validation
│       │   ├── mappers.py       # Data mapping
│       │   ├── transformers.py  # Graph transformation
│       │   └── importer.py      # Main importer
│       ├── api/                 # API layer
│       │   ├── __init__.py
│       │   └── app.py          # Flask API server
│       ├── utils/               # Utility functions
│       │   └── __init__.py
│       └── config/              # Configuration management
│           └── __init__.py
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── conftest.py             # Pytest configuration
│   ├── unit/                   # Unit tests
│   │   ├── test_models.py
│   │   ├── test_validators.py
│   │   ├── test_mappers.py
│   │   ├── test_transformers.py
│   │   └── test_importer.py
│   ├── integration/            # Integration tests
│   ├── functional/             # Functional tests
│   │   ├── demo.py
│   │   └── test_import.py
│   └── api/                    # API tests
├── data/                       # Data files
│   ├── samples/                # Sample data files
│   ├── test_data/              # Test data files
│   │   ├── test_data.csv
│   │   ├── test_edges.csv
│   │   ├── test_data_json.json
│   │   ├── test_data_xml.xml
│   │   ├── test_data_invalid.csv
│   │   ├── test_data_empty.csv
│   │   └── test_data_duplicates.csv
│   └── uploads/                # User uploaded files
├── docs/                       # Documentation
│   ├── api/                    # API documentation
│   └── user_guide/             # User guides
│       ├── README.md
│       └── TESTING.md
├── scripts/                    # Scripts and utilities
│   ├── deployment/             # Deployment scripts
│   │   ├── setup.py
│   │   └── requirements.txt
│   └── development/            # Development scripts
│       ├── run_tests.py
│       └── pytest.ini
├── specs/                      # YAML specifications
│   ├── 01_data_model_import.yaml
│   ├── 02_graph_engine.yaml
│   ├── 03_graph_analytics.yaml
│   ├── 04_graph_visualization.yaml
│   ├── 05_user_interface.yaml
│   ├── 06_data_persistence.yaml
│   ├── 07_export_engine.yaml
│   └── 08_main_integration.yaml
├── main.py                     # Main entry point
├── PROJECT_STRUCTURE.md        # This file
└── .gitignore                  # Git ignore file
```

## 🏗️ Architecture Overview

### Core Module (`src/network_ui/core/`)

The core module contains the fundamental functionality:

- **models.py**: Data structures for nodes, edges, graphs, and import configurations
- **validators.py**: Data validation and type detection
- **mappers.py**: Data mapping and transformation utilities
- **transformers.py**: Graph transformation and hierarchical structure creation
- **importer.py**: Main orchestration for data import process

### API Module (`src/network_ui/api/`)

The API module provides REST endpoints:

- **app.py**: Flask application with endpoints for data import, preview, and file management

### Utils Module (`src/network_ui/utils/`)

Utility functions and helpers (to be expanded as needed).

### Config Module (`src/network_ui/config/`)

Configuration management (to be expanded as needed).

## 🧪 Testing Structure

### Unit Tests (`tests/unit/`)

Tests for individual components in isolation:
- `test_models.py`: Data model tests
- `test_validators.py`: Validation logic tests
- `test_mappers.py`: Data mapping tests
- `test_transformers.py`: Graph transformation tests
- `test_importer.py`: Main importer tests

### Integration Tests (`tests/integration/`)

Tests for component interactions and workflows.

### Functional Tests (`tests/functional/`)

Tests for real-world usage scenarios:
- `demo.py`: Interactive demonstration
- `test_import.py`: End-to-end import testing

### API Tests (`tests/api/`)

Tests for REST API endpoints.

## 📊 Data Organization

### Sample Data (`data/samples/`)

Example data files for demonstration and documentation.

### Test Data (`data/test_data/`)

Data files specifically for testing:
- Valid data files for positive testing
- Invalid data files for error handling
- Edge case data for boundary testing

### Uploads (`data/uploads/`)

Temporary storage for user-uploaded files.

## 📚 Documentation

### API Documentation (`docs/api/`)

API endpoint documentation, schemas, and examples.

### User Guide (`docs/user_guide/`)

User-facing documentation:
- `README.md`: Project overview and getting started
- `TESTING.md`: Comprehensive testing guide

## 🛠️ Scripts and Utilities

### Deployment Scripts (`scripts/deployment/`)

- `setup.py`: Package installation script
- `requirements.txt`: Python dependencies

### Development Scripts (`scripts/development/`)

- `run_tests.py`: Comprehensive test runner
- `pytest.ini`: Pytest configuration

## 🎯 Key Benefits of This Structure

### 1. **Modularity**
- Clear separation of concerns
- Easy to extend and maintain
- Independent module testing

### 2. **Scalability**
- Ready for additional modules (analytics, visualization, etc.)
- Structured for team development
- Clear import paths

### 3. **Testability**
- Organized test structure
- Comprehensive coverage
- Easy to run specific test categories

### 4. **Maintainability**
- Clear file organization
- Consistent naming conventions
- Logical grouping of related functionality

### 5. **Deployment Ready**
- Proper package structure
- Configuration management
- Script automation

## 🚀 Usage Examples

### Running the Application

```bash
# Start API server
python main.py server

# Start server on specific port
python main.py server --port 8080

# Start server in debug mode
python main.py server --debug
```

### Running Tests

```bash
# Run all tests
python main.py test

# Run specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/
python -m pytest tests/functional/
```

### Running Demo

```bash
# Run interactive demo
python main.py demo
```

## 🔄 Migration Notes

### Import Changes

Old imports:
```python
from data_model_import import DataImporter
from data_model_import.models import Node, Edge
```

New imports:
```python
from network_ui.core import DataImporter
from network_ui.core.models import Node, Edge
```

### File Path Changes

- Core functionality moved to `src/network_ui/core/`
- API server moved to `src/network_ui/api/`
- Test files organized by category
- Data files moved to `data/` directory

### Configuration Updates

- Update `PYTHONPATH` to include `src/`
- Update import statements in existing code
- Update test file paths in CI/CD configurations

## 📈 Future Expansion

This structure is designed to accommodate future modules:

- **Graph Analytics**: `src/network_ui/analytics/`
- **Visualization**: `src/network_ui/visualization/`
- **User Interface**: `src/network_ui/ui/`
- **Data Persistence**: `src/network_ui/persistence/`
- **Export Engine**: `src/network_ui/export/`

Each new module can follow the same pattern with its own tests, documentation, and utilities. 