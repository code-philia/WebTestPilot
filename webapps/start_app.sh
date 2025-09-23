#!/bin/bash

wait_for_application() {
    local app_name="$1"
    local max_wait=${2:-240}  # Default 4 minutes
    local start_time=$(date +%s)
    local url=""
    local check_text=""
    
    # Map application to URL and readiness check text
    case "$app_name" in
        "indico")
            url="http://localhost:8080"
            check_text="All events"
            ;;
        "invoiceninja")
            url="http://localhost:8082"
            check_text="Invoice Ninja"
            ;;
        "prestashop")
            url="http://localhost:8083"
            check_text="Ecommerce software by PrestaShop"
            ;;
        "bookstack")
            url="http://localhost:8081/"
            check_text="Redirecting to"
            ;;
        *)
            echo "Error: Unknown application '$app_name' for wait check"
            return 1
            ;;
    esac
    
    echo "⏳ Waiting for $app_name to be ready at $url..."
    
    while [ $(( $(date +%s) - start_time )) -lt $max_wait ]; do
        if curl -s "$url" 2>/dev/null | grep -q "$check_text"; then
            echo "✅ $app_name is ready"
            return 0
        else
            echo "   ... $app_name not ready, retrying in 15s"
            sleep 15
        fi
    done
    
    echo "Warning: $app_name may not be fully ready after ${max_wait}s"
    return 1
}

# Usage check
if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    echo "Usage: $0 <app_name> [patch_file]"
    return 1
fi

app_name="$1"
patch_name="${2:-}"   # optional

# Resolve script directory (absolute path, independent of where script is called)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Supported apps
case "$app_name" in
    "bookstack")
        app_config="bookstack-app-1:/var/www/bookstack/resources -p0"
        ;;
    "indico")
        app_config="indico-web-1:/opt/indico/.venv/lib/python3.12/site-packages -p1"
        ;;
    "invoiceninja")
        app_config="invoiceninja-app-1:/var/www/html -p1"
        ;;
    "prestashop")
        app_config="prestashop-app-1:/var/www/html -p1"
        ;;
    *)
        echo "Error: Unsupported app '$app_name'"
        echo "Supported apps: bookstack, indico, invoiceninja, prestashop"
        return 1
        ;;
esac

# If patch is provided, validate file
if [[ -n "$patch_name" ]]; then
    patch_path="$SCRIPT_DIR/$app_name/bugs/$patch_name"
    if [ ! -f "$patch_path" ]; then
        echo "Error: Patch file not found: $patch_path"
        return 1
    fi
fi

# Parse container and target path
container=$(echo "$app_config" | cut -d: -f1)
workdir=$(echo "$app_config" | cut -d: -f2 | awk '{print $1}')
patch_level=$(echo "$app_config" | awk '{print $NF}')

# Reset app
echo "🔄 Resetting $app_name environment..."
(
    cd "$SCRIPT_DIR/$app_name"
    if [[ "$app_name" == "indico" ]]; then
        # Special handling for Indico to retry down on volume mkdir error
        success=false
        while ! $success; do
            output=$(docker compose down -v --remove-orphans 2>&1)
            if echo "$output" | grep -q "failed to mkdir.*file exists"; then
                echo "Detected Indico volume mkdir error during down, retrying in 5s..."
                sleep 5
            else
                success=true
            fi
        done
    else
        docker compose down -v --remove-orphans
    fi
    sleep 5
    docker compose up -d
)

wait_for_application "$app_name"

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
            docker compose -f "$SCRIPT_DIR/$app_name/docker-compose.yaml" restart web
        else
            echo "🔄 Restarting $app_name app service..."
            docker compose -f "$SCRIPT_DIR/$app_name/docker-compose.yaml" restart app
        fi
    )
    
    echo "Checking after injecting bug for $app_name..."
    wait_for_application "$app_name"
else
    echo "ℹ️  No patch provided. Skipping bug injection."
fi

# Create buyer user for PrestaShop, by this point, app is always ready.
if [[ "$app_name" == "prestashop" ]]; then
    echo "👤 Creating buyer user..."
    docker exec "$container" php /var/www/html/tools/create_user.php
    echo "👤 Created buyer user..."
fi

echo "$app_name start script done!"
