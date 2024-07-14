from typing import Type

import pytest

from src.ast.ast import (
    ArrayLiteral,
    BooleanLiteral,
    CallExpression,
    Expression,
    ExpressionStatement,
    FunctionLiteral,
    HashLiteral,
    Identifier,
    IfExpression,
    IndexExpression,
    IntegerLiteral,
    LetStatement,
    PrefixExpression,
    Program,
    ReturnStatement,
    StringLiteral,
)
from tests.parser.conftest import (
    check_identifier,
    check_infix_expression,
    check_integer_literal,
    check_let_statement,
    check_literal_expression,
    parser_factory_for_test,
)


@pytest.mark.parametrize(
    "input, expected_identifier, expected_value",
    [
        ("let x = 5;", "x", 5),
        ("let y = true;", "y", True),
        ("let foobar = y;", "foobar", "y"),
    ],
)
def test_parse_let_statements(
    input: str,
    expected_identifier: str,
    expected_value: str | bool | int,
):
    program: Program = parser_factory_for_test(input=input)

    assert len(program.statements) == 1

    stmt = program.statements[0]
    assert isinstance(stmt, LetStatement)
    assert check_let_statement(stmt=stmt, name=expected_identifier)

    exp = stmt.value
    assert check_literal_expression(exp=exp, expected=expected_value)


@pytest.mark.parametrize(
    "input, expected_value",
    [
        ("return 5;", 5),
        ("return true;", True),
        ("return foobar;", "foobar"),
    ],
)
def test_parse_return_statements(input: str, expected_value: str | bool | int):
    program: Program = parser_factory_for_test(input=input)

    assert len(program.statements) == 1

    stmt = program.statements[0]
    assert isinstance(stmt, ReturnStatement)
    assert stmt.token_literal() == "return"

    assert check_literal_expression(stmt.return_value, expected_value)


def test_parse_identifier():
    input = "foobar;"

    program: Program = parser_factory_for_test(input=input)

    stmt = program.statements[0]
    assert isinstance(stmt, ExpressionStatement)

    ident = stmt.expression
    assert isinstance(ident, Identifier)

    assert ident.value == "foobar"
    assert ident.token_literal() == "foobar"


def test_parse_integer_literal():
    input = "5;"

    program: Program = parser_factory_for_test(input=input)

    stmt = program.statements[0]
    assert isinstance(stmt, ExpressionStatement)

    ident = stmt.expression
    assert isinstance(ident, IntegerLiteral)

    assert ident.value == 5
    assert ident.token_literal() == "5"


@pytest.mark.parametrize(
    "input, expected_prefix, expected_value",
    [
        ("!5;", "!", 5),
        ("-15;", "-", 15),
        ("!foobar;", "!", "foobar"),
        ("-foobar;", "-", "foobar"),
        ("!true;", "!", True),
        ("!false;", "!", False),
    ],
)
def test_parse_prefix_statements(
    input: str,
    expected_prefix: str,
    expected_value: str | bool | int,
):
    program: Program = parser_factory_for_test(input=input)

    assert len(program.statements) == 1

    stmt = program.statements[0]
    assert isinstance(stmt, ExpressionStatement)

    exp = stmt.expression
    assert isinstance(exp, PrefixExpression)

    assert exp.operator == expected_prefix

    assert check_literal_expression(exp=exp.right, expected=expected_value)


