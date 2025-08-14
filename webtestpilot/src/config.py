import yaml
import logging.config
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from dotenv import load_dotenv

from baml_py import ClientRegistry


@dataclass(frozen=True)
class Config:
    parser: ClientRegistry
    assertion_generation: ClientRegistry
    assertion_api: ClientRegistry
    action_proposer: ClientRegistry
    action_proposer_name: str
    ui_locator: ClientRegistry
    page_reidentification: ClientRegistry
    max_retries: int

    @staticmethod
    def load(path: Path | str) -> "Config":
        # Load environment variables
        load_dotenv()

        # Load YAML config
        yaml_path = Path(path)
        with yaml_path.open("r") as f:
            yaml_data: dict[str, Any] = yaml.safe_load(f) or {}

        # LLM client configurations
        parser = ClientRegistry().set_primary(yaml_data["parser"]["llm_client"])
        executor_clients = yaml_data["executor"]["llm_clients"]
        assertion_generation = ClientRegistry().set_primary(
            executor_clients["assertion_generation"]
        )
        assertion_api = ClientRegistry().set_primary(executor_clients["assertion_api"])
        action_proposer_name = executor_clients["action_proposer"]
        action_proposer = ClientRegistry().set_primary(action_proposer_name)
        ui_locator = ClientRegistry().set_primary(executor_clients["ui_locator"])
        page_reidentification = ClientRegistry().set_primary(
            executor_clients["page_reidentification"]
        )
        max_retries = yaml_data["max_retries"]

        # Apply logging config if present
        logging_cfg = yaml_data.get("logging")
        if logging_cfg:
            logging.config.dictConfig(logging_cfg)

        return Config(
            parser=parser,
            assertion_generation=assertion_generation,
            assertion_api=assertion_api,
            action_proposer_name=action_proposer_name,
            action_proposer=action_proposer,
            ui_locator=ui_locator,
            page_reidentification=page_reidentification,
            max_retries=max_retries,
        )
