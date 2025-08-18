import os
import json
import random
from ruamel.yaml import YAML

from typo import StrErrer
from dotenv import load_dotenv

from baml_client.sync_client import b


load_dotenv()


APP_NAME = "bookstack"
TRANSFORMATION = "default"


def default(actions: list[dict]) -> str:
    description = ". ".join(
        val
        for action in actions
        for val in (action["action"], action["expectedResult"])
    )
    return description


def dropout(actions: list[dict]) -> str:
    n = len(actions)
    items = [(i, t) for i in range(n) for t in ("action", "expected")]
    drop = set(random.sample(items, max(1, int(len(items) * 0.1))))

    steps = []
    for i, step in enumerate(actions):
        parts = {
            "action": step["action"].rstrip("."),
            "expected": step["expectedResult"].rstrip("."),
        }
        text = ". ".join(parts[t] for t in ("action", "expected") if (i, t) not in drop)
        if text:
            steps.append(f"{text}.")
    return " ".join(steps)


def summarize(actions: list[dict]) -> str:
    description = ". ".join(
        val
        for action in actions
        for val in (action["action"], action["expectedResult"])
    )
    result = b.Summarize(description)
    return result.output


def restyle(actions: list[dict]) -> str:
    description = ". ".join(
        val
        for action in actions
        for val in (action["action"], action["expectedResult"])
    )
    result = b.Restyle(description)
    return result.output


def add_noise(actions: list[dict], error_rate=0.10):
    description = ". ".join(
        val
        for action in actions
        for val in (action["action"], action["expectedResult"])
    )
    description = b.Restyle(description).output

    num_errors = max(1, int(len(description) * error_rate))
    error = StrErrer(description, seed=None)
    typo_methods = [
        error.char_swap,
        error.missing_char,
        error.nearby_char,
        error.similar_char,
    ]
    for _ in range(num_errors):
        method = random.choice(typo_methods)
        error = method()

    return error.result


def process_json_file(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        data: dict = json.load(f)

    name: str = data.get("name")
    url: str = data.get("url")
    setup_function: str = data.get("setup_function")
    actions: list[dict] = data.get("actions", [])

    assert name is not None
    assert url is not None
    assert setup_function is not None
    assert len(actions) > 0

    description = globals()[TRANSFORMATION](actions)
    print("transformed:", "\n", description)

    return {
        "name": name,
        "url": url,
        "setup_function": setup_function,
        "description": description,
    }


def main(input_folder):
    yaml = YAML()
    yaml.allow_unicode = True
    yaml.sort_keys = True
    yaml.width = 1000

    filenames: list[str] = sorted(os.listdir(input_folder))

    for i, filename in enumerate(filenames):
        print(f"{i + 1}/{len(filenames)}")
        if filename.endswith(".json"):
            filepath = os.path.join(input_folder, filename)
            case = process_json_file(filepath)

            # Dump to YAML with block scalar style
            OUTPUT_DIR = f"/home/xiwen/WebTestPilot/experiments/rq3_4/input/{APP_NAME}/{TRANSFORMATION}"
            if not os.path.exists(OUTPUT_DIR):
                os.makedirs(OUTPUT_DIR)

            with open(
                f"{OUTPUT_DIR}/{filename.replace('.json', '.yaml')}",
                "w",
                encoding="utf-8",
            ) as f:
                yaml.dump(case, f)


if __name__ == "__main__":
    # Change this to your folder path
    main(f"/home/xiwen/WebTestPilot/testcases/eval_data/test_cases/{APP_NAME}")
