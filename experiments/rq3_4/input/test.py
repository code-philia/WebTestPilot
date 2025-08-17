import os
import glob
import re
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString

BASE_DIR = "./case_*"
DELIMITER = "-" * 56


def process_file(filepath):
    """Read a file and split by delimiter, return 2nd, 3rd, last parts if exist."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    parts = [p.strip() for p in content.split(DELIMITER) if p.strip()]

    if len(parts) < 3:
        return None
    return {"noise": parts[0], "summarize": parts[1], "restyle": parts[-1]}


def convert_to_literal(obj):
    """Recursively convert all strings to LiteralScalarString for block style YAML."""
    if isinstance(obj, dict):
        return {k: convert_to_literal(v) for k, v in obj.items()}
    elif isinstance(obj, str):
        return LiteralScalarString(obj)
    return obj


def get_case_number(foldername):
    """Extract numeric part from 'case_x'"""
    match = re.search(r"case_(\d+)", foldername)
    return int(match.group(1)) if match else float("inf")


def main():
    # Configure ruamel.yaml
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 4096  # Prevent line wrapping
    yaml.default_style = None  # Let ruamel decide based on content type

    noise_data, summarize_data, restyle_data = {}, {}, {}
    # Get all case folders and sort by numeric case number
    folders = sorted(glob.glob(BASE_DIR), key=get_case_number)

    for folder in folders:
        dirname = os.path.basename(folder)
        txt_files = glob.glob(os.path.join(folder, "Out*.txt"))
        for filepath in txt_files:
            dirname = os.path.basename(os.path.dirname(filepath))  # e.g. case_10
            parts = process_file(filepath)
            if parts:
                noise_data[dirname] = parts["noise"]
                summarize_data[dirname] = parts["summarize"]
                restyle_data[dirname] = parts["restyle"]

    # Convert all strings to literal block format
    with open("noise.yaml", "w", encoding="utf-8") as f:
        yaml.dump(convert_to_literal(noise_data), f)

    with open("summarize.yaml", "w", encoding="utf-8") as f:
        yaml.dump(convert_to_literal(summarize_data), f)

    with open("restyle.yaml", "w", encoding="utf-8") as f:
        yaml.dump(convert_to_literal(restyle_data), f)


if __name__ == "__main__":
    main()
