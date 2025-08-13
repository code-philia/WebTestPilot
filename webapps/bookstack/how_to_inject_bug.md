## Injecting Bugs in BookStack

This guide explains how to inject and roll back bugs inside a running **BookStack** Docker Container (e.g., `bookstack-app-1`).

------

### 1. Copy the Patch File into the Container

Suppose your patch file is located at `./bugs/book-create-1.patch` on your host machine. To copy it to your container’s `/tmp/` directory, use:

```bash
docker cp ./bugs/book-create-1.patch bookstack-app-1:/tmp/change.patch
```

------

### 2. Apply the Patch Inside the Container

Run the following command to enter the BookStack codebase directory (usually `/var/www/html`) and apply the patch:

```bash
docker exec -w /var/www/bookstack bookstack-app-1 patch -p0 -i /tmp/change.patch --fuzz=10 --verbose
```

- `-p1`: Strips the first component of the patch paths (adjust if your patch is generated differently).
- `--fuzz=10`: Allows some flexibility for minor code shifts.
- `--verbose`: Prints detailed output for debugging.

------

### 3. Restart the Web Service

**After applying or reverting a patch, restart for changes to take effect:**

```bash
docker compose restart app
```

------

### 4. Roll Back (Revert) a Previously Applied Patch

If you need to **undo** a patch (revert changes), use the same command with the `-R` flag:

```bash
docker exec -w /var/www/html bookstack-app-1 patch -p1 -R -i /tmp/change.patch --fuzz=10 --verbose
```

> **Note:** The patch file content must be exactly the same as the one you applied, otherwise the revert may fail.
