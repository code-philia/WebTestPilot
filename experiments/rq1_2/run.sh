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

if [[ -z "$BASELINE" ]]; then
    echo "Error: BASELINE is required. Valid options: ${BASELINES[*]}"
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
BASELINE_DIR="$SCRIPT_DIR/baselines/"
VENV_DIR="$BASELINE_DIR/.venv-$BASELINE"

EXPERIMENTS_DIR="$SCRIPT_DIR/experiments/"
RESULTS_DIR="$EXPERIMENTS_DIR/rq1_2/results/$BASELINE"
TEST_DIR="$EXPERIMENTS_DIR/rq1_2/input/$APP"

# ---------------------------
# Run evaluation
# ---------------------------
echo "Running baseline: $BASELINE, app: $APP"
echo "Output directory: $RESULTS_DIR"
echo "Test directory: $TEST_DIR"

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Run the evaluation script
python "$BASELINE_DIR/evaluate.py" "$BASELINE" "$APP" \
    --headless \
    --output-dir "$RESULTS_DIR" \
    --test-dir "$TEST_DIR"