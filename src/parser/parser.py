from typing import Callable

from src.ast.ast import (
    ArrayLiteral,
    BlockStatement,
    BooleanLiteral,
    CallExpression,
    Expression,
    ExpressionStatement,
    FunctionLiteral,
    HashLiteral,
    Identifier,
    IfExpression,
    IndexExpression,
    InfixExpression,
    IntegerLiteral,
    LetStatement,
    PrefixExpression,
    Program,
    ReturnStatement,
    Statement,
    StringLiteral,
)
from src.lexer.lexer import Lexer
from src.tokens.tokens import Token, TokenType

LOWEST = 1
EQUALS = 2
LESSGREATER = 3
SUM = 4
PRODUCT = 5
PREFIX = 6
CALL = 7
INDEX = 8

precedences: dict[TokenType, int] = {
    TokenType.EQ: EQUALS,
    TokenType.NOT_EQ: EQUALS,
    TokenType.LT: LESSGREATER,
    TokenType.GT: LESSGREATER,
    TokenType.PLUS: SUM,
    TokenType.MINUS: SUM,
    TokenType.SLASH: PRODUCT,
    TokenType.ASTERISK: PRODUCT,
    TokenType.LPAREN: CALL,
    TokenType.LBRACKET: INDEX,
}


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.errors_list: list[str] = []

        self.cur_token: Token | None = None
        self.peek_token: Token | None = None

        self.prefix_parse_fns: dict[TokenType, Callable] = {}
        self.infix_parse_fns: dict[TokenType, Callable] = {}

        self.register_prefix(TokenType.IDENT, self.parse_identifier)
        self.register_prefix(TokenType.INT, self.parse_integer_literal)
        self.register_prefix(TokenType.STRING, self.parse_string_literal)
        self.register_prefix(TokenType.BANG, self.parse_prefix_expression)
        self.register_prefix(TokenType.MINUS, self.parse_prefix_expression)
        self.register_prefix(TokenType.TRUE, self.parse_boolean)
        self.register_prefix(TokenType.FALSE, self.parse_boolean)
        self.register_prefix(TokenType.LPAREN, self.parse_grouped_expression)
        self.register_prefix(TokenType.IF, self.parse_if_expression)
        self.register_prefix(TokenType.FUNCTION, self.parse_function_literal)
        self.register_prefix(TokenType.LBRACKET, self.parse_array_literal)
        self.register_prefix(TokenType.LBRACE, self.parse_hash_literal)

        self.register_infix(TokenType.PLUS, self.parse_infix_expression)
        self.register_infix(TokenType.MINUS, self.parse_infix_expression)
        self.register_infix(TokenType.SLASH, self.parse_infix_expression)
        self.register_infix(TokenType.ASTERISK, self.parse_infix_expression)
        self.register_infix(TokenType.EQ, self.parse_infix_expression)
        self.register_infix(TokenType.NOT_EQ, self.parse_infix_expression)
        self.register_infix(TokenType.LT, self.parse_infix_expression)
        self.register_infix(TokenType.GT, self.parse_infix_expression)

        self.register_infix(TokenType.LPAREN, self.parse_call_expression)
        self.register_infix(TokenType.LBRACKET, self.parse_index_expression)

        # Read two tokens, so curToken and peekToken are both set
        self.next_token()
        self.next_token()

    def register_prefix(self, token: TokenType, callable: Callable):
        self.prefix_parse_fns[token] = callable

    def register_infix(self, token: TokenType, callable: Callable):
        self.infix_parse_fns[token] = callable

    def next_token(self):
        self.cur_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def current_token_is(self, token: TokenType) -> bool:
        assert self.cur_token is not None
        return self.cur_token.type == token

    def peek_token_is(self, token: TokenType) -> bool:
        assert self.peek_token is not None
        return self.peek_token.type == token

    def expect_peek(self, token: TokenType) -> bool:
        if self.peek_token_is(token):
            self.next_token()
            return True
        else:
            self.peek_error(token)
            return False

    def get_errors(self):
        return self.errors_list

    def peek_error(self, token_type: TokenType):
        assert self.peek_token is not None
        msg = f"expected next token to be {token_type}, got {self.peek_token.type} instead"
        self.errors_list.append(msg)

    def no_prefix_parse_fn_error(self, token_type: TokenType):
        msg = f"no prefix parse function for {token_type} found"
        self.errors_list.append(msg)

    def parse_program(self) -> Program:
        program = Program()
        program.statements = []

        while not self.current_token_is(TokenType.EOF):
            stmt: Statement | None = self.parse_statement()
            if stmt is not None:
                program.statements.append(stmt)
            self.next_token()

        return program

    def parse_statement(self) -> Statement | None:
        assert self.cur_token is not None
        if self.cur_token.type == TokenType.LET:
            return self.parse_let_statement()
        elif self.cur_token.type == TokenType.RETURN:
            return self.parse_return_statement()
        else:
            return self.parse_expression_statement()

    def parse_let_statement(self) -> None | LetStatement:
        cur_token: Token | None = self.cur_token
        assert cur_token is not None

        if not self.expect_peek(TokenType.IDENT):
            return None

        assert self.cur_token is not None
        name = Identifier(token=self.cur_token, value=self.cur_token.literal)

        if not self.expect_peek(TokenType.ASSIGN):
            return None

        self.next_token()

        value: Expression | None = self.parse_expression(LOWEST)
        assert value is not None

        if self.peek_token_is(TokenType.SEMICOLON):
            self.next_token()

        stmt = LetStatement(
            token=cur_token,
            name=name,
            value=value,
        )

        return stmt

    def parse_return_statement(self) -> ReturnStatement:
        cur_token: Token | None = self.cur_token
        assert cur_token is not None

        self.next_token()

        return_value: Expression | None = self.parse_expression(LOWEST)
        assert return_value is not None

        if self.peek_token_is(TokenType.SEMICOLON):
            self.next_token()

        stmt = ReturnStatement(
            token=cur_token,
            return_value=return_value,
        )

        return stmt

    def parse_expression_statement(self) -> ExpressionStatement:
        cur_token: Token | None = self.cur_token
        assert cur_token is not None

        expression: Expression | None = self.parse_expression(LOWEST)
        assert expression is not None

        if self.peek_token_is(TokenType.SEMICOLON):
            self.next_token()

        stmt = ExpressionStatement(
            token=cur_token,
            expression=expression,
        )

        return stmt

    def parse_expression(self, precedence: int) -> Expression | None:
        assert self.cur_token is not None
        prefix: Callable | None = self.prefix_parse_fns.get(self.cur_token.type)
        if prefix is None:
            self.no_prefix_parse_fn_error(self.cur_token.type)
            return None

        left_expression: Expression | None = prefix()
        assert left_expression is not None

        while not self.peek_token_is(TokenType.SEMICOLON) and precedence < self.peek_precedence():
            assert self.peek_token is not None
            infix: Callable | None = self.infix_parse_fns.get(self.peek_token.type)
            if infix is None:
                return left_expression

            self.next_token()

            left_expression = infix(left_expression)

        return left_expression

    def peek_precedence(self) -> int:
        assert self.peek_token is not None
        return precedences.get(self.peek_token.type, LOWEST)

    def current_precedence(self) -> int:
        assert self.cur_token is not None
        return precedences.get(self.cur_token.type, LOWEST)

    def parse_identifier(self) -> Identifier:
        assert self.cur_token is not None
        return Identifier(
            token=self.cur_token,
            value=self.cur_token.literal,
        )

    def parse_integer_literal(self) -> None | IntegerLiteral:
        assert self.cur_token is not None
        try:

            lit = IntegerLiteral(
                token=self.cur_token,
                value=int(self.cur_token.literal),
            )
        except ValueError:
            msg = f"could not parse {self.cur_token.literal} as integer"
            self.errors_list.append(msg)
            return None

        return lit

    def parse_string_literal(self) -> StringLiteral:
        assert self.cur_token is not None
        return StringLiteral(token=self.cur_token, value=self.cur_token.literal)

    def parse_prefix_expression(self) -> PrefixExpression:
        cur_token: Token | None = self.cur_token
        assert cur_token is not None

        self.next_token()

        right: Expression | None = self.parse_expression(PREFIX)
        assert right is not None

        expression = PrefixExpression(token=cur_token, operator=cur_token.literal, right=right)

        return expression

    def parse_infix_expression(self, left: Expression) -> InfixExpression:
        cur_token: Token | None = self.cur_token
        assert cur_token is not None

        precedence: int = self.current_precedence()
        self.next_token()
        right: Expression | None = self.parse_expression(precedence)
        assert right is not None
        expression = InfixExpression(token=cur_token, operator=cur_token.literal, left=left, right=right)

        return expression

    def parse_boolean(self) -> BooleanLiteral:
        assert self.cur_token is not None
        return BooleanLiteral(token=self.cur_token, value=self.current_token_is(TokenType.TRUE))

    def parse_grouped_expression(self) -> None | Expression:
        self.next_token()

        exp: Expression | None = self.parse_expression(LOWEST)

        if not self.expect_peek(TokenType.RPAREN):
            return None

        return exp

    def parse_if_expression(self) -> None | IfExpression:
        cur_token: Token | None = self.cur_token
        assert cur_token is not None

        if not self.expect_peek(TokenType.LPAREN):
            return None

        self.next_token()
        condition: Expression | None = self.parse_expression(LOWEST)
        assert condition is not None

        if not self.expect_peek(TokenType.RPAREN):
            return None

        if not self.expect_peek(TokenType.LBRACE):
            return None

        consequence: BlockStatement = self.parse_block_statement()

        alternative: BlockStatement | None = None

        if self.peek_token_is(TokenType.ELSE):
            self.next_token()

            if not self.expect_peek(TokenType.LBRACE):
                return None

            alternative = self.parse_block_statement()

        expression = IfExpression(
            token=cur_token,
            condition=condition,
            consequence=consequence,
            alternative=alternative,
        )

        return expression

    def parse_block_statement(self) -> BlockStatement:
        assert self.cur_token is not None
        block = BlockStatement(token=self.cur_token)

        self.next_token()

        while not self.current_token_is(TokenType.RBRACE) and not self.current_token_is(TokenType.EOF):
            stmt: Statement | None = self.parse_statement()
            if stmt is not None:
                block.statements.append(stmt)
            self.next_token()

        return block

    def parse_function_literal(self):
        cur_token: Token | None = self.cur_token
        assert cur_token is not None

        if not self.expect_peek(TokenType.LPAREN):
            return None

        parameters: list[Identifier] | None = self.parse_function_parameters()
        assert parameters is not None

        if not self.expect_peek(TokenType.LBRACE):
            return None

        body: BlockStatement = self.parse_block_statement()

        lit = FunctionLiteral(token=cur_token, parameters=parameters, body=body)

        return lit

    def parse_function_parameters(self) -> list[Identifier] | None:
        identifiers: list[Identifier] = []

        if self.peek_token_is(TokenType.RPAREN):
            self.next_token()
            return identifiers

        self.next_token()

        assert self.cur_token is not None
        ident = Identifier(token=self.cur_token, value=self.cur_token.literal)
        identifiers.append(ident)

        while self.peek_token_is(TokenType.COMMA):
            self.next_token()
            self.next_token()
            assert self.cur_token is not None
            ident = Identifier(token=self.cur_token, value=self.cur_token.literal)
            identifiers.append(ident)

        if not self.expect_peek(TokenType.RPAREN):
            return None

        return identifiers

    def parse_call_expression(self, function: Expression) -> CallExpression:
        arguments: list[Expression] | None = self.parse_expression_list(TokenType.RPAREN)
        assert arguments is not None
        assert self.cur_token is not None
        exp = CallExpression(
            token=self.cur_token,
            function=function,
            arguments=arguments,
        )
        return exp

    def parse_expression_list(self, end: TokenType) -> list[Expression] | None:
        expressions: list[Expression] = []

        if self.peek_token_is(end):
            self.next_token()
            return expressions

        self.next_token()
        exp: Expression | None = self.parse_expression(LOWEST)
        assert exp is not None
        expressions.append(exp)

        while self.peek_token_is(TokenType.COMMA):
            self.next_token()
            self.next_token()
            next_exp: Expression | None = self.parse_expression(LOWEST)
            assert next_exp is not None
            expressions.append(next_exp)

        if not self.expect_peek(end):
            return None

        return expressions

    def parse_array_literal(self) -> ArrayLiteral:
        elements: list[Expression] | None = self.parse_expression_list(TokenType.RBRACKET)
        assert elements is not None
        assert self.cur_token is not None
        array = ArrayLiteral(token=self.cur_token, elements=elements)
        return array

    def parse_index_expression(self, left: Expression) -> None | IndexExpression:
        cur_token: Token | None = self.cur_token
        assert cur_token is not None

        self.next_token()
        index: Expression | None = self.parse_expression(LOWEST)
        assert index is not None

        if not self.expect_peek(TokenType.RBRACKET):
            return None

        exp = IndexExpression(token=cur_token, left=left, index=index)

        return exp

    def parse_hash_literal(self) -> None | HashLiteral:
        assert self.cur_token is not None
        hash = HashLiteral(token=self.cur_token, pairs={})

        while not self.peek_token_is(TokenType.RBRACE):
            self.next_token()
            key: Expression | None = self.parse_expression(LOWEST)
            assert key is not None

            if not self.expect_peek(TokenType.COLON):
                return None

            self.next_token()
            value: Expression | None = self.parse_expression(LOWEST)
            assert value is not None

            hash.pairs[key] = value

            if not self.peek_token_is(TokenType.RBRACE) and not self.expect_peek(TokenType.COMMA):
                return None

        if not self.expect_peek(TokenType.RBRACE):
            return None

        return hash
