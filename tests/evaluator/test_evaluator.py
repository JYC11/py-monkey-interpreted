import pytest

from src.object.object import Array, Boolean, Error, Function, Hash, HashKey, Integer, Object, String
from tests.evaluator.conftest import (
    check_boolean_object,
    check_integer_object,
    check_null_object,
    eval_factory_for_test,
)


@pytest.mark.parametrize(
    "input, expected",
    [
        ("5", 5),
        ("10", 10),
        ("-5", -5),
        ("-10", -10),
        ("5 + 5 + 5 + 5 - 10", 10),
        ("2 * 2 * 2 * 2 * 2", 32),
        ("-50 + 100 + -50", 0),
        ("5 * 2 + 10", 20),
        ("5 + 2 * 10", 25),
        ("20 + 2 * -10", 0),
        ("50 / 2 * 2 + 10", 60),
        ("2 * (5 + 10)", 30),
        ("3 * 3 * 3 + 10", 37),
        ("3 * (3 * 3) + 10", 37),
        ("(5 + 10 * 2 + 15 / 3) * 2 + -10", 50),
    ],
)
def test_evaluate_integer_expression(input: str, expected: int):
    evaluated = eval_factory_for_test(input=input)
    check_integer_object(obj=evaluated, expected=expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        ("true", True),
        ("false", False),
        ("1 < 2", True),
        ("1 > 2", False),
        ("1 < 1", False),
        ("1 > 1", False),
        ("1 == 1", True),
        ("1 != 1", False),
        ("1 == 2", False),
        ("1 != 2", True),
        ("true == true", True),
        ("false == false", True),
        ("true == false", False),
        ("true != false", True),
        ("false != true", True),
        ("(1 < 2) == true", True),
        ("(1 < 2) == false", False),
        ("(1 > 2) == true", False),
        ("(1 > 2) == false", True),
    ],
)
def test_evaluate_boolean_expression(input: str, expected: int):
    evaluated = eval_factory_for_test(input=input)
    check_boolean_object(obj=evaluated, expected=expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        ("!true", False),
        ("!false", True),
        ("!5", False),
        ("!!true", True),
        ("!!false", False),
        ("!!5", True),
    ],
)
def test_evaluate_bang_operator(input: str, expected: int):
    evaluated = eval_factory_for_test(input=input)
    check_boolean_object(obj=evaluated, expected=expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        ("if (true) { 10 }", 10),
        ("if (false) { 10 }", None),
        ("if (1) { 10 }", 10),
        ("if (1 < 2) { 10 }", 10),
        ("if (1 > 2) { 10 }", None),
        ("if (1 > 2) { 10 } else { 20 }", 20),
        ("if (1 < 2) { 10 } else { 20 }", 10),
    ],
)
def test_evaluate_if_else_expression(input: str, expected: int | None):
    evaluated = eval_factory_for_test(input=input)
    if expected is None:
        check_null_object(obj=evaluated)
    else:
        check_integer_object(obj=evaluated, expected=expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        ("return 10;", 10),
        ("return 10; 9;", 10),
        ("return 2 * 5; 9;", 10),
        ("9; return 2 * 5; 9;", 10),
        ("if (10 > 1) { return 10; }", 10),
        (
            """
if (10 > 1) {
  if (10 > 1) {
    return 10;
  }

  return 1;
}
""",
            10,
        ),
        (
            """
let f = fn(x) {
  return x;
  x + 10;
};
f(10);""",
            10,
        ),
        (
            """
let f = fn(x) {
   let result = x + 10;
   return result;
   return 10;
};
f(10);""",
            20,
        ),
    ],
)
def test_evaluate_return_statement(input: str, expected: int):
    evaluated = eval_factory_for_test(input=input)
    check_integer_object(obj=evaluated, expected=expected)


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            "5 + true;",
            "type mismatch: INTEGER + BOOLEAN",
        ),
        (
            "5 + true; 5;",
            "type mismatch: INTEGER + BOOLEAN",
        ),
        (
            "-true",
            "unknown operator: -BOOLEAN",
        ),
        (
            "true + false;",
            "unknown operator: BOOLEAN + BOOLEAN",
        ),
        (
            "true + false + true + false;",
            "unknown operator: BOOLEAN + BOOLEAN",
        ),
        (
            "5; true + false; 5",
            "unknown operator: BOOLEAN + BOOLEAN",
        ),
        (
            '"Hello" - "World"',
            "unknown operator: STRING - STRING",
        ),
        (
            "if (10 > 1) { true + false; }",
            "unknown operator: BOOLEAN + BOOLEAN",
        ),
        (
            """
if (10 > 1) {
  if (10 > 1) {
    return true + false;
  }

  return 1;
}
""",
            "unknown operator: BOOLEAN + BOOLEAN",
        ),
        (
            "foobar",
            "identifier not found: foobar",
        ),
        (
            '{"name": "Monkey"}[fn(x) { x }];',
            "unusable as hash key: FUNCTION",
        ),
        (
            "999[1]",
            "index operator not supported: INTEGER",
        ),
    ],
)
def test_error_handling(input: str, expected: str):
    evaluated = eval_factory_for_test(input=input)
    assert isinstance(evaluated, Error)
    assert evaluated.message == expected


