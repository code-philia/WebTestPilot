import difflib
import os
import subprocess
import sys
from pathlib import Path

# Configuration for all applications
APPS_CONFIG = {
    "bookstack": {
        "db_type": "mysql",
        "container": "bookstack-db-1",
        "user": "admin",
        "password": "admin",
        "database": "bookstack",
        "port": 8081,
    },
    "invoiceninja": {
        "db_type": "mysql",
        "container": "invoiceninja-mysql-1",
        "user": "ninja",
        "password": "ninja",
        "database": "ninja",
        "port": 8082,
    },
    "prestashop": {
        "db_type": "mysql",
        "container": "prestashop-db-1",
        "user": "root",
        "password": "root",
        "database": "prestashop",
        "port": 8083,
    },
    "indico": {
        "db_type": "postgres",
        "container": "indico-postgres-1",
        "user": "indico",
        "password": "indicopass",
        "database": "indico",
        "port": 8080,
    },
}


def run_command(cmd: str, timeout: int = 120):
    """Run a command"""
    subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)


def dump_database_mysql(config, output_file: str):
    """Dump MySQL database"""
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    cmd = f"""docker exec {config["container"]} mysqldump \
        --default-character-set=utf8 \
        --user={config["user"]} \
        --password={config["password"]} \
        --extended-insert=FALSE \
        --single-transaction=TRUE \
        --column-statistics=0 \
        --skip-triggers \
        "{config["database"]}" > {output_file}"""

    run_command(cmd)


def dump_database_postgres(config, output_file: str):
    """Dump PostgreSQL database"""
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    cmd = f"""docker exec {config["container"]} pg_dump \
        -U {config["user"]} \
        -d {config["database"]} \
        --inserts \
        --no-owner \
        --no-privileges \
        --exclude-table-data='alembic_version' > {output_file}"""

    run_command(cmd)


def dump_database(app_name: str, output_file: str):
    """Dump database for specified application"""
    config = APPS_CONFIG[app_name]

    if config["db_type"] == "mysql":
        dump_database_mysql(config, output_file)
    elif config["db_type"] == "postgres":
        dump_database_postgres(config, output_file)


def run_seed_test(app_name: str):
    """Run seed test for specified application"""
    base_dir = Path(__file__).parent.parent / "testcases"
    cmd = f"cd {base_dir} && pytest ./{app_name}/seed.py::test_seed -v --tb=short -s --no-seed"

    print(f"Running seed test for {app_name}...")
    run_command(cmd, timeout=360)


def generate_seed_sql(
    initial_file: str,
    populated_file: str,
    seed_output_file: str,
    db_type: str = "mysql",
) -> int:
    """Compare dumps and generate seed.sql using difflib"""
    with open(initial_file, "r") as f:
        initial_lines = f.readlines()

    with open(populated_file, "r") as f:
        populated_lines = f.readlines()

    # Use difflib to find additions only
    diff_lines = list(
        difflib.unified_diff(
            initial_lines,
            populated_lines,
            fromfile="initial.sql",
            tofile="populated.sql",
            lineterm="",
        )
    )

    # with open("diff.txt", "w") as f:
    #     for line in diff_lines:
    #         f.write(line)

    # Extract only addition lines (start with '+') but not '+++'
    # -INSERT INTO `company_user`
    # +INSERT INTO `company_user`
    # +INSERT INTO `company_user` <- This is added
    # +INSERT INTO `company_user` <- This is added
    addition_lines = []
    count = 0
    for line in diff_lines:
        if line.startswith("+") and not line.startswith("+++"):
            count += 1
        elif line.startswith("-") and not line.startswith("---"):
            count -= 1

        if count > 0:
            addition_lines.append(line[1:] + "\n")  # Remove leading '+'
            count = 0  # to avoid accumulating

    with open(seed_output_file, "w") as f:
        if db_type == "mysql":
            f.write("""
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO';
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
""")
        elif db_type == "postgres":
            pass

        for line in addition_lines:
            f.write(line)

    os.remove(initial_file)
    os.remove(populated_file)

    return len(addition_lines)


def dump_app(app_name: str):
    """Dump single application"""
    print(f"\n{'=' * 50}")
    print(f"Processing {app_name.upper()}")

    # Use webapps directory for output files
    base_dir = Path(__file__).parent / app_name

    initial_file = base_dir / "initial.sql"
    populated_file = base_dir / "populated.sql"
    seed_output_file = base_dir / "seed.sql"

    print("1. Starting application...")
    start_app_script = Path(__file__).parent / "start_app.sh"
    cmd = f"bash {start_app_script} {app_name} --no-seed"
    run_command(cmd, timeout=300)

    print("2. Dumping initial database...")
    dump_database(app_name, str(initial_file))

    print("3. Running seed test...")
    run_seed_test(app_name)

    print("4. Dumping populated database...")
    dump_database(app_name, str(populated_file))

    print("5. Generating seed.sql...")
    db_type = APPS_CONFIG[app_name]["db_type"]
    insert_count = generate_seed_sql(
        str(initial_file),
        str(populated_file),
        str(seed_output_file),
        db_type=str(db_type),
    )

    print(f"Done! Generated {insert_count} line additions")
    print(f"Files: {initial_file.name}, {populated_file.name}, {seed_output_file.name}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python dump_database.py <app_name>")
        print("Available apps: " + ", ".join(APPS_CONFIG.keys()))
        return

    app_name = sys.argv[1]
    if app_name not in APPS_CONFIG:
        print(f"Unknown application: {app_name}")
        print("Available apps: " + ", ".join(APPS_CONFIG.keys()))
        return

    print("Generalized Database Dump Script")
    dump_app(app_name)


if __name__ == "__main__":
    main()
