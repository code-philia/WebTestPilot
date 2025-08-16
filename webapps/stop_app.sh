#!/bin/bash
set -euo pipefail

# Usage check
if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    echo "Usage: $0 <app_name> [patch_file]"
    exit 1
fi

app_name="$1"

# Resolve script directory (absolute path, independent of where script is called)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Supported apps
declare -A apps
apps=(
    ["bookstack"]="bookstack-app-1:/var/www/bookstack -p0"
    ["indico"]="indico-web-1:/opt/indico/.venv/lib/python3.12/site-packages -p1"
    ["invoiceninja"]="invoiceninja-app-1:/var/www/html -p1"
    ["prestashop"]="prestashop-app-1:/var/www/html -p1"
)

# Validate app
if [[ -z "${apps[$app_name]+x}" ]]; then
    echo "Error: Unsupported app '$app_name'"
    echo "Supported apps: ${!apps[@]}"
    exit 1
fi

cd "$SCRIPT_DIR/$app_name"
docker compose down -v

echo "✅ Done. $app_name is stopped."