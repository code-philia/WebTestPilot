#!/usr/bin/env python3
"""
Combine versioned JSON run results into final files.
Logic:
1. If a test case is not present in existing version, insert it
2. If a test case in newer version has better quality, replace it
"""

import json
import os
import glob
from pathlib import Path
import shutil
from typing import Dict, List, Any


def is_better_quality(
    new_result: Dict[str, Any], existing_result: Dict[str, Any]
) -> bool:
    # Priority 1: Success over failure
    if new_result["success"] != existing_result["success"]:
        return new_result["success"]

    # Priority 2: Higher correct trace percentage
    new_trace_pct = new_result.get("correct_trace_percentage", 0)
    existing_trace_pct = existing_result.get("correct_trace_percentage", 0)

    if new_trace_pct != existing_trace_pct:
        return new_trace_pct > existing_trace_pct

    # Priority 3: If both successful with same trace percentage, prefer lower runtime
    if new_result["success"] and existing_result["success"]:
        new_runtime = new_result.get("runtime", float("inf"))
        existing_runtime = existing_result.get("runtime", float("inf"))
        return new_runtime < existing_runtime

    # Priority 4: If lower token, prefer it
    new_token_count = new_result.get("token_count", float("inf"))
    existing_token_count = existing_result.get("token_count", float("inf"))
    if new_token_count != existing_token_count:
        return new_token_count < existing_token_count

    # Default: keep existing
    return False


def combine_versions(files: List[str]) -> Dict[str, Any]:
    """
    Combine multiple version files into a single result.
    Files should be in order (v1, v2, v3, ...)
    """
    combined_results = {}
    all_data = []

    # Process files in order
    for file_path in files:
        with open(file_path, "r") as f:
            data = json.load(f)
            all_data.append(data)
            file_version = file_path.split("/")[-1].split(".")[1]

            # Process each test result
            for result in data.get("results", []):
                test_name = result["test_name"]

                if test_name not in combined_results:
                    # New test case, insert it
                    result["version"] = file_version
                    combined_results[test_name] = result
                else:
                    # Existing test case, check if newer version is better
                    if is_better_quality(result, combined_results[test_name]):
                        print(
                            f"Replacing {test_name} with better version {file_version}"
                        )
                        result["version"] = file_version
                        combined_results[test_name] = result

    # Recalculate summary statistics
    results_list = list(combined_results.values())

    if not results_list:
        return {
            "summary": {
                "total_runs": 0,
                "success_rate": 0.0,
                "correct_trace_percentage": 0.0,
                "normal_tests": 0,
                "buggy_tests": 0,
                "bug_detection_rate": 0.0,
            },
            "results": [],
        }

    total_runs = len(results_list)
    successful_runs = sum(1 for r in results_list if r.get("success", False))
    total_trace_percentage = sum(
        r.get("correct_trace_percentage", 0) for r in results_list
    )
    normal_tests = sum(1 for r in results_list if not r.get("has_bug", False))
    buggy_tests = sum(1 for r in results_list if r.get("has_bug", False))

    # Calculate bug detection rate (assuming bug is detected if test with bug fails)
    bugs_detected = sum(
        1
        for r in results_list
        if r.get("has_bug", False) and not r.get("success", True)
    )
    bug_detection_rate = bugs_detected / buggy_tests if buggy_tests > 0 else 0.0

    summary = {
        "total_runs": total_runs,
        "success_rate": successful_runs / total_runs if total_runs > 0 else 0.0,
        "correct_trace_percentage": total_trace_percentage / total_runs
        if total_runs > 0
        else 0.0,
        "normal_tests": normal_tests,
        "buggy_tests": buggy_tests,
        "bug_detection_rate": bug_detection_rate,
    }

    return {"summary": summary, "results": results_list}


def process_directory(base_dir: str):
    """
    Process all versioned JSON files in the given directory structure.
    """
    base_path = Path(base_dir)

    # Find all methods (top-level directories)
    methods = [d for d in base_path.iterdir() if d.is_dir()]

    for method_dir in methods:
        method_name = method_dir.name
        print(f"\n\n\n==== Processing method: {method_name} ====")

        # Find all applications under this method
        apps = [d for d in method_dir.iterdir() if d.is_dir()]

        for app_dir in apps:
            app_name = app_dir.name

            # Find all versioned JSON files for this application
            version_pattern = str(app_dir / f"{app_name}.v*.json")
            version_files = sorted(glob.glob(version_pattern))

            # Print the cleaned versions
            print(
                f"\n\n{app_name}: Found {len(version_files)} version files: {json.dumps(['/'.join(x.split('/')[-3:]) for x in version_files], indent=4)}"
            )

            if not version_files:
                single_file = app_dir / f"{app_name}.json"
                if single_file.exists():
                    # Copy the file to app_name.final.json
                    shutil.copy(single_file, app_dir / f"{app_name}.final.json")
                    print(
                        f"-> {app_name}: Single file (no versions), copied content to {app_name}.final.json"
                    )
                continue

            # Combine versions
            combined = combine_versions(version_files)

            # Save to .final.json
            output_file = app_dir / f"{app_name}.final.json"
            with open(output_file, "w") as f:
                json.dump(combined, f, indent=4)

            print(f"-> Created: {'/'.join(str(output_file).split('/')[-3:])}")
            print(f"-> Combined {combined['summary']['total_runs']} tests")
            print(f"-> Success rate: {combined['summary']['success_rate']:.2%}")


def main():
    """Main function to run the combination process."""
    # Get the results directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = script_dir  # Script is already in results directory

    print(f"Combining JSON results in: {results_dir}")
    print("=" * 60)

    process_directory(results_dir)

    print("=" * 60)
    print("Combination complete!")


if __name__ == "__main__":
    main()
