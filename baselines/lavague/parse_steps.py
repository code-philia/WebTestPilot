"""
This script demonstrates how to parse LaVague's steps DataFrame from a pickle file.
It will iterate through the file contents to print navigation steps.
"""
from pathlib import Path

import pandas as pd
from pandas import DataFrame

# (Change the path) Load the steps DataFrame from a pickle file
steps_path = Path("steps.pkl")
steps: DataFrame = pd.read_pickle(steps_path)

# Data types and non-null counts
print(steps.info())

# Quick stats for numeric columns
print(steps.describe())

# Each unique run_id has only one navigation step, print them
prev_id = None
for index, row in steps.iterrows():
    run_id = row["run_id"]
    if run_id != prev_id:
        print(run_id)
        prev_id = run_id

    print(row["step"], row["engine"])
    print(row["code"])