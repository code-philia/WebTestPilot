from collections.abc import Generator
from playwright.async_api import async_playwright
import pytest
from VTAAS.data.testcase import TestCase, TestCaseCollection
from VTAAS.orchestrator import Orchestrator
from unittest.mock import AsyncMock, MagicMock

from VTAAS.orchestrator.orchestrator import TestExecutionContext
from VTAAS.schemas.llm import (
    LLMTestStepPlanResponse,
    MessageRole,
    SequenceType,
    WorkerConfig,
    WorkerType,
)
from VTAAS.schemas.verdict import (
    ActorAction,
    ActorResult,
    AssertorResult,
    Status,
    WorkerResult,
)
from VTAAS.llm.openai_client import OpenAILLMClient
from VTAAS.workers.actor import Actor
from VTAAS.workers.browser import Browser


@pytest.fixture
def mock_history() -> list[str]:
    return ["did this initially", "eventually did that"]


def llm_plan_response_generator() -> Generator[LLMTestStepPlanResponse, None, None]:
    responses = [
        LLMTestStepPlanResponse(
            current_step_analysis="step analysis 1",
            screenshot_analysis="screenshot analysis 1",
            previous_actions_analysis="previous actions analysis 1",
            workers=[
                WorkerConfig(
                    type=WorkerType.ACTOR, query="type 'user1' in username field"
                ),
                WorkerConfig(
                    type=WorkerType.ASSERTOR, query="username field contains 'user1'"
                ),
            ],
            sequence_type=SequenceType.full,
        ),
    ]
    for response in responses:
        yield response


@pytest.fixture
def mock_llm_client() -> OpenAILLMClient:
    mock_instance: OpenAILLMClient = AsyncMock(spec=OpenAILLMClient)
    response_generator = llm_plan_response_generator()
    mock_instance.plan = AsyncMock(side_effect=lambda _: next(response_generator))
    return mock_instance


@pytest.fixture
def mock_test_case() -> TestCase:
    mock_instance = MagicMock(
        spec=TestCase,
        id="1",
        type="P",
        full_name="Test Case 1",
        actions=["Action 1", "Action 2"],
        expected_results=["Result 1", "Result 2"],
        url="http://example.com",
        steps=list(zip(["Action 1", "Action 2"], ["Result 1", "Result 2"])),
    )

    mock_instance.name = "test case 1"
    mock_instance.__str__.return_value = (
        "content of test case 1\n1. Action 1 ; Assert 1\n2. Action 2; Assert 2"
    )
    mock_instance.get_step.return_value = ["Action 1", "Result 1"]
    return mock_instance


@pytest.fixture
def mock_browser() -> Browser:
    mock_instance = AsyncMock(spec=Browser)
    mock_instance.click.side_effect = lambda label: f"clicked on {label}"
    mock_instance.fill.side_effect = lambda field, value: f"filled '{value}' in {field}"
    mock_instance.select.side_effect = (
        lambda field, value: f"selected '{value}' in {field}"
    )
    mock_instance.goto.side_effect = lambda url: f"navigated to '{url}'"
    mock_instance.vertical_scroll.side_effect = (
        lambda direction: f"Scrolled '{direction}'"
    )
    mock_instance.screenshot.side_effect = [b"1", b"2", b"3"]
    mock_instance.mark_page = AsyncMock()

    return mock_instance


@pytest.fixture
def empty_orchestrator(
    mock_llm_client: OpenAILLMClient,
) -> Orchestrator:
    return Orchestrator()


@pytest.mark.asyncio
async def test_user_prompt(
    empty_orchestrator: Orchestrator, mock_test_case: TestCase, mock_history: list[str]
):
    """Test main prompt builds itself"""
    page_info = "page info"
    viewport_info = "top of the page"
    context = TestExecutionContext(
        test_case=mock_test_case,
        current_step=mock_test_case.get_step(2),
        step_index=2,
        history=mock_history,
    )
    prompt = empty_orchestrator._build_user_init_prompt(
        context, page_info, viewport_info
    )
    action, assertion = context.current_step
    test_step = f"{context.step_index}. action: {action}, assertion: {assertion}"
    assert f"<test_case>\n{context.test_case.__str__()}\n</test_case>" in prompt
    assert f"<current_step>\n{test_step}\n</current_step>" in prompt
    assert page_info in prompt
    assert viewport_info in prompt
    for history in mock_history:
        assert history in prompt


