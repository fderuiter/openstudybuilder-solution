#!/usr/bin/env python3
import subprocess
import sys
import os

def get_modified_files():
    modified = []
    # 1. Check uncommitted/unstaged changes
    try:
        status_output = subprocess.check_output(
            ["git", "status", "--porcelain"],
            text=True
        )
        for line in status_output.splitlines():
            if line.strip():
                parts = line.strip().split(maxsplit=1)
                if len(parts) == 2:
                    modified.append(parts[1])
    except Exception as e:
        print(f"Warning: git status failed: {e}")

    # 2. Check changes compared to origin/main (standard target branch)
    try:
        diff_output = subprocess.check_output(
            ["git", "diff", "--name-only", "origin/main"],
            text=True
        )
        modified.extend([line.strip() for line in diff_output.splitlines() if line.strip()])
    except Exception as e:
        print(f"Warning: git diff with origin/main failed: {e}")
        # Fallback: check changes in the last commit
        try:
            diff_output = subprocess.check_output(
                ["git", "diff", "--name-only", "HEAD~1"],
                text=True
            )
            modified.extend([line.strip() for line in diff_output.splitlines() if line.strip()])
        except Exception as e2:
            print(f"Warning: git diff with HEAD~1 failed: {e2}")

    return list(set(modified))

def main():
    print("==================================================")
    print("Starting SBOM and Dependency Drift Check")
    print("==================================================")

    # List of components with their (manifest, sbom) paths relative to repo root
    components = [
        ("clinical-mdr-api", "clinical-mdr-api/Pipfile.lock", "clinical-mdr-api/sbom.md"),
        ("documentation-portal", "documentation-portal/yarn.lock", "documentation-portal/sbom.md"),
        ("system-tests/ui-tests", "system-tests/ui-tests/yarn.lock", "system-tests/ui-tests/sbom.md"),
        ("mdr-standards-import", "mdr-standards-import/Pipfile.lock", "mdr-standards-import/sbom.md"),
        ("neo4j-mdr-db", "neo4j-mdr-db/Pipfile.lock", "neo4j-mdr-db/sbom.md"),
        ("studybuilder", "studybuilder/yarn.lock", "studybuilder/sbom.md"),
        ("db-schema-migration", "db-schema-migration/Pipfile.lock", "db-schema-migration/sbom.md"),
        ("studybuilder-export", "studybuilder-export/Pipfile.lock", "studybuilder-export/sbom.md"),
        ("studybuilder-import", "studybuilder-import/Pipfile.lock", "studybuilder-import/sbom.md"),
    ]

    modified_files = get_modified_files()
    print(f"Modified files detected: {modified_files}")

    drift_detected = False

    for name, manifest, sbom in components:
        # Check if manifest is in the modified files list
        manifest_modified = any(m == manifest or m.endswith("/" + manifest) for m in modified_files)
        sbom_modified = any(s == sbom or s.endswith("/" + sbom) for s in modified_files)

        if manifest_modified:
            print(f"Component '{name}':")
            print(f"  Manifest '{manifest}' is modified in this change.")
            if not sbom_modified:
                print(f"  [DRIFT DETECTED] Dependency change in '{manifest}' committed without regenerating '{sbom}'!")
                drift_detected = True
            else:
                print(f"  [OK] Associated SBOM '{sbom}' is also modified/regenerated.")

    if drift_detected:
        print("\nError: Build failed because active package dependencies drifted from static SBOM documentation.")
        print("Please run the generator script (e.g., 'pipenv run build-sbom' or 'yarn build-sbom') in the modified component directories and commit the updated sbom.md files.")
        sys.exit(1)
    else:
        print("\nSuccess: No SBOM or dependency drift detected.")
        sys.exit(0)

if __name__ == "__main__":
    main()
