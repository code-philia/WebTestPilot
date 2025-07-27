"""
XPath Tracing Library

A clean, modular tracing system for Playwright that captures user interactions
and assertions with XPath information for web automation testing.

Public API:
    - TracedPage: Enhanced Page with tracing capabilities
    - create_traced_page: Factory function for traced pages
    - traced_expect: Enhanced expect function with tracing
    - XPathTracer: Core tracing functionality
"""

from .core.tracer import XPathTracer, TraceEntry
from .playwright.traced_page import TracedPage, create_traced_page
from .playwright.traced_expect import traced_expect

__all__ = [
    # Core tracing
    "XPathTracer",
    "TraceEntry",
    # Playwright integration
    "TracedPage",
    "create_traced_page",
    "traced_expect",
]
