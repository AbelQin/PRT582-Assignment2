import pytest

from analyzer.complexity import analyse_complexity


def test_straight_line_function_has_complexity_one():
    """Normal case: no branches -> base complexity of 1."""
    source = "def add(a, b):\n    return a + b\n"
    result = analyse_complexity(source)
    assert len(result) == 1
    assert result[0].name == "add"
    assert result[0].complexity == 1


def test_single_if_adds_one():
    """Normal case: one decision point -> complexity 2."""
    source = (
        "def sign(x):\n"
        "    if x > 0:\n"
        "        return 1\n"
        "    return 0\n"
    )
    result = analyse_complexity(source)
    assert result[0].complexity == 2


def test_boundary_many_branches():
    """Boundary case: many chained decision points accumulate correctly."""
    source = (
        "def classify(x):\n"
        "    if x == 1:\n"
        "        return 'a'\n"
        "    elif x == 2:\n"
        "        return 'b'\n"
        "    elif x == 3:\n"
        "        return 'c'\n"
        "    for i in range(x):\n"
        "        if i % 2 == 0:\n"
        "            print(i)\n"
        "    while x > 0:\n"
        "        x -= 1\n"
        "    return x\n"
    )
    result = analyse_complexity(source)
    # elif is a nested `If` node in the AST, so there are 3 `If` nodes
    # here (the initial `if` plus 2 `elif`), not 2: base(1) + 3 if
    # + for + nested if + while = 7.
    assert result[0].complexity == 7


def test_bool_ops_count_as_branches():
    """Boundary case: and/or short-circuit operators each add a branch."""
    source = "def check(a, b, c):\n    return a and b or c\n"
    result = analyse_complexity(source)
    # base(1) + (and: 1 extra operand) + (or: 1 extra operand) = 3
    assert result[0].complexity == 3


def test_nested_function_reported_separately():
    """Regression: nested functions must not inflate the outer function's
    complexity, and must appear as their own entry."""
    source = (
        "def outer(x):\n"
        "    def inner(y):\n"
        "        if y > 0:\n"
        "            return y\n"
        "        return -y\n"
        "    return inner(x)\n"
    )
    result = {fc.name: fc.complexity for fc in analyse_complexity(source)}
    assert result["outer"] == 1
    assert result["inner"] == 2


def test_empty_source_returns_no_functions():
    """Boundary case: a file with no function definitions."""
    assert analyse_complexity("x = 1\ny = 2\n") == []


def test_invalid_syntax_raises_syntax_error():
    """Invalid input: malformed Python must raise SyntaxError, not fail
    silently or return a misleading empty result."""
    with pytest.raises(SyntaxError):
        analyse_complexity("def broken(:\n    pass\n")
