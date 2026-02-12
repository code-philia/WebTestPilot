import re
from pathlib import Path


BUG_TEMPLATE_PATH = Path(__file__).parent / "bug_injector.js"


def prepare_bug_script(bug_path: Path) -> str:
    """
    Prepare a JavaScript bug injection script by merging user-defined function blocks into a template.

    Args:
        bug_path (Path): Path to the user-defined JS file containing function blocks.

    Returns:
        str: The merged JavaScript code as a string with the user functions injected into the template.
    """
    bug_code = bug_path.read_text()
    is_condition_met = re.findall(r"// BEGIN isConditionMet\s*(.*?)\s*// END isConditionMet", bug_code, re.DOTALL)
    on_condition_met = re.findall(r"// BEGIN onConditionMet\s*(.*?)\s*// END onConditionMet", bug_code, re.DOTALL)

    bug_template = BUG_TEMPLATE_PATH.read_text()
    bug_template = bug_template.replace(r"const isConditionMet = () => {};", is_condition_met[-1])
    bug_template = bug_template.replace(r"const onConditionMet = () => {};", on_condition_met[-1])
    return bug_template