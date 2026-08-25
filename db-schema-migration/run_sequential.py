import os
import sys
import re
import subprocess

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
        
    # 3. Execute migrations sequentially
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
                check=True
            )
            print(f"[SCHEMA MIGRATION] Successfully executed migrations.{module_name}")
        except subprocess.CalledProcessError as e:
            print(f"\n[ERROR] Migration '{module_name}' failed with exit code {e.returncode}.", file=sys.stderr)
            sys.exit(1)
            
    # 4. Execute data corrections sequentially
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
                check=True
            )
            print(f"[DATA CORRECTION] Successfully executed data_corrections.{module_name}")
        except subprocess.CalledProcessError as e:
            print(f"\n[ERROR] Data correction '{module_name}' failed with exit code {e.returncode}.", file=sys.stderr)
            sys.exit(1)
            
    # 5. Execute single-pass deferred schema reconciliation
    print("\n==========================================")
    print(">>> Executing deferred single-pass schema reconciliation...")
    print("==========================================")
    try:
        from migrations.common import migrate_indexes_and_constraints
        from migrations.utils.utils import get_db_connection, get_logger
        logger = get_logger("SchemaReconciliation")
        db_conn = get_db_connection()
        migrate_indexes_and_constraints(db_conn, logger)
        print("[SCHEMA RECONCILIATION] Successfully reconciled schema indexes and constraints")
    except Exception as e:
        print(f"\n[ERROR] Schema reconciliation failed: {e}", file=sys.stderr)
        sys.exit(1)

    print("\n==========================================")
    print("All sequential migrations, data corrections, and schema reconciliation executed successfully!")
    print("==========================================")

if __name__ == "__main__":
    main()
