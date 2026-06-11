import ast
import json
import logging
import re
from copy import deepcopy
from dataclasses import dataclass, field, replace
from typing import Any

from playwright.sync_api import Page

from webtestpilot.baml_client.sync_client import b
from webtestpilot.utils import get_screenshot, pil_to_baml, wait_for_dom_stability

logger = logging.getLogger(__name__)

_SAFE_BUILTIN_CALLS = {
    "abs",
    "bool",
    "dict",
    "float",
    "int",
    "len",
    "list",
    "max",
    "min",
    "range",
    "str",
}
_MAX_PLAYWRIGHT_ACTION_TIMEOUT_MS = 10_000
_DENIED_PAGE_CALL_PATHS = {
    ("page", "add_init_script"),
    ("page", "add_script_tag"),
    ("page", "add_style_tag"),
    ("page", "close"),
    ("page", "context"),
    ("page", "evaluate"),
    ("page", "evaluate_handle"),
    ("page", "expose_binding"),
    ("page", "expose_function"),
    ("page", "goto"),
    ("page", "opener"),
    ("page", "pdf"),
    ("page", "reload"),
    ("page", "request_gc"),
    ("page", "route"),
    ("page", "route_from_har"),
    ("page", "set_content"),
    ("page", "unroute"),
}
_DENIED_PAGE_DERIVED_CALLS = {
    "dispatch_event",
    "evaluate",
    "evaluate_all",
    "evaluate_handle",
}
_RESERVED_RUNTIME_NAMES = {"helpers", "json", "page", "re"}


@dataclass(frozen=True)
class PlaywrightCodeGeneration:
    code: str
    rationale: str
    expected_effect: str
    output_type: str = "code"
    error_type: str | None = None
    target: str | None = None
    message: str | None = None
    evidence: dict[str, Any] = field(default_factory=dict)
    observation_mode: str = "unknown"


class _PlaywrightCodeHelpers:
    def __init__(self, page: Page, trace: list[dict[str, Any]]):
        self.page = page
        self.trace = trace

    def log(self, message: str) -> None:
        self.trace.append({"action": "log", "message": str(message)})

    def wait_for_stable(self, timeout_ms: int = 1000) -> None:
        wait_for_dom_stability(self.page, idle_ms=max(0, int(timeout_ms)))
        self.trace.append({"action": "wait_for_stable", "timeout_ms": int(timeout_ms)})


def execute_action_playwright_codegen(session, action: str) -> None:
    """
    Execute a natural language action by generating and running Playwright code.

    This mode keeps the paper implementation contract: callers pass the same
    session and task/action string used by SoM and browser-use modes. The LLM
    call goes through BAML client registries stored on the session config.
    """
    options = {
        "client_registry": session.config.playwright_codegen,
        "collector": session.collector,
    }
    max_revisions = max(0, int(session.config.playwright_codegen_max_revisions))
    snapshot_fallback_after_attempts = max(
        0, int(session.config.playwright_codegen_snapshot_fallback_after_attempts)
    )
    timeout_ms = max(1000, int(session.config.playwright_codegen_timeout_ms))
    previous_failure: dict[str, Any] | None = None
    last_error: Exception | None = None

    for attempt in range(max_revisions + 1):
        observation_mode = (
            "fallback-dom-summary"
            if attempt >= snapshot_fallback_after_attempts
            else "playwright-ai-snapshot"
        )
        try:
            generation = _propose_playwright_code(
                page=session.page,
                action=action,
                baml_options=options,
                previous_failure=previous_failure,
                attempt=attempt,
                observation_mode=observation_mode,
            )
        except Exception as exc:
            last_error = exc
            previous_failure = {
                "kind": "generation_failed",
                "attempt": attempt,
                "error": str(exc),
            }
            logger.warning(
                "playwright-code-gen generation attempt %d failed: %s", attempt, exc
            )
            continue

        session.trace.append(
            {
                "action": action,
                "action_code": generation.code,
                "rationale": generation.rationale,
                "expected_effect": generation.expected_effect,
                "mode": "playwright-code-gen",
                "attempt": attempt,
                "observation_mode": (
                    generation.observation_mode
                    if generation.observation_mode != "unknown"
                    else observation_mode
                ),
            }
        )

        if generation.output_type == "error":
            payload = {
                "error_type": generation.error_type or "code_generation_error",
                "target": generation.target,
                "message": generation.message or generation.rationale,
                "evidence": generation.evidence or {},
            }
            if attempt < max_revisions:
                previous_failure = {
                    "kind": "model_reported_error",
                    "attempt": attempt,
                    "observation_mode": (
                        generation.observation_mode
                        if generation.observation_mode != "unknown"
                        else observation_mode
                    ),
                    "error": payload,
                }
                last_error = RuntimeError(json.dumps(payload, ensure_ascii=False))
                logger.warning(
                    "playwright-code-gen attempt %d returned structured error: %s",
                    attempt,
                    payload,
                )
                continue
            raise RuntimeError(json.dumps(payload, ensure_ascii=False))

        try:
            trace = _execute_generated_code(generation.code, session.page)
            session.trace.extend(trace)
            _wait_after_generated_action(session.page, timeout_ms)
            session.capture_state(prev_action=action)
            return
        except Exception as exc:
            last_error = exc
            previous_failure = {
                "kind": "execution_failed",
                "attempt": attempt,
                "code": generation.code,
                "error": str(exc),
            }
            logger.warning("playwright-code-gen attempt %d failed: %s", attempt, exc)

    raise RuntimeError(f"playwright-code-gen failed after retries: {last_error}")


