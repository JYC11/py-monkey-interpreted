from src.ast.ast import Identifier, LetStatement, Program
from src.tokens.tokens import Token, TokenType


def test_ast_to_string():
    program = Program()
    program.statements = [
        LetStatement(
            token=Token(
                type=TokenType.LET,
                literal="let",
            ),
            name=Identifier(
                token=Token(type=TokenType.IDENT, literal="myVar"),
                value="myVar",
            ),
            value=Identifier(
                token=Token(type=TokenType.IDENT, literal="anotherVar"),
                value="anotherVar",
            ),
        )
    ]
    assert str(program) == "let myVar = anotherVar;"
