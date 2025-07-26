## 🛠️ Applying and Rolling Back Patches in PrestaShop Docker Containers

This guide explains how to apply and roll back code patches inside a running PrestaShop Docker container (e.g., `prestashop-app-1`). These instructions are useful for hotfixes, feature experiments, or bug injections during testing.

### 1. Copy the Patch File into the Container

Suppose your patch file is located at `./bugs/supplier-delete-1.patch` on your host machine. To copy it to your container’s `/tmp/` directory, use:

```bash
docker cp ./bugs/supplier-delete-1.patch prestashop-app-1:/tmp/
```

### 2. Apply the Patch Inside the Container

Run the following command to enter the PrestaShop codebase directory (usually `/var/www/html`) and apply the patch:

```bash
docker exec -w /var/www/html prestashop-app-1 patch -p1 -i /tmp/supplier-delete-1.patch --fuzz=10 --verbose
```

- `-p1`: Strips the first component of the patch paths (adjust if your patch is generated differently).
- `--fuzz=10`: Allows some flexibility for minor code shifts.
- `--verbose`: Prints detailed output for debugging.

### 3. Roll Back (Revert) a Previously Applied Patch

If you need to **undo** a patch (revert changes), use the same command with the `-R` flag:

```bash
docker exec -w /var/www/html prestashop-app-1 patch -p1 -R -i /tmp/supplier-delete-1.patch --fuzz=10 --verbose
```

> **Note:** The patch file content must be exactly the same as the one you applied, otherwise the revert may fail.

### 4. Troubleshooting Tips

- **“No such file or directory”**: Double-check the patch file’s path inside the container.
- **“Reversed (or previously applied) patch detected!”**: The patch has already been applied or reverted. Follow the prompts or use the `-R` flag as needed.
- **Patch fails or partial application**: Make sure you’re in the correct working directory, and that your PrestaShop source matches the patch’s context.

------

### Example Command Summary

```bash
# Copy patch into container
docker cp ./bugs/your-patch.patch prestashop-app-1:/tmp/

# Apply patch inside container
docker exec -w /var/www/html prestashop-app-1 patch -p1 -i /tmp/your-patch.patch --fuzz=10 --verbose

# Revert patch inside container
docker exec -w /var/www/html prestashop-app-1 patch -p1 -R -i /tmp/your-patch.patch --fuzz=10 --verbose
```

------

**Customize `your-patch.patch`, the container name, and the code directory as needed for your setup.**
 If you run into any issues, check the patch output for hints or reach out for help!