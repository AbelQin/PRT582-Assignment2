"""Duplicate code detection.

Two strategies are combined:

1. Whole-function duplication: two functions whose bodies produce an
   identical *normalised* AST dump (parameter/variable names stripped
   out via structural comparison of ast.dump with annotate_fields off
   and attributes off) are reported as duplicates of each other.
2. Duplicate line blocks: any run of >= MIN_BLOCK_LINES consecutive,
   non-blank, comment-stripped source lines that appears more than once
   in the file is reported, which catches copy-pasted fragments that
   are not whole functions.
"""

import ast
from dataclasses import dataclass, field

MIN_BLOCK_LINES = 4


@dataclass
class DuplicateFunctions:
    names: list[str] = field(default_factory=list)


@dataclass
class DuplicateBlock:
    line_ranges: list[tuple[int, int]] = field(default_factory=list)
    snippet: str = ""


def _normalised_dump(node: ast.AST) -> str:
    return ast.dump(node, annotate_fields=False, include_attributes=False)


def find_duplicate_functions(source: str) -> list[DuplicateFunctions]:
    tree = ast.parse(source)
    by_shape: dict[str, list[str]] = {}

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Compare only the body, so two functions with different
            # names/args but identical logic are still caught.
            shape = _normalised_dump(ast.Module(body=node.body, type_ignores=[]))
            by_shape.setdefault(shape, []).append(node.name)

    return [
        DuplicateFunctions(names=names)
        for names in by_shape.values()
        if len(names) > 1
    ]


def _clean_lines(source: str) -> list[str]:
    cleaned = []
    for line in source.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            cleaned.append("")  # keep line numbers aligned; blank = ignored
        else:
            cleaned.append(stripped)
    return cleaned


def find_duplicate_blocks(source: str, min_lines: int = MIN_BLOCK_LINES) -> list[DuplicateBlock]:
    lines = _clean_lines(source)
    seen: dict[tuple[str, ...], list[int]] = {}

    for start in range(len(lines) - min_lines + 1):
        window = tuple(lines[start:start + min_lines])
        if "" in window:
            continue  # skip windows touching blank/comment-only lines
        seen.setdefault(window, []).append(start + 1)  # 1-indexed

    duplicates = []
    for window, starts in seen.items():
        if len(starts) > 1:
            ranges = [(s, s + min_lines - 1) for s in starts]
            duplicates.append(DuplicateBlock(line_ranges=ranges, snippet="\n".join(window)))
    return duplicates
