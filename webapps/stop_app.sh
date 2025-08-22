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

echo "✅ Done. $app_name is stopped and all volumes deleted."