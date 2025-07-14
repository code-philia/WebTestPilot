import argparse
import asyncio
import datetime
import os
from pathlib import Path
import random
import string
import sys
import time
from urllib.error import HTTPError
from playwright.async_api import async_playwright
import requests
import urllib.request
import json

# Add parent directory to path for relative imports when running as script
if __name__ == "__main__":
    sys.path.append(os.path.join(str(Path(__file__).parent), "src"))

from VTAAS.data.testcase import TestCaseCollection
from VTAAS.llm.llm_client import LLMProvider
from VTAAS.orchestrator.orchestrator import Orchestrator
from VTAAS.schemas.verdict import Status
from VTAAS.workers.browser import Browser


async def reset_application(port):
    print("Initialising application reset")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {os.environ['GITHUB_TOKEN']}",
    }

    delta_time = datetime.timedelta(minutes=2)
    run_date_filter = (datetime.datetime.now(datetime.UTC) - delta_time).strftime(
        "%Y-%m-%dT%H:%M"
    )

    match int(port):
        case 9999:
            ga_name = "reset_postmill.yaml"
        case 7770:
            ga_name = "reset_shopping.yaml"
        case 9980:
            ga_name = "reset_classifieds.yaml"

    run_identifier = "".join(
        random.choices(string.ascii_uppercase + string.digits, k=15)
    )
    r = requests.post(
        f"https://api.github.com/repos/Smartesting/vtaas-benchmark/actions/workflows/{ga_name}/dispatches",
        headers=headers,
        json={"ref": "main", "inputs": {"run_identifier": f"{run_identifier}"}},
    )

    workflow_id = ""
    while workflow_id == "":
        r = requests.get(
            f"https://api.github.com/repos/Smartesting/vtaas-benchmark/actions/runs?created=%3E{run_date_filter}",
            headers=headers,
        )

        runs = r.json()["workflow_runs"]
        if len(runs) > 0:
            for workflow in runs:
                jobs_url = workflow["jobs_url"]
                r = requests.get(jobs_url, headers=headers)
                jobs = r.json()["jobs"]
                if len(jobs) > 0:
                    # we only take the first job, edit this if you need multiple jobs
                    for job in jobs:
                        steps = job["steps"]
                        if len(steps) >= 2:
                            second_step = steps[1]
                            if second_step["name"] == run_identifier:
                                workflow_id = job["run_id"]
                    else:
                        time.sleep(3)
                else:
                    time.sleep(3)
        else:
            time.sleep(3)

    r = requests.get(
        f"https://api.github.com/repos/Smartesting/vtaas-benchmark/actions/runs/{workflow_id}",
        headers=headers,
    )
    status = "in_progress"
    while status != "completed":
        r = requests.get(
            f"https://api.github.com/repos/Smartesting/vtaas-benchmark/actions/runs/{workflow_id}",
            headers=headers,
        )

        status = r.json()["status"]
        time.sleep(20)
        print(f"Database reset : {status}")

    print("Reset successful. Waiting for application to restart")
    success = 0
    while success < 2:
        try:
            urllib.request.urlopen(f"http://www.vtaas-benchmark.com:{port}/", timeout=3)
        except (TimeoutError, HTTPError):
            print("Application not on yet...")
            time.sleep(10)
            continue
        success += 1


