from typing import Optional
from pathlib import Path
from pydantic import BaseModel

from baselines.const import ApplicationEnum, MethodEnum


class MethodConfig(BaseModel):
    method: MethodEnum
    # Target application under test
    application: ApplicationEnum
    # Result output dir for all test cases in the run
    run_output_dir: Path
    # Run browser in headless mode
    headless: bool
    # Inject bug from bug path for all test cases in the run
    inject_bug: bool


class PinataConfig(MethodConfig):
    method: MethodEnum = MethodEnum.pinata
    # Optional LLM model identifier
    model: Optional[str] = "gpt-4.1"
    # Save screenshots during execution
    save_screenshot: bool = True
    # Enable internal tracing
    tracer: bool = True
    # Max tries per test step
    max_tries: int = 1
    # Whether to check expectation in test steps and report bug(s)
    assertion: bool = True


class NaviqateConfig(MethodConfig):
    method: MethodEnum = MethodEnum.naviqate
    # Optional LLM model identifier
    model: Optional[str] = "gpt-4.1"
    # Maximum crawler loop steps per action
    max_steps: int = 1
    # Use abstracted action representation
    abstracted: bool = False
    # Remote chrome browser debugging port
    browser_script_path: Path = Path(__file__).parent / "naviqate" / "browser.sh"


class LavagueConfig(MethodConfig):
    method: MethodEnum = MethodEnum.lavague
    # Optional LLM model identifier
    model: Optional[str] = "gpt-4.1"

    
class WebTestPilotConfig(MethodConfig):
    method: MethodEnum = MethodEnum.webtestpilot
    # Optional WebTestPilot YAML configuration
    config_path: Optional[Path] = Path(__file__).parent.parent / "webtestpilot" / "src" / "webtestpilot" / "config.yaml"
    # Whether to check expectation in test steps and report bug(s)
    assertion: bool = True
    # Whether to enable parser (will convert steps into a single string paragraph)
    parser: bool = False