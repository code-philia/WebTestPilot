#!/bin/bash
set -euo pipefail

# Usage check
if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    echo "Usage: $0 <app_name> [patch_file]"
    exit 1
fi

app_name="$1"
patch_name="${2:-}"   # optional

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

# If patch is provided, validate file
if [[ -n "$patch_name" ]]; then
    patch_path="$SCRIPT_DIR/$app_name/bugs/$patch_name"
    if [ ! -f "$patch_path" ]; then
        echo "Error: Patch file not found: $patch_path"
        exit 1
    fi
fi

# Parse container and target path
container=$(echo "${apps[$app_name]}" | cut -d: -f1)
workdir=$(echo "${apps[$app_name]}" | cut -d' ' -f2)
patch_level=$(echo "${apps[$app_name]}" | awk '{print $NF}')

# Reset app
echo "🔄 Resetting $app_name environment..."
(
    cd "$SCRIPT_DIR/$app_name"
    docker compose down -v
    sleep 3
    docker compose up -d
)

# If patch provided → inject bug
if [[ -n "$patch_name" ]]; then
    echo "📦 Injecting patch: $patch_name into $app_name"
    docker cp "$patch_path" "$container:/tmp/change.patch"
    docker exec -w "$workdir" "$container" patch "$patch_level" -i /tmp/change.patch --fuzz=10 --verbose

    # Restart app
    echo "🔄 Restarting $app_name environment..."
    (
        cd "$SCRIPT_DIR/$app_name"
        if [[ "$app_name" == "indico" ]]; then
            echo "🔄 Restarting Indico web service..."
            docker compose -f "$SCRIPT_DIR/$app_name/docker-compose.yml" restart web
        else
            echo "🔄 Restarting $app_name app service..."
            docker compose -f "$SCRIPT_DIR/$app_name/docker-compose.yml" restart app
        fi
    )
    
else
    echo "ℹ️  No patch provided. Skipping bug injection."
fi

echo "✅ Done. $app_name is up and running."