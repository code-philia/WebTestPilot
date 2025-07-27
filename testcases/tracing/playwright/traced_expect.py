"""
Traced Expect Implementation

Enhanced expect function that adds tracing capabilities to Playwright assertions.
"""

from typing import Any, Optional, Union

from playwright.sync_api import (
    Page,
    Locator,
    LocatorAssertions,
)
from playwright.sync_api import expect as original_expect

from ..core.utils import is_tracing_enabled
from .proxy import PlaywrightProxy


def _is_wrapped_proxy(obj: Any) -> bool:
    """Check if object is a wrapped PlaywrightProxy instance."""
    return (
        hasattr(obj, "_tracer")
        and hasattr(obj, "_wrapped")
        and hasattr(obj, "_context")
    )


def traced_expect(
    actual: Union[Page, Locator], message: Optional[str] = None
) -> LocatorAssertions:
    """
    Enhanced wrapper for Playwright's expect() function.

    Automatically wraps the returned assertion object with tracing capabilities
    while maintaining full compatibility with the original expect() behavior.

    Args:
        actual: Page or Locator to create assertions for
        message: Optional message for assertion failures

    Returns:
        Assertion object (wrapped if tracing enabled, original otherwise)
    """
    # Extract underlying object and context if it's wrapped
    original_locator = None

    # Check if it's a wrapped object by looking for _tracer attribute
    # This is more reliable than isinstance() due to __class__ property override
    if _is_wrapped_proxy(actual):
        # It's a wrapped object (PlaywrightProxy)
        underlying_actual = actual._wrapped
        page = actual._context.get("page")
        tracer = actual._tracer
        # Store reference to original locator for assertion context
        if isinstance(underlying_actual, Locator):
            original_locator = underlying_actual

    else:
        # It's an unwrapped object
        underlying_actual = actual
        # Try to extract page for context
        if isinstance(actual, Page):
            page = actual
        elif hasattr(actual, "page"):
            page = actual.page
        else:
            page = None
        tracer = None
        # Store reference to original locator for assertion context
        if isinstance(actual, Locator):
            original_locator = actual

    # Call original expect function
    original_assertion = original_expect(underlying_actual, message)

    # If tracing is enabled, wrap the assertion object with enhanced context
    if is_tracing_enabled() and tracer:
        # Create proxy with additional context for assertion target
        proxy = PlaywrightProxy(original_assertion, page, tracer)
        # Store original locator reference for proper XPath extraction in assertions
        if original_locator is not None:
            proxy._context["assertion_target"] = original_locator

        return proxy

    return original_assertion
