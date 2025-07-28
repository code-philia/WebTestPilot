"""
Utility functions for tracing configuration and common operations.
"""

import os


def is_tracing_enabled() -> bool:
    """Check if XPath tracing is enabled via environment variable."""
    return os.getenv("ENABLE_XPATH_TRACING", "false").lower() == "true"


def get_trace_output_path() -> str:
    """Get the output path for trace files from environment variable."""
    return os.getenv("XPATH_OUTPUT_PATH", "./traces")


def is_debug_enabled() -> bool:
    """Check if debug mode is enabled for XPath tracing."""
    return os.getenv("XPATH_TRACE_DEBUG", "false").lower() == "true"