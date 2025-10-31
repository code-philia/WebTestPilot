import yaml
import logging.config
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from dotenv import load_dotenv

from baml_py import ClientRegistry


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Config:
    parser: ClientRegistry
    assertion_generation: ClientRegistry
    assertion_api: ClientRegistry
    action_proposer: ClientRegistry
    action_proposer_name: str
    ui_locator: ClientRegistry
    page_reidentification: ClientRegistry

    infer_missing_steps: bool
    max_tries: int

    @staticmethod
    def load(path: Path | str) -> "Config":
        # Load environment variables
        load_dotenv()

        # Load YAML config
        yaml_path = Path(path)
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
        action_proposer_name = executor_clients["action_proposer"]

        action_proposer = ClientRegistry()
        action_proposer.set_primary(action_proposer_name)

        ui_locator = ClientRegistry()
        ui_locator.set_primary(executor_clients["ui_locator"])

        page_reidentification = ClientRegistry()
        page_reidentification.set_primary(executor_clients["page_reidentification"])

        max_tries = yaml_data["executor"]["max_tries"]

        logging.config.dictConfig(yaml_data.get("logging", {}))

        return Config(
            parser=parser,
            assertion_generation=assertion_generation,
            assertion_api=assertion_api,
            action_proposer_name=action_proposer_name,
            action_proposer=action_proposer,
            ui_locator=ui_locator,
            page_reidentification=page_reidentification,
            infer_missing_steps=infer_missing_steps,
            max_tries=max_tries,
        )
