#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
BASELINE_DIR="$SCRIPT_DIR/../../baselines"
VENV_DIR="$BASELINE_DIR/webtestpilot/.venv"

source "$VENV_DIR/bin/activate"

transforms=("add_noise" "default" "dropout" "restyle" "summarize")

# Run for each transform
for TRANSFORM in "${transforms[@]}"; do
    echo "Running with transform: $TRANSFORM"
    python run.py "bookstack" "${TRANSFORM}" --config-path "./configs/qwen-7b/${TRANSFORM}.yaml"
done