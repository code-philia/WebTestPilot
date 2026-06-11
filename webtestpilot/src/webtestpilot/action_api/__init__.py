from webtestpilot.data_models import Session


def execute_action(session: Session, action: str) -> None:
    """
    Executes a natural language action on the current page.

    The execution mode is controlled by ``session.config.mode``:

    - ``"som"`` (default): Two-stage pipeline — GUI grounding model proposes
      coordinates, then Set-of-Mark annotation identifies nearby elements and
      generates interaction code.
    - ``"browser-use"``: One-shot LLM agent via browser-use. The agent receives
      the task description and navigates the browser directly, with no GUI
      grounding model required.
    - ``"playwright-code-gen"``: One-shot BAML LLM call that observes the DOM
      and screenshot, generates sync Playwright Python code, and executes it in
      the current browser page.

    Args:
        session (Session): The current browser session containing the page and trace history.
        action (str): The natural language description of the action to perform.

    Raises:
        Exception: If the action fails to execute after retries or encounters a critical error.
    """
    if session.config.mode == "browser-use":
        from webtestpilot.action_api.browser_use import execute_action_browser_use

        execute_action_browser_use(session, action)
        return

    if session.config.mode in {"playwright-code-gen", "playwright-codegen"}:
        from webtestpilot.action_api.playwright_codegen import (
            execute_action_playwright_codegen,
        )

        execute_action_playwright_codegen(session, action)
        return

    from webtestpilot.action_api.som import execute_action_som

    execute_action_som(session, action)
