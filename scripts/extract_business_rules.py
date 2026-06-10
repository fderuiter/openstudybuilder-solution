import ast
import os
import sys

def sorted_walk(directory):
    for root, dirs, files in os.walk(directory):
        dirs.sort()
        files.sort()
        yield root, dirs, files

def extract_message(node):
    if isinstance(node, ast.Constant):
        return str(node.value)
    elif isinstance(node, ast.JoinedStr):
        parts = []
        for val in node.values:
            if isinstance(val, ast.Constant):
                parts.append(str(val.value))
            elif isinstance(val, ast.FormattedValue):
                parts.append(f"{{{ast.unparse(val.value)}}}")
        return "".join(parts)
    elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'format':
        return ast.unparse(node)
    return ast.unparse(node)

def process_file(filepath):
    with open(filepath, 'r') as f:
        source = f.read()

    try:
        tree = ast.parse(source, filename=filepath)
    except (SyntaxError, ValueError, TypeError) as e:
        print(f"Failed to parse {filepath}: {type(e).__name__}: {e}", file=sys.stderr)
        return []

    rules = []

    # Track variable assignments to resolve msg argument references
    variable_assignments = {}

    class Visitor(ast.NodeVisitor):
        def visit_Assign(self, node):
            # Track simple variable assignments for error messages
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                var_name = node.targets[0].id
                if 'error' in var_name.lower() or 'msg' in var_name.lower() or 'message' in var_name.lower():
                    variable_assignments[var_name] = node.value
            self.generic_visit(node)

        def visit_Call(self, node):
            is_validation = False
            func = node.func
            if isinstance(func, ast.Attribute):
                if isinstance(func.value, ast.Name):
                    if func.value.id in ('ValidationException', 'BusinessLogicException', 'AlreadyExistsException', 'exceptions') and func.attr in ('raise_if', 'raise_if_not'):
                        is_validation = True
                elif isinstance(func.value, ast.Attribute):
                    if func.value.attr in ('ValidationException', 'BusinessLogicException', 'AlreadyExistsException') and func.attr in ('raise_if', 'raise_if_not'):
                        is_validation = True
            elif isinstance(func, ast.Name) and func.id in ('raise_if', 'raise_if_not'):
                is_validation = True

            if is_validation:
                msg = None
                for keyword in node.keywords:
                    if keyword.arg == 'msg':
                        # Check if it's a variable reference that we've tracked
                        if isinstance(keyword.value, ast.Name) and keyword.value.id in variable_assignments:
                            msg = extract_message(variable_assignments[keyword.value.id])
                        else:
                            msg = extract_message(keyword.value)

                rules.append({
                    'file': filepath,
                    'line': node.lineno,
                    'msg': msg
                })

            self.generic_visit(node)

        def visit_Raise(self, node):
            if isinstance(node.exc, ast.Call):
                func = node.exc.func
                is_validation = False
                if isinstance(func, ast.Name):
                    if func.id in ('ValidationException', 'BusinessLogicException', 'AlreadyExistsException'):
                        is_validation = True
                elif isinstance(func, ast.Attribute):
                    if func.attr in ('ValidationException', 'BusinessLogicException', 'AlreadyExistsException'):
                        is_validation = True

                if is_validation:
                    msg = None
                    for keyword in node.exc.keywords:
                        if keyword.arg == 'msg':
                            msg = extract_message(keyword.value)

                    if not msg and node.exc.args:
                        if isinstance(node.exc.args[0], ast.Constant) and isinstance(node.exc.args[0].value, str):
                            value = node.exc.args[0].value
                            # Require minimum length and space to avoid capturing short identifiers
                            if len(value) >= 5 and " " in value:
                                msg = extract_message(node.exc.args[0])

                    rules.append({
                        'file': filepath,
                        'line': node.lineno,
                        'msg': msg
                    })

            self.generic_visit(node)

    Visitor().visit(tree)
    return rules

