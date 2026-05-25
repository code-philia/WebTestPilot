from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml
from baml_py import ClientRegistry

from webtestpilot.action_api import execute_action
from webtestpilot.action_api.playwright_codegen import (
    PlaywrightCodeGeneration,
    _execute_generated_code,
    _parse_generation,
    _validate_generated_code,
)
from webtestpilot.config import Config


def test_config_loads_playwright_codegen_settings(tmp_path):
    config_data = yaml.safe_load(
        """
parser:
  llm_client: GPT
  infer_missing_steps: false
executor:
  mode: playwright-code-gen
  max_tries: 1
  playwright_codegen:
    llm_client: OpenRouter
    max_revisions: 2
    timeout_ms: 7000
  llm_clients:
    assertion_generation: GPT
    assertion_api: GPT
    action_proposer: GPT
    page_reidentification: GPT
"""
    )
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config_data), encoding="utf-8")

    config = Config.load(config_path)

    assert config.mode == "playwright-code-gen"
    assert isinstance(config.playwright_codegen, ClientRegistry)
    assert config.playwright_codegen_max_revisions == 2
    assert config.playwright_codegen_timeout_ms == 7000


def test_execute_action_dispatches_playwright_codegen(monkeypatch):
    calls = []

    def fake_execute(session, action):
        calls.append((session, action))

    monkeypatch.setattr(
        "webtestpilot.action_api.playwright_codegen.execute_action_playwright_codegen",
        fake_execute,
    )
    session = SimpleNamespace(config=SimpleNamespace(mode="playwright-code-gen"))

    execute_action(session, "Click the Submit button")

    assert calls == [(session, "Click the Submit button")]


def test_parse_generation_accepts_json_fenced_response():
    generation = _parse_generation(
        """```json
{"code": "page.get_by_text('Save').click(timeout=3000)", "rationale": "Use text", "expected_effect": "Saved"}
```"""
    )

    assert generation == PlaywrightCodeGeneration(
        code="page.get_by_text('Save').click(timeout=3000)",
        rationale="Use text",
        expected_effect="Saved",
    )


def test_execute_generated_code_runs_sync_playwright_body():
    class FakeTextLocator:
        def __init__(self):
            self.clicked = False

        def click(self, timeout=0):
            self.clicked = timeout

    class FakePage:
        def __init__(self):
            self.locator = FakeTextLocator()

        def get_by_text(self, text):
            assert text == "Save"
            return self.locator

    page = FakePage()
    trace = _execute_generated_code(
        "helpers.log('about to click')\npage.get_by_text('Save').click(timeout=3000)",
        page,
    )

    assert page.locator.clicked == 3000
    assert trace == [{"action": "log", "message": "about to click"}]


def test_validate_generated_code_rejects_loops():
    with pytest.raises(ValueError, match="For"):
        _validate_generated_code("for _ in range(10):\n    helpers.log('loop')")

    with pytest.raises(ValueError, match="While"):
        _validate_generated_code("while True:\n    pass")


def test_prompt_uses_paper_style_terms():
    prompt_path = (
        Path(__file__).resolve().parents[1]
        / "baml_src"
        / "action_api"
        / "playwright_codegen.baml"
    )
    text = prompt_path.read_text(encoding="utf-8")

    assert "later verifier" not in text
    assert "Hard rules" not in text
    assert "WebTestPilot's assertion API" in text
