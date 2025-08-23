import sys
from pathlib import Path
from enum import Enum
from typing import Optional

# Add project directory
PROJECT_DIR = Path(__file__).parent.parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.append(str(PROJECT_DIR))

# Add webtestpilot directory
WEBTESTPILOT_DIR = PROJECT_DIR / "webtestpilot" / "src"
if str(WEBTESTPILOT_DIR) not in sys.path:
    sys.path.append(str(WEBTESTPILOT_DIR))

import typer
from typing_extensions import Annotated
from baselines.const import ApplicationEnum
from runner import WebTestPilotTestRunner

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

    runner = WebTestPilotTestRunner(
        test_case_path=str(test_case_path),
        test_output_path=str(test_output_path),
        application=application.value,
        model=None,
        headless=True,
        config=config
    )
    runner.run_all_test_cases()


if __name__ == "__main__":
    cli()
