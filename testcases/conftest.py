import subprocess
from pathlib import Path

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--no-seed",
        action="store_true",
        default=False,
        help="Skip seeding initial data when starting applications",
    )


def detect_app_from_test_path(test_path: str):
    path = Path(test_path)

    # Extract the directory name containing the test
    for parent in path.parents:
        if parent.name in ["bookstack", "invoiceninja", "indico", "prestashop"]:
            return parent.name
    return None


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """Restart app from fresh before all tests."""
    app_name = detect_app_from_test_path(str(item.fspath))

    if not app_name:
        return

    SCRIPT_PATH = Path(__file__).parent.parent / "webapps" / "start_app.sh"

    cmd = ["bash", str(SCRIPT_PATH), app_name]
    if item.config.getoption("--no-seed"):
        cmd.append("--no-seed")

    result = subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        check=True,
    )

    if result.returncode != 0:
        print(f"Failed to start application {app_name}")
        if result.stderr:
            print(f"Script error: {result.stderr}")
        pytest.fail(f"Failed to start application: {app_name}")
        return

    print(f"Application {app_name} started successfully.")
