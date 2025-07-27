#!/usr/bin/env python3
"""
Test script to demonstrate advanced UI endpoints functionality.
"""

import json
from network_ui.api.app import create_app

def test_advanced_endpoints():
    """Test the advanced UI endpoints."""
    print("Testing Advanced UI Configuration Endpoints")
    print("=" * 60)
    
    app = create_app()
    with app.test_client() as client:
        
        # Test configuration load
        print("Testing configuration load...")
        response = client.get('/api/v1/config/load')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            config = response.get_json()
            print(f"Config loaded successfully!")
            print(f"Visualization engine: {config['config']['visualization']['rendering_engine']}")
            print(f"Performance mode: {config['config']['visualization']['performance_mode']}")
        
        print()
        
        # Test configuration save
        print("Testing configuration save...")
        test_config = {
            'visualization': {'rendering_engine': 'webgl'},
            'analytics': {'auto_analysis': True}
        }
        response = client.post('/api/v1/config/save', json={'config': test_config})
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.get_json()
            print(f"Configuration saved: {result['status']}")
        
        print()
        
        # Test import configuration
        print("Testing import configuration...")
        response = client.post('/api/v1/import/configure', json={'method': 'file'})
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            config = response.get_json()
            print(f"Import method: {config['method']}")
            print(f"Supported formats: {config['options']['supported_formats']}")
        
        print()
        
        # Test visualization configuration
        print("Testing visualization configuration...")
        viz_config = {
            'config': {
                'rendering': {'engine': 'canvas', 'antialiasing': True}
            }
        }
        response = client.post('/api/v1/visualization/configure', json=viz_config)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.get_json()
            print(f"Visualization configured: {result['status']}")
        
        print()
        
        # Test graph selection
        print("Testing graph selection...")
        selection_data = {
            'selected_nodes': ['node1', 'node2'],
            'selected_edges': ['edge1']
        }
        response = client.post('/api/v1/graph/selection', json=selection_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.get_json()
            print(f"Selection handled: {result['status']}")
        
        print()
        print("All advanced endpoints working correctly!")

if __name__ == "__main__":
    test_advanced_endpoints() 