@pytest.mark.parametrize(
    "input, left_value, operator, right_value",
    [
        ("5 + 5;", 5, "+", 5),
        ("5 - 5;", 5, "-", 5),
        ("5 * 5;", 5, "*", 5),
        ("5 / 5;", 5, "/", 5),
        ("5 > 5;", 5, ">", 5),
        ("5 < 5;", 5, "<", 5),
        ("5 == 5;", 5, "==", 5),
        ("5 != 5;", 5, "!=", 5),
        ("foobar + barfoo;", "foobar", "+", "barfoo"),
        ("foobar - barfoo;", "foobar", "-", "barfoo"),
        ("foobar * barfoo;", "foobar", "*", "barfoo"),
        ("foobar / barfoo;", "foobar", "/", "barfoo"),
        ("foobar > barfoo;", "foobar", ">", "barfoo"),
        ("foobar < barfoo;", "foobar", "<", "barfoo"),
        ("foobar == barfoo;", "foobar", "==", "barfoo"),
        ("foobar != barfoo;", "foobar", "!=", "barfoo"),
        ("true == true", True, "==", True),
        ("true != false", True, "!=", False),
        ("false == false", False, "==", False),
    ],
)
def test_parse_infix_statements(
    input: str,
    left_value: str | bool | int,
    operator: str,
    right_value: str | bool | int,
):
    program: Program = parser_factory_for_test(input=input)

    assert len(program.statements) == 1

    stmt = program.statements[0]
    assert isinstance(stmt, ExpressionStatement)

    check_infix_expression(
        exp=stmt.expression,
        left_value=left_value,
        operator=operator,
        right_value=right_value,
    )


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            "-a * b",
            "((-a) * b)",
        ),
        (
            "!-a",
            "(!(-a))",
        ),
        (
            "a + b + c",
            "((a + b) + c)",
        ),
        (
            "a + b - c",
            "((a + b) - c)",
        ),
        (
            "a * b * c",
            "((a * b) * c)",
        ),
        (
            "a * b / c",
            "((a * b) / c)",
        ),
        (
            "a + b / c",
            "(a + (b / c))",
        ),
        (
            "a + b * c + d / e - f",
            "(((a + (b * c)) + (d / e)) - f)",
        ),
        (
            "3 + 4; -5 * 5",
            "(3 + 4)((-5) * 5)",
        ),
        (
            "5 > 4 == 3 < 4",
            "((5 > 4) == (3 < 4))",
        ),
        (
            "5 < 4 != 3 > 4",
            "((5 < 4) != (3 > 4))",
        ),
        (
            "3 + 4 * 5 == 3 * 1 + 4 * 5",
            "((3 + (4 * 5)) == ((3 * 1) + (4 * 5)))",
        ),
        (
            "true",
            "true",
        ),
        (
            "false",
            "false",
        ),
        (
            "3 > 5 == false",
            "((3 > 5) == false)",
        ),
        (
            "3 < 5 == true",
            "((3 < 5) == true)",
        ),
        (
            "1 + (2 + 3) + 4",
            "((1 + (2 + 3)) + 4)",
        ),
        (
            "(5 + 5) * 2",
            "((5 + 5) * 2)",
        ),
        (
            "2 / (5 + 5)",
            "(2 / (5 + 5))",
        ),
        (
            "(5 + 5) * 2 * (5 + 5)",
            "(((5 + 5) * 2) * (5 + 5))",
        ),
        (
            "-(5 + 5)",
            "(-(5 + 5))",
        ),
        (
            "!(true == true)",
            "(!(true == true))",
        ),
        (
            "a + add(b * c) + d",
            "((a + add((b * c))) + d)",
        ),
        (
            "add(a, b, 1, 2 * 3, 4 + 5, add(6, 7 * 8))",
            "add(a, b, 1, (2 * 3), (4 + 5), add(6, (7 * 8)))",
        ),
        (
            "add(a + b + c * d / f + g)",
            "add((((a + b) + ((c * d) / f)) + g))",
        ),
        (
            "a * [1, 2, 3, 4][b * c] * d",
            "((a * ([1, 2, 3, 4][(b * c)])) * d)",
        ),
        (
            "add(a * b[2], b[1], 2 * [1, 2][1])",
            "add((a * (b[2])), (b[1]), (2 * ([1, 2][1])))",
        ),
    ],
)
def test_parse_operator_precedence(input: str, expected: str):
    program: Program = parser_factory_for_test(input=input)

    assert str(program) == expected


