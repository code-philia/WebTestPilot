#!/bin/bash

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
    docker compose down -v
    sleep 3
    docker compose up -d
)

# If patch provided → inject bug
if [[ -n "$patch_name" ]]; then
    if [[ "$app_name" == "indico" ]]; then
        echo "⏳ Waiting for Indico setup to complete..."
        until curl -s http://localhost:8080 | grep -q "All events"; do
            echo "   ... Indico not ready yet, retrying in 5s"
            sleep 5
        done
        echo "✅ Indico is ready, continuing with patch"
    fi

    if [[ "$app_name" == "prestashop" ]]; then
        echo "⏳ Waiting for Prestashop setup to complete..."
        until curl -s http://localhost:8083 | grep -q "PrestaShop"; do
            echo "   ... Prestashop not ready yet, retrying in 5s"
            sleep 5
        done
        echo "✅ Prestashop is ready, continuing with patch"
    fi

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
    
else
    echo "ℹ️  No patch provided. Skipping bug injection."
fi

# Create buyer user for PrestaShop at the beginning
if [[ "$app_name" == "prestashop" ]]; then
    until curl -s http://localhost:8083 > /dev/null 2>&1; do
        echo "Waiting for PrestaShop to ready..."
        sleep 10
    done
    
    echo "PrestaShop is ready, creating buyer user..."
    docker exec "$container" php /var/www/html/tools/create_user.php
fi

echo "✅ Done."