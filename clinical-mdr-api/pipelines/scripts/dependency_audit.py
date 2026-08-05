#!/usr/bin/env python3
import os
import sys
import re
import subprocess
import tempfile

try:
    import tomllib
except ImportError:
    # Fallback for Python versions < 3.11 if any
    import pipenv.patched.pip._vendor.tomli as tomllib

def main():
    print("==================================================")
    print("Starting Targeted Native API Security Gate Scan")
    print("==================================================")

    # 1. Locate Pipfile
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # The clinical-mdr-api root is 2 levels up from pipelines/scripts/
    api_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    pipfile_path = os.path.join(api_root, "Pipfile")

    if not os.path.exists(pipfile_path):
        print(f"Error: Pipfile not found at {pipfile_path}")
        sys.exit(1)

    print(f"Reading Pipfile from: {pipfile_path}")

    # 2. Parse Pipfile to extract ignored vulnerabilities
    try:
        with open(pipfile_path, "rb") as f:
            config = tomllib.load(f)
    except Exception as e:
        print(f"Error parsing Pipfile: {e}")
        sys.exit(1)

    audit_script = config.get("scripts", {}).get("audit", "")
    print(f"Found pre-configured audit script: {audit_script}")

    # Extract vulnerability exemptions from the Pipfile audit command
    ignore_vulns = re.findall(r'--ignore-vuln[=\s]+([A-Za-z0-9-]+)', audit_script)
    print(f"Automatically extracted vulnerability exemptions: {ignore_vulns}")

    # 3. Generate requirements using pipenv
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

    # 5. Execute pip-audit
    # Construct the pip-audit command with standard local security tools
    cmd = ["pip-audit", "-r", tmp_path]
    for vuln in ignore_vulns:
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
