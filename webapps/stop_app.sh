#!/bin/bash

# Usage check
if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    echo "Usage: $0 <app_name> [patch_file]"
    return 1
fi

app_name="$1"

# Resolve script directory (absolute path, independent of where script is called)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Validate app
case "$app_name" in
    "bookstack"|"indico"|"invoiceninja"|"prestashop")
        # Valid app name
        ;;
    *)
        echo "Error: Unsupported app '$app_name'"
        echo "Supported apps: bookstack indico invoiceninja prestashop"
        return 1
        ;;
esac

cd "$SCRIPT_DIR/$app_name"
docker compose down -v

# Delete all the volumes used in the app to restart the data as well
echo "🗑️  Deleting volumes for $app_name..."

# Define actual volume names for each app (based on current Docker volumes)
case "$app_name" in
    "bookstack")
        volumes_to_delete="bookstack_app_config bookstack_db"
        ;;
    "indico")
        volumes_to_delete="prod_archive prod_customization prod_indico-logs prod_postgres-data prod_redis prod_static-files"
        ;;
    "invoiceninja")
        volumes_to_delete="invoiceninja_app_cache invoiceninja_app_public invoiceninja_app_storage invoiceninja_mysql invoiceninja_redis"
        ;;
    "prestashop")
        volumes_to_delete=""
        ;;
    *)
        volumes_to_delete=""
        ;;
esac

if [ -n "$volumes_to_delete" ]; then
    for volume_name in $volumes_to_delete; do
        if docker volume inspect "$volume_name" >/dev/null 2>&1; then
            # Find and remove any containers using this volume
            containers_using_volume=$(docker ps -a --filter volume="$volume_name" -q 2>/dev/null)
            if [ -n "$containers_using_volume" ]; then
                echo "  Removing containers using volume $volume_name: $containers_using_volume"
                docker rm -f $containers_using_volume 2>/dev/null || echo "    ⚠️  Some containers couldn't be removed"
            fi
            
            echo "  Removing volume: $volume_name"
            docker volume rm "$volume_name" 2>/dev/null || echo "  ⚠️  Failed to remove volume: $volume_name"
        else
            echo "  Volume $volume_name not found (already removed or never created)"
        fi
    done
else
    echo "  No named volumes to delete for $app_name"
fi

echo "✅ Done. $app_name is stopped and all volumes deleted."