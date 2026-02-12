#!/usr/bin/env bash
set -euo pipefail

# ============================================
# Configuration
# ============================================

# Allowed methods and applications
ALLOWED_METHODS=("pinata" "webtestpilot" "naviqate" "lavague")
ALLOWED_APPLICATIONS=("indico" "invoiceninja" "prestashop" "bookstack")

# ============================================
# Helper Functions
# ============================================

# Print usage
usage() {
    echo "Usage: $0 <METHOD> <APPLICATION>"
    echo "METHOD options: ${ALLOWED_METHODS[*]}"
    echo "APPLICATION options: ${ALLOWED_APPLICATIONS[*]}"
    exit 1
}

# Validate that a value is in an array
validate_choice() {
    local value="$1"
    shift
    local choices=("$@")
    if [[ ! " ${choices[*]} " =~ " ${value} " ]]; then
        echo "❌ Invalid value: $value"
        echo "Allowed values: ${choices[*]}"
        exit 1
    fi
}

# Determine virtualenv path based on method
get_venv_path() {
    local method="$1"
    if [[ "$method" == "webtestpilot" ]]; then
        echo "$BASE_PATH/webtestpilot/.venv"
    else
        echo "$BASE_PATH/baselines/$method/.venv"
    fi
}

# Run the Python evaluation
run_python_module() {
    local method="$1"
    local application="$2"
    local output_dir="$3"
    local benchmark_dir="$4"

    mkdir -p "$output_dir"

    # Run Python module after activating venv
    LOG_FILE="$output_dir/run_$(date +%Y%m%d_%H%M%S).log"

    python -u -m baselines.evaluate \
        "$method" \
        "$application" \
        --output-dir "$output_dir" \
        --headless \
        --test-paths "$benchmark_dir/test_cases" \
        2>&1 | tee "$LOG_FILE"
}

# ============================================
# Main Script
# ============================================

# Check arguments
if [[ $# -ne 2 ]]; then
    usage
fi

METHOD="$1"
APPLICATION="$2"

# Current script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Project directory
BASE_PATH="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Validate inputs
validate_choice "$METHOD" "${ALLOWED_METHODS[@]}"
validate_choice "$APPLICATION" "${ALLOWED_APPLICATIONS[@]}"

# Determine venv path and ensure it exists
VENV_PATH="$(get_venv_path "$METHOD")"
ACTIVATE_SCRIPT="$VENV_PATH/bin/activate"

if [[ ! -f "$ACTIVATE_SCRIPT" ]]; then
    echo "❌ Virtualenv not found at $ACTIVATE_SCRIPT"
    exit 1
fi

# Activate virtualenv
# shellcheck disable=SC1090
source "$ACTIVATE_SCRIPT"

# Set output and benchmark directories
OUTPUT_DIR="$SCRIPT_DIR/results/${METHOD}_${APPLICATION}"
BENCHMARK_DIR="$BASE_PATH/benchmark/$APPLICATION"

# Run evaluation
cd "$BASE_PATH"
run_python_module "$METHOD" "$APPLICATION" "$OUTPUT_DIR" "$BENCHMARK_DIR"

echo "✅ Evaluation finished for METHOD=$METHOD APPLICATION=$APPLICATION"
echo "Results saved to $OUTPUT_DIR"
