#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

wait_for_application() {
    local app_name="$1"
    local max_wait=${2:-60}  # Default 60 seconds
    local start_time=$(date +%s)
    local url=""
    local check_text=""
    
    # Map application to URL and readiness check text
    case "$app_name" in
        "indico") url="http://localhost:8080"; check_text="All events";;
        "invoiceninja") url="http://localhost:8082"; check_text="Invoice Ninja";;
        "prestashop") url="http://localhost:8083"; check_text="Ecommerce software by PrestaShop";;
        "bookstack") url="http://localhost:8081/"; check_text="Redirecting to";;
        *) echo "❌ Unknown application '$app_name' for wait check" >&2; exit 1;;
    esac
    
    echo "⏳ Waiting for $app_name to be ready at $url..."
    
    while [ $(( $(date +%s) - start_time )) -lt $max_wait ]; do
        if curl -s "$url" 2>/dev/null | grep -q "$check_text"; then
            echo "✅ $app_name is ready"
            return 0
        else
            echo "   ... $app_name not ready, retrying in 5s"
            sleep 5
        fi
    done
    
    echo "❌ $app_name did not become ready after ${max_wait}s" >&2
    exit 1
}

seed_data() {
    local app="$1"
    local SEED_FILE="$SCRIPT_DIR/$app/seed.sql"

    case "$app" in
        "indico") docker exec -i indico-postgres-1 psql -U "$PGUSER" -d "$PGDATABASE" < "$SEED_FILE" > /dev/null ;;
        "prestashop")
            YESTERDAY=$(date -d "yesterday" +"%Y-%m-%d")
            sed "s/YYYY-MM-DD/$YESTERDAY/g" "$SEED_FILE" | \
                docker exec -i prestashop-db-1 mysql -u root -proot prestashop > /dev/null
            ;;
        "bookstack")
            YESTERDAY=$(date -d "yesterday" +"%Y-%m-%d")
            sed "s/YYYY-MM-DD/$YESTERDAY/g" "$SEED_FILE" | \
                docker exec -i bookstack-db-1 \
                    mysql -u admin -padmin bookstack > /dev/null
            ;;
        "invoiceninja") docker exec -i invoiceninja-mysql-1 mysql -u "$DB_USERNAME" -p"$DB_PASSWORD" "$DB_DATABASE" < "$SEED_FILE" > /dev/null ;;
        *) echo "❌ No seed data available for app '$app'" >&2; exit 1 ;;
    esac

    # Special case: Create buyer user for PrestaShop
    if [[ "$app" == "prestashop" ]]; then
        docker exec "$container" php /var/www/html/tools/create_user.php > /dev/null
    fi

    echo "✅ Seed data loaded successfully for $app"
}

# ----- Argument Parsing -----
if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    echo "Usage: $0 <app_name> [--no-seed]" >&2
    exit 1
fi


app_name="$1"

# Check for --no-seed flag
no_seed=false
if [[ "${2:-}" == "--no-seed" ]]; then
    no_seed=true
fi

# Load env if exists
if [[ -f "$SCRIPT_DIR/$app_name/.env" ]]; then
    source "$SCRIPT_DIR/$app_name/.env"
    echo "📝 Loaded environment variables from $SCRIPT_DIR/$app_name/.env"
fi

# Supported apps
case "$app_name" in
    "bookstack") app_config="bookstack-app-1:/var/www/bookstack/resources -p0";;
    "indico") app_config="indico-web-1:/opt/indico/.venv/lib/python3.12/site-packages -p1";;
    "invoiceninja") app_config="invoiceninja-app-1:/var/www/html -p1";;
    "prestashop") app_config="prestashop-app-1:/var/www/html -p1";;
    *) echo "❌ Unsupported app '$app_name'" >&2; exit 1;;
esac

container=$(echo "$app_config" | cut -d: -f1)
workdir=$(echo "$app_config" | cut -d: -f2 | awk '{print $1}')

# Reset app
echo "🔄 Resetting $app_name environment..."
(
    cd "$SCRIPT_DIR/$app_name"
    docker compose down -v --remove-orphans > /dev/null

    if [[ "$app_name" == "indico" ]]; then
        docker volume rm indico_static-files 2>/dev/null || true
    fi

    sleep 5

    success=false
    while ! $success; do
        if docker compose up -d > /dev/null | tee /dev/tty | grep -iE "mkdir|failed|error"; then
            echo "⚠️ Detected error during compose up, retrying in 5s..." >&2
            sleep 5
        else
            success=true
        fi
    done
)

wait_for_application "$app_name"

# Seed
if [[ "$no_seed" == false ]]; then
    seed_data "$app_name"
else
    echo "ℹ️  Skipping seed data loading due to --no-seed flag"
fi

echo "✅ $app_name start script done!"
