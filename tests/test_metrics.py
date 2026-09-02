import pytest

from analyzer.metrics import analyse_metrics


def test_basic_metrics_counts():
    """Normal case: line/function/class counts on a small known file."""
    source = (
        "# a comment\n"
        "\n"
        "def add(a, b):\n"
        "    return a + b\n"
        "\n"
        "class Thing:\n"
        "    pass\n"
    )
    m = analyse_metrics(source)
    assert m.total_lines == 7
    assert m.blank_lines == 2
    assert m.comment_lines == 1
    assert m.code_lines == 4
    assert m.num_functions == 1
    assert m.num_classes == 1


def test_average_and_max_complexity():
    """Normal case: average/max complexity aggregated across functions."""
    source = (
        "def simple():\n"
        "    return 1\n"
        "\n"
        "def branchy(x):\n"
        "    if x > 0:\n"
        "        return 1\n"
        "    return -1\n"
    )
    m = analyse_metrics(source)
    assert m.average_complexity == 1.5
    assert m.max_complexity == 2


def test_empty_file_boundary():
    """Boundary case: an empty file should not crash and should report
    zeroed-out metrics rather than raising an exception."""
    m = analyse_metrics("")
    assert m.total_lines == 0
    assert m.num_functions == 0
    assert m.average_complexity == 0.0
    assert m.max_complexity == 0


def test_invalid_syntax_raises_syntax_error():
    with pytest.raises(SyntaxError):
        analyse_metrics("def broken(:\n    pass\n")
