#!/usr/bin/env python3
"""
Network UI - Main Application Entry Point
A comprehensive graph visualization and analysis platform.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from network_ui.api.app import create_app
from network_ui.core.models import GraphData
from network_ui.visualization.renderer import GraphRenderer, VisualConfig
from network_ui.visualization.interactions import InteractionManager
from network_ui.visualization.visual_mapping import VisualMapper, MappingConfig, MappingType, ColorScheme

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('network_ui.log')
    ]
)

logger = logging.getLogger(__name__)


def create_sample_data() -> GraphData:
    """Create sample graph data for demonstration."""
    from network_ui.core.models import Node, Edge
    
    # Create sample nodes
    nodes = [
        Node(
            id="1",
            label="Alice",
            attributes={
                "age": 25,
                "department": "Engineering",
                "salary": 75000,
                "experience": 3
            }
        ),
        Node(
            id="2", 
            label="Bob",
            attributes={
                "age": 30,
                "department": "Marketing",
                "salary": 65000,
                "experience": 5
            }
        ),
        Node(
            id="3",
            label="Charlie", 
            attributes={
                "age": 28,
                "department": "Engineering",
                "salary": 80000,
                "experience": 4
            }
        ),
        Node(
            id="4",
            label="Diana",
            attributes={
                "age": 35,
                "department": "Sales",
                "salary": 70000,
                "experience": 8
            }
        ),
        Node(
            id="5",
            label="Eve",
            attributes={
                "age": 27,
                "department": "Engineering",
                "salary": 72000,
                "experience": 2
            }
        )
    ]
    
    # Create sample edges
    edges = [
        Edge(
            id="1-2",
            source="1",
            target="2",
            label="Collaborates",
            attributes={
                "strength": 0.8,
                "type": "work",
                "frequency": "daily"
            }
        ),
        Edge(
            id="1-3",
            source="1", 
            target="3",
            label="Mentors",
            attributes={
                "strength": 0.9,
                "type": "mentorship",
                "frequency": "weekly"
            }
        ),
        Edge(
            id="2-4",
            source="2",
            target="4",
            label="Reports to",
            attributes={
                "strength": 1.0,
                "type": "hierarchy",
                "frequency": "daily"
            }
        ),
        Edge(
            id="3-5",
            source="3",
            target="5",
            label="Collaborates",
            attributes={
                "strength": 0.7,
                "type": "work",
                "frequency": "weekly"
            }
        ),
        Edge(
            id="4-5",
            source="4",
            target="5",
            label="Manages",
            attributes={
                "strength": 0.6,
                "type": "hierarchy",
                "frequency": "monthly"
            }
        )
    ]
    
    return GraphData(nodes=nodes, edges=edges)


def setup_visualization(graph_data: GraphData) -> tuple[GraphRenderer, InteractionManager, VisualMapper]:
    """Set up the visualization components."""
    # Create renderer
    config = VisualConfig(
        canvas_width=1200,
        canvas_height=800,
        node_size=25,
        node_color="#4A90E2",
        edge_width=3,
        edge_color="#666666",
        show_node_labels=True,
        show_edge_labels=True,
        enable_drag=True,
        enable_zoom=True,
        enable_pan=True
    )
    
    renderer = GraphRenderer(config)
    renderer.set_graph_data(graph_data)
    
    # Create interaction manager
    interaction_manager = InteractionManager()
    
    # Create visual mapper
    visual_mapper = VisualMapper()
    
    # Set up some sample visual mappings
    # Node size based on salary
    salary_mapping = MappingConfig(
        attribute="salary",
        mapping_type=MappingType.LINEAR,
        min_value=60000,
        max_value=85000
    )
    visual_mapper.add_node_mapping("size", salary_mapping)
    
    # Node color based on department
    dept_mapping = MappingConfig(
        attribute="department",
        mapping_type=MappingType.CATEGORICAL,
        categories=["Engineering", "Marketing", "Sales"],
        color_scheme=ColorScheme.VIRIDIS
    )
    visual_mapper.add_node_mapping("color", dept_mapping)
    
    # Edge width based on strength
    strength_mapping = MappingConfig(
        attribute="strength",
        mapping_type=MappingType.LINEAR,
        min_value=0.0,
        max_value=1.0
    )
    visual_mapper.add_edge_mapping("width", strength_mapping)
    
    return renderer, interaction_manager, visual_mapper


def main():
    """Main application entry point."""
    print("🚀 Network UI - Graph Visualization Platform")
    print("=" * 50)
    
    try:
        # Create sample data
        logger.info("Creating sample graph data...")
        graph_data = create_sample_data()
        
        # Set up visualization components
        logger.info("Setting up visualization components...")
        renderer, interaction_manager, visual_mapper = setup_visualization(graph_data)
        
        # Create Flask app
        logger.info("Initializing Flask application...")
        app = create_app()
        
        # Store components in app context
        app.graph_data = graph_data
        app.renderer = renderer
        app.interaction_manager = interaction_manager
        app.visual_mapper = visual_mapper
        
        # Print startup information
        print(f"✅ Sample data loaded: {len(graph_data.nodes)} nodes, {len(graph_data.edges)} edges")
        print(f"✅ Visualization components initialized")
        print(f"✅ Flask application ready")
        print()
        print("🌐 Starting web server...")
        print("📱 Open your browser and navigate to: http://localhost:5000")
        print("📊 API endpoints available at: http://localhost:5000/api/")
        print()
        print("🔧 Available features:")
        print("   • Data import (CSV, JSON, XML)")
        print("   • Interactive graph visualization")
        print("   • Data-driven visual mapping")
        print("   • Layout algorithms (Force-directed, Circular, Hierarchical)")
        print("   • Node/edge selection and highlighting")
        print("   • Graph analysis and metrics")
        print("   • Export capabilities")
        print()
        print("⏹️  Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Start the Flask development server
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False  # Disable reloader to avoid duplicate processes
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        logger.info("Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        logger.error(f"Application startup error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main() 