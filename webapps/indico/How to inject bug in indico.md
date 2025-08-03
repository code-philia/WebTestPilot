## 🛠️ Applying and Rolling Back Patches in Indico Docker Containers

This guide explains how to apply and roll back code patches inside a running **Indico Docker container** (e.g., `indico-web-1`). These steps are helpful for hotfixes, feature experiments, or injecting bugs during testing.

------

### 1. Copy the Patch File into the Container

Suppose your patch file is located at `./bugs/conference-registration-setup-1.patch` on your host machine. Copy it to the container’s `/tmp/` directory:

```bash
docker cp ./bugs/conference-registration-setup-1.patch indico-web-1:/tmp/change.patch
```

------

### 2. Apply the Patch Inside the Container

Change to the Indico code directory (typically within Python site-packages), and apply the patch:

```bash
docker exec -w /opt/indico/.venv/lib/python3.12/site-packages indico-web-1 patch -p1 -i /tmp/change.patch --verbose --fuzz=10
```

- `-p1`: Strips the first component of the patch paths (adjust if your patch was generated differently).
- `--fuzz=10`: Allows for minor mismatches in the context lines.
- `--verbose`: Prints detailed output for debugging.

------

### 3. Restart the Web Service

**After applying or reverting a patch, you must restart the web service for changes to take effect:**

```bash
docker compose restart web
```

------

### 4. Roll Back (Revert) a Previously Applied Patch

To **undo** (revert) a patch, use the same command with the `-R` flag, and restart the service:

```bash
docker exec -w /opt/indico/.venv/lib/python3.12/site-packages indico-web-1 patch -p1 -R -i /tmp/change.patch --verbose --fuzz=10

docker compose restart web
```

> **Note:** The patch file must be exactly the same as the one you originally applied.

------

### 5. Troubleshooting Tips

- **"No such file or directory":** Double-check the patch file’s path inside the container.
- **"Reversed (or previously applied) patch detected!":** The patch has already been applied or reverted. Use the `-R` flag or follow the prompts as needed.
- **Patch fails or is only partially applied:** Ensure you’re in the correct working directory, and that your Indico source code matches the patch’s context.
- **Changes don’t take effect:** Always restart the web service after patching.

------

### Example Command Summary

```bash
# Copy patch into container
docker cp ./bugs/your-patch.patch indico-web-1:/tmp/change.patch

# Apply patch inside container
docker exec -w /opt/indico/.venv/lib/python3.12/site-packages indico-web-1 patch -p1 -i /tmp/change.patch --verbose --fuzz=10

# Restart web service
docker compose restart web

# Revert patch and restart
docker exec -w /opt/indico/.venv/lib/python3.12/site-packages indico-web-1 patch -p1 -R -i /tmp/change.patch --verbose --fuzz=10

docker compose restart web
```

------

**Customize the patch filename, container name, and code directory as needed for your setup.**
 If you run into any issues, check the patch output for hints or reach out for help!