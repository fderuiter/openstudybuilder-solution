#!/usr/bin/env python3

import os
import subprocess
import sys
from pathlib import Path

# Constants
FALLBACK_LICENSE_DIR = Path(__file__).resolve().parent.parent.parent / "doc/sbom/licenses"


# Utility functions
def fatal(message):
    """Log an error message and exit."""
    log(message)
    sys.exit(1)


def log(message):
    """Log a message to stderr."""
    print(message, file=sys.stderr)


def sort_license_files_key(file: str):
    # LICENCE: Should come first.
    # LICENSE.xyz: Should come after LICENCE.
    # COPYING: Should come after LICENSE.xyz.
    # COPYING.xyz: Should come last.

    # Normalize the file name to lowercase for case-insensitive comparison
    file_lower = file.split("/")[-1].lower()

    # Assign priority based on the desired order
    if file_lower == "licence" or file_lower == "license":
        return (0, file_lower)  # Highest priority
    elif "licen" in file_lower:
        return (1, file_lower)  # Second priority
    elif file_lower == "copying":
        return (2, file_lower)  # Third priority
    elif "copying" in file_lower:
        return (3, file_lower)  # Fourth priority
    else:
        return (4, file_lower)  # Lowest priority for other files


def find_python_package_directory():
    """Find the Python package directory."""
    if "VIRTUAL_ENV" in os.environ:
        return Path(os.environ["VIRTUAL_ENV"])
    else:
        result = subprocess.run(
            ["python3", "-m", "site", "--user-site"],
            stdout=subprocess.PIPE,
            text=True,
            check=True,
        )
        return Path(result.stdout.strip())


def validate_directories(search_dirs, fallback_license_dir):
    """Validate the existence and readability of directories."""
    if not search_dirs:
        fatal("Can't find Python package directory")
    if not search_dirs.is_dir():
        fatal(f"Python package directory doesn't exist: {search_dirs}")
    if not fallback_license_dir:
        fatal("Fallback license directory not set")
    if not fallback_license_dir.is_dir():
        fatal(f"Fallback license directory doesn't exist: {fallback_license_dir}")
    if not os.access(fallback_license_dir, os.R_OK):
        fatal(f"Fallback license directory is not readable: {fallback_license_dir}")


def generate_sbom(search_dirs, fallback_license_dir):
    """Generate the SBOM."""

    print("\ufeff", end="")  # UTF-8 BOM
    print("\n## Installed packages\n")

    # Get the list of installed packages
    # Run the pip list command and capture the output
    result = subprocess.run(
        ["pip", "list", "--format", "freeze"],
        stdout=subprocess.PIPE,
        text=True,  # Ensures the output is returned as a string
        check=True,
    )

    # Split the output into a list of lines
    package_list = result.stdout.strip().split("\n")
    # log(package_list)

    # Print the packages table
    print("|            Package             |       Version        |")
    print("|--------------------------------|----------------------|")
    for line in package_list:
        package, version = line.strip().split("==")
        print(f"| {package:<30} | {version:<20} |")

    # Print the license information for each package
    print("\n\n## Third-party package licenses\n")

    # Find all license files
    all_license_files = []
    for root, _, files in os.walk(search_dirs):
        for file in files:
            if (
                "license" in file.lower()
                or "licence" in file.lower()
                or "copying" in file.lower()
            ) and not file.endswith((".py", ".pyc")):
                log(f"Found license file: {os.path.join(root, file)}")
                all_license_files.append(f"{os.path.join(root, file)}\n")

    all_license_files = sorted(all_license_files, key=sort_license_files_key)

    # For each package: Print all package licenses
    for line in package_list:
        # log(f"Searching for license files for package: {line}")
        package, version = line.strip().split("==")
        package_license_files = []
        for license_file in all_license_files:
            if f"/{package.replace('-', '_')}-" in license_file:
                package_license_files.append(license_file.strip())
                # log(f"Found package {package} license file: {license_file.strip()}")

        # log(f"All license files for {package}: {license_files}")
        if not package_license_files:
            # Fallback to the fallback license directory
            package_license_files = list(
                fallback_license_dir.glob(f"{package.lower()}*")
            )
            log(f"Fallback license file for {package}: {package_license_files}")

        if not package_license_files:
            log(f"WARNING: License file not found for package: {package}")
            continue

        print(f"\n---\n\n### License for 3rd party library {package}\n")
        for license_file in package_license_files:
            with open(license_file, "r") as lf:
                print(lf.read())


if __name__ == "__main__":
    try:
        log("Generating SBOM...")
        search_dirs = find_python_package_directory()
        log(f"Python packages directory: {search_dirs}")
        validate_directories(search_dirs, FALLBACK_LICENSE_DIR)
        generate_sbom(search_dirs, FALLBACK_LICENSE_DIR)
    except Exception as e:
        fatal(str(e))