def find_test_file(domain_filepath):
    """
    Locate the corresponding test file for a given domain file using a multi-strategy heuristic.

    The function attempts to find test files in the following order:
    1. Primary path: Constructs test path by replacing 'domains' with 'tests/unit/domain' and
       prefixing the filename with 'test_'. Returns immediately if this path exists.
    2. Pluralization fallback: If the primary path contains 'aggregates', tries replacing it with
       'aggregate' to handle inconsistent directory naming conventions.
    3. Fallback search: If neither above succeeds, performs a recursive search under the 'tests'
       directory for any file matching 'test_{filename}', then sorts candidates using
       candidate_sort_key to prefer:
       - Paths containing '/tests/unit/domain/' (highest priority)
       - Paths containing '/tests/unit/' (second priority)
       - Paths NOT containing '/tests/integration/' (deprioritize integration tests)
       - Alphabetical order as final tiebreaker

    Args:
        domain_filepath: Absolute or relative path to a domain source file

    Returns:
        str: Absolute path to the corresponding test file, or None if no test file is found
    """
    parts = domain_filepath.split(os.sep)
    if 'domains' in parts:
        idx = parts.index('domains')
        test_parts = parts[:idx] + ['tests', 'unit', 'domain'] + parts[idx+1:]
        test_parts[-1] = 'test_' + test_parts[-1]

        test_path = os.sep.join(test_parts)
        if os.path.exists(test_path):
            return test_path

        # Compatibility fallback: handle inconsistent test directory naming where domain code
        # uses 'aggregates' but test directories may use 'aggregate' (singular form)
        if 'aggregates' in test_path:
            test_path_alt = test_path.replace('aggregates', 'aggregate')
            if os.path.exists(test_path_alt):
                return test_path_alt

        filename = parts[-1]
        search_dir = os.sep.join(parts[:idx] + ['tests'])
        candidates = []
        for root, _, files in sorted_walk(search_dir):
            if f"test_{filename}" in files:
                candidates.append(os.path.join(root, f"test_{filename}"))
        if candidates:
            def candidate_sort_key(path):
                normalized_path = path.replace(os.sep, '/')
                return (
                    '/tests/unit/domain/' not in normalized_path,
                    '/tests/unit/' not in normalized_path,
                    '/tests/integration/' in normalized_path,
                    normalized_path,
                )

            return min(candidates, key=candidate_sort_key)
    return None

def main():
    directory = 'clinical-mdr-api/clinical_mdr_api/domains'
    all_rules = []
    missing_descriptions = 0

    # Open missing_descriptions.txt for writing (truncate if exists)
    missing_desc_file = open('missing_descriptions.txt', 'w')

    for root, _, files in sorted_walk(directory):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                filepath = os.path.join(root, file)
                rules = process_file(filepath)
                for r in rules:
                    rel_path = os.path.relpath(filepath, directory)
                    parts = rel_path.split(os.sep)
                    area = parts[0] if len(parts) > 1 else "General"
                    area = area.replace('_', ' ').title()

                    r['area'] = area
                    r['test_file'] = find_test_file(filepath)

                    if not r['msg']:
                        print(f"WARNING: Missing human-readable description for validation rule at {r['file']}:{r['line']}", file=sys.stderr)
                        missing_desc_file.write(f"{r['file']}:{r['line']}\n")
                        missing_descriptions += 1

                all_rules.extend(rules)

    missing_desc_file.close()

    if missing_descriptions > 0:
        print(f"\nFound {missing_descriptions} validation rules lacking a human-readable description. Please provide the necessary context (e.g. using the 'msg' argument).", file=sys.stderr)

    md_content = "<!--\n"
    md_content += "WARNING: DO NOT EDIT THIS FILE MANUALLY.\n"
    md_content += "This file is automatically generated by the Code-to-Doc Extraction Pipeline.\n"
    md_content += "Any manual changes will be overwritten by the next pipeline execution.\n"
    md_content += "To update a validation rule, please modify the corresponding domain logic and accompanying description in the source code.\n"
    md_content += "-->\n\n"

    md_content += "# Business Rule Catalog\n\n"
    md_content += "This catalog contains domain validation rules extracted directly from the application's source code.\n\n"

    areas = {}
    for r in all_rules:
        areas.setdefault(r['area'], []).append(r)

    for area in sorted(areas.keys()):
        md_content += f"## {area}\n\n"
        for r in sorted(areas[area], key=lambda rule: (rule['file'], rule['line'])):
            msg = r['msg']
            if not msg:
                msg = "**⚠️ MISSING HUMAN-READABLE DESCRIPTION**"

            # format msg block properly if multiline
            msg_str = str(msg).strip().replace('\n', ' ')
            md_content += f"- **Rule:** {msg_str}\n"
            md_content += f"  - *Source:* `{r['file']}:{r['line']}`\n"
            if r['test_file']:
                md_content += f"  - *Traceability:* Verified by tests in `{r['test_file']}`\n"
            md_content += "\n"

    output_dir = 'documentation-portal/docs'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'business_rule_catalog.md')

    with open(output_path, 'w') as f:
        f.write(md_content)

    print(f"Generated {output_path}")

if __name__ == '__main__':
    main()
