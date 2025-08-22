#!/usr/bin/env bash

# ---------------------------
# Configurable lists
# ---------------------------
BASELINES=("lavague" "pinata" "naviqate" "webtestpilot")
APPS=("bookstack" "invoiceninja" "indico" "prestashop")

# ---------------------------
# Input arguments
# ---------------------------
BASELINE=${1:-}
APP=${2:-}
RERUN=${3:-}  # Optional: comma-separated test numbers (e.g., "1,10,7,24,25")

if [[ -z "$BASELINE" ]]; then
    echo "Usage: $0 <baseline> <app> [rerun_numbers]"
    echo "  baseline: ${BASELINES[*]}"
    echo "  app: ${APPS[*]}"
    echo "  rerun_numbers: optional comma-separated test numbers (e.g., '1,10,7,24,25')"
    return 1
fi

if [[ -z "$APP" ]]; then
    echo "Error: APP is required. Valid options: ${APPS[*]}"
    return 1
fi

# ---------------------------
# Validate choices
# ---------------------------
if [[ ! " ${BASELINES[*]} " =~ " $BASELINE " ]]; then
    echo "Invalid baseline: $BASELINE"
    echo "Valid options: ${BASELINES[*]}"
    return 1
fi

if [[ ! " ${APPS[*]} " =~ " $APP " ]]; then
    echo "Invalid app: $APP"
    echo "Valid options: ${APPS[*]}"
    return 1
fi

# ---------------------------
# Absolute paths relative to script
# ---------------------------
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
BASELINE_DIR="$SCRIPT_DIR/../../baselines"
VENV_DIR="$BASELINE_DIR/$BASELINE/.venv"

EXPERIMENTS_DIR="$SCRIPT_DIR"
RESULTS_DIR="$EXPERIMENTS_DIR/results/$BASELINE"
TEST_DIR="$EXPERIMENTS_DIR/input/$APP"

# ---------------------------
# Run evaluation
# ---------------------------
echo "Running baseline: $BASELINE, app: $APP"
echo "Output directory: $RESULTS_DIR"
echo "Test directory: $TEST_DIR"

if [[ -n "$RERUN" ]]; then
    echo "Rerunning tests: $RERUN"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Run the evaluation script
if [[ -n "$RERUN" ]]; then
    python "$BASELINE_DIR/evaluate.py" "$BASELINE" "$APP" \
        --output-dir "$RESULTS_DIR" \
        --test-dir "$TEST_DIR" \
        --rerun "$RERUN"
else
    python "$BASELINE_DIR/evaluate.py" "$BASELINE" "$APP" \
        --output-dir "$RESULTS_DIR" \
        --test-dir "$TEST_DIR"
fi