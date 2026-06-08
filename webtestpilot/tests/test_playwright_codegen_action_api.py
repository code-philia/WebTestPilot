from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml
from baml_py import ClientRegistry

from webtestpilot.action_api import execute_action
from webtestpilot.action_api.playwright_codegen import (
    PlaywrightCodeGeneration,
    _build_page_observation,
    _build_page_snapshot,
    execute_action_playwright_codegen,
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
    snapshot_fallback_after_attempts: 4
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
    assert config.playwright_codegen_snapshot_fallback_after_attempts == 4
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


def test_build_page_snapshot_uses_playwright_ai_mode():
    class FakePage:
        def __init__(self):
            self.calls = []

        def aria_snapshot(self, **kwargs):
            self.calls.append(kwargs)
            return "- textbox \"Search\" [ref=e2]"

    page = FakePage()

    assert _build_page_snapshot(page) == "- textbox \"Search\" [ref=e2]"
    assert page.calls == [{"mode": "ai", "timeout": 5000}]


def test_build_page_snapshot_truncates_long_snapshot():
    class FakePage:
        def aria_snapshot(self, **kwargs):
            return "x" * 20

    assert _build_page_snapshot(FakePage(), limit=10) == "xxxxxxxxxx\n... truncated ..."


def test_build_page_observation_falls_back_to_dom_when_snapshot_unavailable():
    class FakePage:
        def aria_snapshot(self, **kwargs):
            raise AttributeError("aria_snapshot unavailable")

        def evaluate(self, script):
            return [{"tag": "button", "text": "Save"}]

    observation, source = _build_page_observation(FakePage())

    assert source == "fallback-dom-summary"
    assert "Observation source: fallback-dom-summary" in observation
    assert '"text": "Save"' in observation


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

    with pytest.raises(ValueError, match="ListComp"):
        _validate_generated_code("[helpers.log(str(i)) for i in range(3)]")


def test_validate_generated_code_rejects_unsafe_waits_and_unknown_calls():
    with pytest.raises(ValueError, match="timeout"):
        _validate_generated_code("page.get_by_role('button', name='Save').click()")

    with pytest.raises(ValueError, match="timeout value"):
        _validate_generated_code("page.get_by_text('Save').click(timeout=600000)")

    with pytest.raises(ValueError, match="wait_for_timeout"):
        _validate_generated_code("page.wait_for_timeout(60000)")

    with pytest.raises(ValueError, match="Unsupported call root"):
        _validate_generated_code("time.sleep(60)")

    with pytest.raises(ValueError, match="page.evaluate"):
        _validate_generated_code("page.evaluate('document.body.innerHTML = \"\"')")

    with pytest.raises(ValueError, match="evaluate"):
        _validate_generated_code("page.locator('body').evaluate('el => el.remove()')")

    with pytest.raises(ValueError, match="page.goto"):
        _validate_generated_code("page.goto('https://example.com')")

    with pytest.raises(ValueError, match="page.context"):
        _validate_generated_code("page.context.new_page()")

    with pytest.raises(ValueError, match="reserved runtime name"):
        _validate_generated_code("helpers = page\nhelpers.evaluate('1')")

    with pytest.raises(ValueError, match="timeout value"):
        _validate_generated_code("page.get_by_text('Save').click(timeout=True)")


def test_validate_generated_code_allows_safe_builtin_calls():
    _validate_generated_code(
        "helpers.log(str(len(['a', 'b'])))\n"
        "page.get_by_text('Save').click(timeout=3000)"
    )


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


def test_generation_parse_failure_is_retried(monkeypatch):
    class FakePage:
        pass

    class FakeConfig:
        playwright_codegen = object()
        playwright_codegen_max_revisions = 1
        playwright_codegen_snapshot_fallback_after_attempts = 3
        playwright_codegen_timeout_ms = 1000

    session = SimpleNamespace(
        page=FakePage(),
        config=FakeConfig(),
        collector=object(),
        trace=[],
        capture_state=lambda prev_action: None,
    )
    calls = []

    def fake_propose(**kwargs):
        calls.append(kwargs["previous_failure"])
        if len(calls) == 1:
            raise ValueError("not json")
        return PlaywrightCodeGeneration(
            code="helpers.log('recovered')",
            rationale="Recovered after invalid JSON",
            expected_effect="Action runs",
        )

    monkeypatch.setattr(
        "webtestpilot.action_api.playwright_codegen._propose_playwright_code",
        fake_propose,
    )
    monkeypatch.setattr(
        "webtestpilot.action_api.playwright_codegen._execute_generated_code",
        lambda code, page: [{"action": "log", "message": "recovered"}],
    )
    monkeypatch.setattr(
        "webtestpilot.action_api.playwright_codegen._wait_after_generated_action",
        lambda page, timeout_ms: None,
    )

    execute_action_playwright_codegen(session, "Click Save")

    assert calls[0] is None
    assert calls[1]["kind"] == "generation_failed"
    assert session.trace[-1] == {"action": "log", "message": "recovered"}


def test_falls_back_to_dom_observation_after_configured_snapshot_attempts(monkeypatch):
    class FakePage:
        pass

    class FakeConfig:
        playwright_codegen = object()
        playwright_codegen_max_revisions = 3
        playwright_codegen_snapshot_fallback_after_attempts = 3
        playwright_codegen_timeout_ms = 1000

    session = SimpleNamespace(
        page=FakePage(),
        config=FakeConfig(),
        collector=object(),
        trace=[],
        capture_state=lambda prev_action: None,
    )
    observation_modes = []

    def fake_propose(**kwargs):
        observation_modes.append(kwargs["observation_mode"])
        if len(observation_modes) < 4:
            raise ValueError("generation failed")
        return PlaywrightCodeGeneration(
            code="helpers.log('dom fallback recovered')",
            rationale="Recovered using fallback DOM observation",
            expected_effect="Action runs",
        )

    monkeypatch.setattr(
        "webtestpilot.action_api.playwright_codegen._propose_playwright_code",
        fake_propose,
    )
    monkeypatch.setattr(
        "webtestpilot.action_api.playwright_codegen._execute_generated_code",
        lambda code, page: [{"action": "log", "message": "dom fallback recovered"}],
    )
    monkeypatch.setattr(
        "webtestpilot.action_api.playwright_codegen._wait_after_generated_action",
        lambda page, timeout_ms: None,
    )

    execute_action_playwright_codegen(session, "Click Save")

    assert observation_modes == [
        "playwright-ai-snapshot",
        "playwright-ai-snapshot",
        "playwright-ai-snapshot",
        "fallback-dom-summary",
    ]
    assert session.trace[-1] == {"action": "log", "message": "dom fallback recovered"}


def test_model_reported_error_is_retried_until_dom_fallback(monkeypatch):
    class FakePage:
        pass

    class FakeConfig:
        playwright_codegen = object()
        playwright_codegen_max_revisions = 3
        playwright_codegen_snapshot_fallback_after_attempts = 3
        playwright_codegen_timeout_ms = 1000

    session = SimpleNamespace(
        page=FakePage(),
        config=FakeConfig(),
        collector=object(),
        trace=[],
        capture_state=lambda prev_action: None,
    )
    observation_modes = []

    def fake_propose(**kwargs):
        observation_modes.append(kwargs["observation_mode"])
        if len(observation_modes) < 4:
            return PlaywrightCodeGeneration(
                output_type="error",
                code="",
                rationale="Target not visible in snapshot",
                expected_effect="Action would run",
                error_type="target_ui_unavailable",
                target="Save button",
                message="No matching control in snapshot",
            )
        return PlaywrightCodeGeneration(
            code="helpers.log('dom fallback recovered')",
            rationale="Recovered using fallback DOM observation",
            expected_effect="Action runs",
        )

    monkeypatch.setattr(
        "webtestpilot.action_api.playwright_codegen._propose_playwright_code",
        fake_propose,
    )
    monkeypatch.setattr(
        "webtestpilot.action_api.playwright_codegen._execute_generated_code",
        lambda code, page: [{"action": "log", "message": "dom fallback recovered"}],
    )
    monkeypatch.setattr(
        "webtestpilot.action_api.playwright_codegen._wait_after_generated_action",
        lambda page, timeout_ms: None,
    )

    execute_action_playwright_codegen(session, "Click Save")

    assert observation_modes == [
        "playwright-ai-snapshot",
        "playwright-ai-snapshot",
        "playwright-ai-snapshot",
        "fallback-dom-summary",
    ]
    assert session.trace[-1] == {"action": "log", "message": "dom fallback recovered"}
