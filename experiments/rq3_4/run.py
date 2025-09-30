import asyncio
import inspect
import sys
from enum import Enum
from functools import partial, wraps
from pathlib import Path
from typing import Any, Callable, Optional

# Add project directory
PROJECT_DIR = Path(__file__).parent.parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.append(str(PROJECT_DIR))

# Add webtestpilot directory
WEBTESTPILOT_DIR = PROJECT_DIR / "webtestpilot" / "src"
if str(WEBTESTPILOT_DIR) not in sys.path:
    sys.path.append(str(WEBTESTPILOT_DIR))

import typer
from baselines.const import ApplicationEnum
from main import Config
from typing_extensions import Annotated

from runner import WebTestPilotTestRunner


class TransformationEnum(str, Enum):
    default = "default"
    add_noise = "add_noise"
    dropout = "dropout"
    restyle = "restyle"
    summarize = "summarize"


# Source: https://github.com/fastapi/typer/issues/950#issuecomment-2646361943
class AsyncTyper(typer.Typer):
    @staticmethod
    def maybe_run_async(decorator: Callable, func: Callable) -> Any:
        if inspect.iscoroutinefunction(func):

            @wraps(func)
            def runner(*args: Any, **kwargs: Any) -> Any:
                return asyncio.run(func(*args, **kwargs))

            decorator(runner)
        else:
            decorator(func)
        return func

    def callback(self, *args: Any, **kwargs: Any) -> Any:
        decorator = super().callback(*args, **kwargs)
        return partial(self.maybe_run_async, decorator)

    def command(self, *args: Any, **kwargs: Any) -> Any:
        decorator = super().command(*args, **kwargs)
        return partial(self.maybe_run_async, decorator)


cli = AsyncTyper(
    help="Run test cases using different agent implementations",
    no_args_is_help=True,
)


@cli.command()
async def main(
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
        config=config,
    )
    await runner.run_all_test_cases()


if __name__ == "__main__":
    cli()
