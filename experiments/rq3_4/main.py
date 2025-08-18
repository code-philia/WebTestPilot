import sys
from pathlib import Path
from enum import Enum
from typing import Optional

# Ensure repo root and webtestpilot/src are importable
REPO_ROOT = Path(__file__).resolve().parents[2]
WEBTESTPILOT_SRC = REPO_ROOT / "webtestpilot" / "src"
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))
if str(WEBTESTPILOT_SRC) not in sys.path:
    sys.path.append(str(WEBTESTPILOT_SRC))

import typer
from typing_extensions import Annotated
from testcases.baselines.const import ApplicationEnum
from experiments.rq3_4.runner import WebTestPilotTestRunner_RQ3_4

from main import Config


class TransformationEnum(str, Enum):
    default = "default"
    add_noise = "add_noise"
    dropout = "dropout"
    restyle = "restyle"
    summarize = "summarize"


cli = typer.Typer(
    help="Run test cases using different agent implementations",
    no_args_is_help=True,
)


@cli.command()
def main(
    application: Annotated[
        ApplicationEnum, typer.Argument(help="The application to test")
    ],
    transformation: Annotated[
        TransformationEnum, typer.Argument(help="The input transformation")
    ],
    config_path: Annotated[
        Optional[Path],
        typer.Option(
            "--config-path",
            "-c",
            help="Custom YAML config path for WebTestPilot",
        ),
    ] = None,
):
    base = Path(__file__).parent

    # Config
    config = Config.load(config_path)

    # Test cases directory
    test_case_path = base / "input" / application.value / transformation.value

    # Output directory
    test_output_path = (
        base / f"{config.parser}_{application.value}_{transformation.value}.json"
    )

    runner = WebTestPilotTestRunner_RQ3_4(
        test_case_path=str(test_case_path),
        test_output_path=str(test_output_path),
        application=application.value,
        config=config,
        headless=True,
    )
    runner.run_test_cases()


if __name__ == "__main__":
    main()
