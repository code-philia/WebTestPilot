import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from baml_py import ClientRegistry
from dotenv import find_dotenv, load_dotenv

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Config:
    parser: ClientRegistry

    assertion_generation: ClientRegistry

    assertion_api: ClientRegistry

    action_proposer: ClientRegistry

    ui_locator: ClientRegistry

    page_reidentification: ClientRegistry

    infer_missing_steps: bool

    max_tries: int

    # Action execution mode: "som" (default), "browser-use", or "playwright-code-gen"
    mode: str

    # Client registry used by the Playwright code generation action executor.
    playwright_codegen: ClientRegistry

    # Maximum number of repair generations after a generated Playwright snippet fails.
    playwright_codegen_max_revisions: int

    # Timeout budget passed to post-action page load waits.
    playwright_codegen_timeout_ms: int

    # Client name (from config.yaml) used as the LLM for the browser-use agent
    browser_use_agent: str

    # CDP endpoint for browser-use to connect to the existing browser session.
    # Empty string means browser-use mode is not fully configured.
    browser_use_cdp_url: str

    # Maximum steps the browser-use agent may take per action.
    browser_use_max_steps: int

    @staticmethod
    def load(path: Path | str) -> "Config":
        # Load environment variables
        dotenv_path = find_dotenv(raise_error_if_not_found=False)
        load_dotenv(dotenv_path)

        # Load YAML config
        yaml_path = (
            Path(path) if path is not None else Path(__file__).parent / "config.yaml"
        )
        with yaml_path.open("r") as f:
            yaml_data: dict[str, Any] = yaml.safe_load(f) or {}

        # LLM client configurations
        parser = ClientRegistry()
        parser.set_primary(yaml_data["parser"]["llm_client"])
        infer_missing_steps = yaml_data["parser"]["infer_missing_steps"]

        executor_clients = yaml_data["executor"]["llm_clients"]
        assertion_generation = ClientRegistry()
        assertion_generation.set_primary(executor_clients["assertion_generation"])

        assertion_api = ClientRegistry()
        assertion_api.set_primary(executor_clients["assertion_api"])

        action_proposer = ClientRegistry()
        action_proposer.set_primary(executor_clients["action_proposer"])

        som_cfg = yaml_data["executor"].get("som", {})
        ui_locator = ClientRegistry()
        ui_locator.set_primary(som_cfg.get("ui_locator", "GUI_Grounding_Model"))

        page_reidentification = ClientRegistry()
        page_reidentification.set_primary(executor_clients["page_reidentification"])

        max_tries = yaml_data["executor"]["max_tries"]

        mode = yaml_data["executor"].get("mode", "browser-use")

        playwright_codegen_cfg = yaml_data["executor"].get("playwright_codegen", {})
        playwright_codegen = ClientRegistry()
        playwright_codegen.set_primary(
            playwright_codegen_cfg.get(
                "llm_client",
                executor_clients.get("action_proposer", "GPT"),
            )
        )
        playwright_codegen_max_revisions = int(
            playwright_codegen_cfg.get("max_revisions", 1)
        )
        playwright_codegen_timeout_ms = int(
            playwright_codegen_cfg.get("timeout_ms", 5000)
        )

        browser_use_cfg = yaml_data["executor"].get("browser_use", {})
        browser_use_agent = browser_use_cfg.get("llm_client", "Claude")
        browser_use_cdp_url = browser_use_cfg.get("cdp_url", "") or ""
        browser_use_max_steps = int(browser_use_cfg.get("max_steps", 1))

        return Config(
            parser=parser,
            assertion_generation=assertion_generation,
            assertion_api=assertion_api,
            action_proposer=action_proposer,
            ui_locator=ui_locator,
            page_reidentification=page_reidentification,
            infer_missing_steps=infer_missing_steps,
            max_tries=max_tries,
            mode=mode,
            playwright_codegen=playwright_codegen,
            playwright_codegen_max_revisions=playwright_codegen_max_revisions,
            playwright_codegen_timeout_ms=playwright_codegen_timeout_ms,
            browser_use_agent=browser_use_agent,
            browser_use_cdp_url=browser_use_cdp_url,
            browser_use_max_steps=browser_use_max_steps,
        )