def _propose_playwright_code(
    *,
    page: Page,
    action: str,
    baml_options: dict,
    previous_failure: dict[str, Any] | None,
    attempt: int,
    observation_mode: str,
) -> PlaywrightCodeGeneration:
    screenshot_baml = pil_to_baml(get_screenshot(page))
    page_observation, actual_observation_mode = _build_page_observation(
        page,
        force_dom_summary=observation_mode == "fallback-dom-summary",
    )
    page_context = _build_page_context(page)
    failure_context = json.dumps(previous_failure or {}, ensure_ascii=False, indent=2)

    raw = b.GeneratePlaywrightCode(
        screenshot=screenshot_baml,
        task=action,
        page_context=page_context,
        page_observation=page_observation,
        previous_failure=failure_context,
        attempt=attempt,
        baml_options=baml_options,
    )
    generation = _parse_generation(raw)
    generation = replace(generation, observation_mode=actual_observation_mode)
    logger.info(
        "Generated Playwright code using %s:\n%s",
        actual_observation_mode,
        generation.code,
    )
    return generation


def _build_page_context(page: Page) -> str:
    try:
        title = page.title()
    except Exception:
        title = ""
    return json.dumps(
        {
            "url": getattr(page, "url", ""),
            "title": title,
            "viewport": page.viewport_size,
        },
        ensure_ascii=False,
        default=str,
    )


def _build_page_snapshot(page: Page, *, limit: int = 14000) -> str:
    text = page.aria_snapshot(mode="ai", timeout=5000)
    if len(text) <= limit:
        return text
    return text[:limit] + "\n... truncated ..."


def _build_page_observation(
    page: Page,
    *,
    force_dom_summary: bool = False,
    limit: int = 14000,
) -> tuple[str, str]:
    if not force_dom_summary:
        try:
            snapshot = _build_page_snapshot(page, limit=limit)
            return (
                _format_page_observation("playwright-ai-snapshot", snapshot),
                "playwright-ai-snapshot",
            )
        except Exception as exc:
            logger.warning(
                "Falling back to DOM summary because Playwright AI snapshot failed: %s",
                exc,
            )

    dom_context = _build_dom_context(page, limit=limit)
    return (
        _format_page_observation("fallback-dom-summary", dom_context),
        "fallback-dom-summary",
    )


def _format_page_observation(source: str, text: str) -> str:
    return f"Observation source: {source}\n\n{text}"


