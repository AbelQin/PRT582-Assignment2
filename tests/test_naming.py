import pytest

from analyzer.naming import analyse_naming


def test_camelcase_function_flagged():
    """Normal case: a camelCase function name violates snake_case."""
    source = "def myFunction():\n    pass\n"
    result = analyse_naming(source)
    assert any(v.kind == "function" and v.name == "myFunction" for v in result)


def test_snake_case_function_not_flagged():
    """Normal case: a correctly-named function passes."""
    source = "def my_function():\n    pass\n"
    assert analyse_naming(source) == []


def test_lowercase_class_flagged():
    """Normal case: a class name must be PascalCase."""
    source = "class myClass:\n    pass\n"
    result = analyse_naming(source)
    assert any(v.kind == "class" and v.name == "myClass" for v in result)


def test_pascalcase_class_not_flagged():
    source = "class MyClass:\n    pass\n"
    assert analyse_naming(source) == []


def test_camelcase_parameter_flagged():
    """Normal case: a camelCase parameter name is flagged too."""
    source = "def greet(userName):\n    return userName\n"
    result = analyse_naming(source)
    assert any(v.name == "userName" for v in result)


def test_self_and_cls_never_flagged():
    """Boundary case: conventional method parameters are exempt even
    though they are single lowercase words with no underscore -- this
    guards against false positives on every method in the codebase."""
    source = (
        "class Widget:\n"
        "    def resize(self, new_size):\n"
        "        return new_size\n"
        "    @classmethod\n"
        "    def create(cls):\n"
        "        return cls()\n"
    )
    assert analyse_naming(source) == []


def test_underscore_prefixed_names_exempt():
    """Boundary case: private/dunder names are not subject to case
    checks (leading underscore already signals convention)."""
    source = "def __init__(self):\n    self._Value = 1\n"
    assert analyse_naming(source) == []


def test_invalid_syntax_raises_syntax_error():
    with pytest.raises(SyntaxError):
        analyse_naming("class Broken(:\n    pass\n")
