from typing import Any

from src.lexer.lexer import Lexer
from src.tokens.tokens import Token, TokenType


def test_lexer_next_token():
    code = """let five = 5;
let ten = 10;

let add = fn(x, y) {
  x + y;
};

let result = add(five, ten);
!-/*5;
5 < 10 > 5;

if (5 < 10) {
	return true;
} else {
	return false;
}

10 == 10;
10 != 9;
"foobar"
"foo bar"
[1, 2];
{"foo": "bar"}
"""
    tests: list[dict[str, Any]] = [
        {"expected_type": TokenType.LET, "expected_literal": "let"},
        {"expected_type": TokenType.IDENT, "expected_literal": "five"},
        {"expected_type": TokenType.ASSIGN, "expected_literal": "="},
        {"expected_type": TokenType.INT, "expected_literal": "5"},
        {"expected_type": TokenType.SEMICOLON, "expected_literal": ";"},
        {"expected_type": TokenType.LET, "expected_literal": "let"},
        {"expected_type": TokenType.IDENT, "expected_literal": "ten"},
        {"expected_type": TokenType.ASSIGN, "expected_literal": "="},
        {"expected_type": TokenType.INT, "expected_literal": "10"},
        {"expected_type": TokenType.SEMICOLON, "expected_literal": ";"},
        {"expected_type": TokenType.LET, "expected_literal": "let"},
        {"expected_type": TokenType.IDENT, "expected_literal": "add"},
        {"expected_type": TokenType.ASSIGN, "expected_literal": "="},
        {"expected_type": TokenType.FUNCTION, "expected_literal": "fn"},
        {"expected_type": TokenType.LPAREN, "expected_literal": "("},
        {"expected_type": TokenType.IDENT, "expected_literal": "x"},
        {"expected_type": TokenType.COMMA, "expected_literal": ","},
        {"expected_type": TokenType.IDENT, "expected_literal": "y"},
        {"expected_type": TokenType.RPAREN, "expected_literal": ")"},
        {"expected_type": TokenType.LBRACE, "expected_literal": "{"},
        {"expected_type": TokenType.IDENT, "expected_literal": "x"},
        {"expected_type": TokenType.PLUS, "expected_literal": "+"},
        {"expected_type": TokenType.IDENT, "expected_literal": "y"},
        {"expected_type": TokenType.SEMICOLON, "expected_literal": ";"},
        {"expected_type": TokenType.RBRACE, "expected_literal": "}"},
        {"expected_type": TokenType.SEMICOLON, "expected_literal": ";"},
        {"expected_type": TokenType.LET, "expected_literal": "let"},
        {"expected_type": TokenType.IDENT, "expected_literal": "result"},
        {"expected_type": TokenType.ASSIGN, "expected_literal": "="},
        {"expected_type": TokenType.IDENT, "expected_literal": "add"},
        {"expected_type": TokenType.LPAREN, "expected_literal": "("},
        {"expected_type": TokenType.IDENT, "expected_literal": "five"},
        {"expected_type": TokenType.COMMA, "expected_literal": ","},
        {"expected_type": TokenType.IDENT, "expected_literal": "ten"},
        {"expected_type": TokenType.RPAREN, "expected_literal": ")"},
        {"expected_type": TokenType.SEMICOLON, "expected_literal": ";"},
        {"expected_type": TokenType.BANG, "expected_literal": "!"},
        {"expected_type": TokenType.MINUS, "expected_literal": "-"},
        {"expected_type": TokenType.SLASH, "expected_literal": "/"},
        {"expected_type": TokenType.ASTERISK, "expected_literal": "*"},
        {"expected_type": TokenType.INT, "expected_literal": "5"},
        {"expected_type": TokenType.SEMICOLON, "expected_literal": ";"},
        {"expected_type": TokenType.INT, "expected_literal": "5"},
        {"expected_type": TokenType.LT, "expected_literal": "<"},
        {"expected_type": TokenType.INT, "expected_literal": "10"},
        {"expected_type": TokenType.GT, "expected_literal": ">"},
        {"expected_type": TokenType.INT, "expected_literal": "5"},
        {"expected_type": TokenType.SEMICOLON, "expected_literal": ";"},
        {"expected_type": TokenType.IF, "expected_literal": "if"},
        {"expected_type": TokenType.LPAREN, "expected_literal": "("},
        {"expected_type": TokenType.INT, "expected_literal": "5"},
        {"expected_type": TokenType.LT, "expected_literal": "<"},
        {"expected_type": TokenType.INT, "expected_literal": "10"},
        {"expected_type": TokenType.RPAREN, "expected_literal": ")"},
        {"expected_type": TokenType.LBRACE, "expected_literal": "{"},
        {"expected_type": TokenType.RETURN, "expected_literal": "return"},
        {"expected_type": TokenType.TRUE, "expected_literal": "true"},
        {"expected_type": TokenType.SEMICOLON, "expected_literal": ";"},
        {"expected_type": TokenType.RBRACE, "expected_literal": "}"},
        {"expected_type": TokenType.ELSE, "expected_literal": "else"},
        {"expected_type": TokenType.LBRACE, "expected_literal": "{"},
        {"expected_type": TokenType.RETURN, "expected_literal": "return"},
        {"expected_type": TokenType.FALSE, "expected_literal": "false"},
        {"expected_type": TokenType.SEMICOLON, "expected_literal": ";"},
        {"expected_type": TokenType.RBRACE, "expected_literal": "}"},
        {"expected_type": TokenType.INT, "expected_literal": "10"},
        {"expected_type": TokenType.EQ, "expected_literal": "=="},
        {"expected_type": TokenType.INT, "expected_literal": "10"},
        {"expected_type": TokenType.SEMICOLON, "expected_literal": ";"},
        {"expected_type": TokenType.INT, "expected_literal": "10"},
        {"expected_type": TokenType.NOT_EQ, "expected_literal": "!="},
        {"expected_type": TokenType.INT, "expected_literal": "9"},
        {"expected_type": TokenType.SEMICOLON, "expected_literal": ";"},
        {"expected_type": TokenType.STRING, "expected_literal": "foobar"},
        {"expected_type": TokenType.STRING, "expected_literal": "foo bar"},
        {"expected_type": TokenType.LBRACKET, "expected_literal": "["},
        {"expected_type": TokenType.INT, "expected_literal": "1"},
        {"expected_type": TokenType.COMMA, "expected_literal": ","},
        {"expected_type": TokenType.INT, "expected_literal": "2"},
        {"expected_type": TokenType.RBRACKET, "expected_literal": "]"},
        {"expected_type": TokenType.SEMICOLON, "expected_literal": ";"},
        {"expected_type": TokenType.LBRACE, "expected_literal": "{"},
        {"expected_type": TokenType.STRING, "expected_literal": "foo"},
        {"expected_type": TokenType.COLON, "expected_literal": ":"},
        {"expected_type": TokenType.STRING, "expected_literal": "bar"},
        {"expected_type": TokenType.RBRACE, "expected_literal": "}"},
        {"expected_type": TokenType.EOF, "expected_literal": ""},
    ]

    lexer = Lexer(input=code)

    for test_case in tests:
        token: Token = lexer.next_token()
        assert token.type == test_case["expected_type"]
        assert token.literal == test_case["expected_literal"]
