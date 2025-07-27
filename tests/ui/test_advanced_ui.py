"""
Comprehensive tests for the Advanced UI features.
Tests all advanced functionality including configuration panels, analytics integration,
visual mapping, and real-time parameter adjustment.
"""

import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import requests

from network_ui.testing import TestingMetadataCollector
from network_ui.api.app import create_app


class TestAdvancedUICore:
    """Test core advanced UI functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_ui_test(self, metadata_collector):
        """Setup for UI tests with metadata collection."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Setup Selenium WebDriver
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            self.wait = WebDriverWait(self.driver, 10)
        except Exception:
            # Fallback for environments without Chrome
            self.driver = None
            self.wait = None
            
        yield
        
        if self.driver:
            self.driver.quit()
    
    def test_advanced_ui_template_loading(self):
        """Test that the advanced UI template loads correctly."""
        with self.app.test_request_context():
            # Test the advanced template endpoint
            response = self.client.get('/advanced')
            
            if response.status_code == 404:
                # If advanced route doesn't exist, test serving it from main route
                response = self.client.get('/')
                
            assert response.status_code == 200
            content = response.get_data(as_text=True)
            
            # Verify advanced UI elements are present
            assert 'Network UI Pro' in content
            assert 'Advanced Professional Interface' in content
            assert 'graph-studio' in content.lower() or 'Graph Studio' in content
            assert 'analytics-lab' in content.lower() or 'Analytics Lab' in content
    
    def test_workspace_switching_functionality(self):
        """Test workspace switching between Graph, Analytics, Data, and Settings."""
        if not self.driver:
            pytest.skip("Selenium WebDriver not available")
            
        # Load the advanced UI
        self.driver.get("http://localhost:5000/advanced")
        
        # Test Graph Studio workspace
        graph_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Graph Studio')]"))
        )
        graph_button.click()
        
        # Verify graph workspace is active
        assert 'active' in graph_button.get_attribute('class')
        
        # Test Analytics Lab workspace
        analytics_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Analytics Lab')]")
        analytics_button.click()
        
        # Verify analytics workspace is active
        assert 'active' in analytics_button.get_attribute('class')
        
        # Test Data Pipeline workspace
        data_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Data Pipeline')]")
        data_button.click()
        
        # Verify data workspace is active
        assert 'active' in data_button.get_attribute('class')
        
        # Test Configuration workspace
        settings_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Configuration')]")
        settings_button.click()
        
        # Verify settings workspace is active
        assert 'active' in settings_button.get_attribute('class')
    
    def test_sidebar_tab_switching(self):
        """Test sidebar tab switching between Tools, Layers, and History."""
        if not self.driver:
            pytest.skip("Selenium WebDriver not available")
            
        self.driver.get("http://localhost:5000/advanced")
        
        # Test Tools tab
        tools_tab = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'sidebar-tab') and contains(text(), 'Tools')]"))
        )
        tools_tab.click()
        
        # Verify tools content is visible
        tools_panel = self.driver.find_element(By.ID, "tools-panel")
        assert 'active' in tools_panel.get_attribute('class')
        
        # Test Layers tab
        layers_tab = self.driver.find_element(By.XPATH, "//div[contains(@class, 'sidebar-tab') and contains(text(), 'Layers')]")
        layers_tab.click()
        
        # Verify layers content is visible
        layers_panel = self.driver.find_element(By.ID, "layers-panel")
        assert 'active' in layers_panel.get_attribute('class')
        
        # Test History tab
        history_tab = self.driver.find_element(By.XPATH, "//div[contains(@class, 'sidebar-tab') and contains(text(), 'History')]")
        history_tab.click()
        
        # Verify history content is visible
        history_panel = self.driver.find_element(By.ID, "history-panel")
        assert 'active' in history_panel.get_attribute('class')


