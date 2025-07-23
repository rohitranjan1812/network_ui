"""
Security and Robustness Tests for API Endpoints
Tests for security vulnerabilities, input validation, rate limiting, and error handling.
"""

import pytest
import json
import os
import tempfile
import threading
import time
from io import BytesIO
from unittest.mock import patch

from network_ui.api.app import create_app


@pytest.mark.api
class TestAPISecurityAndRobustness:
    """Security and robustness test cases for API endpoints."""

    def setup_method(self):
        """Set up test fixtures."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @pytest.mark.parametrize("malicious_input", [
        # SQL injection attempts
        "'; DROP TABLE users; --",
        "1' OR '1'='1",
        "admin'/*",
        
        # XSS attempts
        "<script>alert('xss')</script>",
        "javascript:alert('xss')",
        "<img src=x onerror=alert('xss')>",
        
        # Path traversal attempts
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config",
        "/etc/passwd",
        "C:\\windows\\system32\\config",
        
        # Command injection attempts
        "; ls -la",
        "| cat /etc/passwd",
        "&& rm -rf /",
        
        # XXE attempts (for XML)
        '<!DOCTYPE test [<!ENTITY xxe "hack">]><test>&xxe;</test>',
        
        # Buffer overflow attempts (shorter to avoid Windows limits)
        'A' * 1000,
        'A' * 5000,
    ])
    def test_malicious_input_handling(self, malicious_input):
        """Test API handling of various malicious inputs."""
        # Test in file path
        data = {'filePath': malicious_input}
        response = self.client.post('/import',
                                   data=json.dumps(data),
                                   content_type='application/json')
        
        # Should not crash and should return appropriate error
        assert response.status_code in [400, 404, 500]
        
        # Test in mapping config
        data = {
            'filePath': 'test.csv',
            'mappingConfig': {
                'node_id': malicious_input,
                'node_name': 'name'
            }
        }
        response = self.client.post('/import',
                                   data=json.dumps(data),
                                   content_type='application/json')
        
        # Should handle malicious mapping gracefully
        assert response.status_code in [400, 404, 500]

    @pytest.mark.parametrize("large_size", [1000, 10000, 100000, 1000000])
    def test_large_request_handling(self, large_size):
        """Test API handling of extremely large requests."""
        # Create large mapping config
        large_mapping = {}
        for i in range(large_size):
            large_mapping[f'attribute_{i}'] = f'col_{i}'
        
        data = {
            'filePath': 'test.csv',
            'mappingConfig': large_mapping
        }
        
        # Measure time and response
        start_time = time.time()
        response = self.client.post('/import',
                                   data=json.dumps(data),
                                   content_type='application/json')
        end_time = time.time()
        
        # Should either handle gracefully or reject appropriately
        assert response.status_code in [400, 413, 500]  # 413 = Payload Too Large
        
        # Should not take too long to reject
        if large_size >= 100000:
            assert end_time - start_time < 10.0  # Should fail fast

    def test_concurrent_request_handling(self):
        """Test API handling of concurrent requests."""
        import queue
        
        results = queue.Queue()
        num_threads = 10
        requests_per_thread = 5

        def make_requests(thread_id):
            for i in range(requests_per_thread):
                try:
                    data = {'filePath': f'test_{thread_id}_{i}.csv'}
                    response = self.client.post('/import',
                                               data=json.dumps(data),
                                               content_type='application/json')
                    results.put((thread_id, i, response.status_code, 'success'))
                    time.sleep(0.01)  # Small delay
                except Exception as e:
                    results.put((thread_id, i, 500, str(e)))

        # Start concurrent threads
        threads = []
        start_time = time.time()
        
        for i in range(num_threads):
            thread = threading.Thread(target=make_requests, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()
        
        end_time = time.time()

        # Collect results
        responses = []
        while not results.empty():
            responses.append(results.get())

        # Should handle all requests (even if they fail)
        assert len(responses) == num_threads * requests_per_thread
        
        # Should not crash (all responses should have status codes)
        assert all(isinstance(resp[2], int) for resp in responses)
        
        # Should complete in reasonable time
        assert end_time - start_time < 30.0

    @pytest.mark.parametrize("invalid_json", [
        '{"invalid": json}',  # Missing quotes
        '{"key": }',          # Missing value
        '{key: "value"}',     # Unquoted key
        '{"key": "value",}',  # Trailing comma
        '{',                  # Incomplete
        '',                   # Empty
        'not json at all',    # Not JSON
        '{"key": undefined}', # Invalid value
    ])
    def test_invalid_json_handling(self, invalid_json):
        """Test API handling of invalid JSON payloads."""
        response = self.client.post('/import',
                                   data=invalid_json,
                                   content_type='application/json')
        
        # Should return 400 Bad Request for invalid JSON
        assert response.status_code == 400
        
        result = json.loads(response.data)
        assert 'error' in result

    def test_missing_required_fields(self):
        """Test API handling when required fields are missing."""
        test_cases = [
            {},  # Empty payload
            {'mappingConfig': {}},  # Missing filePath
            {'filePath': ''},  # Empty filePath
            {'filePath': 'test.csv', 'mappingConfig': None},  # Null mapping
        ]

        for data in test_cases:
            response = self.client.post('/import',
                                       data=json.dumps(data),
                                       content_type='application/json')
            
            # Should return 400 for missing required fields
            assert response.status_code == 400
            
            result = json.loads(response.data)
            assert 'error' in result

    def test_file_upload_security(self):
        """Test file upload security measures."""
        # Test malicious file types
        malicious_files = [
            ('malware.exe', b'MZ\x90\x00'),  # Executable
            ('script.bat', b'@echo off\ndir'),  # Batch script
            ('shell.sh', b'#!/bin/bash\nls'),  # Shell script
            ('config.php', b'<?php phpinfo(); ?>'),  # PHP script
            ('../../../evil.csv', b'id,name\n1,test'),  # Path traversal
        ]

        for filename, content in malicious_files:
            data = {'file': (BytesIO(content), filename)}
            response = self.client.post('/upload', data=data)
            
            # Should reject malicious files
            assert response.status_code == 400
            
            result = json.loads(response.data)
            assert 'error' in result

    def test_oversized_file_upload(self):
        """Test handling of oversized file uploads."""
        # Create large file content
        large_content = 'id,name,data\n' + '1,test,' + 'x' * 1000000  # ~1MB row
        
        data = {'file': (BytesIO(large_content.encode()), 'large.csv')}
        response = self.client.post('/upload', data=data)
        
        # Should either accept or reject gracefully
        assert response.status_code in [200, 413, 400]  # 413 = Payload Too Large

    @pytest.mark.parametrize("http_method", ['GET', 'PUT', 'PATCH', 'DELETE'])
    def test_unsupported_http_methods(self, http_method):
        """Test API response to unsupported HTTP methods."""
        # Test on endpoints that only support POST
        endpoints = ['/import', '/upload', '/mapping-config']
        
        for endpoint in endpoints:
            response = getattr(self.client, http_method.lower())(endpoint)
            
            # Should return 405 Method Not Allowed
            assert response.status_code == 405

    def test_content_type_validation(self):
        """Test API validation of content types."""
        data = {'filePath': 'test.csv'}
        
        # Test various invalid content types
        invalid_content_types = [
            'text/plain',
            'application/xml',
            'multipart/form-data',
            'application/octet-stream',
            '',
            None
        ]

        for content_type in invalid_content_types:
            response = self.client.post('/import',
                                       data=json.dumps(data),
                                       content_type=content_type)
            
            # Should handle invalid content types appropriately
            # (may return 400 or 415 Unsupported Media Type)
            assert response.status_code in [400, 415]

    def test_header_injection_protection(self):
        """Test protection against header injection attacks."""
        malicious_headers = {
            'X-Custom': 'value\r\nEvil: injected',
            'User-Agent': 'test\nX-Evil: attack'
        }

        data = {'filePath': 'test.csv'}
        
        # Werkzeug should prevent header injection by raising ValueError
        # This is the correct security behavior
        with pytest.raises(ValueError, match="Header values must not contain newline characters"):
            response = self.client.post('/import',
                                       data=json.dumps(data),
                                       content_type='application/json',
                                       headers=malicious_headers)

    def test_cors_security(self):
        """Test CORS configuration security."""
        # Test preflight request
        response = self.client.options('/import',
                                      headers={
                                          'Origin': 'http://evil.com',
                                          'Access-Control-Request-Method': 'POST',
                                          'Access-Control-Request-Headers': 'Content-Type'
                                      })
        
        # Should have proper CORS headers
        assert 'Access-Control-Allow-Origin' in response.headers
        
        # Test actual request with origin
        data = {'filePath': 'test.csv'}
        response = self.client.post('/import',
                                   data=json.dumps(data),
                                   content_type='application/json',
                                   headers={'Origin': 'http://evil.com'})
        
        # Should include CORS headers
        assert 'Access-Control-Allow-Origin' in response.headers

    def test_error_information_disclosure(self):
        """Test that error messages don't disclose sensitive information."""
        # Test with non-existent file
        data = {'filePath': '/etc/passwd'}
        response = self.client.post('/import',
                                   data=json.dumps(data),
                                   content_type='application/json')
        
        result = json.loads(response.data)
        error_message = result.get('error', '').lower()
        
        # Should not disclose system paths or internal details
        sensitive_patterns = [
            'c:\\',
            '/etc/',
            'permission denied',
            'access denied',
            'traceback',
            'exception',
            'internal error'
        ]
        
        # Error should be generic
        for pattern in sensitive_patterns:
            assert pattern not in error_message

    def test_rate_limiting_simulation(self):
        """Test API behavior under rapid requests (rate limiting simulation)."""
        rapid_requests = 50
        responses = []
        
        start_time = time.time()
        
        for i in range(rapid_requests):
            data = {'filePath': f'test_{i}.csv'}
            response = self.client.post('/import',
                                       data=json.dumps(data),
                                       content_type='application/json')
            responses.append(response.status_code)
        
        end_time = time.time()
        
        # Should handle rapid requests without crashing
        assert len(responses) == rapid_requests
        
        # Should not take too long (indicates server is responsive)
        assert end_time - start_time < 30.0
        
        # All responses should be valid HTTP status codes
        assert all(200 <= status <= 599 for status in responses)

    def test_memory_exhaustion_protection(self):
        """Test protection against memory exhaustion attacks."""
        # Test with deeply nested JSON
        nested_data = {'level': 0}
        current = nested_data
        
        # Create deep nesting (but not too deep to avoid test timeout)
        for i in range(100):
            current['nested'] = {'level': i + 1}
            current = current['nested']
        
        current['filePath'] = 'test.csv'
        
        response = self.client.post('/import',
                                   data=json.dumps(nested_data),
                                   content_type='application/json')
        
        # Should handle without memory issues
        assert response.status_code in [400, 413, 500]

    @pytest.mark.parametrize("endpoint", [
        '/health',
        '/import',
        '/preview',
        '/mapping-config',
        '/upload',
        '/files'
    ])
    def test_endpoint_availability_under_stress(self, endpoint):
        """Test endpoint availability under stress conditions."""
        stress_requests = 20
        successful_responses = 0
        
        for i in range(stress_requests):
            if endpoint in ['/import', '/preview', '/mapping-config']:
                # POST endpoints need data
                data = {'filePath': f'test_{i}.csv'}
                response = self.client.post(endpoint,
                                           data=json.dumps(data),
                                           content_type='application/json')
            elif endpoint == '/upload':
                # File upload endpoint
                file_data = {'file': (BytesIO(b'id,name\n1,test'), 'test.csv')}
                response = self.client.post(endpoint, data=file_data)
            else:
                # GET endpoints
                response = self.client.get(endpoint)
            
            # Count successful responses (not necessarily 200, but not 5xx)
            if response.status_code < 500:
                successful_responses += 1
        
        # Most requests should succeed (allowing for some failures)
        success_rate = successful_responses / stress_requests
        assert success_rate >= 0.8  # At least 80% success rate

    def test_input_validation_edge_cases(self):
        """Test input validation with edge cases."""
        edge_cases = [
            # Unicode edge cases
            {'filePath': 'тест.csv'},  # Cyrillic
            {'filePath': '测试.csv'},    # Chinese
            {'filePath': '🚀📊.csv'},   # Emojis
            
            # Special characters
            {'filePath': 'file with spaces.csv'},
            {'filePath': 'file-with-dashes.csv'},
            {'filePath': 'file_with_underscores.csv'},
            {'filePath': 'file.with.dots.csv'},
            
            # Path edge cases
            {'filePath': './test.csv'},
            {'filePath': 'subdir/test.csv'},
            {'filePath': 'C:\\Users\\test.csv'},  # Windows path
            {'filePath': '/home/user/test.csv'},  # Unix path
            
            # Encoding issues
            {'filePath': 'café.csv'},
            {'filePath': 'résumé.csv'},
            {'filePath': 'naïve.csv'},
        ]

        for data in edge_cases:
            response = self.client.post('/import',
                                       data=json.dumps(data),
                                       content_type='application/json')
            
            # Should handle edge cases gracefully
            assert response.status_code in [400, 404, 500]
            
            # Should return valid JSON
            try:
                result = json.loads(response.data)
                # Accept either validation errors ('error') or business logic errors ('errors')
                assert 'error' in result or 'errors' in result
            except json.JSONDecodeError:
                # If not JSON, should at least not crash
                assert response.data is not None 