async def run_evaluation(
    tc_collection: TestCaseCollection, output_folder: Path, provider: str
) -> tuple[dict[str, tuple[Status, int, int]], dict[str, float]]:
    metrics: dict[str, float] = {}
    results: dict[str, tuple[Status, int, int]] = {}

    port = (
        tc_collection.url[-5:-1]
        if tc_collection.url[-1] == "/"
        else tc_collection.url[-4:]
    )

    metrics["FN"] = 0
    metrics["TN"] = 0
    metrics["FP"] = 0
    metrics["AFA"] = 0
    metrics["AFB"] = 0
    metrics["AFC"] = 0

    for test_case in tc_collection:
        test_case_folder = Path(output_folder) / f"TC_{test_case.id}"
        # test_case_folder.mkdir(exist_ok=True)
        if not os.path.exists(test_case_folder):
            os.makedirs(test_case_folder)
        else:
            print(f"{test_case_folder} already exists")
            continue
       # _ = await reset_application(port)
        async with async_playwright() as p:
            browser = await Browser.create(
                name=f"TC_{test_case.id}",
                headless=True,
                playwright=p,
                save_screenshot=True,
                tracer=True,
                trace_folder=str(test_case_folder),
            )

            match provider:
                case "openai":
                    llm_provider = LLMProvider.OPENAI
                case "anthropic":
                    llm_provider = LLMProvider.ANTHROPIC
                case "google":
                    llm_provider = LLMProvider.GOOGLE

            orchestrator = Orchestrator(
                name=f"TC_{test_case.id}",
                browser=browser,
                llm_provider=llm_provider,
                tracer=True,
                output_folder=str(test_case_folder),
            )

            execution_result = await orchestrator.process_testcase(test_case)

            if test_case.type == "F":
                results[test_case.id] = (
                    execution_result.status,
                    execution_result.step_index,
                    test_case.failing_step,
                )
            else:
                results[test_case.id] = (
                    execution_result.status,
                    execution_result.step_index,
                    -1,
                )

            with open(f"{output_folder}/result.json", "w") as fp:
                json.dump(results, fp)

            if execution_result.status == Status.PASS:
                if test_case.type == "F":
                    metrics["FN"] = metrics["FN"] + 1
                elif test_case.type == "P":
                    metrics["TN"] = metrics["TN"] + 1

            else:
                if test_case.type == "F":
                    match execution_result.step_index:
                        case _ if execution_result.step_index < test_case.failing_step:
                            metrics["AFB"] = metrics["AFB"] + 1
                        case _ if execution_result.step_index == test_case.failing_step:
                            metrics["AFC"] = metrics["AFC"] + 1
                        case _ if execution_result.step_index > test_case.failing_step:
                            metrics["AFA"] = metrics["AFA"] + 1

                elif test_case.type == "P":
                    metrics["FP"] = metrics["FP"] + 1

        with open(f"{output_folder}/metrics.json", "w") as fp:
            json.dump(metrics, fp)

    metrics["TP"] = metrics["AFA"] + metrics["AFB"] + metrics["AFC"]
    metrics["accuracy"] = (metrics["TP"] + metrics["TN"]) / (
        metrics["TP"] + metrics["TN"] + metrics["FP"] + metrics["FN"]
    )
    metrics["specificity"] = (
        metrics["TN"] / (metrics["TN"] + metrics["FP"])
        if (metrics["TN"] + metrics["FP"]) > 0
        else 0
    )
    metrics["sensitivity"] = (
        metrics["TP"] / (metrics["TP"] + metrics["FN"])
        if (metrics["TP"] + metrics["FN"]) > 0
        else 0
    )
    metrics["AER"] = metrics["AFB"] / metrics["TP"] if metrics["TP"] > 0 else 0
    metrics["HER"] = metrics["AFA"] / metrics["TP"] if metrics["TP"] > 0 else 0
    metrics["SMER"] = metrics["AER"] + metrics["HER"]
    metrics["truacc"] = (metrics["AFC"] + metrics["TN"]) / (
        metrics["TP"] + metrics["TN"] + metrics["FP"] + metrics["FN"]
    )

    return results, metrics


async def main():
    parser = argparse.ArgumentParser(
        description="Evaluate a Test Case Collection from a CSV file"
    )
    parser.add_argument(
        "-f", "--file", required=True, help="Path to the CSV file containing test cases"
    )
    parser.add_argument(
        "-u",
        "--url",
        default="http://www.vtaas-benchmark.com:9980",
        help="Base URL for the test cases. Don't forget the :port",
    )

    parser.add_argument(
        "-p", "--provider", choices=["openai", "anthropic", "google"], default="openai"
    )

    parser.add_argument(
        "-o",
        "--output",
        default="./results/",
        help="Output folder for the executions and metrics (default: results)",
    )

    args = parser.parse_args()

    try:
        # Ensure output directory exists
        os.makedirs(args.output, exist_ok=True)

        # Create TestCaseCollection
        collection = TestCaseCollection(args.file, args.url, args.output)

        results, metrics = await run_evaluation(collection, args.output, args.provider)

        with open(f"{args.output}/result.json", "w") as fp:
            json.dump(results, fp)

        with open(f"{args.output}/metrics.json", "w") as fp:
            json.dump(metrics, fp)

    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