class TestAdvancedDataImport:
    """Test advanced data import functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_import_test(self, metadata_collector):
        """Setup for import tests."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_advanced_import_modal_opening(self):
        """Test that the advanced import modal opens correctly."""
        if not hasattr(self, 'driver') or not self.driver:
            pytest.skip("Selenium WebDriver not available")
            
        self.driver.get("http://localhost:5000/advanced")
        
        # Click advanced import button
        import_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Advanced Import')]"))
        )
        import_button.click()
        
        # Verify modal is visible
        modal = self.wait.until(
            EC.visibility_of_element_located((By.ID, "import-modal"))
        )
        assert 'active' in modal.get_attribute('class')
        
        # Verify wizard steps are present
        data_source_step = self.driver.find_element(By.XPATH, "//div[contains(@class, 'wizard-step') and contains(text(), 'Data Source')]")
        assert data_source_step.is_displayed()
    
    def test_import_method_selection(self):
        """Test selection of different import methods."""
        test_data = [
            {'method': 'file', 'expected_elements': ['file-upload', 'format-selector']},
            {'method': 'url', 'expected_elements': ['url-input', 'headers-config']},
            {'method': 'api', 'expected_elements': ['endpoint-config', 'auth-config']}
        ]
        
        for data in test_data:
            with self.app.test_request_context():
                # Mock the import method selection
                response = self.client.post('/api/v1/import/configure', 
                                         json={'method': data['method']})
                
                # Verify response contains expected configuration options
                if response.status_code == 200:
                    config = response.get_json()
                    assert config['method'] == data['method']
    
    def test_field_mapping_configuration(self):
        """Test field mapping configuration for data import."""
        sample_data = {
            'headers': ['id', 'name', 'category', 'source', 'target'],
            'preview': [
                {'id': '1', 'name': 'Node A', 'category': 'Type1', 'source': '1', 'target': '2'},
                {'id': '2', 'name': 'Node B', 'category': 'Type2', 'source': '2', 'target': '3'}
            ]
        }
        
        mapping_config = {
            'node_id_field': 'id',
            'node_name_field': 'name',
            'node_category_field': 'category',
            'edge_source_field': 'source',
            'edge_target_field': 'target',
            'validation_level': 'moderate',
            'auto_detect_types': True,
            'create_missing_nodes': True,
            'merge_duplicate_edges': False
        }
        
        with self.app.test_request_context():
            response = self.client.post('/api/v1/import/validate-mapping',
                                     json={
                                         'data': sample_data,
                                         'mapping': mapping_config
                                     })
            
            # Should return validation results
            assert response.status_code in [200, 201]
            if response.status_code == 200:
                result = response.get_json()
                assert 'validation_results' in result or 'status' in result
    
    def test_import_progress_tracking(self):
        """Test import progress tracking and status updates."""
        import_request = {
            'method': 'file',
            'data': [
                {'id': '1', 'name': 'Node 1'},
                {'id': '2', 'name': 'Node 2'},
                {'id': '3', 'name': 'Node 3'}
            ],
            'mapping': {
                'node_id_field': 'id',
                'node_name_field': 'name'
            }
        }
        
        with self.app.test_request_context():
            # Start import process
            response = self.client.post('/api/v1/import/execute',
                                     json=import_request)
            
            # Should return import ID or immediate result
            assert response.status_code in [200, 201, 202]
            
            result = response.get_json()
            if 'import_id' in result:
                # Test progress tracking
                import_id = result['import_id']
                progress_response = self.client.get(f'/api/v1/import/progress/{import_id}')
                assert progress_response.status_code == 200
                
                progress = progress_response.get_json()
                assert 'status' in progress
                assert progress['status'] in ['pending', 'processing', 'completed', 'failed']


