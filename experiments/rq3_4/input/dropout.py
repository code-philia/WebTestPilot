import os
import json
import random
import yaml


def process_json_file(filepath, case_id):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    actions = data.get("actions", [])
    if not actions:
        return None

    # Collect all item identifiers (step index, field type)
    all_items = [(i, "action") for i in range(len(actions))] + [
        (i, "expected") for i in range(len(actions))
    ]

    # Drop ~20% (min 1)
    drop_count = max(1, int(len(all_items) * 0.1))
    drop_set = set(random.sample(all_items, drop_count))

    steps = []
    for idx, step in enumerate(actions, start=1):
        action = step["action"].rstrip(".")
        expected = step["expectedResult"].rstrip(".")

        if (idx - 1, "action") in drop_set:
            action = None
        if (idx - 1, "expected") in drop_set:
            expected = None

        if action and expected:
            text = f"{action}. {expected}."
        elif action:
            text = f"{action}."
        elif expected:
            text = f"{expected}."
        else:
            continue  # shouldn't happen

        steps.append(text)

    paragraph = " ".join(steps)
    return {f"case_{case_id}": paragraph}


def main(input_folder, output_file="output.yaml"):
    cases = {}
    case_counter = 1

    for filename in sorted(os.listdir(input_folder)):
        if filename.endswith(".json"):
            filepath = os.path.join(input_folder, filename)
            case = process_json_file(filepath, case_counter)
            if case:
                cases.update(case)
                case_counter += 1

    # Dump to YAML with block scalar style
    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(cases, f, allow_unicode=True, sort_keys=True, width=1000)


if __name__ == "__main__":
    # Change this to your folder path
    main("/home/xiwen/WebTestPilot/testcases/eval_data/test_cases/bookstack")
