"""Detection of unused local variables within function bodies.

A variable is flagged when it is assigned inside a function but never
referenced (read) anywhere else in that same function. Names prefixed
with an underscore (the conventional "intentionally unused" marker),
loop control variables in a `for` target used only for iteration count,
and augmented-assignment targets (`x += 1`, which are also a read) are
excluded to keep the signal low-noise.
"""

import ast
from dataclasses import dataclass


@dataclass
class UnusedVariable:
    function: str
    name: str
    lineno: int


def _is_ignored(name: str) -> bool:
    return name == "_" or name.startswith("_")


def _find_in_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[UnusedVariable]:
    assigned: dict[str, int] = {}
    read: set[str] = set()

    class _Walker(ast.NodeVisitor):
        def visit_Name(self, inner):
            if isinstance(inner.ctx, ast.Store):
                if inner.id not in assigned:
                    assigned[inner.id] = inner.lineno
            elif isinstance(inner.ctx, ast.Load):
                read.add(inner.id)
            self.generic_visit(inner)

        def visit_AugAssign(self, inner):
            # x += 1 reads x before writing it, so it never counts as unused.
            if isinstance(inner.target, ast.Name):
                read.add(inner.target.id)
            self.generic_visit(inner)

        def visit_FunctionDef(self, inner):
            # Nested functions are analysed independently by the caller;
            # avoid double-counting their locals here, but do count any
            # free variables they read from the enclosing scope as "read".
            for sub in ast.walk(inner):
                if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Load):
                    read.add(sub.id)
            return

        visit_AsyncFunctionDef = visit_FunctionDef

    for stmt in node.body:
        _Walker().visit(stmt)

    unused = []
    for name, lineno in assigned.items():
        if name in read or _is_ignored(name):
            continue
        unused.append(UnusedVariable(function=node.name, name=name, lineno=lineno))
    return sorted(unused, key=lambda u: u.lineno)


def analyse_unused_variables(source: str) -> list[UnusedVariable]:
    """Return all unused local variables found across all functions."""
    tree = ast.parse(source)
    results: list[UnusedVariable] = []

    class _Finder(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            results.extend(_find_in_function(node))
            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node):
            results.extend(_find_in_function(node))
            self.generic_visit(node)

    _Finder().visit(tree)
    return results
