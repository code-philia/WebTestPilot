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

seed_data() {
    SEED_FILE="$SCRIPT_DIR/$1/seed.sql"

    case "$1" in
        "indico") docker exec -i indico-postgres-1 psql -U "$PGUSER" -d "$PGDATABASE" < "$SEED_FILE" ;;
        "prestashop") docker exec -i prestashop-db-1 mysql -u root -proot prestashop < "$SEED_FILE" ;;
        "bookstack") docker exec -i bookstack-db-1 mysql -u admin -padmin bookstack < "$SEED_FILE" ;;
        "invoiceninja") docker exec -i invoiceninja-mysql-1 mysql -u "$DB_USERNAME" -p"$DB_PASSWORD" "$DB_DATABASE" < "$SEED_FILE" ;;
        *) echo "Error: No seed data available for app '$1'"; return 1 ;;
    esac

    # Special case: Create buyer user for PrestaShop
    # TODO: Put this in seed.sql file?
    if [[ "$1" == "prestashop" ]]; then
        docker exec "$container" php /var/www/html/tools/create_user.php
    fi

    if [ $? -eq 0 ]; then
        echo "✅ Seed data loaded successfully for $1"
    else
        echo "❌ Failed to load seed data for $1"
        return 1
    fi
}

# Usage check
if [ $# -lt 1 ] || [ $# -gt 3 ]; then
    echo "Usage: $0 <app_name> [patch_file] [--no-seed]"
    echo "  --no-seed: Skip seeding initial data (default: seed data)"
    return 1
fi

app_name="$1"
patch_name="${2:-}"   # optional
no_seed=false

# Check for --no-seed flag
if [[ "$2" == "--no-seed" ]]; then
    no_seed=true
    patch_name=""
elif [[ "$3" == "--no-seed" ]]; then
    no_seed=true
fi

# Resolve script directory (absolute path, independent of where script is called)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load environment variables from .env file if it exists
if [[ -f "$SCRIPT_DIR/$app_name/.env" ]]; then
    source "$SCRIPT_DIR/$app_name/.env"
    echo "📝 Loaded environment variables from $SCRIPT_DIR/$app_name/.env"
fi

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
    docker compose down -v --remove-orphans

    sleep 5

    # Add retries to make sure app will start
    success=false
    while ! $success; do
        if docker compose up -d 2>&1 | tee /dev/tty | grep -iE "mkdir|failed|error"; then
            echo "Detected error during compose up, retrying in 5s..."
            sleep 5
        else
            success=true
        fi
    done
)

wait_for_application "$app_name"
if [[ "$no_seed" == false ]]; then
    seed_data "$app_name"
else
    echo "ℹ️  Skipping seed data loading due to --no-seed flag"
fi

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

echo "$app_name start script done!"
