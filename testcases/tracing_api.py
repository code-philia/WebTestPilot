# Import and re-export the public API
from testcases.tracing.core.tracer import XPathTracer, TraceEntry
from testcases.tracing.playwright.traced_page import TracedPage, create_traced_page
from testcases.tracing.playwright.traced_expect import traced_expect

# Export everything for easy import
__all__ = [
    "XPathTracer",
    "TraceEntry",
    "TracedPage",
    "create_traced_page",
    "traced_expect",
]