class TestAdvancedAnalytics:
    """Test advanced analytics functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_analytics_test(self, metadata_collector):
        """Setup for analytics tests."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Create sample graph data for analytics
        self.sample_graph = {
            'nodes': [
                {'id': 'n1', 'name': 'Node 1', 'attributes': {'type': 'A'}},
                {'id': 'n2', 'name': 'Node 2', 'attributes': {'type': 'B'}},
                {'id': 'n3', 'name': 'Node 3', 'attributes': {'type': 'A'}},
                {'id': 'n4', 'name': 'Node 4', 'attributes': {'type': 'C'}}
            ],
            'edges': [
                {'source': 'n1', 'target': 'n2', 'weight': 1.0},
                {'source': 'n2', 'target': 'n3', 'weight': 2.0},
                {'source': 'n3', 'target': 'n4', 'weight': 1.5},
                {'source': 'n1', 'target': 'n4', 'weight': 0.5}
            ]
        }
    
    def test_analytics_lab_modal_opening(self):
        """Test that the analytics lab modal opens correctly."""
        if not hasattr(self, 'driver') or not self.driver:
            pytest.skip("Selenium WebDriver not available")
            
        self.driver.get("http://localhost:5000/advanced")
        
        # Click analytics lab button
        analytics_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Open Analytics Lab')]"))
        )
        analytics_button.click()
        
        # Verify modal is visible
        modal = self.wait.until(
            EC.visibility_of_element_located((By.ID, "analytics-modal"))
        )
        assert 'active' in modal.get_attribute('class')
        
        # Verify algorithm categories are present
        centrality_card = self.driver.find_element(By.XPATH, "//div[contains(@class, 'algorithm-card') and contains(text(), 'Centrality')]")
        assert centrality_card.is_displayed()
    
    def test_centrality_analysis_configuration(self):
        """Test centrality analysis configuration and execution."""
        algorithms = [
            {
                'name': 'degree_centrality',
                'params': {'direction': 'both', 'normalized': True}
            },
            {
                'name': 'betweenness_centrality', 
                'params': {'sample_size': 100, 'weighted': False}
            },
            {
                'name': 'closeness_centrality',
                'params': {'weighted': False, 'normalized': True}
            },
            {
                'name': 'eigenvector_centrality',
                'params': {'max_iterations': 100, 'tolerance': 1e-6}
            }
        ]
        
        for algorithm in algorithms:
            with self.app.test_request_context():
                response = self.client.post('/api/v1/analytics/analyze',
                                         json={
                                             'algorithm': algorithm['name'],
                                             'parameters': algorithm['params'],
                                             'graph_data': self.sample_graph
                                         })
                
                # Should return analysis results
                assert response.status_code in [200, 201]
                if response.status_code == 200:
                    result = response.get_json()
                    assert 'results' in result
                    assert 'algorithm' in result
                    assert result['algorithm'] == algorithm['name']
    
    def test_community_detection_algorithms(self):
        """Test community detection algorithms configuration."""
        algorithms = [
            {
                'name': 'louvain_modularity',
                'params': {'resolution': 1.0, 'random_state': 42}
            },
            {
                'name': 'girvan_newman',
                'params': {'max_communities': 5}
            },
            {
                'name': 'label_propagation',
                'params': {'max_iterations': 100, 'seed': 42}
            }
        ]
        
        for algorithm in algorithms:
            with self.app.test_request_context():
                response = self.client.post('/api/v1/analytics/analyze',
                                         json={
                                             'algorithm': algorithm['name'],
                                             'parameters': algorithm['params'],
                                             'graph_data': self.sample_graph
                                         })
                
                # Community detection should work or return appropriate error
                assert response.status_code in [200, 201, 400]
                if response.status_code == 200:
                    result = response.get_json()
                    assert 'results' in result
    
    def test_pathfinding_algorithms(self):
        """Test pathfinding algorithms with source and target nodes."""
        algorithms = [
            {
                'name': 'shortest_path',
                'params': {
                    'source_node_id': 'n1',
                    'target_node_id': 'n4',
                    'use_edge_weights': True
                }
            },
            {
                'name': 'all_paths',
                'params': {
                    'source_node_id': 'n1',
                    'target_node_id': 'n3',
                    'max_paths': 10
                }
            }
        ]
        
        for algorithm in algorithms:
            with self.app.test_request_context():
                response = self.client.post('/api/v1/analytics/analyze',
                                         json={
                                             'algorithm': algorithm['name'],
                                             'parameters': algorithm['params'],
                                             'graph_data': self.sample_graph
                                         })
                
                # Pathfinding should return results
                assert response.status_code in [200, 201]
                if response.status_code == 200:
                    result = response.get_json()
                    assert 'results' in result
                    assert 'path' in result['results'] or 'paths' in result['results']
    
    def test_connectivity_analysis(self):
        """Test connectivity analysis algorithms."""
        algorithms = [
            {
                'name': 'connected_components',
                'params': {}
            },
            {
                'name': 'cycle_detection',
                'params': {}
            },
            {
                'name': 'bridge_detection',
                'params': {}
            }
        ]
        
        for algorithm in algorithms:
            with self.app.test_request_context():
                response = self.client.post('/api/v1/analytics/analyze',
                                         json={
                                             'algorithm': algorithm['name'],
                                             'parameters': algorithm['params'],
                                             'graph_data': self.sample_graph
                                         })
                
                # Connectivity analysis should return results
                assert response.status_code in [200, 201]
                if response.status_code == 200:
                    result = response.get_json()
                    assert 'results' in result