@pytest.mark.parametrize(
    "input, expected_value",
    [
        ("true;", True),
        ("false;", False),
    ],
)
def test_parse_boolean_expression(input: str, expected_value: bool):
    program: Program = parser_factory_for_test(input=input)

    assert len(program.statements) == 1

    stmt = program.statements[0]
    assert isinstance(stmt, ExpressionStatement)

    boolean = stmt.expression
    assert isinstance(boolean, BooleanLiteral)
    assert boolean.value == expected_value


def test_parse_if_expression():
    input = "if (x < y) { x };"

    program: Program = parser_factory_for_test(input=input)

    stmt = program.statements[0]
    assert isinstance(stmt, ExpressionStatement)

    exp = stmt.expression
    assert isinstance(exp, IfExpression)

    assert check_infix_expression(
        exp=exp.condition,
        left_value="x",
        operator="<",
        right_value="y",
    )

    assert len(exp.consequence.statements) == 1

    consequence = exp.consequence.statements[0]
    assert isinstance(consequence, ExpressionStatement)

    check_identifier(exp=consequence.expression, value="x")


def test_parse_if_else_expression():
    input = "if (x < y) { x } else { y }"

    program: Program = parser_factory_for_test(input=input)

    stmt = program.statements[0]
    assert isinstance(stmt, ExpressionStatement)

    exp = stmt.expression
    assert isinstance(exp, IfExpression)

    assert check_infix_expression(
        exp=exp.condition,
        left_value="x",
        operator="<",
        right_value="y",
    )

    assert len(exp.consequence.statements) == 1

    consequence = exp.consequence.statements[0]
    assert isinstance(consequence, ExpressionStatement)

    check_identifier(exp=consequence.expression, value="x")

    assert exp.alternative is not None
    assert len(exp.alternative.statements) == 1

    alternative = exp.alternative.statements[0]
    assert isinstance(alternative, ExpressionStatement)

    check_identifier(exp=alternative.expression, value="y")


def test_parse_function_literal():
    input = "fn(x, y) { x + y; }"

    program: Program = parser_factory_for_test(input=input)

    stmt = program.statements[0]
    assert isinstance(stmt, ExpressionStatement)

    function = stmt.expression
    assert isinstance(function, FunctionLiteral)

    assert len(function.parameters) == 2

    check_literal_expression(exp=function.parameters[0], expected="x")

    check_literal_expression(exp=function.parameters[1], expected="y")

    assert len(function.body.statements) == 1

    body_stmt = function.body.statements[0]
    assert isinstance(body_stmt, ExpressionStatement)

    check_infix_expression(exp=body_stmt.expression, left_value="x", operator="+", right_value="y")


@pytest.mark.parametrize(
    "input, expected_params",
    [
        ("fn() {};", []),
        ("fn(x) {};", ["x"]),
        ("fn(x, y, z) {};", ["x", "y", "z"]),
    ],
)
def test_parse_function_parameters(input: str, expected_params: list[str]):
    program: Program = parser_factory_for_test(input=input)

    stmt = program.statements[0]
    assert isinstance(stmt, ExpressionStatement)

    function = stmt.expression
    assert isinstance(function, FunctionLiteral)

    assert len(function.parameters) == len(expected_params)

    for i in range(len(expected_params)):
        check_literal_expression(exp=function.parameters[i], expected=expected_params[i])


def test_parse_call_expression():
    input = "add(1, 2 * 3, 4 + 5);"

    program: Program = parser_factory_for_test(input=input)

    assert len(program.statements) == 1
    stmt = program.statements[0]
    assert isinstance(stmt, ExpressionStatement)

    exp = stmt.expression
    assert isinstance(exp, CallExpression)

    check_identifier(exp=exp.function, value="add")

    assert len(exp.arguments) == 3

    check_literal_expression(exp=exp.arguments[0], expected=1)
    check_infix_expression(exp=exp.arguments[1], left_value=2, operator="*", right_value=3)
    check_infix_expression(exp=exp.arguments[2], left_value=4, operator="+", right_value=5)


