"""
API layer for the Network UI platform.

This module provides REST API endpoints for data import, analysis, and visualization.
"""

from .app import create_app

__all__ = ['create_app']
