import os
import json
import time
import shutil
import socket
import logging
import tempfile
import subprocess
import urllib.request
from pathlib import Path
from typing import Optional

from playwright.sync_api import Playwright, Browser, BrowserContext, Page

from baselines.const import ApplicationEnum, Viewport

PROJECT_DIR = Path(__file__).parent.parent
BENCHMARK_DIR = PROJECT_DIR / "benchmark"
RUNTIME_FILES = ["browser.Dockerfile", "init.py", "bug_injector.js"]

logger = logging.getLogger(__name__)


# The benchmark's browser service serves CDP at browser:9222 and rewrites the
# WebSocket URLs it returns to ws://browser:9222/, which only resolves inside the
# compose network. This proxy publishes CDP on a host port and rewrites those URLs
# again so host-side clients (Playwright, Selenium, browser-use) can follow them.
CDP_PROXY_CONF = """\
events {{}}
http {{
    map $http_upgrade $connection_upgrade {{
        default upgrade;
        ''      close;
    }}
    server {{
        listen 9222;
        location / {{
            proxy_pass         http://browser:9222;
            proxy_http_version 1.1;
            proxy_set_header   Upgrade         $http_upgrade;
            proxy_set_header   Connection      $connection_upgrade;
            proxy_set_header   Accept-Encoding "";
            proxy_read_timeout 3600s;
            proxy_send_timeout 3600s;
            sub_filter         '"ws://browser:9222/' '"ws://127.0.0.1:{port}/';
            sub_filter_once    off;
            sub_filter_types   application/json;
        }}
    }}
}}
"""

CDP_PROXY_COMPOSE = """\
services:
  cdp-proxy:
    image: nginx:1.27-alpine
    ports:
      - "127.0.0.1:{port}:9222"
    volumes:
      - ./cdp-proxy.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - browser
"""


def _free_port() -> int:
    """Return an OS-assigned free TCP port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class TaskEnvironment:
    """
    An isolated Docker Compose stack for one test case, assembled from the benchmark
    submodule: `<app>/environment/` plus the shared files in `runtime/`.

    The stack's browser service seeds the app, runs the test case's setup function,
    and registers the bug script (if any) before exposing CDP, so the browser is
    ready for the agent as soon as `start` returns.
    """

    def __init__(
        self,
        application: ApplicationEnum,
        setup_function: str,
        bug_path: Optional[Path],
        log_path: Path,
        startup_timeout: float = 900,
    ):
        self.application = application
        self.setup_function = setup_function
        self.bug_path = bug_path
        self.log_path = log_path
        self.startup_timeout = startup_timeout
        # A stable project name per app reuses built images across test cases.
        self.project = f"wtp-{application.value}"
        self.port = _free_port()
        self.cdp_url = f"http://127.0.0.1:{self.port}"
        self.task_dir: Optional[Path] = None


    def start(self) -> str:
        """Bring up the stack and return the host CDP URL of its browser."""
        self.task_dir = Path(tempfile.mkdtemp(prefix=f"{self.project}-"))
        self._assemble(self.task_dir)

        # Clear leftovers from an interrupted run before starting fresh.
        self._compose("down", "--volumes", "--remove-orphans", check=False)

        logger.info(f"Starting {self.application.value} environment ({self.project})")
        self._compose("up", "--detach", "--build", "--quiet-pull")
        self._wait_until_ready()
        logger.info(f"Environment ready, CDP at {self.cdp_url}")
        return self.cdp_url


    def stop(self) -> None:
        """Save the stack's logs, then remove its containers, volumes, and task directory."""
        if self.task_dir is None:
            return

        try:
            logs = self._compose("logs", "--no-color", "--timestamps", check=False)
            self.log_path.write_text(logs.stdout + logs.stderr, encoding="utf-8")
        except Exception as e:
            logger.warning("Failed to save environment logs: %s", e)

        self._compose("down", "--volumes", "--remove-orphans", "--timeout", "5", check=False)
        shutil.rmtree(self.task_dir, ignore_errors=True)
        self.task_dir = None


    def _assemble(self, task_dir: Path) -> None:
        app_environment_dir = BENCHMARK_DIR / self.application.value / "environment"
        if not app_environment_dir.is_dir():
            raise FileNotFoundError(
                f"{app_environment_dir} not found. Run `git submodule update --init` to fetch the benchmark."
            )

        shutil.copytree(app_environment_dir, task_dir, dirs_exist_ok=True)
        for name in RUNTIME_FILES:
            shutil.copy2(BENCHMARK_DIR / "runtime" / name, task_dir / name)

        # The browser service always mounts ./bug.js, so it must exist even without a bug.
        bug_js = self.bug_path.read_text(encoding="utf-8") if self.bug_path else ""
        (task_dir / "bug.js").write_text(bug_js, encoding="utf-8")

        (task_dir / "cdp-proxy.conf").write_text(CDP_PROXY_CONF.format(port=self.port))
        (task_dir / "docker-compose.override.yaml").write_text(CDP_PROXY_COMPOSE.format(port=self.port))


    def _compose(self, *args: str, check: bool = True) -> subprocess.CompletedProcess:
        env = {
            "INJECT_BUG": "true" if self.bug_path else "false",
            "SETUP_FUNCTION": self.setup_function,
        }
        result = subprocess.run(
            ["docker", "compose", "--project-name", self.project, *args],
            cwd=self.task_dir,
            env={**os.environ, **env},
            text=True,
            capture_output=True,
        )
        if check and result.returncode != 0:
            raise RuntimeError(
                f"`docker compose {' '.join(args)}` failed (returncode={result.returncode}).\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )
        return result


    def _wait_until_ready(self) -> None:
        """Wait until the browser exposes CDP, which init.py does only after setup completes."""
        deadline = time.monotonic() + self.startup_timeout
        while time.monotonic() < deadline:
            if self._is_cdp_ready():
                return

            failed = self._failed_services()
            if failed:
                raise RuntimeError(f"Environment services failed: {failed}. See {self.log_path}")

            time.sleep(2)

        raise TimeoutError(f"Environment not ready after {self.startup_timeout}s. See {self.log_path}")


    def _is_cdp_ready(self) -> bool:
        try:
            with urllib.request.urlopen(f"{self.cdp_url}/json/version", timeout=2) as response:
                return "webSocketDebuggerUrl" in json.load(response)
        except Exception:
            return False


    def _failed_services(self) -> list[str]:
        """One-shot services that exited non-zero, and services stuck restarting."""
        result = self._compose("ps", "--all", "--format", "json", check=False)
        failed = []
        for line in result.stdout.splitlines():
            try:
                container = json.loads(line)
            except json.JSONDecodeError:
                continue

            state, exit_code = container.get("State"), container.get("ExitCode", 0)
            if (state == "exited" and exit_code != 0) or state == "restarting":
                failed.append(container.get("Service", container.get("Name", "?")))
        return failed


def connect_to_environment(playwright: Playwright, cdp_url: str) -> tuple[Browser, BrowserContext, Page]:
    """Attach to the environment's browser and return its already set-up page."""
    browser = playwright.chromium.connect_over_cdp(cdp_url)
    browser_context = browser.contexts[0]
    page = browser_context.pages[0]
    page.set_viewport_size({"width": Viewport.WIDTH, "height": Viewport.HEIGHT})
    return browser, browser_context, page
