from src.ast.ast import (
    BooleanLiteral,
    Expression,
    Identifier,
    InfixExpression,
    IntegerLiteral,
    LetStatement,
    Program,
    Statement,
)
from src.lexer.lexer import Lexer
from src.parser.parser import Parser


def parser_factory_for_test(input: str) -> Program:
    lexer = Lexer(input=input)
    parser = Parser(lexer=lexer)
    program = parser.parse_program()
    check_parser_errors(parser=parser)
    return program


def check_parser_errors(parser: Parser):
    errors = parser.get_errors()
    assert len(errors) == 0


def check_let_statement(stmt: Statement, name: str):
    assert isinstance(stmt, LetStatement)
    if stmt.token_literal() != "let":
        return False
    if stmt.name.value != name:
        return False
    if stmt.name.token_literal() != name:
        return False
    return True


def check_literal_expression(exp: Expression, expected):
    if isinstance(expected, int) and type(expected) == int:  # noqa: E721
        return check_integer_literal(exp, expected)
    elif isinstance(expected, bool) and type(expected) == bool:  # noqa: E721
        return check_boolean_literal(exp, expected)
    elif isinstance(expected, str):
        return check_identifier(exp, expected)
    return False


def check_integer_literal(il: IntegerLiteral, value: int):
    if il.value != value:
        return False
    if il.token_literal() != str(value):
        return False
    return True


def check_boolean_literal(bl: BooleanLiteral, value: bool):
    if bl.value != value:
        return False
    if bl.token_literal() != str(value).lower():
        return False
    return True


def check_identifier(exp: Expression, value: str):
    assert isinstance(exp, Identifier)
    if exp.value != value:
        return False
    if exp.token_literal() != value:
        return False
    return True


def check_infix_expression(
    exp: Expression,
    left_value: str | bool | int,
    operator: str,
    right_value: str | bool | int,
):
    assert isinstance(exp, InfixExpression)

    left_check = check_literal_expression(exp=exp.left, expected=left_value)
    if left_check is False:
        return left_check

    assert exp.operator == operator

    right_check = check_literal_expression(exp=exp.right, expected=right_value)
    if right_check is False:
        return right_check

    return True
