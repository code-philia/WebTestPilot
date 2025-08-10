## 🛠️ Applying and Rolling Back Patches in Invoice Ninja Docker Containers

This guide explains how to apply and roll back code patches inside a running **Invoice Ninja** Docker container (e.g., `invoiceninja-app-1`). These steps are handy for hotfixes, feature experiments, or **injecting bugs** during testing.

------

### 1. Copy the Patch File into the Container

Suppose your patch file is at `./bugs/payment-email-1.patch` on your host. Copy it to `/tmp/` in the container:

```bash
docker cp ./bugs/payment-email-1.patch invoiceninja-app-1:/tmp/my-patch.patch
```

------

### 2. Apply the Patch Inside the Container

Change to the Invoice Ninja code directory (`/var/www/html`) and apply the patch:

```bash
docker exec -w /var/www/html invoiceninja-app-1 patch -p1 -i /tmp/my-patch.patch --verbose --fuzz=10
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
docker exec -w /var/www/html invoiceninja-app-1 patch -p1 -R -i /tmp/my-patch.patch --verbose --fuzz=10

docker compose restart app
```

> **Note:** Use the **exact same** patch file you originally applied.

------

### 5. Troubleshooting Tips

- **"No such file or directory"**
   Check the patch path inside the container (`/tmp/my-patch.patch`) and that you’re in `/var/www/html`.
- **"Reversed (or previously applied) patch detected!"**
   The patch was already applied (or reverted). Use `-R` to revert, or re-apply appropriately.
- **Patch fails or partially applies**
   Ensure your working directory and code version match the patch’s context. Consider increasing `--fuzz` slightly, or merge manually.
- **Changes don’t take effect**
   Always `docker compose restart app`. For PHP changes, clear Laravel caches as shown above. For front-end files (e.g., `public/main.dart.js`), force-refresh the browser cache too.

------

### Example Command Summary

```bash
# Copy patch into container
docker cp ./bugs/payment-email-1.patch invoiceninja-app-1:/tmp/my-patch.patch

# Apply patch
docker exec -w /var/www/html invoiceninja-app-1 patch -p1 -i /tmp/my-patch.patch --verbose --fuzz=10

# Restart web service
docker compose restart app

# Revert patch
docker exec -w /var/www/html invoiceninja-app-1 patch -p1 -R -i /tmp/my-patch.patch --verbose --fuzz=10

# Restart again
docker compose restart app
```

------

**Customize the patch filename, container name, and code directory as needed for your setup.**
 If anything looks off, check the `patch` output—it usually tells you exactly what went wrong.