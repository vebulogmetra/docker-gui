"""
Core module for Docker GUI application.

This module contains base classes and abstractions for managing Docker resources.
"""

from .resource_manager import ResourceManager
from .resource_view import ResourceView
from .base_operations import BaseOperations

__all__ = ['ResourceManager', 'ResourceView', 'BaseOperations'] 