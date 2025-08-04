"""
XPath Tracing API

Clean, simple API for the XPath tracing system.
This module provides the main entry points that users should import.

Usage:
    from tracing_api import TracedPage, create_traced_page, traced_expect
    
    # Use in pytest fixtures
    traced_page = create_traced_page(page)
"""

# Import and re-export the public API
from tracing import (
    XPathTracer,
    TraceEntry,
    TracedPage,
    create_traced_page,
    traced_expect,
)

# Export everything for easy import
__all__ = [
    'XPathTracer',
    'TraceEntry',
    'TracedPage',
    'create_traced_page',
    'traced_expect',
]

# Version information
__version__ = "2.0.0"
__author__ = "WebTestPilot Team"
