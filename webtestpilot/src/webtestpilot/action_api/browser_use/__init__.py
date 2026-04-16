import asyncio
import logging
import os
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from webtestpilot.data_models import Session

logger = logging.getLogger(__name__)

# Each CDP URL gets a dedicated event loop running in a daemon thread and a
# BrowserSession kept alive across action calls.  Using a persistent loop
# (instead of asyncio.run()) means the loop is never torn down between actions,
# so bubus's internal asyncio queue stays live and BrowserSession can be reused.
_loops: dict[str, asyncio.AbstractEventLoop] = {}
_browser_sessions: dict[str, object] = {}
_lock = threading.Lock()


def _get_loop(cdp_url: str) -> asyncio.AbstractEventLoop:
    with _lock:
        if cdp_url not in _loops:
            loop = asyncio.new_event_loop()
            threading.Thread(
                target=loop.run_forever,
                daemon=True,
                name=f"bu-loop-{cdp_url}",
            ).start()
            _loops[cdp_url] = loop
    return _loops[cdp_url]


def _get_browser_session(cdp_url: str):
    with _lock:
        if cdp_url not in _browser_sessions:
            from browser_use.browser.session import BrowserSession
            _browser_sessions[cdp_url] = BrowserSession(cdp_url=cdp_url, keep_alive=True)
            logger.debug("Created new BrowserSession for %s", cdp_url)
    return _browser_sessions[cdp_url]


def teardown_browser_session(cdp_url: str) -> None:
    """
    Stop the persistent event loop and remove the BrowserSession for a CDP URL.

    Call this when the Playwright browser is about to be closed (e.g. at test-case
    teardown) so the cached session does not attempt to reconnect to a dead endpoint.
    """
    with _lock:
        loop = _loops.pop(cdp_url, None)
        _browser_sessions.pop(cdp_url, None)

    if loop is not None:
        loop.call_soon_threadsafe(loop.stop)
        logger.debug("Stopped browser-use event loop for %s", cdp_url)


def _build_llm(client_name: str):
    """Map a config.yaml client name to a browser-use LLM instance."""
    from browser_use.llm import ChatOpenAI

    match client_name:
        case "Claude":
            from browser_use.llm import ChatAnthropic
            return ChatAnthropic(
                model=os.environ["ANTHROPIC_MODEL_NAME"],
                api_key=os.environ.get("ANTHROPIC_API_KEY"),
            )
        case "GPT":
            return ChatOpenAI(
                model=os.environ["OPENAI_MODEL_NAME"],
                api_key=os.environ.get("OPENAI_API_KEY"),
                base_url=os.environ.get("OPENAI_BASE_URL") or None,
            )
        case "Gemini":
            from browser_use.llm import ChatGoogle
            return ChatGoogle(
                model=os.environ["GOOGLEAI_MODEL_NAME"],
                api_key=os.environ.get("GOOGLEAI_API_KEY"),
            )
        case "OpenRouter":
            from browser_use.llm import ChatOpenRouter
            return ChatOpenRouter(
                model=os.environ["OPENROUTER_MODEL_NAME"],
                api_key=os.environ.get("OPENROUTER_API_KEY"),
            )
        case _:
            raise ValueError(
                f"Unsupported browser-use LLM client: '{client_name}'. "
                f"Supported values: Claude, GPT, Gemini, OpenRouter."
            )


async def _run_agent(action: str, llm, browser_session, max_steps: int) -> tuple[str, int, int]:
    from browser_use import Agent

    agent = Agent(task=action, llm=llm, browser=browser_session)
    history = await agent.run(max_steps=max_steps)

    input_tokens = sum(e.usage.prompt_tokens for e in agent.token_cost_service.usage_history)
    output_tokens = sum(e.usage.completion_tokens for e in agent.token_cost_service.usage_history)

    return str(history), input_tokens, output_tokens


def execute_action_browser_use(session: "Session", action: str) -> None:
    """
    Execute a natural language action using the browser-use one-shot LLM agent.

    browser-use connects to the existing browser via CDP, so it shares the same
    cookies, auth state, and current page as the Playwright session.

    Requires the browser to expose a CDP endpoint on port 9222 (the default):
        browser = playwright.chromium.launch(args=["--remote-debugging-port=9222"])
    """
    from webtestpilot.utils import wait_for_dom_stability

    cdp_url = session.config.browser_use_cdp_url
    loop = _get_loop(cdp_url)
    browser_session = _get_browser_session(cdp_url)
    llm = _build_llm(session.config.browser_use_agent)
    logger.info("browser-use executing: %r", action)

    future = asyncio.run_coroutine_threadsafe(
        _run_agent(action=action, llm=llm, browser_session=browser_session, max_steps=session.config.browser_use_max_steps),
        loop,
    )
    result, input_tokens, output_tokens = future.result()

    session.browser_use_input_tokens += input_tokens
    session.browser_use_output_tokens += output_tokens
    logger.debug("browser-use tokens: input=%d output=%d", input_tokens, output_tokens)
    session.trace.append({"action": action, "action_code": f"[browser-use] {result}"})

    session.page.wait_for_load_state()
    wait_for_dom_stability(session.page)
    session.capture_state(prev_action=action)
