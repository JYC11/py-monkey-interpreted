from src.tokens.tokens import Token, TokenType, lookup_ident


class Lexer:
    def __init__(self, input: str):
        self.input = input
        self.position = 0
        self.read_position = 0
        self.ch = ""
        self.read_char()

    def read_char(self):
        if self.read_position >= len(self.input):
            self.ch = "\0"
        else:
            self.ch = self.input[self.read_position]
        self.position = self.read_position
        self.read_position += 1

    def peek_char(self) -> str:
        if self.read_position >= len(self.input):
            return "\0"
        else:
            return self.input[self.read_position]

    def next_token(self) -> Token:
        self.skip_whitespace()
        tok: Token

        if self.ch == "=":
            if self.peek_char() == "=":
                ch = self.ch
                self.read_char()
                literal = ch + self.ch
                tok = Token(TokenType.EQ, literal)
            else:
                tok = self.new_token(TokenType.ASSIGN, self.ch)
        elif self.ch == "+":
            tok = self.new_token(TokenType.PLUS, self.ch)
        elif self.ch == "-":
            tok = self.new_token(TokenType.MINUS, self.ch)
        elif self.ch == "!":
            if self.peek_char() == "=":
                ch = self.ch
                self.read_char()
                literal = ch + self.ch
                tok = Token(TokenType.NOT_EQ, literal)
            else:
                tok = self.new_token(TokenType.BANG, self.ch)
        elif self.ch == "/":
            tok = self.new_token(TokenType.SLASH, self.ch)
        elif self.ch == "*":
            tok = self.new_token(TokenType.ASTERISK, self.ch)
        elif self.ch == "<":
            tok = self.new_token(TokenType.LT, self.ch)
        elif self.ch == ">":
            tok = self.new_token(TokenType.GT, self.ch)
        elif self.ch == ";":
            tok = self.new_token(TokenType.SEMICOLON, self.ch)
        elif self.ch == ":":
            tok = self.new_token(TokenType.COLON, self.ch)
        elif self.ch == ",":
            tok = self.new_token(TokenType.COMMA, self.ch)
        elif self.ch == "{":
            tok = self.new_token(TokenType.LBRACE, self.ch)
        elif self.ch == "}":
            tok = self.new_token(TokenType.RBRACE, self.ch)
        elif self.ch == "(":
            tok = self.new_token(TokenType.LPAREN, self.ch)
        elif self.ch == ")":
            tok = self.new_token(TokenType.RPAREN, self.ch)
        elif self.ch == '"':
            tok = Token(TokenType.STRING, self.read_string())
        elif self.ch == "[":
            tok = self.new_token(TokenType.LBRACKET, self.ch)
        elif self.ch == "]":
            tok = self.new_token(TokenType.RBRACKET, self.ch)
        elif self.ch == "\0":
            tok = Token(TokenType.EOF, "")
        else:
            if self.is_letter(self.ch):
                literal = self.read_identifier()
                tok_type = lookup_ident(literal)
                return Token(tok_type, literal)
            elif self.is_digit(self.ch):
                return Token(TokenType.INT, self.read_number())
            else:
                tok = self.new_token(TokenType.ILLEGAL, self.ch)

        self.read_char()
        return tok

    def skip_whitespace(self):
        while self.ch in {" ", "\t", "\n", "\r"}:
            self.read_char()

    def read_identifier(self) -> str:
        start_position = self.position
        while self.is_letter(self.ch):
            self.read_char()
        return self.input[start_position : self.position]

    def read_number(self) -> str:
        start_position = self.position
        while self.is_digit(self.ch):
            self.read_char()
        return self.input[start_position : self.position]

    def read_string(self) -> str:
        start_position = self.position + 1
        while True:
            self.read_char()
            if self.ch == '"' or self.ch == "\0":
                break
        return self.input[start_position : self.position]

    def is_letter(self, ch: str) -> bool:
        return ch.isalpha() or ch == "_"

    def is_digit(self, ch: str) -> bool:
        return ch.isnumeric()

    def new_token(self, token_type: TokenType, ch: str) -> Token:
        return Token(token_type, ch)
