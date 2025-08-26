import os

from testcases.tracing.core.tracer import TraceEntry


def is_tracing_enabled() -> bool:
    """Check if XPath tracing is enabled via environment variable."""
    return os.getenv("ENABLE_XPATH_TRACING", "false").lower() == "true"


def get_trace_output_path() -> str:
    """Get the output path for trace files from environment variable."""
    return os.getenv("XPATH_OUTPUT_PATH", "./traces")


def is_debug_enabled() -> bool:
    """Check if debug mode is enabled for XPath tracing."""
    return os.getenv("XPATH_TRACE_DEBUG", "false").lower() == "true"


def insert_start_event_to_page(page):
    if hasattr(page, "_tracer") and page._tracer is not None:
        page._tracer.traces.append(TraceEntry("START", "START", "START"))
