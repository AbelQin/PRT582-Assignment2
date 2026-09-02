import pytest

from analyzer.duplicates import find_duplicate_blocks, find_duplicate_functions


def test_identical_function_bodies_detected():
    """Normal case: two differently-named functions with the same logic
    are reported as duplicates of each other."""
    source = (
        "def add_a(x, y):\n"
        "    result = x + y\n"
        "    return result\n"
        "\n"
        "def add_b(x, y):\n"
        "    result = x + y\n"
        "    return result\n"
    )
    dups = find_duplicate_functions(source)
    assert len(dups) == 1
    assert set(dups[0].names) == {"add_a", "add_b"}


def test_different_function_bodies_not_flagged():
    """Normal case: functions with genuinely different logic are not
    reported as duplicates."""
    source = (
        "def add(x, y):\n"
        "    return x + y\n"
        "\n"
        "def multiply(x, y):\n"
        "    return x * y\n"
    )
    assert find_duplicate_functions(source) == []


def test_single_function_no_duplicates():
    """Boundary case: a file with only one function cannot have duplicates."""
    source = "def solo():\n    return 1\n"
    assert find_duplicate_functions(source) == []


def test_duplicate_line_block_detected():
    """Normal case: a repeated block of >= 4 lines is caught even when
    it is not a standalone function (e.g. copy-pasted into two branches)."""
    source = (
        "if flag:\n"
        "    a = 1\n"
        "    b = 2\n"
        "    c = 3\n"
        "    d = 4\n"
        "else:\n"
        "    a = 1\n"
        "    b = 2\n"
        "    c = 3\n"
        "    d = 4\n"
    )
    dups = find_duplicate_blocks(source, min_lines=4)
    assert len(dups) >= 1


def test_short_repeated_lines_below_threshold_not_flagged():
    """Boundary case: a repeated block shorter than the minimum block
    size should not be reported (avoids noisy false positives on
    common short idioms like `return None`)."""
    source = "x = 1\nreturn None\ny = 2\nreturn None\n"
    assert find_duplicate_blocks(source, min_lines=4) == []


def test_invalid_syntax_raises_syntax_error():
    """Invalid input: find_duplicate_functions must raise on bad syntax
    since it relies on ast.parse."""
    with pytest.raises(SyntaxError):
        find_duplicate_functions("def broken(:\n    pass\n")
