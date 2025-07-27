"""
Flask API server for the Network UI platform.

This module provides REST API endpoints for data import, analysis, and visualization.
"""

import os
import logging
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import numpy as np
from werkzeug.exceptions import BadRequest, UnsupportedMediaType

# Import from the new package structure
from ..core import DataImporter, ImportConfig
# Import Spec 2:   Graph Engine API
from .graph_engine import graph_engine_api

def convert_to_json_serializable(obj): 
    """Convert objects to JSON serializable format."""
    if isinstance(obj, np.integer): 
        return int(obj)
    elif isinstance(obj, np.floating): 
        return float(obj)
    elif isinstance(obj, np.ndarray): 
        return obj.tolist()
    elif hasattr(obj, 'to_dict'): 
        return obj.to_dict()
    elif isinstance(obj, dict): 
        return {key:   convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list): 
        return [convert_to_json_serializable(item) for item in obj]
    else: 
        return obj

def create_app(config=None): 
    """Create and configure the Flask application."""
    app = Flask(__name__)

  # Configure CORS
    CORS(app)

  # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

  # Configure upload folder
    UPLOAD_FOLDER = os.path.join(os.path.dirname(
        __file__), '..', '..', 'data', 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

  # Configure allowed file extensions
    ALLOWED_EXTENSIONS = {'csv', 'json', 'xml'}

    def allowed_file(filename): 
        """Check if file extension is allowed."""
        return '.' in filename and filename.rsplit(
            '.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @app.route('/')
    def index(): 
        """Serve the main web interface."""
        try: 
            ui_template_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'templates', 'index.html')
            if os.path.exists(ui_template_path): 
                return send_file(ui_template_path)
            else: 
                return jsonify({
                    'message':  'Network UI - Complete Platform',
                    'description':  'Graph visualization platform with full UI implementation',
                    'endpoints':  {
                        'health':  '/health',
                        'graph':  '/api/v1/graph',
                        'import':  '/import',
                        'files':  '/files',
                        'analytics':  '/api/v1/analytics'
                    },
                    'features':  [
                        'Interactive graph visualization',
                        'Data import wizard',
                        'Graph analytics',
                        'Visual styling',
                        'Details on demand'
                    ]
                })
        except Exception as e: 
            logger.error(f"Error serving web interface:   {str(e)}")
            return jsonify({'error':  'Failed to serve web interface'}), 500

    @app.route('/advanced', methods=['GET'])
    def serve_advanced_interface():
        """Serve the advanced professional web interface."""
        try:
            advanced_template_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'templates', 'advanced.html')
            if os.path.exists(advanced_template_path):
                return send_file(advanced_template_path)
            else:
                return jsonify({
                    'message': 'Network UI Pro - Advanced Interface',
                    'description': 'Professional-grade graph visualization with advanced analytics',
                    'features': [
                        'Multi-workspace environment',
                        'Advanced analytics laboratory',
                        'Real-time performance monitoring',
                        'Professional configuration panels',
                        'Advanced data import pipeline',
                        'Visual mapping system',
                        'High-performance rendering'
                    ],
                    'workspaces': {
                        'graph_studio': 'Interactive graph visualization and editing',
                        'analytics_lab': 'Advanced graph analysis and algorithms',
                        'data_pipeline': 'Comprehensive data import and processing',
                        'configuration': 'System-wide settings and preferences'
                    }
                }), 200
        except Exception as e:
            logger.error(f"Error serving advanced interface: {str(e)}")
            return jsonify({'error': 'Failed to serve advanced interface'}), 500

    @app.route('/health', methods=['GET'])
    def health_check(): 
        """Health check endpoint."""
        return jsonify({
            'status':  'healthy',
            'timestamp':  datetime.now().isoformat(),
            'version':  '1.0.0'
        })

    @app.route('/import', methods=['POST'])
    def import_data(): 
        """Import data from file with mapping configuration."""
        try: 
            data = request.get_json()

            if not data: 
                return jsonify({'error':  'No data provided'}), 400

            file_path = data.get('filePath')
            mapping_config = data.get('mappingConfig', {})
            data_types = data.get('dataTypes', {})
            file_encoding = data.get('fileEncoding', 'utf - 8')
            delimiter = data.get('delimiter', ',')
            skip_rows = data.get('skipRows', 0)
            max_rows = data.get('maxRows')

            if not file_path or file_path.strip() == '': 
                return jsonify({'error':  'File path is required'}), 400

  # Check for potentially dangerous path patterns
  # Allow absolute paths for testing but prevent directory traversal
            if '..' in file_path: 
                return jsonify({'error':  'Directory traversal not allowed'}), 400

  # Check if file exists (basic validation)
            if not os.path.exists(file_path): 
                return jsonify({'error':  'Invalid file path'}), 400

            if mapping_config is None: 
                return jsonify({'error':  'Mapping configuration is required'}), 400

  # Create import configuration
            config = ImportConfig(
                file_path=file_path,
                mapping_config=mapping_config,
                data_types=data_types,
                file_encoding=file_encoding,
                delimiter=delimiter,
                skip_rows=skip_rows,
                max_rows=max_rows
            )

  # Import data
            importer = DataImporter()
            result = importer.import_data(config)

  # Prepare response
            response = {
                'success':  result.success,
                'processedRows':  result.processed_rows,
                'totalRows':  result.total_rows,
                'nodesCreated':  len(
                    result.graph_data.nodes) if result.graph_data else 0,
                'edgesCreated':  len(
                    result.graph_data.edges) if result.graph_data else 0,
                'errors':  result.errors,
                'warnings':  result.warnings,
                'importLog':  result.import_log}

            if result.success and result.graph_data:  
  # Spec 2 Integration:   Add imported data to Graph Engine storage
                graph_engine_graph = graph_engine_api.get_graph()
                if graph_engine_graph: 
  # Add all imported nodes to Graph Engine
                    for node in result.graph_data.nodes:  
  # Check if node already exists to avoid duplicates
                        existing_node = graph_engine_graph.get_node_by_id(node.id)
                        if not existing_node: 
                            graph_engine_graph.add_node(node)

  # Add all imported edges to Graph Engine
                    for edge in result.graph_data.edges:  
  # Check if edge already exists to avoid duplicates
                        existing_edge = graph_engine_graph.get_edge_by_id(edge.id)
                        if not existing_edge: 
                            graph_engine_graph.add_edge(edge)

                    logger.info(f"Added {len(result.graph_data.nodes)} nodes and {len(result.graph_data.edges)} edges to Graph Engine")

  # Add graph summary
                response['graphSummary'] = {
                    'totalNodes':  len(result.graph_data.nodes),
                    'totalEdges':  len(result.graph_data.edges),
                    'nodeLevels':  {},
                    'edgeTypes':  {}
                }

  # Count node levels
                for node in result.graph_data.nodes:  
                    level = node.level
                    response['graphSummary']['nodeLevels'][level] = response['graphSummary']['nodeLevels'].get(
                        level, 0) + 1

  # Count edge types
                for edge in result.graph_data.edges:  
                    edge_type = edge.relationship_type
                    response['graphSummary']['edgeTypes'][edge_type] = response['graphSummary']['edgeTypes'].get(
                        edge_type, 0) + 1

  # Return appropriate status code based on success
            if result.success:  
                return jsonify(response)
            else: 
                return jsonify(response), 400

        except BadRequest as e: 
            logger.warning(f"Bad request in import endpoint:   {str(e)}")
            return jsonify({'error':  'Invalid JSON format or request structure'}), 400
        except UnsupportedMediaType as e: 
            logger.warning(f"Unsupported media type in import endpoint:   {str(e)}")
            return jsonify({'error':  'Content - Type must be application / json'}), 415
        except Exception as e: 
            logger.error(f"Error in import endpoint:   {str(e)}")
            return jsonify({'error':  str(e)}), 500

    @app.route('/preview', methods=['POST'])
    def preview_data(): 
        """Preview data from file without importing."""
        try: 
            data = request.get_json()

            if not data: 
                return jsonify({'error':  'No data provided'}), 400

            file_path = data.get('filePath')
            max_rows = data.get('maxRows', 10)

            if not file_path: 
                return jsonify({'error':  'File path is required'}), 400

  # Get data preview
            importer = DataImporter()
            preview = importer.get_data_preview(file_path, max_rows=max_rows)

            if preview is None: 
                return jsonify({'error':  'Failed to preview data'}), 400

  # Convert to JSON serializable format
            preview = convert_to_json_serializable(preview)
            return jsonify(preview)

        except BadRequest as e: 
            logger.warning(f"Bad request in preview endpoint:   {str(e)}")
            return jsonify({'error':  'Invalid JSON format or request structure'}), 400
        except Exception as e: 
            logger.error(f"Error in preview endpoint:   {str(e)}")
            return jsonify({'error':  str(e)}), 500

    @app.route('/mapping-config', methods=['POST'])
    def get_mapping_config(): 
        """Get mapping configuration for data file."""
        try: 
            data = request.get_json()

            if not data: 
                return jsonify({'error':  'No data provided'}), 400

            file_path = data.get('filePath')

            if not file_path: 
                return jsonify({'error':  'File path is required'}), 400

  # Get mapping UI configuration
            importer = DataImporter()
            ui_config = importer.create_mapping_ui_config(file_path)

            if ui_config is None: 
                return jsonify(
                    {'error':  'Failed to create mapping configuration'}), 400

  # Convert to JSON serializable format
            ui_config = convert_to_json_serializable(ui_config)
            return jsonify(ui_config)

        except BadRequest as e: 
            logger.warning(f"Bad request in mapping - config endpoint:   {str(e)}")
            return jsonify({'error':  'Invalid JSON format or request structure'}), 400
        except Exception as e: 
            logger.error(f"Error in mapping - config endpoint:   {str(e)}")
            return jsonify({'error':  str(e)}), 500

    @app.route('/upload', methods=['POST'])
    def upload_file(): 
        """Upload a file to the server."""
        try: 
            if 'file' not in request.files:  
                return jsonify({'error':  'No file provided'}), 400

            file = request.files['file']

            if file.filename == '': 
                return jsonify({'error':  'No file selected'}), 400

            if not allowed_file(file.filename): 
                return jsonify({'error':  'File type not allowed'}), 400

  # Check for path traversal attempts
            if '..' in file.filename or '/' in file.filename or '\\' in file.filename:  
                return jsonify({'error':  'Invalid filename - path traversal not allowed'}), 400

  # Secure filename and save
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"

            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            return jsonify({
                'success':  True,
                'filename':  filename,
                'filePath':  file_path,
                'message':  'File uploaded successfully'
            })

        except Exception as e: 
            logger.error(f"Error in upload endpoint:   {str(e)}")
            return jsonify({'error':  str(e)}), 500

    @app.route('/files', methods=['GET'])
    def list_files(): 
        """List uploaded files."""
        try: 
            files = []
            upload_folder = app.config['UPLOAD_FOLDER']

            if os.path.exists(upload_folder): 
                for filename in os.listdir(upload_folder): 
                    if allowed_file(filename): 
                        file_path = os.path.join(upload_folder, filename)
                        file_stat = os.stat(file_path)
                        files.append({
                            'filename':  filename,
                            'filePath':  file_path,
                            'size':  file_stat.st_size,
                            'modified':  datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                        })

            return jsonify({'files':  files})

        except Exception as e: 
            logger.error(f"Error in list files endpoint:   {str(e)}")
            return jsonify({'error':  str(e)}), 500

    @app.route('/files/<filename>', methods=['DELETE'])
    def delete_file(filename): 
        """Delete an uploaded file."""
        try: 
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            if os.path.exists(file_path): 
                os.remove(file_path)
                return jsonify({'success':  True,
                                'message':  'File deleted successfully'})
            else: 
                return jsonify({'error':  'File not found'}), 404

        except Exception as e: 
            logger.error(f"Error in delete file endpoint:   {str(e)}")
            return jsonify({'error':  str(e)}), 500

    @app.errorhandler(404)
    def not_found(error): 
        """Handle 404 errors."""
        return jsonify({'error':  'Endpoint not found'}), 404

    @app.errorhandler(500)
    def internal_error(error): 
        """Handle 500 errors."""
        logger.error(f"Internal server error:   {str(error)}")
        return jsonify({'error':  'Internal server error'}), 500

  # Register Spec 2:   Graph Engine API blueprint
    graph_blueprint = graph_engine_api.create_blueprint()
    app.register_blueprint(graph_blueprint)
    logger.info("Registered Graph Engine API endpoints")

  # Register Spec 3:   Analytics API blueprint
    try: 
        from ..analytics.api.analytics import AnalyticsAPI
        analytics_api = AnalyticsAPI()
        analytics_blueprint = analytics_api.create_blueprint()
        app.register_blueprint(analytics_blueprint)
        logger.info("Registered Analytics API endpoints")
    except ImportError as e: 
        logger.warning(f"Could not import analytics API:   {e}")
        logger.info("Analytics API endpoints not registered")

  # Register Spec 4:   Visualization API blueprint (with circular import protection)
    try: 
        from ..visualization.api.visualization import visualization_api
        visualization_blueprint = visualization_api.create_blueprint()
        app.register_blueprint(visualization_blueprint)
        logger.info("Registered Visualization API endpoints")
    except ImportError as e: 
        logger.warning(f"Could not import visualization API:   {e}")
        logger.info("Visualization API endpoints not registered")

    # Advanced UI Configuration Endpoints
    @app.route('/api/v1/config/save', methods=['POST'])
    def save_configuration():
        """Save advanced UI configuration."""
        try:
            config_data = request.get_json()
            if not config_data:
                return jsonify({'error': 'No configuration data provided'}), 400
            
            # In a production system, this would save to a database or file
            logger.info(f"Configuration saved: {config_data}")
            return jsonify({
                'status': 'success',
                'message': 'Configuration saved successfully',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            return jsonify({'error': 'Failed to save configuration'}), 500

    @app.route('/api/v1/config/load', methods=['GET'])
    def load_configuration():
        """Load advanced UI configuration."""
        try:
            # Default configuration
            default_config = {
                'visualization': {
                    'rendering_engine': 'canvas',
                    'performance_mode': 'balanced',
                    'layout_algorithm': 'force_directed'
                },
                'analytics': {
                    'default_algorithms': ['degree_centrality'],
                    'auto_analysis': False
                },
                'interface': {
                    'theme': 'dark',
                    'sidebar_collapsed': False,
                    'properties_collapsed': False
                }
            }
            
            return jsonify({
                'config': default_config,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return jsonify({'error': 'Failed to load configuration'}), 500

    @app.route('/api/v1/import/configure', methods=['POST'])
    def configure_import():
        """Configure import method and parameters."""
        try:
            config_data = request.get_json()
            method = config_data.get('method')
            
            if method == 'file':
                return jsonify({
                    'method': 'file',
                    'options': {
                        'supported_formats': ['csv', 'json', 'xml', 'xlsx'],
                        'encoding_options': ['utf-8', 'latin-1', 'cp1252'],
                        'delimiter_options': [',', ';', '\t', '|']
                    }
                })
            elif method == 'url':
                return jsonify({
                    'method': 'url',
                    'options': {
                        'authentication': ['none', 'basic', 'bearer', 'api_key'],
                        'headers': ['content-type', 'authorization'],
                        'timeout': 30
                    }
                })
            elif method == 'api':
                return jsonify({
                    'method': 'api',
                    'options': {
                        'protocols': ['rest', 'graphql'],
                        'authentication': ['none', 'oauth2', 'api_key'],
                        'rate_limiting': True
                    }
                })
            else:
                return jsonify({'error': 'Unsupported import method'}), 400
                
        except Exception as e:
            logger.error(f"Error configuring import: {str(e)}")
            return jsonify({'error': 'Failed to configure import'}), 500

    @app.route('/api/v1/visualization/configure', methods=['POST'])
    def configure_visualization():
        """Configure visualization rendering engine and settings."""
        try:
            config_data = request.get_json()
            config = config_data.get('config', {})
            
            logger.info(f"Visualization configured: {config}")
            return jsonify({
                'status': 'success',
                'message': 'Visualization configured successfully',
                'applied_config': config
            })
        except Exception as e:
            logger.error(f"Error configuring visualization: {str(e)}")
            return jsonify({'error': 'Failed to configure visualization'}), 500

    @app.route('/api/v1/graph/selection', methods=['POST'])
    def handle_selection():
        """Handle node/edge selection events."""
        try:
            selection_data = request.get_json()
            selected_nodes = selection_data.get('selected_nodes', [])
            selected_edges = selection_data.get('selected_edges', [])
            
            return jsonify({
                'status': 'success',
                'selection': {
                    'nodes': selected_nodes,
                    'edges': selected_edges
                }
            })
        except Exception as e:
            logger.error(f"Error handling selection: {str(e)}")
            return jsonify({'error': 'Failed to handle selection'}), 500

    return app

if __name__ == '__main__': 
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
