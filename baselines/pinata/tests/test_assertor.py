import logging
from tempfile import mktemp
import time
from typing import cast
from unittest.mock import Mock

import pytest
from playwright.async_api import async_playwright
from pytest_mock import MockerFixture

from VTAAS.data.testcase import TestCaseCollection
from VTAAS.llm.llm_client import LLMClient, LLMProvider
from VTAAS.schemas.llm import MessageRole
from VTAAS.schemas.verdict import Status
from VTAAS.schemas.worker import AssertorInput
from VTAAS.workers.assertor import Assertor
from VTAAS.workers.browser import Browser

MOCKED_ASSERTION = "This is a mocked assertion"


@pytest.fixture
def mock_llm_client(mocker: MockerFixture) -> LLMClient:
    mocked_class = mocker.patch("VTAAS.workers.assertor.LLMClient", autospec=True)
    mock_instance: LLMClient = cast(LLMClient, mocked_class.return_value)

    mock_instance.plan_step = Mock()
    return mock_instance


@pytest.fixture
def mock_browser(mocker: MockerFixture) -> Browser:
    mocked_class = mocker.patch("VTAAS.workers.assertor.Browser", autospec=True)
    mock_instance: Browser = cast(Browser, mocked_class.return_value)

    mock_instance.goto = Mock()
    mock_instance.click = Mock()
    mock_instance.fill = Mock()
    mock_instance.select = Mock()
    mock_instance.vertical_scroll = Mock()

    return mock_instance


@pytest.fixture
def mock_assertion() -> str:
    return MOCKED_ASSERTION


@pytest.fixture
def mock_assertor_input() -> AssertorInput:
    return AssertorInput(
        test_case="TC-1-P: Login & Logout\n1. login\n2.logout",
        test_step=("1. login", ""),
        history="filled 'user' in username field",
    )


@pytest.fixture
def empty_assertor(mock_assertion: str, mock_browser: Browser) -> Assertor:
    start_time = 1740697199
    output_folder = mktemp()
    return Assertor(
        "assertor_tu",
        mock_assertion,
        mock_browser,
        LLMProvider.OPENAI,
        start_time,
        output_folder,
    )


@pytest.mark.asyncio
async def test_main_prompt(
    empty_assertor: Assertor, mock_assertor_input: AssertorInput
):
    """Test main prompt builds itself"""
    page_info = "page info"
    viewport_info = "top of the page"
    prompt = empty_assertor._build_user_prompt(
        mock_assertor_input, page_info, viewport_info
    )
    current_step = (
        mock_assertor_input.test_step[0] + "; " + mock_assertor_input.test_step[1]
    )
    assert f"<test_case>\n{mock_assertor_input.test_case}\n</test_case>" in prompt
    assert f"<current_step>\n{current_step}\n</current_step>" in prompt
    assert f"<assertion>\n{MOCKED_ASSERTION}\n</assertion>" in prompt
    assert page_info in prompt
    assert viewport_info in prompt


@pytest.mark.asyncio
async def test_conversation(
    empty_assertor: Assertor, mock_assertor_input: AssertorInput
):
    """Test main prompt builds itself"""
    fake_screenshot = b"screen"
    page_info = "page info"
    viewport_info = "top of the page"
    empty_assertor._setup_conversation(
        mock_assertor_input, fake_screenshot, page_info, viewport_info
    )
    assert empty_assertor.conversation[0].role == MessageRole.System
    assert (
        "Your role is to assert the expected state"
        in empty_assertor.conversation[0].content
    )
    assert empty_assertor.conversation[0].screenshot is None
    assert empty_assertor.conversation[1].role == MessageRole.User
    assert (
        "Your role is to verify assertions based on a screenshot"
        in empty_assertor.conversation[1].content
    )
    assert viewport_info in empty_assertor.conversation[1].content
    assert page_info in empty_assertor.conversation[1].content
    assert empty_assertor.conversation[1].screenshot == [fake_screenshot]


@pytest.mark.asyncio
@pytest.mark.llm
async def test_integ():
    logging.getLogger("VTAAS.worker.assertor").setLevel(logging.DEBUG)
    url = "http://www.vtaas-benchmark.com:9999/"
    test_collection = TestCaseCollection("./benchmark/postmill_passing.csv", url)
    test_case = test_collection.get_test_case_by_id("1")
    test_step = test_case.get_step(1)
    # assertion = "The page contains a 'Create an Account' link at the top right corner"
    assertion = "The page contains a search field"
    assertor_input = AssertorInput(
        test_case=str(test_case), test_step=test_step, history=None
    )
    async with async_playwright() as p:
        start_time = 1740697199
        output_folder = mktemp()
        browser = await Browser.create(
            id="assertor_test_integ_browser",
            headless=False,
            playwright=p,
            save_screenshot=True,
            start_time=start_time,
            trace_folder=output_folder,
        )
        _ = await browser.goto(url)
        assertor = Assertor(
            name="assertor_test_integ",
            query=assertion,
            browser=browser,
            llm_provider=LLMProvider.OPENROUTER,
            start_time=start_time,
            output_folder=output_folder,
        )
        verdict = await assertor.process(assertor_input)
        assert verdict.status == Status.PASS
