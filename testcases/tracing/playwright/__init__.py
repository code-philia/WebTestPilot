"""
Playwright-specific tracing components.

This module contains Playwright integration for the XPath tracing system,
including traced wrappers for Page objects and expect functions.
"""

from .traced_page import TracedPage, create_traced_page
from .traced_expect import traced_expect

__all__ = ['TracedPage', 'create_traced_page', 'traced_expect']