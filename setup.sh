#!/usr/bin/env bash

set -e

# ---- check for uv ----
if ! command -v uv >/dev/null 2>&1; then
    echo "'uv' is not installed."
    echo "Please install it from:"
    echo "  https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# ---- check for docker ----
if ! command -v docker >/dev/null 2>&1; then
    echo "'docker' is not installed."
    echo "Please install Docker from:"
    echo "  https://docs.docker.com/get-docker/"
    exit 1
fi

# ---- check for docker-compose ----
# supports both docker-compose standalone and v2 plugin
if ! command -v docker-compose >/dev/null 2>&1 && ! docker compose version >/dev/null 2>&1; then
    echo "'docker-compose' is not installed."
    echo "Please install Docker Compose from:"
    echo "  https://docs.docker.com/compose/install/"
    exit 1
fi

# ---- helper function ----
ask_yes_no() {
    local prompt="$1"
    while true; do
        read -r -p "$prompt (y/n): " ans
        case "$ans" in
            [Yy]* ) return 0 ;;
            [Nn]* ) return 1 ;;
            * ) echo "Please answer y or n." ;;
        esac
    done
}

# ---- baselines setup ----
if ask_yes_no "Set up baselines (PinATA, LaVague, NaviQAte)?"; then
    echo "Setting up baselines..."
    for dir in pinata lavague naviqate; do
        echo "→ $dir"
        cd "./baselines/$dir"
        uv sync
        cd - >/dev/null
    done
    echo "Baselines setup complete."
else
    echo "Skipping baselines."
fi

# ---- webtestpilot setup ----
if ask_yes_no "Set up WebTestPilot?"; then
    echo "Setting up WebTestPilot..."
    cd "./webtestpilot"
    uv sync
    uv run baml-cli generate
    cd - >/dev/null
    echo "WebTestPilot setup complete."
else
    echo "Skipping webtestpilot."
fi