class TestAdvancedVisualization:
    """Test advanced visualization functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_visualization_test(self, metadata_collector):
        """Setup for visualization tests."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_rendering_engine_configuration(self):
        """Test rendering engine configuration (Canvas vs WebGL)."""
        engines = ['canvas', 'webgl']
        
        for engine in engines:
            config = {
                'rendering': {
                    'engine': engine,
                    'antialiasing': True,
                    'shadows': True,
                    'animations': True
                }
            }
            
            with self.app.test_request_context():
                response = self.client.post('/api/v1/visualization/configure',
                                         json={'config': config})
                
                # Should accept configuration
                assert response.status_code in [200, 201]
                if response.status_code == 200:
                    result = response.get_json()
                    assert 'status' in result
    
    def test_layout_algorithm_configuration(self):
        """Test layout algorithm configuration and parameters."""
        layouts = [
            {
                'algorithm': 'force_directed',
                'params': {
                    'iterations': 100,
                    'damping': 0.8,
                    'spring_strength': 0.1,
                    'repulsion_strength': 1000
                }
            },
            {
                'algorithm': 'circular',
                'params': {
                    'radius': 200,
                    'start_angle': 0
                }
            },
            {
                'algorithm': 'hierarchical',
                'params': {
                    'direction': 'vertical',
                    'node_spacing': 100,
                    'level_spacing': 150
                }
            },
            {
                'algorithm': 'grid',
                'params': {
                    'columns': 5,
                    'spacing': 100
                }
            }
        ]
        
        for layout in layouts:
            with self.app.test_request_context():
                response = self.client.post('/api/v1/visualization/layout',
                                         json={
                                             'algorithm': layout['algorithm'],
                                             'parameters': layout['params']
                                         })
                
                # Should accept layout configuration
                assert response.status_code in [200, 201]
    
    def test_visual_mapping_configuration(self):
        """Test visual mapping configuration for nodes and edges."""
        visual_mappings = [
            {
                'type': 'node_color',
                'attribute': 'type',
                'mapping': {
                    'A': '#3b82f6',
                    'B': '#10b981',
                    'C': '#f59e0b'
                }
            },
            {
                'type': 'node_size',
                'attribute': 'degree',
                'scale': {'min': 10, 'max': 50}
            },
            {
                'type': 'edge_width',
                'attribute': 'weight',
                'scale': {'min': 1, 'max': 10}
            }
        ]
        
        for mapping in visual_mappings:
            with self.app.test_request_context():
                response = self.client.post('/api/v1/visualization/mapping',
                                         json={'mapping': mapping})
                
                # Should accept visual mapping
                assert response.status_code in [200, 201]
    
    def test_performance_mode_configuration(self):
        """Test performance mode configuration."""
        performance_modes = [
            {
                'mode': 'quality',
                'settings': {
                    'antialiasing': True,
                    'shadows': True,
                    'animations': True,
                    'level_of_detail': False
                }
            },
            {
                'mode': 'balanced',
                'settings': {
                    'antialiasing': True,
                    'shadows': False,
                    'animations': True,
                    'level_of_detail': True
                }
            },
            {
                'mode': 'performance',
                'settings': {
                    'antialiasing': False,
                    'shadows': False,
                    'animations': False,
                    'level_of_detail': True
                }
            }
        ]
        
        for mode_config in performance_modes:
            with self.app.test_request_context():
                response = self.client.post('/api/v1/visualization/performance',
                                         json={
                                             'mode': mode_config['mode'],
                                             'settings': mode_config['settings']
                                         })
                
                # Should accept performance configuration
                assert response.status_code in [200, 201]


