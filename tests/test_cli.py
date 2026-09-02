import pytest

from analyzer.cli import AnalysisError, analyse_file, format_report, main


def _write(tmp_path, name, content):
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return str(path)


def test_analyse_file_normal_case(tmp_path):
    """Normal case: a well-formed file produces a full report dict with
    every analyser's results populated correctly."""
    path = _write(tmp_path, "sample.py", "def add(a, b):\n    return a + b\n")
    report = analyse_file(path)
    assert report["metrics"].num_functions == 1
    assert report["complexity"][0].name == "add"
    assert report["unused_variables"] == []
    assert report["naming_violations"] == []


def test_analyse_file_missing_file_raises(tmp_path):
    """Invalid input: a nonexistent path raises FileNotFoundError so the
    caller can report it explicitly instead of crashing unhelpfully."""
    with pytest.raises(FileNotFoundError):
        analyse_file(str(tmp_path / "does_not_exist.py"))


def test_analyse_file_invalid_syntax_raises_analysis_error(tmp_path):
    """Invalid input: malformed Python is wrapped in a friendly
    AnalysisError rather than an unhandled SyntaxError."""
    path = _write(tmp_path, "broken.py", "def broken(:\n    pass\n")
    with pytest.raises(AnalysisError):
        analyse_file(path)


def test_format_report_includes_high_complexity_flag(tmp_path):
    """Boundary case: functions above the complexity-10 threshold are
    visibly flagged as [HIGH] in the formatted report."""
    body = "def tangled(x):\n" + "".join(
        f"    if x == {i}:\n        pass\n" for i in range(12)
    ) + "    return x\n"
    path = _write(tmp_path, "tangled.py", body)
    report = analyse_file(path)
    text = format_report(report)
    assert "[HIGH]" in text


def test_main_returns_zero_on_success(tmp_path, capsys):
    """Regression: the CLI's exit code must stay 0 when every file
    given to it analyses successfully."""
    path = _write(tmp_path, "ok.py", "def ok():\n    return 1\n")
    exit_code = main([path])
    assert exit_code == 0
    assert "ok.py" in capsys.readouterr().out


def test_main_returns_nonzero_when_any_file_fails(tmp_path, capsys):
    """Exceptional case: mixing a valid file with a missing one should
    still process the valid file but report a nonzero exit code overall."""
    good = _write(tmp_path, "good.py", "def good():\n    return 1\n")
    missing = str(tmp_path / "missing.py")
    exit_code = main([good, missing])
    assert exit_code == 1
    err = capsys.readouterr().err
    assert "not found" in err


def test_format_report_lists_every_section(tmp_path):
    """Regression: a file that triggers every analyser at once should
    produce a report containing all section headers, guarding against
    a future change accidentally dropping one of the five checks."""
    source = (
        "def myFunction(x):\n"
        "    unused = 1\n"
        "    if x == 1:\n"
        "        return 'a'\n"
        "    elif x == 2:\n"
        "        return 'b'\n"
        "    return None\n"
        "\n"
        "def myFunction2(x):\n"
        "    unused = 1\n"
        "    if x == 1:\n"
        "        return 'a'\n"
        "    elif x == 2:\n"
        "        return 'b'\n"
        "    return None\n"
    )
    path = _write(tmp_path, "everything.py", source)
    report = analyse_file(path)
    text = format_report(report)
    assert "Complexity:" in text
    assert "Unused variables:" in text
    assert "Duplicate functions:" in text
    assert "Naming violations:" in text


def test_main_with_no_arguments_returns_usage_error(capsys):
    """Boundary case: calling the CLI with zero files is a usage error,
    not a silent no-op."""
    exit_code = main([])
    assert exit_code == 2
    assert "Usage" in capsys.readouterr().err