@pytest.mark.asyncio
async def test_conversation(
    empty_orchestrator: Orchestrator, mock_test_case: TestCase, mock_history: list[str]
):
    """Test prompt builds itself"""
    context = TestExecutionContext(
        test_case=mock_test_case,
        current_step=mock_test_case.get_step(3),
        step_index=3,
        history=mock_history,
    )
    fake_screenshot = b"screen"
    page_info = "page info"
    viewport_info = "top of the page"
    empty_orchestrator._setup_conversation(
        context, fake_screenshot, page_info, viewport_info
    )
    assert empty_orchestrator.conversation[0].role == MessageRole.System
    assert (
        "Your role is to analyze test steps"
        in empty_orchestrator.conversation[0].content
    )
    assert empty_orchestrator.conversation[0].screenshot is None
    assert empty_orchestrator.conversation[1].role == MessageRole.User
    assert (
        "Plan for the current test step" in empty_orchestrator.conversation[1].content
    )
    for history in mock_history:
        assert history in empty_orchestrator.conversation[1].content
    assert empty_orchestrator.conversation[1].screenshot is not None
    assert len(empty_orchestrator.conversation[1].screenshot) == 1
    assert empty_orchestrator.conversation[1].screenshot[0] == fake_screenshot


@pytest.fixture
def mock_actor() -> Browser:
    mock_instance = AsyncMock(spec=Actor)
    mock_instance.process.side_effect = lambda label: f"clicked on {label}"
    return mock_instance


def test_merge_worker_results_success(empty_orchestrator: Orchestrator):
    actor_action_1 = ActorAction(action="move", chain_of_thought="Plan to move forward")
    actor_action_2 = ActorAction(
        action="click", chain_of_thought="We have to click somewhere"
    )
    actor_result = ActorResult(
        query="search data",
        status=Status.PASS,
        explaination="All good",
        screenshot=b"actor screenshot",
        actions=[actor_action_1, actor_action_2],
    )
    assertor_result = AssertorResult(
        query="validate result",
        status=Status.PASS,
        explaination=None,
        screenshot=b"assertor screenshot",
        synthesis="Everything checks out",
    )
    results = [actor_result, assertor_result]
    message, screenshots = empty_orchestrator._merge_worker_results(True, results)

    expected_header = "The sequence of workers was executed successfully:"
    assert message.startswith(expected_header)

    assert 'Act("search data") -> success' in message
    assert "  Actions:" in message
    assert "  - Plan to move forward" in message
    assert "  - We have to click somewhere" in message

    assert 'Assert("validate result") -> success' in message
    assert "  Report: Everything checks out" in message

    assert screenshots == [b"actor screenshot", b"assertor screenshot"]


def test_merge_worker_results_failure(empty_orchestrator: Orchestrator):
    actor_action = ActorAction(
        action="goto", chain_of_thought="Let's browse to the home page"
    )
    actor_result = ActorResult(
        query="go to myspace.com",
        status=Status.FAIL,
        explaination="Could not go to myspace.com",
        screenshot=b"goto screenshot",
        actions=[actor_action],
    )
    results: list[WorkerResult] = [actor_result]
    message, screenshots = empty_orchestrator._merge_worker_results(False, results)

    expected_header = "The sequence of workers was executed but eventually failed:"
    assert message.startswith(expected_header)

    assert 'Act("go to myspace.com") -> fail' in message
    assert "  Actions:" in message
    assert "  - Let's browse to the home page" in message

    assert screenshots == [b"goto screenshot"]


@pytest.mark.asyncio
@pytest.mark.llm
async def test_integ_step():
    url = "http://www.vtaas-benchmark.com:7770/"
    test_collection = TestCaseCollection("data/OneStop_Passing.csv", url)
    test_case = test_collection.get_test_case_by_id("1")
    async with async_playwright() as p:
        browser = await Browser.create(
            id="actor_test_integ_browser",
            headless=False,
            playwright=p,
            save_screenshot=True,
        )
        orchestrator = Orchestrator(browser=browser)
        context = TestExecutionContext(
            test_case=test_case, current_step=test_case.get_step(2), step_index=2
        )
        _ = await browser.goto(url)
        verdict = await orchestrator.process_step(context)
        print(verdict.model_dump_json())
        assert verdict.status == Status.PASS