def _build_dom_context(page: Page, *, limit: int = 14000) -> str:
    data = page.evaluate(
        """
        () => {
          const isVisible = (el) => {
            const style = window.getComputedStyle(el);
            const rect = el.getBoundingClientRect();
            return style && style.visibility !== 'hidden' &&
              style.display !== 'none' && Number(style.opacity || '1') > 0 &&
              rect.width > 0 && rect.height > 0;
          };
          const textOf = (el) => (el.innerText || el.textContent || '').replace(/\\s+/g, ' ').trim();
          const selectorFor = (el) => {
            if (el.id) return `#${CSS.escape(el.id)}`;
            const testId = el.getAttribute('data-testid') || el.getAttribute('data-test-id');
            if (testId) return `[data-testid="${CSS.escape(testId)}"]`;
            const name = el.getAttribute('name');
            if (name) return `${el.tagName.toLowerCase()}[name="${CSS.escape(name)}"]`;
            const aria = el.getAttribute('aria-label');
            if (aria) return `${el.tagName.toLowerCase()}[aria-label="${CSS.escape(aria)}"]`;
            return el.tagName.toLowerCase();
          };
          const nodes = Array.from(document.querySelectorAll(
            'a,button,input,textarea,select,[role],[contenteditable="true"],[tabindex],summary'
          ));
          return nodes.filter(isVisible).slice(0, 120).map((el, index) => {
            const rect = el.getBoundingClientRect();
            return {
              index,
              tag: el.tagName.toLowerCase(),
              role: el.getAttribute('role') || '',
              type: el.getAttribute('type') || '',
              text: textOf(el).slice(0, 160),
              aria_label: el.getAttribute('aria-label') || '',
              title: el.getAttribute('title') || '',
              placeholder: el.getAttribute('placeholder') || '',
              name: el.getAttribute('name') || '',
              value: el.value || '',
              disabled: Boolean(el.disabled || el.getAttribute('aria-disabled') === 'true'),
              selector_hint: selectorFor(el),
              rect: {
                x: Math.round(rect.x),
                y: Math.round(rect.y),
                width: Math.round(rect.width),
                height: Math.round(rect.height)
              }
            };
          });
        }
        """
    )
    text = json.dumps(data, ensure_ascii=False, indent=2, default=str)
    if len(text) <= limit:
        return text
    return text[:limit] + "\n... truncated ..."


def _wait_after_generated_action(page: Page, timeout_ms: int) -> None:
    try:
        page.wait_for_load_state(timeout=timeout_ms)
    except Exception:
        logger.debug("Page did not reach load state within %d ms", timeout_ms)
    wait_for_dom_stability(page)


def _parse_generation(content: str) -> PlaywrightCodeGeneration:
    payload = json.loads(_extract_json_text(content))
    if not isinstance(payload, dict):
        raise ValueError("Playwright code generation output must be a JSON object")

    output_type = str(payload.get("output_type") or "code")
    if output_type not in {"code", "error"}:
        raise ValueError(f"Unsupported playwright-code-gen output_type: {output_type}")
    return PlaywrightCodeGeneration(
        output_type=output_type,
        code=str(payload.get("code") or ""),
        rationale=str(payload.get("rationale") or ""),
        expected_effect=str(payload.get("expected_effect") or ""),
        error_type=payload.get("error_type"),
        target=payload.get("target"),
        message=payload.get("message"),
        evidence=payload.get("evidence") if isinstance(payload.get("evidence"), dict) else {},
    )


def _extract_json_text(content: str) -> str:
    text = content.strip()
    fenced = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, flags=re.IGNORECASE)
    if fenced:
        return fenced.group(1).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end >= start:
        return text[start : end + 1]
    return text


def _execute_generated_code(code: str, page: Page) -> list[dict[str, Any]]:
    cleaned_code = _clean_code_block(code)
    _validate_generated_code(cleaned_code)
    trace: list[dict[str, Any]] = []
    helpers = _PlaywrightCodeHelpers(page, trace)
    safe_builtins = {
        "abs": abs,
        "bool": bool,
        "dict": dict,
        "enumerate": enumerate,
        "float": float,
        "int": int,
        "len": len,
        "list": list,
        "max": max,
        "min": min,
        "range": range,
        "str": str,
        "Exception": Exception,
        "RuntimeError": RuntimeError,
        "TimeoutError": TimeoutError,
        "ValueError": ValueError,
    }
    safe_globals = {
        "__builtins__": safe_builtins,
        "json": json,
        "page": page,
        "re": re,
        "helpers": helpers,
    }
    exec(cleaned_code, safe_globals, safe_globals)
    return deepcopy(trace)


def _clean_code_block(code: str) -> str:
    text = code.strip()
    fenced = re.search(r"```(?:python)?\s*([\s\S]*?)```", text, flags=re.IGNORECASE)
    return fenced.group(1).strip() if fenced else text


def _validate_generated_code(code: str) -> None:
    tree = ast.parse(code)
    denied_nodes = (
        ast.For,
        ast.While,
        ast.AsyncFor,
        ast.ListComp,
        ast.SetComp,
        ast.DictComp,
        ast.GeneratorExp,
        ast.Import,
        ast.ImportFrom,
        ast.FunctionDef,
        ast.AsyncFunctionDef,
        ast.ClassDef,
        ast.Global,
        ast.Nonlocal,
        ast.Lambda,
    )
    denied_calls = {
        "__import__",
        "compile",
        "delattr",
        "eval",
        "exec",
        "getattr",
        "globals",
        "input",
        "locals",
        "open",
        "setattr",
        "vars",
    }
    for node in ast.walk(tree):
        if isinstance(node, denied_nodes):
            raise ValueError(f"Generated code uses disallowed syntax: {type(node).__name__}")
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.NamedExpr)):
            _validate_assignment_targets(node)
        if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            raise ValueError("Generated code cannot access dunder attributes")
        if isinstance(node, ast.Name) and node.id.startswith("__"):
            raise ValueError("Generated code cannot access dunder names")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in denied_calls:
            raise ValueError(f"Generated code cannot call {node.func.id}()")
        if isinstance(node, ast.Call):
            _validate_generated_call(node)


