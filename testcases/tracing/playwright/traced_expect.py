"""
Traced Expect Implementation

Enhanced expect function that adds tracing capabilities to Playwright assertions.
"""

from typing import Optional, Union

from playwright.sync_api import (
    Page,
    Locator,
    LocatorAssertions,
)
from playwright.sync_api import expect as original_expect

from ..core.utils import is_tracing_enabled
from .proxy import PlaywrightProxy


def traced_expect(
    target: Union[Page, Locator, PlaywrightProxy], message: Optional[str] = None
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
    original_locator = None

    if isinstance(target, PlaywrightProxy):
        underlying_target = target._wrapped
        page = target._context.get("page")
        tracer = target._tracer
        # Store reference to original locator for assertion context
        if isinstance(underlying_target, Locator):
            original_locator = underlying_target
    else:
        underlying_target = target
        page = None
        tracer = None
        # Store reference to original locator for assertion context
        if isinstance(target, Locator):
            original_locator = target

    # Call original expect function
    original_assertion = original_expect(underlying_target, message)

    # If tracing is enabled, wrap the assertion object with enhanced context
    if is_tracing_enabled() and tracer:
        # Create proxy with additional context for assertion target
        proxy = PlaywrightProxy(original_assertion, page, tracer)
        # Store original locator reference for proper XPath extraction in assertions
        if original_locator is not None:
            proxy._context["assertion_target"] = original_locator

        return proxy

    return original_assertion