@pytest.mark.parametrize(
    "input, expected",
    [
        ("let a = 5; a;", 5),
        ("let a = 5 * 5; a;", 25),
        ("let a = 5; let b = a; b;", 5),
        ("let a = 5; let b = a; let c = a + b + 5; c;", 15),
    ],
)
def test_evaluate_let_statements(input: str, expected: int):
    evaluated: Object = eval_factory_for_test(input=input)
    check_integer_object(obj=evaluated, expected=expected)


def test_evaluate_function_object():
    input = "fn(x) { x + 2; };"
    evaluated: Object = eval_factory_for_test(input=input)
    assert isinstance(evaluated, Function)

    assert len(evaluated.parameters) == 1

    assert str(evaluated.parameters[0]) == "x"

    assert str(evaluated.body) == "(x + 2)"


@pytest.mark.parametrize(
    "input, expected",
    [
        ("let identity = fn(x) { x; }; identity(5);", 5),
        ("let identity = fn(x) { return x; }; identity(5);", 5),
        ("let double = fn(x) { x * 2; }; double(5);", 10),
        ("let add = fn(x, y) { x + y; }; add(5, 5);", 10),
        ("let add = fn(x, y) { x + y; }; add(5 + 5, add(5, 5));", 20),
        ("fn(x) { x; }(5)", 5),
    ],
)
def test_evaluate_function_application(input: str, expected: int):
    evaluated: Object = eval_factory_for_test(input=input)
    check_integer_object(obj=evaluated, expected=expected)


def test_evaluate_enclosing_environment():
    input = """
let first = 10;
let second = 10;
let third = 10;

let ourFunction = fn(first) {
  let second = 20;

  first + second + third;
};

ourFunction(20) + first + second;
"""
    evaluated: Object = eval_factory_for_test(input=input)
    check_integer_object(obj=evaluated, expected=70)


def test_evaluate_closure():
    input = """
let newAdder = fn(x) {
  fn(y) { x + y };
};

let addTwo = newAdder(2);
addTwo(2);
"""
    evaluated: Object = eval_factory_for_test(input=input)
    check_integer_object(obj=evaluated, expected=4)


def test_evaluate_string_literal():
    input = '"Hello World!"'
    evaluated: Object = eval_factory_for_test(input=input)

    assert isinstance(evaluated, String)
    assert evaluated.value == "Hello World!"


def test_evaluate_string_concatenation():
    input = '"Hello" + " " + "World!"'
    evaluated: Object = eval_factory_for_test(input=input)

    assert isinstance(evaluated, String)
    assert evaluated.value == "Hello World!"


