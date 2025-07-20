"""
Flask API server for the Network UI platform.

This module provides REST API endpoints for data import, analysis, and visualization.
"""

import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import numpy as np

# Import from the new package structure
from ..core import DataImporter, ImportConfig


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
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
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

    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })

    @app.route('/import', methods=['POST'])
    def import_data():
        """Import data from file with mapping configuration."""
        try:
            data = request.get_json()

            if not data:
                return jsonify({'error': 'No data provided'}), 400

            file_path = data.get('filePath')
            mapping_config = data.get('mappingConfig', {})
            data_types = data.get('dataTypes', {})
            file_encoding = data.get('fileEncoding', 'utf-8')
            delimiter = data.get('delimiter', ',')
            skip_rows = data.get('skipRows', 0)
            max_rows = data.get('maxRows')

            if not file_path:
                return jsonify({'error': 'File path is required'}), 400

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
                'success': result.success,
                'processedRows': result.processed_rows,
                'totalRows': result.total_rows,
                'nodesCreated': len(
                    result.graph_data.nodes) if result.graph_data else 0,
                'edgesCreated': len(
                    result.graph_data.edges) if result.graph_data else 0,
                'errors': result.errors,
                'warnings': result.warnings,
                'importLog': result.import_log}

            if result.success and result.graph_data:
                # Add graph summary
                response['graphSummary'] = {
                    'totalNodes': len(result.graph_data.nodes),
                    'totalEdges': len(result.graph_data.edges),
                    'nodeLevels': {},
                    'edgeTypes': {}
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

        except Exception as e:
            logger.error(f"Error in import endpoint: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/preview', methods=['POST'])
    def preview_data():
        """Preview data from file without importing."""
        try:
            data = request.get_json()

            if not data:
                return jsonify({'error': 'No data provided'}), 400

            file_path = data.get('filePath')
            max_rows = data.get('maxRows', 10)

            if not file_path:
                return jsonify({'error': 'File path is required'}), 400

            # Get data preview
            importer = DataImporter()
            preview = importer.get_data_preview(file_path, max_rows=max_rows)

            if preview is None:
                return jsonify({'error': 'Failed to preview data'}), 400

            # Convert to JSON serializable format
            preview = convert_to_json_serializable(preview)
            return jsonify(preview)

        except Exception as e:
            logger.error(f"Error in preview endpoint: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/mapping-config', methods=['POST'])
    def get_mapping_config():
        """Get mapping configuration for data file."""
        try:
            data = request.get_json()

            if not data:
                return jsonify({'error': 'No data provided'}), 400

            file_path = data.get('filePath')

            if not file_path:
                return jsonify({'error': 'File path is required'}), 400

            # Get mapping UI configuration
            importer = DataImporter()
            ui_config = importer.create_mapping_ui_config(file_path)

            if ui_config is None:
                return jsonify(
                    {'error': 'Failed to create mapping configuration'}), 400

            # Convert to JSON serializable format
            ui_config = convert_to_json_serializable(ui_config)
            return jsonify(ui_config)

        except Exception as e:
            logger.error(f"Error in mapping-config endpoint: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/upload', methods=['POST'])
    def upload_file():
        """Upload a file to the server."""
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400

            file = request.files['file']

            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400

            if not allowed_file(file.filename):
                return jsonify({'error': 'File type not allowed'}), 400

            # Secure filename and save
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"

            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            return jsonify({
                'success': True,
                'filename': filename,
                'filePath': file_path,
                'message': 'File uploaded successfully'
            })

        except Exception as e:
            logger.error(f"Error in upload endpoint: {str(e)}")
            return jsonify({'error': str(e)}), 500

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
                            'filename': filename,
                            'filePath': file_path,
                            'size': file_stat.st_size,
                            'modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                        })

            return jsonify({'files': files})

        except Exception as e:
            logger.error(f"Error in list files endpoint: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/files/<filename>', methods=['DELETE'])
    def delete_file(filename):
        """Delete an uploaded file."""
        try:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            if os.path.exists(file_path):
                os.remove(file_path)
                return jsonify({'success': True,
                                'message': 'File deleted successfully'})
            else:
                return jsonify({'error': 'File not found'}), 404

        except Exception as e:
            logger.error(f"Error in delete file endpoint: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({'error': 'Endpoint not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({'error': 'Internal server error'}), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
