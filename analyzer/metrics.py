"""Aggregate code metrics for a Python source file."""

import ast
from dataclasses import dataclass

from analyzer.complexity import analyse_complexity


@dataclass
class CodeMetrics:
    total_lines: int
    code_lines: int
    blank_lines: int
    comment_lines: int
    num_functions: int
    num_classes: int
    average_complexity: float
    max_complexity: int


def analyse_metrics(source: str) -> CodeMetrics:
    lines = source.splitlines()
    total_lines = len(lines)
    blank_lines = sum(1 for line in lines if not line.strip())
    comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
    code_lines = total_lines - blank_lines - comment_lines

    tree = ast.parse(source)
    num_functions = sum(
        1 for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    )
    num_classes = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))

    complexities = [fc.complexity for fc in analyse_complexity(source)]
    average_complexity = (sum(complexities) / len(complexities)) if complexities else 0.0
    max_complexity = max(complexities) if complexities else 0

    return CodeMetrics(
        total_lines=total_lines,
        code_lines=code_lines,
        blank_lines=blank_lines,
        comment_lines=comment_lines,
        num_functions=num_functions,
        num_classes=num_classes,
        average_complexity=round(average_complexity, 2),
        max_complexity=max_complexity,
    )