@pytest.mark.parametrize(
    "input, expected",
    [
        ('len("")', 0),
        ('len("four")', 4),
        ('len("hello world")', 11),
        ("len(1)", "argument to `len` not supported, got INTEGER"),
        ('len("one", "two")', "wrong number of arguments. got=2, want=1"),
        ("len([1, 2, 3])", 3),
        ("len([])", 0),
        ('puts("hello", "world!")', None),
        ("first([1, 2, 3])", 1),
        ("first([])", None),
        ("first(1)", "argument to `first` must be ARRAY, got INTEGER"),
        ("last([1, 2, 3])", 3),
        ("last([])", None),
        ("last(1)", "argument to `last` must be ARRAY, got INTEGER"),
        ("rest([1, 2, 3])", [2, 3]),
        ("rest([])", None),
        ("push([], 1)", [1]),
        ("push(1, 1)", "argument to `push` must be ARRAY, got INTEGER"),
    ],
)
def test_evaluate_built_in_functions(input: str, expected: int | list[int] | str | None):
    evaluated: Object = eval_factory_for_test(input=input)
    if expected is None:
        check_null_object(obj=evaluated)
    if isinstance(expected, int):
        check_integer_object(obj=evaluated, expected=expected)
    if isinstance(expected, str):
        assert isinstance(evaluated, Error)
        assert evaluated.message == expected
    if isinstance(expected, list):
        assert isinstance(evaluated, Array)
        assert len(evaluated.elements) == len(expected)
        for got, exp in zip(evaluated.elements, expected):
            assert isinstance(got, Integer)
            assert got.value == exp


def test_evaluate_array_literal():
    input = "[1, 2 * 2, 3 + 3]"
    evaluated: Object = eval_factory_for_test(input=input)

    assert isinstance(evaluated, Array)
    assert len(evaluated.elements) == 3
    check_integer_object(obj=evaluated.elements[0], expected=1)
    check_integer_object(obj=evaluated.elements[1], expected=4)
    check_integer_object(obj=evaluated.elements[2], expected=6)


@pytest.mark.parametrize(
    "input, expected",
    [
        ("[1, 2, 3][0]", 1),
        ("[1, 2, 3][1]", 2),
        ("[1, 2, 3][2]", 3),
        ("let i = 0; [1][i];", 1),
        ("[1, 2, 3][1 + 1];", 3),
        ("let myArray = [1, 2, 3]; myArray[2];", 3),
        ("let myArray = [1, 2, 3]; myArray[0] + myArray[1] + myArray[2];", 6),
        ("let myArray = [1, 2, 3]; let i = myArray[0]; myArray[i]", 2),
        ("[1, 2, 3][3]", None),
        ("[1, 2, 3][-1]", None),
    ],
)
def test_evaluate_array_index_expressions(input: str, expected: int | None):
    evaluated: Object = eval_factory_for_test(input=input)
    if expected is None:
        check_null_object(obj=evaluated)
    else:
        check_integer_object(obj=evaluated, expected=expected)


def test_evaluate_hash_literal():
    input = """
let two = "two";
{
    "one": 10 - 9,
    two: 1 + 1,
    "thr" + "ee": 6 / 2,
    4: 4,
    true: 5,
    false: 6
}
"""
    evaluated: Object = eval_factory_for_test(input=input)

    assert isinstance(evaluated, Hash)

    expected: dict[HashKey, int] = {
        String("one").hash_key(): 1,
        String("two").hash_key(): 2,
        String("three").hash_key(): 3,
        Integer(4).hash_key(): 4,
        Boolean(True).hash_key(): 5,
        Boolean(False).hash_key(): 6,
    }

    assert len(evaluated.pairs) == len(expected)

    for expected_key, expected_value in expected.items():
        got = evaluated.pairs[expected_key]
        check_integer_object(obj=got.value, expected=expected_value)


@pytest.mark.parametrize(
    "input, expected",
    [
        ('{"foo": 5}["foo"]', 5),
        ('{"foo": 5}["bar"]', None),
        ('let key = "foo"; {"foo": 5}[key]', 5),
        ('{}["foo"]', None),
        ("{5: 5}[5]", 5),
        ("{true: 5}[true]", 5),
        ("{false: 5}[false]", 5),
    ],
)
def test_evaluate_hash_index_expression(input: str, expected: int | None):
    evaluated: Object = eval_factory_for_test(input=input)
    if expected is None:
        check_null_object(obj=evaluated)
    else:
        check_integer_object(obj=evaluated, expected=expected)
