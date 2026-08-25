import os
import sys
import re
import subprocess

from migrations.utils.alias_manager import DatabaseAliasManager

def get_sort_key(filename):
    # Extract all digit sequences from the filename to form a sorting tuple.
    # For example:
    #   "migration_001.py" -> [1]
    #   "migration_006_2.py" -> [6, 2]
    #   "migration_010.py" -> [10]
    parts = re.findall(r'\d+', filename)
    return [int(p) for p in parts]

def main():
    print("Starting sequential database migrations and corrections execution...")
    
    # Get the directory of this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Discover migration scripts
    migrations_dir = os.path.join(base_dir, "migrations")
    migration_files = []
    for f in os.listdir(migrations_dir):
        if f.startswith("migration_") and f.endswith(".py"):
            migration_files.append(f)
            
    # Sort migrations sequentially (e.g., migration_001, ..., migration_006, migration_006_2, ...)
    migration_files.sort(key=get_sort_key)
    
    print(f"\nDiscovered {len(migration_files)} schema migrations to run:")
    for f in migration_files:
        print(f"  - {f}")
        
    # 2. Discover correction scripts
    corrections_dir = os.path.join(base_dir, "data_corrections")
    correction_files = []
    for f in os.listdir(corrections_dir):
        # We only want numbered corrections (e.g. correction_007.py, correction_010_1.py)
        if f.startswith("correction_") and f.endswith(".py") and re.search(r'\d+', f):
            correction_files.append(f)
            
    # Sort data corrections sequentially
    correction_files.sort(key=get_sort_key)
    
    print(f"\nDiscovered {len(correction_files)} data corrections to run:")
    for f in correction_files:
        print(f"  - {f}")

    # 3. Database snapshotting and logical alias configuration
    alias_manager = DatabaseAliasManager()
    try:
        snapshot_db, staging_db = alias_manager.prepare_snapshot_and_staging()
    except Exception as e:
        print(f"\n[ERROR] Failed to prepare pre-migration snapshot and staging database: {e}", file=sys.stderr)
        sys.exit(1)

    env = os.environ.copy()
    env["DATABASE_NAME"] = staging_db
        
    # 4. Execute migrations sequentially
    print("\n==========================================")
    print(">>> Executing schema migrations sequentially...")
    print("==========================================")
    for f in migration_files:
        module_name = f[:-3] # strip .py suffix
        print(f"\n[SCHEMA MIGRATION] Running migrations.{module_name}...")
        try:
            subprocess.run(
                ["python", "-m", f"migrations.{module_name}"],
                cwd=base_dir,
                check=True,
                env=env
            )
            print(f"[SCHEMA MIGRATION] Successfully executed migrations.{module_name}")
        except subprocess.CalledProcessError as e:
            print(f"\n[ERROR] Migration '{module_name}' failed with exit code {e.returncode}. Initiating automated alias rollback...", file=sys.stderr)
            try:
                alias_manager.rollback()
            except Exception as rollback_err:
                print(f"[ERROR] Alias rollback failed: {rollback_err}", file=sys.stderr)
            sys.exit(1)
            
    # 5. Execute data corrections sequentially
    print("\n==========================================")
    print(">>> Executing data corrections sequentially...")
    print("==========================================")
    for f in correction_files:
        module_name = f[:-3] # strip .py suffix
        print(f"\n[DATA CORRECTION] Running data_corrections.{module_name}...")
        try:
            subprocess.run(
                ["python", "-m", f"data_corrections.{module_name}"],
                cwd=base_dir,
                check=True,
                env=env
            )
            print(f"[DATA CORRECTION] Successfully executed data_corrections.{module_name}")
        except subprocess.CalledProcessError as e:
            print(f"\n[ERROR] Data correction '{module_name}' failed with exit code {e.returncode}. Initiating automated alias rollback...", file=sys.stderr)
            try:
                alias_manager.rollback()
            except Exception as rollback_err:
                print(f"[ERROR] Alias rollback failed: {rollback_err}", file=sys.stderr)
            sys.exit(1)

    # 6. Promote staging database to active alias upon successful completion
    try:
        alias_manager.promote_staging()
    except Exception as promote_err:
        print(f"\n[ERROR] Failed to promote staging database to active alias: {promote_err}. Initiating automated alias rollback...", file=sys.stderr)
        try:
            alias_manager.rollback()
        except Exception as rollback_err:
            print(f"[ERROR] Alias rollback failed: {rollback_err}", file=sys.stderr)
        sys.exit(1)

    print("\n==========================================")
    print("All sequential migrations and data corrections executed successfully!")
    print("==========================================")

if __name__ == "__main__":
    main()
