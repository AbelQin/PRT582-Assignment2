# pyanalyzer

A lightweight static analysis tool for Python source code, built as part of
PRT582 Software Unit Testing using an AI-assisted Test-Driven Development
(AI-TDD) workflow.

## What it checks

| Check | Module |
|---|---|
| Cyclomatic complexity per function | `analyzer/complexity.py` |
| Unused local variables | `analyzer/unused_vars.py` |
| Duplicate functions and duplicate code blocks | `analyzer/duplicates.py` |
| PEP 8 naming violations (functions, variables, classes) | `analyzer/naming.py` |
| Aggregate code metrics (LOC, function/class counts, avg/max complexity) | `analyzer/metrics.py` |

## Usage

```bash
pip install -r requirements.txt
python -m analyzer.cli path/to/file.py [more_files.py ...]
```

Example, using the bundled sample:

```bash
python -m analyzer.cli sample_inputs/messy_example.py
```

## Running the tests

```bash
pip install -r requirements.txt
python -m pytest --cov=analyzer --cov-report=term-missing
```

40 tests, 93% statement coverage as of the last run (see
`test_run_output.txt` / `htmlcov/index.html` for the full report).

## Project layout

```
analyzer/
    complexity.py     cyclomatic complexity
    unused_vars.py    unused local variable detection
    duplicates.py     duplicate function / block detection
    naming.py         PEP 8 naming checks
    metrics.py        aggregate metrics
    cli.py            orchestrates all analysers, formats a report
tests/                one test module per analyser module
sample_inputs/        example file used for manual/demo runs
```
