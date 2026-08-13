#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import tempfile
import datetime

def main():
    print("==================================================")
    print("Starting Targeted Native API Security Gate Scan")
    print("==================================================")

    # 1. Locate and load vulnerability exemptions from structured JSON ledger
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # The clinical-mdr-api root is 2 levels up from pipelines/scripts/
    api_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    exemptions_path = os.path.join(api_root, "vulnerability_exemptions.json")

    print(f"Loading vulnerability exemptions ledger from: {exemptions_path}")

    if not os.path.exists(exemptions_path):
        print(f"Error: Vulnerability exemptions JSON ledger not found at {exemptions_path}")
        sys.exit(1)

    try:
        with open(exemptions_path, "r") as f:
            exemptions = json.load(f)
    except Exception as e:
        print(f"Error parsing vulnerability exemptions JSON: {e}")
        sys.exit(1)

    if not isinstance(exemptions, list):
        print("Error: Vulnerability exemptions ledger must be a JSON array (list).")
        sys.exit(1)

    # 2. Validate every active exemption contains mandatory metadata fields
    # and has not expired (expiration date in the past)
    valid_exemptions = []
    errors = []
    today = datetime.date.today()

    for idx, entry in enumerate(exemptions):
        if not isinstance(entry, dict):
            errors.append(f"Entry at index {idx} is not a JSON object.")
            continue

        vuln_id = entry.get("vulnerability_id")
        justification = entry.get("justification")
        expiration_date_str = entry.get("expiration_date")

        # Check mandatory metadata fields
        if not vuln_id or not isinstance(vuln_id, str) or not vuln_id.strip():
            errors.append(f"Entry at index {idx} is missing mandatory field 'vulnerability_id' or it is empty.")
            continue
        
        vuln_id = vuln_id.strip()

        if not justification or not isinstance(justification, str) or not justification.strip():
            errors.append(f"Entry for '{vuln_id}' is missing mandatory field 'justification' or it is empty.")
            continue

        if not expiration_date_str or not isinstance(expiration_date_str, str) or not expiration_date_str.strip():
            errors.append(f"Entry for '{vuln_id}' is missing mandatory field 'expiration_date' or it is empty.")
            continue

        expiration_date_str = expiration_date_str.strip()

        # Validate date format and expiration logic
        try:
            expiration_date = datetime.datetime.strptime(expiration_date_str, "%Y-%m-%d").date()
        except ValueError:
            errors.append(f"Entry for '{vuln_id}' has an invalid 'expiration_date' format: '{expiration_date_str}'. Expected format is YYYY-MM-DD.")
            continue

        if expiration_date < today:
            errors.append(f"Exemption for '{vuln_id}' HAS EXPIRED on {expiration_date_str}! (Justification: {justification})")
            continue

        valid_exemptions.append(vuln_id)

    if errors:
        print("\n--- SECURITY GATE VALIDATION FAILED ---")
        for err in errors:
            print(f"- {err}")
        print("---------------------------------------")
        print("Please correct the validation errors or update/renew the exemptions in vulnerability_exemptions.json.")
        sys.exit(1)

    print(f"Successfully validated {len(valid_exemptions)} active vulnerability exemptions.")

    # 3. Generate requirements using pipenv (production-only dependencies)
    print("Generating production requirements from Pipfile.lock...")
    try:
        # Run pipenv requirements in the clinical-mdr-api directory
        requirements_data = subprocess.check_output(
            ["pipenv", "requirements"],
            cwd=api_root,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print("Error: Failed to generate requirements using pipenv.")
        print(e.output if hasattr(e, 'output') else "")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: pipenv executable not found on the system path.")
        sys.exit(1)

    # 4. Write requirements to a temporary file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp_file:
        tmp_file.write(requirements_data)
        tmp_path = tmp_file.name

    print(f"Temporary requirements file created at: {tmp_path}")

    # 5. Execute pip-audit with standard local security tools
    cmd = ["pip-audit", "-r", tmp_path]
    for vuln in valid_exemptions:
        cmd.extend(["--ignore-vuln", vuln])

    print(f"Executing security scan command: {' '.join(cmd)}")
    print("--------------------------------------------------")

    try:
        # Run pip-audit, sending output directly to stdout/stderr
        result = subprocess.run(cmd, stdout=sys.stdout, stderr=sys.stderr)
        
        print("--------------------------------------------------")
        if result.returncode == 0:
            print("SUCCESS: Dependency security audit passed. No unapproved vulnerabilities found.")
            sys.exit(0)
        else:
            print(f"FAILURE: Dependency security audit failed with exit code {result.returncode}.")
            print("Please see the vulnerability table above for specific package names and CVE identifiers.")
            sys.exit(result.returncode)
    except FileNotFoundError:
        print("Error: pip-audit executable not found on the system path.")
        sys.exit(1)
    finally:
        # Cleanup temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

if __name__ == "__main__":
    main()
