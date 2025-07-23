import logging
import time
from playwright.async_api import async_playwright
import pytest
from VTAAS.data.testcase import TestCaseCollection
from VTAAS.llm.llm_client import LLMProvider
from VTAAS.orchestrator import Orchestrator
from VTAAS.workers.browser import Browser


@pytest.mark.asyncio
@pytest.mark.llm
async def test_one_TC():
    async with async_playwright() as p:
        output_folder = "./results/google/classifieds/passing/TC10"  # {time.time()}"
        browser = await Browser.create(
            id="actor_test_integ_browser",
            headless=False,
            playwright=p,
            save_screenshot=True,
            tracer=False,
            trace_folder=output_folder,
        )
        test_collection = TestCaseCollection(
            # "./data/Benchmark - Classifieds - Fail.csv",
            "./benchmark/classifieds_passing.csv",
            "http://www.vtaas-benchmark.com:9980/",
            # "./benchmark/postmill_passing.csv",
            # "http://www.vtaas-benchmark.com:9999/",
            # "./data/Benchmark - OneStopMarket - Passing.csv",
            # "http://www.vtaas-benchmark.com:7770/",
            # "data/OneStop_Passing.csv", "http://www.vtaas-benchmark.com:7770/"
            output_folder,
        )
        test_case = test_collection.get_test_case_by_id("10")
        orchestrator = Orchestrator(
            browser=browser,
            llm_provider=LLMProvider.GOOGLE,
            output_folder=output_folder,
        )
        # orchestrator.logger.setLevel(logging.DEBUG)

        _ = await orchestrator.process_testcase(test_case)
    # Initialize workers based on a specific task
    # await orchestrator.initialize_workers(
    #     context="Processing a large dataset of customer transactions",
    #     objective="Identify and flag suspicious transactions while monitoring system performance",
    # )
