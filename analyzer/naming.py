"""PEP 8 naming convention checks.

Checked conventions:
    - function and method names:      snake_case
    - parameter and local variables:  snake_case
    - class names:                    PascalCase (CapWords)

Dunder methods (__init__, __str__, ...), and names starting with an
underscore, are treated as valid regardless of case: a leading
underscore already carries its own convention (privacy) and is not
the target of this check.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass

_SNAKE_CASE = re.compile(r"^_*[a-z][a-z0-9_]*$")
_PASCAL_CASE = re.compile(r"^[A-Z][a-zA-Z0-9]*$")


@dataclass
class NamingViolation:
    kind: str  # "function" | "variable" | "class"
    name: str
    lineno: int
    expected: str


def _is_dunder(name: str) -> bool:
    return name.startswith("__") and name.endswith("__")


def _is_exempt(name: str) -> bool:
    return name.startswith("_") or _is_dunder(name)


def analyse_naming(source: str) -> list[NamingViolation]:
    tree = ast.parse(source)
    violations: list[NamingViolation] = []
    seen_variables: set[tuple[str, int]] = set()

    class _Walker(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            if not _is_exempt(node.name) and not _SNAKE_CASE.match(node.name):
                violations.append(NamingViolation(
                    "function", node.name, node.lineno, "snake_case"))
            for arg in node.args.args:
                if arg.arg in ("self", "cls") or _is_exempt(arg.arg):
                    continue
                if not _SNAKE_CASE.match(arg.arg):
                    violations.append(NamingViolation(
                        "variable", arg.arg, node.lineno, "snake_case"))
            self.generic_visit(node)

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_ClassDef(self, node):
            if not _PASCAL_CASE.match(node.name):
                violations.append(NamingViolation(
                    "class", node.name, node.lineno, "PascalCase"))
            self.generic_visit(node)

        def visit_Name(self, node):
            # Only flag on assignment (a Store target), and only once
            # per (name, line) so repeated reads don't cause duplicates.
            if isinstance(node.ctx, ast.Store) and not _is_exempt(node.id):
                key = (node.id, node.lineno)
                if not _SNAKE_CASE.match(node.id) and key not in seen_variables:
                    seen_variables.add(key)
                    violations.append(NamingViolation(
                        "variable", node.id, node.lineno, "snake_case"))
            self.generic_visit(node)

    _Walker().visit(tree)
    return sorted(violations, key=lambda v: v.lineno)