def _validate_generated_call(node: ast.Call) -> None:
    root_name = _call_root_name(node.func)
    if root_name is None:
        raise ValueError("Generated code contains unsupported dynamic call")
    if root_name in _SAFE_BUILTIN_CALLS:
        return
    if root_name not in {"page", "helpers", "re", "json"}:
        raise ValueError(f"Unsupported call root: {root_name}")

    attr_path = _call_attr_path(node.func)
    _validate_page_call_path(attr_path)

    attr_name = _call_attr_name(node.func)
    if root_name == "page" and attr_name == "wait_for_timeout":
        raise ValueError("Generated code cannot call page.wait_for_timeout()")
    if _is_playwright_action_call(node.func):
        _validate_timeout_argument(node)


def _validate_assignment_targets(
    node: ast.Assign | ast.AnnAssign | ast.AugAssign | ast.NamedExpr,
) -> None:
    targets: list[ast.expr]
    if isinstance(node, ast.Assign):
        targets = list(node.targets)
    else:
        targets = [node.target]

    for target in targets:
        for name in _iter_assigned_names(target):
            if name in _RESERVED_RUNTIME_NAMES:
                raise ValueError(f"Generated code cannot reassign reserved runtime name: {name}")


def _iter_assigned_names(target: ast.expr) -> list[str]:
    if isinstance(target, ast.Name):
        return [target.id]
    if isinstance(target, (ast.Tuple, ast.List)):
        names: list[str] = []
        for item in target.elts:
            names.extend(_iter_assigned_names(item))
        return names
    return []


def _call_root_name(func: ast.expr) -> str | None:
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return _call_root_name(func.value)
    if isinstance(func, ast.Call):
        return _call_root_name(func.func)
    return None


def _call_attr_name(func: ast.expr) -> str | None:
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _is_playwright_action_call(func: ast.expr) -> bool:
    attr_name = _call_attr_name(func)
    attr_path = _call_attr_path(func)
    if "keyboard" in attr_path or "mouse" in attr_path:
        return False
    return attr_name in {
        "check",
        "click",
        "dblclick",
        "dispatch_event",
        "drag_to",
        "fill",
        "focus",
        "hover",
        "press",
        "select_option",
        "set_checked",
        "tap",
        "type",
        "uncheck",
    }


def _validate_page_call_path(attr_path: list[str]) -> None:
    for denied_path in _DENIED_PAGE_CALL_PATHS:
        if attr_path[: len(denied_path)] == list(denied_path):
            raise ValueError(f"Generated code cannot call {'.'.join(denied_path)}")
    if attr_path and attr_path[0] == "page":
        denied_attrs = _DENIED_PAGE_DERIVED_CALLS.intersection(attr_path[1:])
        if denied_attrs:
            raise ValueError(
                "Generated code cannot call page-derived "
                f"{sorted(denied_attrs)[0]}()"
            )


def _validate_timeout_argument(node: ast.Call) -> None:
    timeout_keywords = [keyword for keyword in node.keywords if keyword.arg == "timeout"]
    if not timeout_keywords:
        raise ValueError("Generated Playwright action calls must include timeout")

    timeout_value = timeout_keywords[-1].value
    if (
        not isinstance(timeout_value, ast.Constant)
        or not isinstance(timeout_value.value, int)
        or isinstance(timeout_value.value, bool)
    ):
        raise ValueError("Generated Playwright action timeout value must be a literal int")
    if timeout_value.value <= 0 or timeout_value.value > _MAX_PLAYWRIGHT_ACTION_TIMEOUT_MS:
        raise ValueError(
            "Generated Playwright action timeout value must be between "
            f"1 and {_MAX_PLAYWRIGHT_ACTION_TIMEOUT_MS} ms"
        )


def _call_attr_path(func: ast.expr) -> list[str]:
    if isinstance(func, ast.Name):
        return [func.id]
    if isinstance(func, ast.Attribute):
        return [*_call_attr_path(func.value), func.attr]
    if isinstance(func, ast.Call):
        return _call_attr_path(func.func)
    return []
