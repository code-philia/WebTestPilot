"""
Global Registry for Active Traced Pages

Provides centralized tracking of all active TracedPage instances
to enable automatic trace saving in pytest teardown.
"""

from typing import TYPE_CHECKING
from weakref import WeakSet

if TYPE_CHECKING:
    from ..playwright.traced_page import TracedPage

# Global registry using WeakSet to automatically remove pages when they're garbage collected
_active_traced_pages: WeakSet = WeakSet()


def register_traced_page(page: "TracedPage") -> None:
    """Register a TracedPage instance to the global registry"""
    _active_traced_pages.add(page)


def clear_registry() -> None:
    """Clear all pages from the registry"""
    _active_traced_pages.clear()


def save_all_traces() -> int:
    """
    Save traces for all active pages that have traces.
    Returns the number of pages that saved traces.
    """
    saved_count = 0
    for page in set(_active_traced_pages):
        page.save_traces()
        saved_count += 1
    return saved_count
