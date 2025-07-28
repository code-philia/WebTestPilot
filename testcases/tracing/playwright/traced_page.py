"""
Traced Page Implementation

Enhanced Page wrapper that provides tracing functionality and trace management.
"""

from typing import Any, Optional, Union

from playwright.sync_api import Locator, Page

from ..core.registry import register_traced_page
from ..core.tracer import XPathTracer
from ..core.utils import get_trace_output_path, is_tracing_enabled
from .proxy import PlaywrightProxy


class TracedPage(PlaywrightProxy):
    """
    Enhanced Page wrapper that extends PlaywrightProxy with trace management.

    Provides methods for saving, clearing, and summarizing traces while
    maintaining full Playwright Page API compatibility.
    """

    def __init__(self, page: Page, enable_tracing: Optional[bool] = None):
        """
        Initialize TracedPage.

        Args:
            page: The Playwright Page to wrap
            enable_tracing: Override for tracing enablement (None uses env var)
        """
        # Check if tracing is enabled
        if enable_tracing is None:
            enable_tracing = is_tracing_enabled()

        # Initialize tracer if tracing is enabled
        if enable_tracing:
            output_dir = get_trace_output_path()
            tracer = XPathTracer(output_dir)
        else:
            tracer = None

        # Initialize the Playwright proxy
        super().__init__(page, page, tracer)
        self._tracing_enabled = enable_tracing

        # Register this page in the global registry if tracing is enabled
        if enable_tracing:
            register_traced_page(self)

    def save_traces(self) -> Optional[str]:
        """Save traces to file with coverage report"""
        if self._tracing_enabled and self._tracer:
            # Generate coverage report before saving
            self._tracer.report_coverage()
            return self._tracer.save_traces()
        return None

    def _wrap_return_value(self, return_value: Any) -> Any:
        """Ensure locators are wrapped with proper page context"""
        if isinstance(return_value, Locator):
            page = self._context.get("page")
            return PlaywrightProxy(return_value, page, self._tracer)
        elif isinstance(return_value, Page):
            return TracedPage(return_value, self._tracing_enabled)
        else:
            return super()._wrap_return_value(return_value)


def create_traced_page(
    page: Page, enable_tracing: Optional[bool] = None
) -> Union[TracedPage, Page]:
    """
    Factory function to create a traced page or return original based on environment.

    Args:
        page: Original Playwright Page
        enable_tracing: Override for tracing enablement (None uses env var)

    Returns:
        TracedPage if tracing enabled, original Page otherwise
    """
    if enable_tracing is None:
        enable_tracing = is_tracing_enabled()

    if enable_tracing:
        return TracedPage(page, enable_tracing=True)
    else:
        return page
