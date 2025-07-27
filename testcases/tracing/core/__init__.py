"""
Core tracing functionality.

This module contains the fundamental tracing components.
"""

from .tracer import XPathTracer, TraceEntry
from .utils import is_tracing_enabled, get_trace_output_path
from .constants import ErrorTypes, ActionType

__all__ = [
    "XPathTracer",
    "TraceEntry",
    "is_tracing_enabled",
    "get_trace_output_path",
    "ErrorTypes",
    "ActionType",
]
