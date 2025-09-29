import subprocess
from pathlib import Path

import pytest


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
    test_path = str(item.fspath)
    app_name = detect_app_from_test_path(test_path)

    if app_name:
        print(f"Detected application: {app_name} for test: {item.name}")
        SCRIPT_PATH = Path(__file__).parent.parent / "webapps" / "start_app.sh"

        result = subprocess.run(
            ["bash", SCRIPT_PATH, app_name],
            capture_output=True,
            text=True,
            timeout=600,
        )

        if result.returncode != 0:
            print(f"Failed to start application {app_name}")
            if result.stderr:
                print(f"Script error: {result.stderr}")
            pytest.fail(f"Failed to start application: {app_name}")

        print(f"Application {app_name} started successfully.")
