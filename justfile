set shell := ["bash", "-euo", "pipefail", "-c"]

# Experiments: `just run <recipe> ...` (see `just --list run`)
mod run "experiments/run.just"

# List available recipes
default:
    @just --list --unsorted --list-submodules

# ============================================
# Setup
# ============================================

# Set up everything: .env, benchmark submodule, WebTestPilot, and baselines
setup: setup-env setup-benchmark setup-webtestpilot setup-baselines

# Create .env from .env.example (never overwrites an existing .env)
setup-env:
    @if [[ -f .env ]]; then echo ".env already exists, leaving it unchanged"; else cp .env.example .env && echo "Created .env, fill in your API keys"; fi

# Fetch the benchmark submodule
setup-benchmark: _require-tools
    git submodule update --init benchmark

# Install WebTestPilot and generate its BAML client
setup-webtestpilot: _require-tools && generate-baml
    cd webtestpilot && uv sync

# Install the baselines (PinATA, LaVague, NaviQAte)
setup-baselines: _require-tools
    for baseline in pinata lavague naviqate; do \
        echo "→ $baseline"; \
        (cd "baselines/$baseline" && uv sync); \
    done

# ============================================
# WebTestPilot (standalone)
# ============================================

# Install WebTestPilot as an editable package into the active Python environment
install-webtestpilot: && generate-baml
    python -m pip install -e ./webtestpilot

# Generate WebTestPilot's BAML Python client (required before importing webtestpilot)
generate-baml:
    cd webtestpilot && uv run baml-cli generate

# Serve the GUI grounding model used by SoM mode (requires vLLM); extra args go to `vllm serve`
serve-grounding-model *args:
    vllm serve inclusionAI/UI-Venus-Ground-7B \
        --max_model_len 4K \
        --max_num_seqs 8 \
        --trust-remote-code \
        --limit-mm-per-prompt '{"image": 1, "video": 0}' \
        {{args}}

[private]
_require-tools:
    #!/usr/bin/env bash
    set -euo pipefail
    for tool in uv docker; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            echo "❌ '$tool' is not installed." >&2
            exit 1
        fi
    done
    if ! docker compose version >/dev/null 2>&1; then
        echo "❌ The Docker Compose plugin ('docker compose') is not installed." >&2
        exit 1
    fi
