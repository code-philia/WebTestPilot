#!/usr/bin/env bash
set -euo pipefail

# ============================================
# Configuration
# ============================================

ALLOWED_MODELS=("gpt" "qwen-3b" "qwen-7b" "qwen-32b" "qwen-72b")
ALLOWED_APPLICATIONS=("indico" "invoiceninja" "prestashop" "bookstack")
ALLOWED_TRANSFORMATIONS=("dropout" "summarize" "restyle" "add_noise")

# ============================================
# Helper Functions
# ============================================

usage() {
    echo "Usage: $0 <MODEL> <APPLICATION> <TRANSFORMATION>"
    echo "MODEL options      : ${ALLOWED_MODELS[*]}"
    echo "APPLICATION options: ${ALLOWED_APPLICATIONS[*]}"
    echo "TRANSFORMATION options: ${ALLOWED_TRANSFORMATIONS[*]}"
    exit 1
}

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

run_python_module() {
    local application="$1"
    local transformation="$2"
    local method_config_path="$3"
    local output_dir="$4"
    local benchmark_dir="$5"

    mkdir -p "$output_dir"

    local LOG_FILE="$output_dir/run_$(date +%Y%m%d_%H%M%S).log"

    python -u -m baselines.evaluate \
        webtestpilot \
        "$application" \
        --output-dir "$output_dir" \
        --headless \
        --method-config-path "$method_config_path" \
        --test-paths "$benchmark_dir" \
        2>&1 | tee "$LOG_FILE"
}

# ============================================
# Main Script
# ============================================

if [[ $# -ne 3 ]]; then
    usage
fi

MODEL="$1"
APPLICATION="$2"
TRANSFORMATION="$3"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_PATH="$(cd "$SCRIPT_DIR/../.." && pwd)"

validate_choice "$MODEL" "${ALLOWED_MODELS[@]}"
validate_choice "$APPLICATION" "${ALLOWED_APPLICATIONS[@]}"
validate_choice "$TRANSFORMATION" "${ALLOWED_TRANSFORMATIONS[@]}"

# Virtualenv
VENV_PATH="$BASE_PATH/webtestpilot/.venv"
ACTIVATE_SCRIPT="$VENV_PATH/bin/activate"

if [[ ! -f "$ACTIVATE_SCRIPT" ]]; then
    echo "❌ Virtualenv not found: $ACTIVATE_SCRIPT"
    exit 1
fi

# Activate venv
# shellcheck disable=SC1090
source "$ACTIVATE_SCRIPT"

METHOD_CONFIG_PATH="$SCRIPT_DIR/method_config.yaml"
OUTPUT_DIR="$SCRIPT_DIR/results/${MODEL}_${APPLICATION}_${TRANSFORMATION}"
BENCHMARK_DIR="$BASE_PATH/benchmark/transform/$APPLICATION/$TRANSFORMATION"

if [[ ! -d "$BENCHMARK_DIR" ]]; then
    echo "❌ Benchmark directory not found: $BENCHMARK_DIR"
    exit 1
fi

cd "$BASE_PATH"

run_python_module \
    "$APPLICATION" \
    "$TRANSFORMATION" \
    "$METHOD_CONFIG_PATH" \
    "$OUTPUT_DIR" \
    "$BENCHMARK_DIR"

echo
echo "✅ Evaluation completed successfully"
echo "📁 Results saved to: $OUTPUT_DIR"
