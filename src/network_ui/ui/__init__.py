"""
Network UI - User Interface Module (Spec 5)

This module provides the complete web-based user interface including: 
- Main window with menus, toolbars, and panels
- Data import wizard with file browser and mapping UI
- Analysis panel for running graph algorithms
- Visual styling panel for customizing graph appearance
- Details-on-demand panel for node/edge information
- Interactive graph canvas with direct manipulation

The UI module orchestrates all other modules according to Spec 8 integration plan.
"""

__version__ = "1.0.0"
__author__ = "Agentic AI Development"

# Core UI components
from .main_window import MainWindow
from .import_wizard import ImportWizard
from .analysis_panel import AnalysisPanel
from .visual_panel import VisualStylingPanel
from .details_panel import DetailsPanel

__all__ = [
    'MainWindow',
    'ImportWizard',
    'AnalysisPanel',
    'VisualStylingPanel',
    'DetailsPanel'
]
