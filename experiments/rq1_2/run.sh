#!/usr/bin/env bash
set -euo pipefail

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
    exit 1
fi

if [[ -z "$APP" ]]; then
    echo "Error: APP is required. Valid options: ${APPS[*]}"
    exit 1
fi

# ---------------------------
# Validate choices
# ---------------------------
if [[ ! " ${BASELINES[*]} " =~ " $BASELINE " ]]; then
    echo "Invalid baseline: $BASELINE"
    echo "Valid options: ${BASELINES[*]}"
    exit 1
fi

if [[ ! " ${APPS[*]} " =~ " $APP " ]]; then
    echo "Invalid app: $APP"
    echo "Valid options: ${APPS[*]}"
    exit 1
fi

# ---------------------------
# Absolute paths relative to script
# ---------------------------
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
BASELINE_DIR="$SCRIPT_DIR/../../baselines/$BASELINE"
VENV_DIR="$BASELINE_DIR/.venv"
RESULTS_DIR="$BASELINE_DIR/results/$BASELINE"
TEST_DIR="$BASELINE_DIR/input/$APP"

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