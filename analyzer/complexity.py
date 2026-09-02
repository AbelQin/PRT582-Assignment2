"""Cyclomatic complexity analysis for Python source code.

Complexity is computed using the standard McCabe formulation:
complexity = 1 (base path) + number of decision points in the function body.

Decision points counted: if/elif, for, while, except handlers,
boolean operators (and/or) used as short-circuit branches,
ternary (conditional) expressions, and comprehension "if" clauses.
"""

import ast
from dataclasses import dataclass, field


@dataclass
class FunctionComplexity:
    name: str
    lineno: int
    complexity: int


class _ComplexityVisitor(ast.NodeVisitor):
    """Walks a single function body and counts decision points.

    Does NOT recurse into nested function/lambda definitions -- those are
    analysed separately as their own units, matching how most static
    analysers (e.g. radon, flake8-mccabe) report complexity per function.
    """

    def __init__(self):
        self.decisions = 0

    def visit_If(self, node):
        self.decisions += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.decisions += 1
        self.generic_visit(node)

    def visit_AsyncFor(self, node):
        self.decisions += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.decisions += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        self.decisions += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        # Each extra operand after the first introduces a new branch.
        self.decisions += max(len(node.values) - 1, 0)
        self.generic_visit(node)

    def visit_IfExp(self, node):
        self.decisions += 1
        self.generic_visit(node)

    def visit_comprehension(self, node):
        self.decisions += len(node.ifs)
        self.generic_visit(node)

    def _skip_nested(self, node):
        # Stop descending into nested function/lambda scopes.
        return

    visit_FunctionDef = _skip_nested
    visit_AsyncFunctionDef = _skip_nested
    visit_Lambda = _skip_nested


def _visit_top_level(node):
    """Compute complexity for a function/method, excluding nested defs."""
    visitor = _ComplexityVisitor()
    for child in ast.iter_child_nodes(node):
        visitor.visit(child)
    return 1 + visitor.decisions


def analyse_complexity(source: str) -> list[FunctionComplexity]:
    """Return per-function cyclomatic complexity for the given source code.

    Raises SyntaxError if the source cannot be parsed -- callers are
    expected to handle invalid input explicitly (see cli.py).
    """
    tree = ast.parse(source)
    results: list[FunctionComplexity] = []

    class _Finder(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            results.append(FunctionComplexity(
                name=node.name,
                lineno=node.lineno,
                complexity=_visit_top_level(node),
            ))
            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node):
            results.append(FunctionComplexity(
                name=node.name,
                lineno=node.lineno,
                complexity=_visit_top_level(node),
            ))
            self.generic_visit(node)

    _Finder().visit(tree)
    return results
