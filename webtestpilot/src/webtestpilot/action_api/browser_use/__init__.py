import asyncio
import concurrent.futures
import logging
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from webtestpilot.data_models import Session

logger = logging.getLogger(__name__)


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


async def _run_agent(action: str, llm, cdp_url: str) -> str:
    from browser_use import Agent
    from browser_use.browser.session import BrowserSession

    # httpx connection-pool teardown schedules tasks that fire after asyncio.run()
    # closes the loop, producing noisy "Event loop is closed" RuntimeErrors.
    # Suppress that specific error; everything else propagates normally.
    loop = asyncio.get_running_loop()
    _default = loop.get_exception_handler() or loop.default_exception_handler
    def _handler(loop, context):
        if isinstance(context.get("exception"), RuntimeError) and \
                "Event loop is closed" in str(context.get("exception", "")):
            return
        _default(loop, context)
    loop.set_exception_handler(_handler)

    browser_session = BrowserSession(cdp_url=cdp_url)
    agent = Agent(task=action, llm=llm, browser=browser_session)
    result = await agent.run()
    return str(result)


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

    llm = _build_llm(session.config.browser_use_agent)
    logger.info("browser-use executing: %r", action)

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        result = pool.submit(asyncio.run, _run_agent(action=action, llm=llm, cdp_url=cdp_url)).result()
    session.trace.append({"action": action, "action_code": f"[browser-use] {result}"})

    session.page.wait_for_load_state()
    wait_for_dom_stability(session.page)
    session.capture_state(prev_action=action)
