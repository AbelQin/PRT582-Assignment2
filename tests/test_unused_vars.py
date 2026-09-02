import pytest

from analyzer.unused_vars import analyse_unused_variables


def test_unused_variable_is_detected():
    """Normal case: an assigned-but-never-read variable is flagged."""
    source = (
        "def compute():\n"
        "    total = 0\n"
        "    unused = 42\n"
        "    return total\n"
    )
    result = analyse_unused_variables(source)
    assert len(result) == 1
    assert result[0].name == "unused"
    assert result[0].function == "compute"


def test_used_variable_not_flagged():
    """Normal case: a variable that is read later is not flagged."""
    source = "def compute():\n    total = 0\n    return total\n"
    assert analyse_unused_variables(source) == []


def test_underscore_prefixed_variable_ignored():
    """Boundary case: conventionally 'intentionally unused' names are
    exempt from the check."""
    source = "def compute():\n    _ignored = do_something()\n    return 1\n"
    assert analyse_unused_variables(source) == []


def test_augmented_assignment_not_flagged():
    """Boundary case: `x += 1` reads x, so x is never 'purely unused'
    even if the final value of x is discarded."""
    source = "def compute():\n    total = 0\n    total += 1\n    return None\n"
    assert analyse_unused_variables(source) == []


def test_variable_used_only_in_nested_function_not_flagged():
    """Regression: a variable captured by a closure counts as used."""
    source = (
        "def outer():\n"
        "    value = 10\n"
        "    def inner():\n"
        "        return value\n"
        "    return inner()\n"
    )
    assert analyse_unused_variables(source) == []


def test_multiple_unused_variables_all_reported():
    """Boundary case: more than one unused variable in the same function."""
    source = (
        "def compute():\n"
        "    a = 1\n"
        "    b = 2\n"
        "    return None\n"
    )
    result = analyse_unused_variables(source)
    names = {uv.name for uv in result}
    assert names == {"a", "b"}


def test_invalid_syntax_raises_syntax_error():
    """Invalid input: malformed source must raise, not silently return []."""
    with pytest.raises(SyntaxError):
        analyse_unused_variables("def compute(:\n    pass\n")
