# Import and re-export the public API
from tracing.core.tracer import TraceEntry, XPathTracer
from tracing.core.utils import insert_start_event_to_page
from tracing.playwright.traced_expect import traced_expect
from tracing.playwright.traced_page import TracedPage, create_traced_page

# Export everything for easy import
__all__ = [
    "XPathTracer",
    "TraceEntry",
    "TracedPage",
    "create_traced_page",
    "traced_expect",
    "insert_start_event_to_page",
]
