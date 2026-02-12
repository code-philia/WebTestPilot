#!/usr/bin/env bash
set -euo pipefail

# ============================================
# Configuration
# ============================================

ALLOWED_APPLICATIONS=("indico" "invoiceninja" "prestashop" "bookstack")
ALLOWED_MODELS=("qwen-3b" "qwen-7b" "qwen-32b" "qwen-72b")

# ============================================
# Helper Functions
# ============================================

usage() {
    echo "Usage: $0 <MODEL> <APPLICATION>"
    echo "MODEL options      : ${ALLOWED_MODELS[*]}"
    echo "APPLICATION options: ${ALLOWED_APPLICATIONS[*]}"
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
    local method_config_path="$2"
    local output_dir="$3"
    local benchmark_dir="$4"

    mkdir -p "$output_dir"

    local log_file="$output_dir/run_$(date +%Y%m%d_%H%M%S).log"

    python -u -m baselines.evaluate \
        webtestpilot \
        "$application" \
        --output-dir "$output_dir" \
        --headless \
        --method-config-path "$method_config_path" \
        --test-paths "$benchmark_dir" \
        2>&1 | tee "$log_file"
}

# ============================================
# Main Script
# ============================================

if [[ $# -ne 2 ]]; then
    usage
fi

MODEL="$1"
APPLICATION="$2"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_PATH="$(cd "$SCRIPT_DIR/../.." && pwd)"

validate_choice "$MODEL" "${ALLOWED_MODELS[@]}"
validate_choice "$APPLICATION" "${ALLOWED_APPLICATIONS[@]}"

# ============================================
# Virtual environment
# ============================================

VENV_PATH="$BASE_PATH/webtestpilot/.venv"
ACTIVATE_SCRIPT="$VENV_PATH/bin/activate"

if [[ ! -f "$ACTIVATE_SCRIPT" ]]; then
    echo "❌ Virtualenv not found: $ACTIVATE_SCRIPT"
    exit 1
fi

# shellcheck disable=SC1090
source "$ACTIVATE_SCRIPT"

# ============================================
# Paths
# ============================================

METHOD_CONFIG_PATH="$SCRIPT_DIR/method_config.yaml"
OUTPUT_DIR="$SCRIPT_DIR/results/${MODEL}_${APPLICATION}"
BENCHMARK_DIR="$BASE_PATH/benchmark/$APPLICATION/test_cases"

if [[ ! -f "$METHOD_CONFIG_PATH" ]]; then
    echo "❌ Method config not found: $METHOD_CONFIG_PATH"
    exit 1
fi

if [[ ! -d "$BENCHMARK_DIR" ]]; then
    echo "❌ Benchmark directory not found: $BENCHMARK_DIR"
    exit 1
fi

# ============================================
# Run
# ============================================

cd "$BASE_PATH"

run_python_module \
    "$APPLICATION" \
    "$METHOD_CONFIG_PATH" \
    "$OUTPUT_DIR" \
    "$BENCHMARK_DIR"

echo
echo "✅ Evaluation completed successfully"
echo "📦 MODEL       : $MODEL"
echo "📱 APPLICATION : $APPLICATION"
echo "📁 Results     : $OUTPUT_DIR"
