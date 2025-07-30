"""
Playwright-specific proxy implementation

Provides tracing capabilities for Playwright objects with XPath extraction,
method filtering, and object wrapping.
"""

from typing import TYPE_CHECKING, Any, Optional

from playwright.sync_api import (
    Locator,
    Page,
    LocatorAssertions,
    PageAssertions,
    APIResponseAssertions,
)
from playwright_dompath.dompath_sync import xpath_path

from ..core.constants import ActionType, ErrorTypes
from ..core.tracer import TraceEntry

if TYPE_CHECKING:
    from ..core.tracer import XPathTracer


class PlaywrightProxy:
    """
    Playwright-specific proxy with tracing capabilities:
    - XPath extraction using playwright_dompath
    - Smart method filtering to reduce noise
    - Automatic wrapping of Playwright objects
    """

    def __init__(
        self,
        wrapped_object: Any,
        page: Optional[Page] = None,
        tracer: Optional["XPathTracer"] = None,
    ):
        """
        Initialize Playwright proxy.

        Args:
            wrapped_object: The Playwright object to wrap (Page, Locator, Assertions, etc.)
            page: The page instance (for XPath extraction context)
            tracer: The XPath tracer instance
        """
        # Extract page if not provided
        if page is None:
            page = self._extract_page(wrapped_object)

        # Initialize proxy attributes
        self._wrapped = wrapped_object
        self._tracer = tracer
        self._context = {"page": page}
        self._wrapped_type = type(wrapped_object).__name__

    def _extract_page(self, obj: Any) -> Optional[Page]:
        """Try to extract Page from wrapped object"""
        # If it's a Page itself
        if isinstance(obj, Page):
            return obj
        # If it has a page attribute (like Locator)
        if hasattr(obj, "page"):
            return obj.page
        if hasattr(obj, "_page"):
            return obj._page
        return None

    def _is_assertion_object(self, obj: Any) -> bool:
        """Check if object is a Playwright assertion type."""
        return isinstance(
            obj, (LocatorAssertions, PageAssertions, APIResponseAssertions)
        )

    def _should_trace_method(self, method_name: str, method: Any) -> bool:
        """
        Playwright-specific method filtering, will only trace: actions, assertions, and state changes.
        """
        # Skip private methods
        if method_name.startswith("_"):
            return False

        # Skip non-callable attributes
        if not callable(method):
            return False

        # Skip property getters (they don't change state)
        if isinstance(getattr(type(self._wrapped), method_name, None), property):
            return False

        # Trace assertion methods
        if method_name.startswith("to_") or method_name.startswith("not_to_"):
            return True

        # Allowlist of action methods to trace
        action_methods = {
            # Click actions
            "click",
            "dblclick",
            "tap",
            # Input actions
            "fill",
            "type",
            "press",
            "clear",
            "select_option",
            "set_input_files",
            # State changes
            "check",
            "uncheck",
            "drag_to",
            "drop",
            # Focus actions
            "hover",
            "focus",
            "blur",
            # Navigation
            "goto",
            "reload",
            "go_back",
            "go_forward",
            "set_content",
            # Other actions
            "dispatch_event",
            "screenshot",
            "scroll_into_view_if_needed",
            "wait_for",
            # Frame navigation that changes context
            "bring_to_front",
            "close",
        }

        # Trace if it's an action method
        return method_name in action_methods

    def _extract_trace_entry(self, method_name: str) -> TraceEntry:
        """Extract Playwright-specific trace entry for method call"""
        page = self._context.get("page")
        url = getattr(page, "url", ErrorTypes.NO_PAGE) if page else ErrorTypes.NO_PAGE
        xpath = ""

        try:
            # Locator
            if isinstance(self._wrapped, Locator):
                xpath = xpath_path(self._wrapped)
                return TraceEntry(url=url, xpath=xpath, action=method_name)

            # Locator inside assertions
            if self._context.get("assertion_target"):
                assertion_target = self._context.get("assertion_target")
                xpath = xpath_path(assertion_target)
                return TraceEntry(url=url, xpath=xpath, action=method_name)

            # Assertion object without locator context
            if self._is_assertion_object(self._wrapped):
                xpath = ErrorTypes.PAGE
                return TraceEntry(url=url, xpath=xpath, action=method_name)

            # Page-level operation or default
            xpath = ErrorTypes.PAGE if page else f"{self._wrapped_type.upper()}"
            return TraceEntry(url=url, xpath=xpath, action=method_name)

        except Exception as e:
            if isinstance(self._wrapped, Locator) or self._context.get(
                "assertion_target"
            ):
                xpath = ErrorTypes.LOCATOR_ERROR
            elif self._is_assertion_object(self._wrapped):
                xpath = ErrorTypes.ASSERTION_ERROR
            else:
                xpath = f"{self._wrapped_type.upper()}_ERROR"

            return TraceEntry(
                url=url,
                xpath=xpath,
                action=method_name,
                success=False,
                error_message=str(e),
            )

    def _extract_method_value(
        self, method_name: str, args: tuple[Any, ...], kwargs: dict[str, Any]
    ) -> Optional[str]:
        """Extract Playwright-specific values from method arguments"""
        try:
            # Special handling for select_option
            if method_name == "select_option":
                # Check kwargs first (label, value, index)
                if "label" in kwargs:
                    return f"label:{kwargs['label']}"
                elif "value" in kwargs:
                    return f"value:{kwargs['value']}"
                elif "index" in kwargs:
                    return f"index:{kwargs['index']}"
                # Fall back to positional arguments
                elif args:
                    return str(args[0])
                return None

            # Simple first-arg extraction for most methods
            if method_name in [
                "fill",
                "type",
                "press",
                "goto",
                "dispatch_event",
                "to_contain_text",
                "to_have_text",
                "to_have_value",
                "to_have_class",
                "to_have_id",
                "to_have_title",
                "to_have_url",
                "to_have_count",
                "to_have_role",
                "not_to_contain_text",
                "not_to_have_text",
                "not_to_have_value",
                "not_to_have_class",
                "not_to_have_id",
                "not_to_have_title",
                "not_to_have_url",
                "not_to_have_count",
                "not_to_have_role",
            ]:
                return str(args[0]) if args else None

            # Boolean actions
            if method_name == "check":
                return "true"
            if method_name == "uncheck":
                return "false"

            # Key-value pairs
            if method_name in [
                "to_have_attribute",
                "to_have_css",
                "to_have_js_property",
                "not_to_have_attribute",
                "not_to_have_css",
                "not_to_have_js_property",
            ]:
                if len(args) >= 2:
                    return f"{args[0]}={args[1]}"
                if len(args) == 1:
                    return str(args[0])

            # File uploads
            if method_name == "set_input_files" and args:
                first_arg = args[0]
                return f"file:{first_arg}"
        except (IndexError, TypeError, AttributeError):
            pass

        return None

    def _should_wrap_method_returns(self, method_name: str) -> bool:
        """
        Determine if a method's return values should be wrapped even if not traced.

        Locator methods that return other Playwright objects should always wrap
        their returns to maintain the proxy chain for subsequent operations.
        i.e. locator().filter().first() should return a wrapped Locator.
        """
        locator_methods = {
            "locator",
            "get_by_role",
            "get_by_text",
            "get_by_label",
            "get_by_placeholder",
            "get_by_alt_text",
            "get_by_title",
            "get_by_test_id",
            "filter",
            "first",
            "last",
            "nth",
            "and_",
            "or_",
            "frame_locator",
            "content_frame",
        }
        return method_name in locator_methods

    def _wrap_return_value(self, return_value: Any) -> Any:
        """Wrap returned Playwright objects with appropriate proxy."""
        # Early return for non-wrappable types
        if not isinstance(
            return_value,
            (Page, Locator, LocatorAssertions, PageAssertions, APIResponseAssertions),
        ):
            return return_value

        # Wrap the object
        page = self._context.get("page")
        wrapped = PlaywrightProxy(return_value, page, self._tracer)

        # Preserve assertion target context for chained locators
        if isinstance(return_value, Locator) and self._context.get("assertion_target"):
            wrapped._context["assertion_target"] = self._context["assertion_target"]

        return wrapped

    def _get_action_type(self, method_name: str) -> str:
        """
        Categorize method as either action or assertion.

        Returns ActionType.ASSERTION for Playwright assertion methods (to_*, not_to_*),
        ActionType.ACTION for all other traced methods.
        """
        if (
            method_name.startswith("to_")
            or method_name.startswith("not_to_")
            or "assert" in method_name.lower()
        ):
            return ActionType.ASSERTION
        return ActionType.ACTION

    def _trace_method_call(
        self, method_name: str, args: tuple[Any, ...], kwargs: dict[str, Any]
    ) -> None:
        """Trace a method call with error handling"""
        if not self._tracer:
            return

        try:
            trace_entry = self._extract_trace_entry(method_name)
            trace_entry.value = self._extract_method_value(method_name, args, kwargs)
            trace_entry.action_type = self._get_action_type(method_name)

            self._tracer.log_action(
                url=trace_entry.url,
                xpath=trace_entry.xpath,
                action=trace_entry.action,
                success=trace_entry.success,
                error_message=trace_entry.error_message,
                value=trace_entry.value,
                action_type=trace_entry.action_type,
            )

        except Exception as e:
            # If tracing fails, log the error but don't break the original call
            if self._tracer:
                self._tracer.log_action(
                    url=ErrorTypes.TRACE_ERROR,
                    xpath=f"ERROR_{self._wrapped_type.upper()}",
                    action=f"{method_name}_trace_failed",
                    success=False,
                    error_message=str(e),
                    value=None,
                    action_type=ActionType.ACTION,
                )

    def __getattr__(self, name: str) -> Any:
        """
        Dynamic method interception - the core of the proxy approach.
        """
        # Get the original attribute
        original_attr = getattr(self._wrapped, name)

        # If it's not callable, return as-is
        if not callable(original_attr):
            return original_attr

        # Check if we should trace this method
        if not self._should_trace_method(name, original_attr):
            # Even if we don't trace, we still need to wrap return values for certain methods
            def non_traced_wrapper(*args: Any, **kwargs: Any) -> Any:
                result = original_attr(*args, **kwargs)
                return self._wrap_return_value(result)

            # Only wrap if this method might return objects that should be wrapped.
            # This is for chaining like .locator().filter().first, ...
            if self._should_wrap_method_returns(name):
                return non_traced_wrapper
            else:
                return original_attr

        # Create traced wrapper
        def traced_method(*args: Any, **kwargs: Any) -> Any:
            # Trace the method call
            self._trace_method_call(name, args, kwargs)

            try:
                # Execute original method
                result = original_attr(*args, **kwargs)

                # Wrap return value if needed
                return self._wrap_return_value(result)

            except Exception as e:
                # Log execution failure
                if self._tracer:
                    self._tracer.log_action(
                        url=ErrorTypes.EXECUTION_ERROR,
                        xpath=f"ERROR_{self._wrapped_type}",
                        action=f"{name}_failed",
                        success=False,
                        error_message=str(e),
                        value=None,
                        action_type=ActionType.ACTION,
                    )
                raise

        return traced_method

    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"PlaywrightProxy({repr(self._wrapped)})"

    # Properties for framework compatibility
    @property
    def __class__(self) -> type:  # type: ignore[misc]
        """Make isinstance() checks pass for Playwright's expect() function"""
        return type(self._wrapped)
