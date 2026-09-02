"""Command-line entry point for pyanalyzer.

Usage:
    python -m analyzer.cli <path-to-python-file> [<more-files>...]

For each file, prints a report covering complexity, unused variables,
duplicate code, naming violations and overall metrics. Files that
cannot be parsed (invalid Python syntax) are reported as errors and
skipped, rather than crashing the whole run.
"""

import sys

from analyzer.complexity import analyse_complexity
from analyzer.duplicates import find_duplicate_blocks, find_duplicate_functions
from analyzer.metrics import analyse_metrics
from analyzer.naming import analyse_naming
from analyzer.unused_vars import analyse_unused_variables


class AnalysisError(Exception):
    """Raised when a source file cannot be analysed (e.g. bad syntax)."""


def analyse_file(path: str) -> dict:
    """Run every analyser against a single file and return a results dict.

    Raises AnalysisError (wrapping the original SyntaxError) if the file
    is not valid Python, and FileNotFoundError if the path is missing --
    both are deliberate, explicit failure modes rather than silent None
    returns, per the "invalid input scenarios" required by the spec.
    """
    try:
        with open(path, "r", encoding="utf-8") as handle:
            source = handle.read()
    except FileNotFoundError:
        raise
    except UnicodeDecodeError as exc:
        raise AnalysisError(f"{path}: could not decode file as UTF-8") from exc

    try:
        report = {
            "path": path,
            "complexity": analyse_complexity(source),
            "unused_variables": analyse_unused_variables(source),
            "duplicate_functions": find_duplicate_functions(source),
            "duplicate_blocks": find_duplicate_blocks(source),
            "naming_violations": analyse_naming(source),
            "metrics": analyse_metrics(source),
        }
    except SyntaxError as exc:
        raise AnalysisError(f"{path}: invalid Python syntax at line {exc.lineno}") from exc

    return report


def format_report(report: dict) -> str:
    lines = [f"=== {report['path']} ==="]

    m = report["metrics"]
    lines.append(
        f"Metrics: {m.code_lines} code lines, {m.num_functions} functions, "
        f"{m.num_classes} classes, avg complexity {m.average_complexity}, "
        f"max complexity {m.max_complexity}"
    )

    if report["complexity"]:
        lines.append("Complexity:")
        for fc in report["complexity"]:
            flag = "  [HIGH]" if fc.complexity > 10 else ""
            lines.append(f"  {fc.name} (line {fc.lineno}): {fc.complexity}{flag}")

    if report["unused_variables"]:
        lines.append("Unused variables:")
        for uv in report["unused_variables"]:
            lines.append(f"  {uv.function}.{uv.name} (line {uv.lineno})")

    if report["duplicate_functions"]:
        lines.append("Duplicate functions:")
        for dup in report["duplicate_functions"]:
            lines.append(f"  {', '.join(dup.names)}")

    if report["duplicate_blocks"]:
        lines.append("Duplicate code blocks:")
        for dup in report["duplicate_blocks"]:
            ranges = ", ".join(f"L{s}-{e}" for s, e in dup.line_ranges)
            lines.append(f"  {ranges}")

    if report["naming_violations"]:
        lines.append("Naming violations:")
        for nv in report["naming_violations"]:
            lines.append(f"  {nv.kind} '{nv.name}' (line {nv.lineno}) -> expected {nv.expected}")

    return "\n".join(lines)


def main(argv: list[str]) -> int:
    if not argv:
        print("Usage: python -m analyzer.cli <file.py> [<file.py> ...]", file=sys.stderr)
        return 2

    exit_code = 0
    for path in argv:
        try:
            report = analyse_file(path)
        except FileNotFoundError:
            print(f"Error: file not found: {path}", file=sys.stderr)
            exit_code = 1
            continue
        except AnalysisError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            exit_code = 1
            continue

        print(format_report(report))
        print()

    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