@pytest.mark.parametrize(
    "input, expected_ident, expected_args",
    [
        ("add();", "add", []),
        ("add(1);", "add", ["1"]),
        ("add(1, 2 * 3, 4 + 5);", "add", ["1", "(2 * 3)", "(4 + 5)"]),
    ],
)
def test_parse_call_expression_parameters(input: str, expected_ident: str, expected_args: list[str]):
    program: Program = parser_factory_for_test(input=input)

    stmt = program.statements[0]
    assert isinstance(stmt, ExpressionStatement)

    exp = stmt.expression
    assert isinstance(exp, CallExpression)

    check_identifier(exp=exp.function, value=expected_ident)

    assert len(exp.arguments) == len(expected_args)

    for i in range(len(expected_args)):
        assert str(exp.arguments[i]) == expected_args[i]


def test_parse_string_literal():
    input = '"hello world";'

    program: Program = parser_factory_for_test(input=input)

    stmt = program.statements[0]
    assert isinstance(stmt, ExpressionStatement)

    literal = stmt.expression
    assert isinstance(literal, StringLiteral)

    assert literal.value == "hello world"


def test_parse_empty_array_literal():
    input = "[]"

    program: Program = parser_factory_for_test(input=input)

    stmt = program.statements[0]
    assert isinstance(stmt, ExpressionStatement)

    array = stmt.expression
    assert isinstance(array, ArrayLiteral)

    assert len(array.elements) == 0


def test_parse_array_literal():
    input = "[1, 2 * 2, 3 + 3]"

    program: Program = parser_factory_for_test(input=input)

    stmt = program.statements[0]
    assert isinstance(stmt, ExpressionStatement)

    array = stmt.expression
    assert isinstance(array, ArrayLiteral)

    assert len(array.elements) == 3

    check_literal_expression(exp=array.elements[0], expected=1)
    check_infix_expression(exp=array.elements[1], left_value=2, operator="*", right_value=2)
    check_infix_expression(exp=array.elements[2], left_value=3, operator="+", right_value=3)


def test_parse_index_expression():
    input = "myArray[1 + 1]"

    program: Program = parser_factory_for_test(input=input)

    stmt = program.statements[0]
    assert isinstance(stmt, ExpressionStatement)

    index_exp = stmt.expression
    assert isinstance(index_exp, IndexExpression)

    check_identifier(exp=index_exp.left, value="myArray")

    check_infix_expression(exp=index_exp.index, left_value=1, operator="+", right_value=1)


def test_parse_empty_hash_literal():
    input = "{}"

    program: Program = parser_factory_for_test(input=input)

    stmt = program.statements[0]
    assert isinstance(stmt, ExpressionStatement)

    hash = stmt.expression
    assert isinstance(hash, HashLiteral)

    assert len(hash.pairs) == 0


@pytest.mark.parametrize(
    "input, expected, expected_literal",
    [
        (
            '{"one": 1, "two": 2, "three": 3}',
            {
                "one": 1,
                "two": 2,
                "three": 3,
            },
            StringLiteral,
        ),
        (
            "{true: 1, false: 2}",
            {
                "true": 1,
                "false": 2,
            },
            BooleanLiteral,
        ),
        (
            "{1: 1, 2: 2, 3: 3}",
            {
                "1": 1,
                "2": 2,
                "3": 3,
            },
            IntegerLiteral,
        ),
    ],
)
def test_parse_hash_literal(
    input: str,
    expected: dict[str, int],
    expected_literal: Type[Expression],
):
    program: Program = parser_factory_for_test(input=input)

    stmt = program.statements[0]
    assert isinstance(stmt, ExpressionStatement)

    hash = stmt.expression
    assert isinstance(hash, HashLiteral)

    assert len(hash.pairs) == len(expected)

    for key, value in hash.pairs.items():
        assert isinstance(key, expected_literal)

        expected_value = expected[str(key)]

        check_integer_literal(il=value, value=expected_value)
