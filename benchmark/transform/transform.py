import random
from pathlib import Path

import yaml
from tqdm import tqdm
from typo import StrErrer
from dotenv import load_dotenv
from baml_client.sync_client import b
from yaml.dumper import SafeDumper

load_dotenv()


def str_presenter(dumper, data):
    if "\n" in data:
        return dumper.represent_scalar(
            "tag:yaml.org,2002:str", data, style="|"
        )
    return dumper.represent_scalar(
        "tag:yaml.org,2002:str", data
    )

SafeDumper.add_representer(str, str_presenter)


# ===============================
# Transformation functions
# ===============================

def dropout(actions: list[dict]) -> str:
    n = len(actions)
    items = [(i, t) for i in range(n) for t in ("action", "expected")]
    drop = set(random.sample(items, max(1, int(len(items) * 0.1))))

    steps = []
    for i, step in enumerate(actions):
        parts = {
            "action": step["action"].rstrip("."),
            "expected": step.get("expectedResult", step.get("expectation", "")).rstrip("."),
        }
        text = ". ".join(parts[t] for t in ("action", "expected") if (i, t) not in drop)
        if text:
            steps.append(f"{text}.")
    return " ".join(steps)


def summarize(actions: list[dict]) -> str:
    description = ". ".join(
        val
        for action in actions
        for val in (action["action"], action.get("expectedResult", action.get("expectation", "")))
    )
    result = b.Summarize(description)
    return result.output


def restyle(actions: list[dict]) -> str:
    description = ". ".join(
        val
        for action in actions
        for val in (action["action"], action.get("expectedResult", action.get("expectation", "")))
    )
    result = b.Restyle(description)
    return result.output


def add_noise(actions: list[dict], error_rate=0.10) -> str:
    description = ". ".join(
        val
        for action in actions
        for val in (action["action"], action.get("expectedResult", action.get("expectation", "")))
    )
    description = b.AddNoise(description).output

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


# ===============================
# Main pipeline
# ===============================

TRANSFORMATIONS = {
    "dropout": dropout,
    "summarize": summarize,
    "restyle": restyle,
    "add_noise": add_noise,
}


def main(application: str):
    script_dir = Path(__file__).parent
    benchmark_dir = script_dir.parent.parent / "benchmark" / application / "test_cases"

    yaml_files = list(benchmark_dir.glob("*.yaml"))
    if not yaml_files:
        print(f"⚠️ No YAML files found in {benchmark_dir}")
        return

    print(f"Found {len(yaml_files)} YAML files. Applying transformations...")

    # Iterate over all YAML files with a progress bar
    for yaml_file in tqdm(yaml_files, desc="Processing YAMLs", unit="file"):
        with open(yaml_file, "r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"⚠️ Failed to parse {yaml_file}: {e}")
                continue

        actions = data.get("steps", [])
        if not actions:
            print(f"⚠️ No steps found in {yaml_file}")
            continue

        # Apply all transformations
        for name, func in TRANSFORMATIONS.items():
            try:
                transformed_text = func(actions)

                # Prepare output directory: <script_dir>/<application>/<transformation>/
                output_dir = script_dir / application / name
                output_dir.mkdir(parents=True, exist_ok=True)

                # Build new YAML structure
                out_yaml = {
                    "name": data.get("name", yaml_file.stem),
                    "setup_function": data.get("setup_function", ""),
                    "steps": data.get("steps", []),
                    "paragraph": transformed_text
                }

                # Write YAML output
                output_file = output_dir / f"{yaml_file.stem}.yaml"
                with open(output_file, "w", encoding="utf-8") as f_out:
                    yaml.safe_dump(out_yaml, f_out, sort_keys=False, allow_unicode=True)

            except Exception as e:
                print(f"⚠️ Failed to apply {name} on {yaml_file}: {e}")

    print(f"✅ All transformations applied for application '{application}'.")


# ===============================
# CLI
# ===============================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Transform benchmark YAMLs into text files.")
    parser.add_argument(
        "application", type=str, help="Application name (e.g., indico, prestashop)"
    )

    args = parser.parse_args()
    main(args.application)
