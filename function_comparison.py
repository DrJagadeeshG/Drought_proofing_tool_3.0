#!/usr/bin/env python3
"""
Function comparison script for drought proofing tool
Lists all functions from both original and restructured versions
"""

import os
import ast
import glob

def extract_functions_from_file(file_path):
    """Extract function names and their definitions from a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Get function signature
                args = [arg.arg for arg in node.args.args]
                signature = f"{node.name}({', '.join(args)})"

                # Get docstring if available
                docstring = ""
                if (node.body and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)):
                    docstring = node.body[0].value.value.strip()

                functions.append({
                    'name': node.name,
                    'signature': signature,
                    'line': node.lineno,
                    'docstring': docstring
                })

        return functions
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []

def find_python_files(root_dir):
    """Find all Python files in directory and subdirectories"""
    python_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def analyze_codebase(base_dir, label):
    """Analyze all Python files in a codebase"""
    print(f"Analyzing {label} codebase...")

    # Skip certain directories
    skip_dirs = {'__pycache__', '.git', 'venv', 'env', '.pytest_cache'}

    all_functions = {}
    python_files = find_python_files(base_dir)

    for file_path in python_files:
        # Skip files in skip directories
        if any(skip_dir in file_path for skip_dir in skip_dirs):
            continue

        rel_path = os.path.relpath(file_path, base_dir)
        functions = extract_functions_from_file(file_path)

        if functions:
            all_functions[rel_path] = functions

    return all_functions

def write_function_report(output_file):
    """Generate comprehensive function comparison report"""

    # Find original and restructured codebases
    original_dir = None
    restructured_dir = "."

    # Look for original directory
    possible_original_dirs = ["Original", "original", "drought_proofing_tool"]
    for dirname in possible_original_dirs:
        if os.path.exists(dirname) and os.path.isdir(dirname):
            # Check if it contains Python files
            py_files = glob.glob(f"{dirname}/**/*.py", recursive=True)
            if py_files:
                original_dir = dirname
                break

    if not original_dir:
        print("Warning: Could not find original codebase directory")
        return

    # Analyze both codebases
    original_functions = analyze_codebase(original_dir, "Original")
    restructured_functions = analyze_codebase(restructured_dir, "Restructured")

    # Write comprehensive report
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("DROUGHT PROOFING TOOL - FUNCTION COMPARISON REPORT\n")
        f.write("=" * 60 + "\n\n")

        # Summary statistics
        orig_total = sum(len(funcs) for funcs in original_functions.values())
        restr_total = sum(len(funcs) for funcs in restructured_functions.values())

        f.write(f"SUMMARY:\n")
        f.write(f"Original codebase: {len(original_functions)} files, {orig_total} functions\n")
        f.write(f"Restructured codebase: {len(restructured_functions)} files, {restr_total} functions\n\n")

        # Original codebase functions
        f.write("ORIGINAL CODEBASE FUNCTIONS:\n")
        f.write("-" * 40 + "\n")
        for file_path, functions in sorted(original_functions.items()):
            f.write(f"\nFile: {file_path}\n")
            for func in functions:
                f.write(f"  Line {func['line']:3d}: {func['signature']}\n")
                if func['docstring']:
                    # First line of docstring only
                    first_line = func['docstring'].split('\n')[0]
                    f.write(f"            {first_line}\n")

        f.write("\n" + "=" * 60 + "\n")

        # Restructured codebase functions
        f.write("RESTRUCTURED CODEBASE FUNCTIONS:\n")
        f.write("-" * 40 + "\n")
        for file_path, functions in sorted(restructured_functions.items()):
            f.write(f"\nFile: {file_path}\n")
            for func in functions:
                f.write(f"  Line {func['line']:3d}: {func['signature']}\n")
                if func['docstring']:
                    # First line of docstring only
                    first_line = func['docstring'].split('\n')[0]
                    f.write(f"            {first_line}\n")

        f.write("\n" + "=" * 60 + "\n")

        # Function comparison analysis
        f.write("FUNCTION COMPARISON ANALYSIS:\n")
        f.write("-" * 40 + "\n")

        # Get all unique function names
        orig_func_names = set()
        restr_func_names = set()

        for functions in original_functions.values():
            orig_func_names.update(func['name'] for func in functions)

        for functions in restructured_functions.values():
            restr_func_names.update(func['name'] for func in functions)

        # Functions only in original
        only_original = orig_func_names - restr_func_names
        if only_original:
            f.write(f"\nFunctions only in ORIGINAL ({len(only_original)}):\n")
            for func_name in sorted(only_original):
                f.write(f"  - {func_name}\n")

        # Functions only in restructured
        only_restructured = restr_func_names - orig_func_names
        if only_restructured:
            f.write(f"\nFunctions only in RESTRUCTURED ({len(only_restructured)}):\n")
            for func_name in sorted(only_restructured):
                f.write(f"  - {func_name}\n")

        # Common functions
        common_functions = orig_func_names & restr_func_names
        f.write(f"\nCommon functions ({len(common_functions)}):\n")
        for func_name in sorted(list(common_functions)[:20]):  # Limit to first 20
            f.write(f"  - {func_name}\n")
        if len(common_functions) > 20:
            f.write(f"  ... and {len(common_functions) - 20} more\n")

if __name__ == "__main__":
    output_file = "function_comparison_report.txt"
    write_function_report(output_file)
    print(f"Function comparison report written to: {output_file}")