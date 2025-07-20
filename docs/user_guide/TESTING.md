# Comprehensive Testing Guide

This document provides a complete guide to testing the Data Model Import module.

## 🧪 Test Overview

The Data Model Import module includes comprehensive testing with the following coverage:

- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Functional Tests**: Real-world usage scenarios
- **API Tests**: REST API endpoint testing
- **Performance Tests**: Load and stress testing
- **Code Quality Tests**: Linting and type checking

## 📁 Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest configuration and fixtures
├── test_models.py           # Data model tests
├── test_validators.py       # Validation logic tests
├── test_mappers.py          # Data mapping tests
├── test_transformers.py     # Graph transformation tests
├── test_importer.py         # Main importer tests
└── test_api.py              # API endpoint tests (if created)

test_data.csv                # Sample node data
test_edges.csv               # Sample edge data
test_data_json.json          # Sample JSON data
test_data_xml.xml            # Sample XML data
test_data_invalid.csv        # Invalid data for error testing
test_data_empty.csv          # Empty data for edge case testing
test_data_duplicates.csv     # Duplicate data for validation testing
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run All Tests

```bash
python run_tests.py
```

### 3. Run Specific Test Categories

```bash
# Unit tests only
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=data_model_import --cov-report=html

# Specific test file
python -m pytest tests/test_models.py -v

# Specific test class
python -m pytest tests/test_models.py::TestNode -v

# Specific test method
python -m pytest tests/test_models.py::TestNode::test_node_creation -v
```

## 📊 Test Categories

### 1. Unit Tests

**Purpose**: Test individual components in isolation

**Files**:
- `test_models.py` - Data structure tests
- `test_validators.py` - Validation logic tests
- `test_mappers.py` - Data mapping tests
- `test_transformers.py` - Graph transformation tests

**Example**:
```python
def test_node_creation(self):
    """Test basic node creation."""
    node = Node(id="1", name="Test Node")
    
    assert node.id == "1"
    assert node.name == "Test Node"
    assert node.level == 1
```

### 2. Integration Tests

**Purpose**: Test complete workflows and component interactions

**Files**:
- `test_importer.py` - End-to-end import process tests

**Example**:
```python
def test_csv_import_success(self):
    """Test successful CSV import."""
    config = ImportConfig(
        file_path="test_data.csv",
        mapping_config={
            "node_id": "id",
            "node_name": "name"
        }
    )
    
    result = self.importer.import_data(config)
    
    assert result.success is True
    assert len(result.graph_data.nodes) == 8
```

### 3. Functional Tests

**Purpose**: Test real-world usage scenarios

**Files**:
- `demo.py` - Interactive demonstration and testing

**Example**:
```bash
python demo.py
```

### 4. API Tests

**Purpose**: Test REST API endpoints

**Files**:
- `test_api.py` - API endpoint tests

**Example**:
```python
def test_import_endpoint_success(self, client):
    """Test successful import via API."""
    response = client.post('/import', json={
        'filePath': 'test_data.csv',
        'mappingConfig': {
            'node_id': 'id',
            'node_name': 'name'
        }
    })
    
    assert response.status_code == 200
    assert response.json['success'] is True
```

## 🔧 Test Fixtures

The test suite includes comprehensive fixtures for common test scenarios:

### Data Fixtures

```python
@pytest.fixture
def sample_csv_data():
    """Create sample CSV data for testing."""
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['Team A', 'Team B', 'Team C', 'Team D', 'Team E'],
        'category': ['Marketing', 'Engineering', 'Sales', 'HR', 'Finance']
    })

@pytest.fixture
def sample_edge_data():
    """Create sample edge data for testing."""
    return pd.DataFrame({
        'source': [1, 2, 3, 4, 5],
        'target': [2, 3, 4, 5, 1],
        'relationship_type': ['collaborates', 'reports_to', 'mentors', 'partners', 'advises']
    })
```

### File Fixtures

```python
@pytest.fixture
def temp_csv_file(sample_csv_data):
    """Create a temporary CSV file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
        sample_csv_data.to_csv(f, index=False)
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    if os.path.exists(temp_file):
        os.unlink(temp_file)
```

### Configuration Fixtures

```python
@pytest.fixture
def basic_import_config():
    """Create a basic import configuration for testing."""
    return ImportConfig(
        file_path="test_data.csv",
        mapping_config={
            "node_id": "id",
            "node_name": "name",
            "attribute_category": "category"
        }
    )
```

## 🎯 Test Scenarios

### 1. Data Type Detection

Tests automatic detection of data types:

```python
def test_detect_data_type_string(self):
    """Test string data type detection."""
    data = pd.Series(['a', 'b', 'c', 'd'])
    detected_type = self.validator.detect_data_type(data)
    assert detected_type == 'string'

def test_detect_data_type_integer(self):
    """Test integer data type detection."""
    data = pd.Series([1, 2, 3, 4, 5])
    detected_type = self.validator.detect_data_type(data)
    assert detected_type == 'integer'
```

### 2. File Format Support

Tests different file formats:

```python
def test_csv_import_success(self):
    """Test successful CSV import."""
    # Test implementation

def test_json_import_success(self):
    """Test successful JSON import."""
    # Test implementation

def test_xml_import_success(self):
    """Test successful XML import."""
    # Test implementation
```