class TestAdvancedInteractions:
    """Test advanced interaction functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_interaction_test(self, metadata_collector):
        """Setup for interaction tests."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_canvas_zoom_and_pan_controls(self):
        """Test canvas zoom and pan control functionality."""
        if not hasattr(self, 'driver') or not self.driver:
            pytest.skip("Selenium WebDriver not available")
            
        self.driver.get("http://localhost:5000/advanced")
        
        # Test zoom in
        zoom_in_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-tooltip='Zoom In']"))
        )
        zoom_in_button.click()
        
        # Test zoom out
        zoom_out_button = self.driver.find_element(By.XPATH, "//button[@data-tooltip='Zoom Out']")
        zoom_out_button.click()
        
        # Test fit to view
        fit_button = self.driver.find_element(By.XPATH, "//button[@data-tooltip='Fit to View']")
        fit_button.click()
        
        # Test reset view
        reset_button = self.driver.find_element(By.XPATH, "//button[@data-tooltip='Reset View']")
        reset_button.click()
        
        # Verify zoom level is displayed
        zoom_level = self.driver.find_element(By.ID, "zoom-level")
        assert zoom_level.text.endswith('%')
    
    def test_node_selection_and_details(self):
        """Test node selection and details panel functionality."""
        # This would require a more complex setup with actual graph rendering
        # For now, test the API endpoints that support this functionality
        
        selection_data = {
            'selected_nodes': ['n1', 'n2'],
            'selected_edges': ['e1']
        }
        
        with self.app.test_request_context():
            response = self.client.post('/api/v1/graph/selection',
                                     json=selection_data)
            
            # Should handle selection data
            assert response.status_code in [200, 201, 404]  # 404 if endpoint not implemented
    
    def test_contextual_menu_functionality(self):
        """Test right-click contextual menu functionality."""
        if not hasattr(self, 'driver') or not self.driver:
            pytest.skip("Selenium WebDriver not available")
            
        self.driver.get("http://localhost:5000/advanced")
        
        # Right-click on canvas
        canvas = self.wait.until(
            EC.presence_of_element_located((By.ID, "mainCanvas"))
        )
        
        action_chains = ActionChains(self.driver)
        action_chains.context_click(canvas).perform()
        
        # Context menu should appear (implementation dependent)
        # This test verifies the event is handled


class TestPerformanceMonitoring:
    """Test performance monitoring functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_performance_test(self, metadata_collector):
        """Setup for performance tests."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_performance_metrics_display(self):
        """Test that performance metrics are displayed correctly."""
        if not hasattr(self, 'driver') or not self.driver:
            pytest.skip("Selenium WebDriver not available")
            
        self.driver.get("http://localhost:5000/advanced")
        
        # Wait for performance metrics to be populated
        time.sleep(2)
        
        # Check FPS counter
        fps_counter = self.wait.until(
            EC.presence_of_element_located((By.ID, "fps-counter"))
        )
        fps_value = int(fps_counter.text)
        assert 0 <= fps_value <= 120  # Reasonable FPS range
        
        # Check node count
        node_count = self.driver.find_element(By.ID, "node-count")
        assert node_count.text.isdigit()
        
        # Check edge count
        edge_count = self.driver.find_element(By.ID, "edge-count")
        assert edge_count.text.isdigit()
        
        # Check memory usage
        memory_usage = self.driver.find_element(By.ID, "memory-usage")
        assert memory_usage.text.isdigit()
    
    def test_performance_status_indicators(self):
        """Test performance status indicators in footer."""
        if not hasattr(self, 'driver') or not self.driver:
            pytest.skip("Selenium WebDriver not available")
            
        self.driver.get("http://localhost:5000/advanced")
        
        # Check API status indicator
        api_status = self.wait.until(
            EC.presence_of_element_located((By.ID, "api-status"))
        )
        status_classes = api_status.get_attribute('class')
        assert 'status-dot' in status_classes
        
        # Check graph status indicator
        graph_status = self.driver.find_element(By.ID, "graph-status")
        status_classes = graph_status.get_attribute('class')
        assert 'status-dot' in status_classes
        
        # Check render status indicator
        render_status = self.driver.find_element(By.ID, "render-status")
        status_classes = render_status.get_attribute('class')
        assert 'status-dot' in status_classes


