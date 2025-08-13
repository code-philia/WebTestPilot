## Injecting Bugs in Invoice Ninja

This guide explains how to inject and roll back bugs inside a running **Invoice Ninja** Docker container (e.g., `invoiceninja-app-1`).

------

### 1. Copy the Patch File into the Container

Suppose your patch file is at `./bugs/payment-email-1.patch` on your host. Copy it to `/tmp/` in the container:

```bash
docker cp ./bugs/payment-email-1.patch invoiceninja-app-1:/tmp/change.patch
```

------

### 2. Apply the Patch Inside the Container

Change to the Invoice Ninja code directory (`/var/www/html`) and apply the patch:

```bash
docker exec -w /var/www/html invoiceninja-app-1 patch -p1 -i /tmp/change.patch --verbose --fuzz=10
```

- `-p1`: Strips the first path component (Git patches use `a/` and `b/`).
- `--fuzz=10`: Allows minor context mismatches.
- `--verbose`: Prints detailed output for debugging.

------

### 3. Restart the Web Service

**After applying or reverting a patch, restart for changes to take effect:**

```bash
docker compose restart app
```

------

### 4. Roll Back (Revert) a Previously Applied Patch

To **undo** a patch, use `-R` and then restart:

```bash
docker exec -w /var/www/html invoiceninja-app-1 patch -p1 -R -i /tmp/change.patch --verbose --fuzz=10

docker compose restart app
```

> **Note:** Use the **exact same** patch file you originally applied.
