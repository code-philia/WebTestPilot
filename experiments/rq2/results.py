import json
from pathlib import Path

import pandas as pd
from statsmodels.stats.inter_rater import fleiss_kappa


def compute_bug_reporting_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute bug reporting metrics (precision, recall, F1) per method × webapp with total.

    Returns three separate pivot tables: precision, recall, f1.
    """
    # Step 1: Identify last step of each test_case
    df["is_last_step"] = df.groupby(
        ["method", "webapp", "run_id", "test_case"]
    )["step_id"].transform("max") == df["step_id"]

    # Step 2: Compute TP, FP, FN
    df["TP"] = df["is_bug_reported"] & df["is_last_step"]
    df["FP"] = df["is_bug_reported"] & (~df["is_last_step"])
    df["FN"] = (~df["is_bug_reported"]) & df["is_last_step"]

    # Step 3: Aggregate counts per method × webapp
    agg = df.groupby(["method", "webapp"])[["TP", "FP", "FN"]].sum()

    # Step 4: Compute metrics
    agg["precision"] = (agg["TP"] / (agg["TP"] + agg["FP"])).fillna(0)
    agg["recall"] = (agg["TP"] / (agg["TP"] + agg["FN"])).fillna(0)
    agg["f1"] = (2 * agg["precision"] * agg["recall"] / (agg["precision"] + agg["recall"])).fillna(0)

    # Step 5: Pivot tables for each metric
    precision_table = agg["precision"].unstack(fill_value=0)
    recall_table = agg["recall"].unstack(fill_value=0)
    f1_table = agg["f1"].unstack(fill_value=0)

    # Step 6: Compute total across webapps per method
    total = df.groupby("method")[["TP", "FP", "FN"]].sum()
    precision_table["total"] = (total["TP"] / (total["TP"] + total["FP"])).fillna(0)
    recall_table["total"] = (total["TP"] / (total["TP"] + total["FN"])).fillna(0)
    f1_table["total"] = (2 * precision_table["total"] * recall_table["total"] / 
                         (precision_table["total"] + recall_table["total"])).fillna(0)

    # Step 7: Round for readability
    precision_table = precision_table.round(2)
    recall_table = recall_table.round(2)
    f1_table = f1_table.round(2)

    return precision_table, recall_table, f1_table


def compute_bug_reporting_stability(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute stability metrics for bug reporting per method across runs.

    Metrics:
        - Correct Trace Variance: variance of fraction of correctly reported steps per test_case
        - Task Completion Variance: variance of "all steps correctly reported per test_case"
        - Fleiss-Kappa: agreement of bug reporting across runs at step level

    Only the last step of each test_case counts as correct reporting.
    """
    results = []

    # Mark last step
    df["is_last_step"] = df.groupby(["method", "webapp", "run_id", "test_case"])["step_id"].transform("max") == df["step_id"]

    # Define a column indicating correct bug report at step level
    df["is_bug_correct"] = df["is_bug_reported"] & df["is_last_step"] | (~df["is_bug_reported"] & ~df["is_last_step"])

    for method, mdf in df.groupby("method"):

        # ----- Correct Trace Variance -----
        # Fraction of steps correct per test_case × run
        frac_correct = mdf.groupby(["run_id", "test_case"])["is_bug_correct"].mean()
        correct_trace_var = frac_correct.var(ddof=0) if len(frac_correct) > 1 else 0

        # ----- Task Completion Variance -----
        # All steps in a test_case correct
        task_completed = mdf.groupby(["run_id", "test_case"])["is_bug_correct"].all().astype(int)
        task_completion_var = task_completed.var(ddof=0) if len(task_completed) > 1 else 0

        # ----- Fleiss-Kappa -----
        kappa_matrix = []
        for tc in mdf["test_case"].unique():
            tc_df = mdf[mdf["test_case"] == tc]
            steps = tc_df.groupby(tc_df.index)["is_bug_correct"].apply(list)
            for step_vals in steps:
                kappa_matrix.append([step_vals.count(0), step_vals.count(1)])
        # If only one run, no agreement to measure → set to 1.0
        fleiss = fleiss_kappa(kappa_matrix) if len(mdf["run_id"].unique()) > 1 else 1.0

        results.append({
            "method": method,
            "Correct Trace Variance": correct_trace_var,
            "Task Completion Variance": task_completion_var,
            "Fleiss-Kappa": fleiss
        })

    return pd.DataFrame(results).set_index("method").round(2)


root_dir = Path(__file__).parent / "results"
method_webapp_dirs = root_dir.glob("*_*/")

rows = []
# For each (method, webapp) pair
for method_webapp_dir in method_webapp_dirs:
    method, webapp = method_webapp_dir.stem.split("_")
    run_dirs = method_webapp_dir.glob("run_*/")

    # For each run in (method, webapp)
    for run_id, run_dir in enumerate(run_dirs, start=1):
        result_dirs = run_dir.glob("**/result.json")

        # For each test_case in run
        for result_dir in result_dirs:
            test_case = result_dir.parent.stem
            result_data: dict = json.load(result_dir.open())
            steps: list[dict] = result_data.get("steps", [])

            # For each step in test_case
            for step_id, step in enumerate(steps, start=1):
                is_bug_reported: bool = step.get("is_bug_reported")
                start_time: float = step.get("start_time", 0)
                end_time: float = step.get("end_time", 0)
                duration: float = end_time - start_time
                tokens: int = step.get("tokens", 0)

                rows.append((
                    method, webapp, run_id, test_case, step_id,
                    is_bug_reported, duration, tokens
                ))


columns = [
    "method", "webapp", "run_id", "test_case", "step_id",
    "is_bug_reported", "duration", "tokens"
]
df = pd.DataFrame(rows, columns=columns)

run_ids = sorted(df["run_id"].dropna().unique())
for run_id in run_ids:
    run_df = df[df["run_id"] == run_id]
    precision, recall, f1_score = compute_bug_reporting_metrics(run_df)

    print(f"----- Run {run_id} -----")
    print(f"Precision:\n{precision}\n")
    print(f"Recall:\n{recall}\n")
    print(f"F1-Score:\n{f1_score}\n")


precision, recall, f1_score = compute_bug_reporting_metrics(df)
bug_reporting_stability = compute_bug_reporting_stability(df)


print(f"----- Total -----")
print(f"Precision:\n{precision}\n")
print(f"Recall:\n{recall}\n")
print(f"F1-Score:\n{f1_score}\n")
print(f"Bug Reporting Stability:\n{bug_reporting_stability}\n")

df.to_csv(root_dir.parent / "rq2_results.csv", index=False)