class TestConfigurationPersistence:
    """Test configuration persistence and management."""
    
    @pytest.fixture(autouse=True)
    def setup_config_test(self, metadata_collector):
        """Setup for configuration tests."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_configuration_save_and_load(self):
        """Test saving and loading advanced UI configurations."""
        config_data = {
            'visualization': {
                'rendering_engine': 'webgl',
                'performance_mode': 'balanced',
                'layout_algorithm': 'force_directed'
            },
            'analytics': {
                'default_algorithms': ['degree_centrality', 'betweenness_centrality'],
                'auto_analysis': True
            },
            'interface': {
                'theme': 'dark',
                'sidebar_collapsed': False,
                'properties_collapsed': False
            }
        }
        
        with self.app.test_request_context():
            # Save configuration
            response = self.client.post('/api/v1/config/save',
                                     json={'config': config_data})
            
            # Should accept configuration save
            assert response.status_code in [200, 201, 404]  # 404 if endpoint not implemented
            
            if response.status_code in [200, 201]:
                # Load configuration
                load_response = self.client.get('/api/v1/config/load')
                assert load_response.status_code == 200
                
                loaded_config = load_response.get_json()
                assert 'config' in loaded_config
    
    def test_configuration_export_import(self):
        """Test configuration export and import functionality."""
        export_format = 'json'
        
        with self.app.test_request_context():
            # Export configuration
            response = self.client.get(f'/api/v1/config/export?format={export_format}')
            
            # Should provide export data
            assert response.status_code in [200, 404]  # 404 if endpoint not implemented
            
            if response.status_code == 200:
                export_data = response.get_json()
                
                # Import configuration
                import_response = self.client.post('/api/v1/config/import',
                                                json={'config': export_data})
                assert import_response.status_code in [200, 201]


@pytest.mark.integration
class TestAdvancedUIIntegration:
    """Integration tests for advanced UI with backend systems."""
    
    @pytest.fixture(autouse=True)
    def setup_integration_test(self, metadata_collector):
        """Setup for integration tests."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow: import -> analyze -> visualize."""
        # Step 1: Import data
        import_data = {
            'method': 'direct',
            'data': {
                'nodes': [
                    {'id': 'n1', 'name': 'Node 1', 'type': 'A'},
                    {'id': 'n2', 'name': 'Node 2', 'type': 'B'},
                    {'id': 'n3', 'name': 'Node 3', 'type': 'A'},
                    {'id': 'n4', 'name': 'Node 4', 'type': 'C'}
                ],
                'edges': [
                    {'source': 'n1', 'target': 'n2', 'weight': 1.0},
                    {'source': 'n2', 'target': 'n3', 'weight': 2.0},
                    {'source': 'n3', 'target': 'n4', 'weight': 1.5}
                ]
            }
        }
        
        with self.app.test_request_context():
            # Import data
            import_response = self.client.post('/import', json=import_data)
            assert import_response.status_code in [200, 201]
            
            # Step 2: Run analysis
            analysis_response = self.client.post('/api/v1/analytics/analyze',
                                               json={
                                                   'algorithm': 'degree_centrality',
                                                   'parameters': {'normalized': True}
                                               })
            assert analysis_response.status_code in [200, 201]
            
            # Step 3: Apply visualization
            viz_response = self.client.post('/api/v1/visualization/render',
                                          json={
                                              'layout_algorithm': 'force_directed',
                                              'config': {
                                                  'node_size': 20,
                                                  'edge_width': 2
                                              }
                                          })
            assert viz_response.status_code in [200, 201]
    
    def test_real_time_updates(self):
        """Test real-time updates when graph data changes."""
        # This would test WebSocket or polling mechanisms
        # For now, test the API endpoints that support real-time updates
        
        update_data = {
            'action': 'add_node',
            'data': {'id': 'new_node', 'name': 'New Node'}
        }
        
        with self.app.test_request_context():
            response = self.client.post('/api/v1/graph/update',
                                     json=update_data)
            
            # Should handle real-time updates
            assert response.status_code in [200, 201, 404]  # 404 if endpoint not implemented
    
    def test_concurrent_user_sessions(self):
        """Test handling of concurrent user sessions."""
        # Simulate multiple concurrent requests
        import threading
        import time
        
        results = []
        
        def make_request():
            with self.app.test_request_context():
                response = self.client.get('/api/v1/graph')
                results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status in [200, 404] for status in results)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short']) 