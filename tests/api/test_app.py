"""
Tests for the Flask API endpoints.
"""

import pytest
import json
import tempfile
import os
from unittest.mock import patch
from io import BytesIO

from network_ui.api.app import create_app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_csv_data():
    """Create sample CSV data for testing."""
    return """id,name,category,department,region,performance_score,employee_count,revenue
1,Marketing Team A,Marketing,Sales,North,85.5,12,1250000
2,Engineering Team B,Engineering,Technology,South,92.3,18,2100000
3,Sales Team C,Sales,Sales,East,78.9,8,980000"""


@pytest.fixture
def sample_json_data():
    """Create sample JSON data for testing."""
    return json.dumps([
        {"id": 1, "name": "Marketing Team A", "category": "Marketing"},
        {"id": 2, "name": "Engineering Team B", "category": "Engineering"},
        {"id": 3, "name": "Sales Team C", "category": "Sales"}
    ])


@pytest.mark.api
class TestHealthEndpoint:
    """Test the health check endpoint."""

    def test_health_endpoint(self, client):
        """Test that the health endpoint returns 200 OK."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data


@pytest.mark.api
class TestImportEndpoint:
    """Test the data import endpoint."""

    def test_import_csv_success(self, client, sample_csv_data):
        """Test successful CSV import."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv',
                                        delete=False) as f:
            f.write(sample_csv_data)
            temp_file_path = f.name

        try:
            mapping_config = {
                'node_id': 'id',
                'node_name': 'name',
                'node_attributes': ['category', 'department', 'region',
                                   'performance_score', 'employee_count',
                                   'revenue']
            }

            data = {
                'filePath': temp_file_path,
                'mappingConfig': mapping_config
            }

            response = client.post('/import',
                                  data=json.dumps(data),
                                  content_type='application/json')
            assert response.status_code == 200

            result = json.loads(response.data)
            assert 'success' in result
            assert result['success'] is True

        finally:
            os.unlink(temp_file_path)

    def test_import_missing_file(self, client):
        """Test import with missing file."""
        mapping_config = {
            'node_id': 'id',
            'node_name': 'name'
        }

        data = {
            'filePath': '/nonexistent/file.csv',
            'mappingConfig': mapping_config
        }

        response = client.post('/import',
                              data=json.dumps(data),
                              content_type='application/json')
        assert response.status_code == 400

        result = json.loads(response.data)
        assert 'errors' in result
        assert len(result['errors']) > 0

    def test_import_invalid_mapping(self, client, sample_csv_data):
        """Test import with invalid mapping configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv',
                                        delete=False) as f:
            f.write(sample_csv_data)
            temp_file_path = f.name

        try:
            # Invalid mapping - missing required fields
            mapping_config = {
                'node_attributes': ['category']
            }

            data = {
                'filePath': temp_file_path,
                'mappingConfig': mapping_config
            }

            response = client.post('/import',
                                  data=json.dumps(data),
                                  content_type='application/json')
            assert response.status_code == 400

            result = json.loads(response.data)
            assert 'errors' in result
            assert len(result['errors']) > 0

        finally:
            os.unlink(temp_file_path)


@pytest.mark.api
class TestPreviewEndpoint:
    """Test the data preview endpoint."""

    def test_preview_csv_success(self, client, sample_csv_data):
        """Test successful CSV preview."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv',
                                        delete=False) as f:
            f.write(sample_csv_data)
            temp_file_path = f.name

        try:
            data = {
                'filePath': temp_file_path,
                'maxRows': 5
            }

            response = client.post('/preview',
                                  data=json.dumps(data),
                                  content_type='application/json')
            assert response.status_code == 200

            result = json.loads(response.data)
            assert 'columns' in result
            assert 'data' in result
            assert 'total_rows' in result
            assert len(result['data']) <= 5

        finally:
            os.unlink(temp_file_path)

    def test_preview_missing_file(self, client):
        """Test preview with missing file."""
        data = {
            'filePath': '/nonexistent/file.csv',
            'maxRows': 5
        }

        response = client.post('/preview',
                              data=json.dumps(data),
                              content_type='application/json')
        assert response.status_code == 400

        result = json.loads(response.data)
        assert 'error' in result


@pytest.mark.api
class TestMappingEndpoint:
    """Test the mapping configuration endpoint."""

    def test_mapping_success(self, client, sample_csv_data):
        """Test successful mapping configuration generation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv',
                                        delete=False) as f:
            f.write(sample_csv_data)
            temp_file_path = f.name

        try:
            data = {
                'filePath': temp_file_path
            }

            response = client.post('/mapping-config',
                                  data=json.dumps(data),
                                  content_type='application/json')
            assert response.status_code == 200

            result = json.loads(response.data)
            assert 'columns' in result
            assert 'detected_types' in result
            assert 'suggestions' in result

        finally:
            os.unlink(temp_file_path)

    def test_mapping_missing_file(self, client):
        """Test mapping with missing file."""
        data = {
            'filePath': '/nonexistent/file.csv'
        }

        response = client.post('/mapping-config',
                              data=json.dumps(data),
                              content_type='application/json')
        assert response.status_code == 400

        result = json.loads(response.data)
        assert 'error' in result


@pytest.mark.api
class TestFileUploadEndpoint:
    """Test the file upload endpoint."""

    def test_upload_csv_success(self, client, sample_csv_data):
        """Test successful CSV file upload."""
        data = {
            'file': (BytesIO(sample_csv_data.encode()), 'test.csv')
        }

        response = client.post('/upload', data=data,
                              content_type='multipart/form-data')
        assert response.status_code == 200

        result = json.loads(response.data)
        assert 'success' in result
        assert result['success'] is True
        assert 'file_path' in result

    def test_upload_no_file(self, client):
        """Test upload without file."""
        response = client.post('/upload')
        assert response.status_code == 400

        result = json.loads(response.data)
        assert 'error' in result

    def test_upload_invalid_file_type(self, client):
        """Test upload with invalid file type."""
        data = {
            'file': (BytesIO(b'invalid content'), 'test.txt')
        }

        response = client.post('/upload', data=data,
                              content_type='multipart/form-data')
        assert response.status_code == 400

        result = json.loads(response.data)
        assert 'error' in result


@pytest.mark.api
class TestErrorHandling:
    """Test error handling."""

    def test_404_error(self, client):
        """Test 404 error handling."""
        response = client.get('/nonexistent')
        assert response.status_code == 404

    def test_500_error(self, client):
        """Test 500 error handling."""
        with patch('network_ui.api.app.DataImporter') as mock_importer:
            mock_importer.side_effect = Exception("Test error")
            response = client.get('/health')
            assert response.status_code == 500


@pytest.mark.api
class TestAPIConfiguration:
    """Test API configuration."""

    def test_cors_headers(self, client):
        """Test CORS headers are set."""
        response = client.get('/health')
        assert 'Access-Control-Allow-Origin' in response.headers

    def test_content_type_headers(self, client):
        """Test content type headers."""
        response = client.get('/health')
        assert response.content_type == 'application/json'

    def test_app_configuration(self):
        """Test app configuration."""
        app = create_app()
        assert app.config['TESTING'] is False 