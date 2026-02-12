import json
from pathlib import Path

import pandas as pd
from statsmodels.stats.inter_rater import fleiss_kappa


def compute_task_completion(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute task completion per method × webapp with proper total.
    
    Task completion for a test_case is 1 if all its steps have is_action_correct=True, 0 otherwise.
    The rate per method × webapp is (# completed test_cases) / (# test_cases).
    
    The 'total' column aggregates scores across all webapps for each method.
    
    Returns a pivot table:
        - Rows: methods
        - Columns: webapps + total
        - Values: task completion rate (0-1)
    """
    # Step 1: Compute task completion per test_case
    task_completion = (
        df.groupby(["method", "webapp", "run_id", "test_case"])["is_action_correct"]
          .all()
          .astype(int)
          .reset_index(name="task_completed")
    )

    # Step 2: Compute per method × webapp rate
    rate_table = (
        task_completion.groupby(["method", "webapp"])["task_completed"]
                       .mean()
                       .reset_index()
                       .pivot(index="method", columns="webapp", values="task_completed")
    )

    # Step 3: Compute total task completion per method across all webapps
    total_completion = (
        task_completion.groupby("method")["task_completed"]
                       .sum()  # total # of completed test_cases
                       / task_completion.groupby("method")["task_completed"].count()  # total # of test_cases
    )

    # Add total column
    rate_table["total"] = total_completion

    # Step 4: Fill missing values with 0
    rate_table = rate_table.fillna(0)

    return rate_table


def compute_correct_trace(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute correct trace per method × webapp with total.
    
    For each test_case:
        - Count consecutive steps from the start where is_action_correct is True
        - Divide by total steps in that test_case to get score (0-1)
    
    The method × webapp table shows the average progress score across all test_cases.
    The 'total' column aggregates across all webapps.
    
    Returns a pivot table:
        - Rows: methods
        - Columns: webapps + total
        - Values: average progress score (0-1)
    """
    # Step 1: Compute progress score per test_case per run
    def progress_score(steps: pd.Series) -> float:
        """Count consecutive correct steps until first failure / total steps"""
        consecutive = 0
        for correct in steps:
            if correct:
                consecutive += 1
            else:
                break
        return consecutive / len(steps) if len(steps) > 0 else 0

    progress = (
        df.groupby(["method", "webapp", "run_id", "test_case"])["is_action_correct"]
          .apply(progress_score)
          .reset_index(name="progress_score")
    )

    # Step 2: Average progress score per method × webapp
    score_table = (
        progress.groupby(["method", "webapp"])["progress_score"]
                .mean()
                .reset_index()
                .pivot(index="method", columns="webapp", values="progress_score")
    )

    # Step 3: Compute total progress score per method across all webapps
    total_score = (
        progress.groupby("method")["progress_score"]
                .mean()  # average across all test_cases and webapps
    )

    score_table["total"] = total_score

    # Step 4: Fill missing values with 0
    score_table = score_table.fillna(0)

    return score_table


def compute_stability_metrics(df: pd.DataFrame) -> pd.DataFrame:
    results = []

    for method, mdf in df.groupby("method"):
        # ----- Correct Trace Variance -----
        frac_correct = mdf.groupby(["run_id", "test_case"])["is_action_correct"].mean()
        correct_trace_var = frac_correct.var(ddof=0) if len(frac_correct) > 1 else 0

        # ----- Task Completion Variance -----
        task_completed = mdf.groupby(["run_id", "test_case"])["is_action_correct"].all().astype(int)
        task_completion_var = task_completed.var(ddof=0) if len(task_completed) > 1 else 0

        # ----- Fleiss-Kappa -----
        kappa_matrix = []
        for tc in mdf["test_case"].unique():
            tc_df = mdf[mdf["test_case"] == tc]
            steps = tc_df.groupby(tc_df.index)["is_action_correct"].apply(list)
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
                is_action_correct: bool = step.get("is_action_correct")
                is_bug_reported: bool = step.get("is_bug_reported")
                start_time: float = step.get("start_time", 0)
                end_time: float = step.get("end_time", 0)
                duration: float = end_time - start_time
                tokens: int = step.get("tokens", 0)

                rows.append((
                    method, webapp, run_id, test_case, step_id,
                    is_action_correct, is_bug_reported, duration, tokens
                ))


columns = [
    "method", "webapp", "run_id", "test_case", "step_id",
    "is_action_correct", "is_bug_reported", "duration", "tokens"
]
df = pd.DataFrame(rows, columns=columns)

run_ids = sorted(df["run_id"].dropna().unique())
for run_id in run_ids:
    run_df = df[df["run_id"] == run_id]
    task_completion_rate = compute_task_completion(run_df)
    progress_score = compute_correct_trace(run_df)

    print(f"----- Run {run_id} -----")
    print(f"Task Completion:\n{task_completion_rate}\n")
    print(f"Correct Trace:\n{progress_score}\n")

task_completion_rate = compute_task_completion(df)
progress_score = compute_correct_trace(df)
stability_metrics = compute_stability_metrics(df)
duration_by_step = df.groupby("method")["duration"].describe().round(2)
duration_by_test_case = df.groupby(["method", "test_case"], as_index=False)["duration"].sum()
duration_by_test_case = duration_by_test_case.groupby("method")["duration"].describe().round(2)

print(f"----- Total -----")
print(f"Task Completion:\n{task_completion_rate}\n")
print(f"Correct Trace:\n{progress_score}\n")
print(f"Duration by Step:\n{duration_by_step}\n")
print(f"Duration by Test Case:\n{duration_by_test_case}\n")
print(f"Stability Metrics:\n{stability_metrics}\n")

df.to_csv(root_dir.parent / "rq1_results.csv", index=False)