### 3. Error Handling

Tests error scenarios:

```python
def test_import_invalid_file_format(self):
    """Test import with invalid file format."""
    # Test implementation

def test_import_nonexistent_file(self):
    """Test import with non-existent file."""
    # Test implementation

def test_import_invalid_mapping(self):
    """Test import with invalid mapping configuration."""
    # Test implementation
```

### 4. Data Validation

Tests data validation logic:

```python
def test_validate_mapping_config_valid(self):
    """Test valid mapping configuration."""
    # Test implementation

def test_validate_mapping_config_missing_required(self):
    """Test mapping configuration with missing required fields."""
    # Test implementation

def test_validate_graph_structure_duplicate_nodes(self):
    """Test graph structure validation with duplicate node IDs."""
    # Test implementation
```

### 5. Graph Transformation

Tests graph transformation logic:

```python
def test_transform_to_graph_node_data(self):
    """Test graph transformation with node data."""
    # Test implementation

def test_transform_to_graph_edge_data(self):
    """Test graph transformation with edge data."""
    # Test implementation

def test_create_hierarchical_structure(self):
    """Test hierarchical structure creation."""
    # Test implementation
```

## 📈 Coverage Reporting

### Generate Coverage Report

```bash
# HTML coverage report
python -m pytest tests/ --cov=data_model_import --cov-report=html

# XML coverage report (for CI/CD)
python -m pytest tests/ --cov=data_model_import --cov-report=xml

# Terminal coverage report
python -m pytest tests/ --cov=data_model_import --cov-report=term-missing
```

### Coverage Targets

- **Overall Coverage**: > 90%
- **Critical Paths**: > 95%
- **Error Handling**: > 85%

## 🚨 Error Testing

### Invalid Data Scenarios

```python
def test_import_invalid_data_types(self):
    """Test import with invalid data types."""
    config = ImportConfig(
        file_path="test_data_invalid.csv",
        mapping_config={
            "node_id": "id",
            "node_name": "name",
            "kpi_performance": "performance_score"
        },
        data_types={
            "performance_score": "float"  # Will fail on invalid data
        }
    )
    
    result = self.importer.import_data(config)
    
    # Should still succeed but with warnings
    assert result.success is True
    assert len(result.warnings) > 0
```

### Edge Cases

```python
def test_import_empty_file(self):
    """Test import with empty file."""
    config = ImportConfig(
        file_path="test_data_empty.csv",
        mapping_config={
            "node_id": "id",
            "node_name": "name"
        }
    )
    
    result = self.importer.import_data(config)
    
    assert result.success is True
    assert result.processed_rows == 0
    assert len(result.graph_data.nodes) == 0
    assert len(result.warnings) > 0
```

## 🔄 Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python run_tests.py
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
      with:
        file: ./coverage.xml
```

## 🛠️ Test Maintenance

### Adding New Tests

1. **Follow Naming Convention**:
   - Test files: `test_*.py`
   - Test classes: `Test*`
   - Test methods: `test_*`

2. **Use Descriptive Names**:
   ```python
   def test_import_large_csv_file_with_complex_mapping(self):
       """Test import of large CSV file with complex mapping configuration."""
   ```

3. **Include Docstrings**:
   ```python
   def test_node_creation(self):
       """Test basic node creation with required fields."""
   ```

### Test Data Management

1. **Use Fixtures** for reusable test data
2. **Clean Up** temporary files
3. **Version Control** test data files
4. **Document** test data schemas

### Performance Testing

```python
@pytest.mark.slow
def test_import_large_dataset(self):
    """Test import of large dataset (performance test)."""
    # Create large dataset
    large_data = pd.DataFrame({
        'id': range(10000),
        'name': [f'Node {i}' for i in range(10000)]
    })
    
    # Test import performance
    start_time = time.time()
    result = self.importer.import_data(config)
    end_time = time.time()
    
    assert result.success is True
    assert end_time - start_time < 30  # Should complete within 30 seconds
```

## 📋 Test Checklist

Before running tests, ensure:

- [ ] All dependencies installed
- [ ] Test files present
- [ ] Environment variables set (if needed)
- [ ] Database connections configured (if needed)
- [ ] API endpoints accessible (for API tests)

## 🎯 Best Practices

1. **Test Isolation**: Each test should be independent
2. **Descriptive Names**: Use clear, descriptive test names
3. **Arrange-Act-Assert**: Follow AAA pattern
4. **Minimal Fixtures**: Keep fixtures focused and minimal
5. **Error Testing**: Test both success and failure scenarios
6. **Edge Cases**: Test boundary conditions and edge cases
7. **Performance**: Include performance tests for critical paths
8. **Documentation**: Document complex test scenarios

## 🚀 Running Tests in CI/CD

### Local CI Simulation

```bash
# Run all tests with coverage
python run_tests.py

# Run specific test categories
python -m pytest tests/ -v --tb=short --cov=data_model_import

# Run with parallel execution
python -m pytest tests/ -n auto
```

### Docker Testing

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python run_tests.py
```

This comprehensive testing guide ensures the Data Model Import module is thoroughly tested and ready for production use. 