from abc import ABC, abstractmethod
from typing import Optional

from src.tokens.tokens import Token


class Node(ABC):
    @abstractmethod
    def token_literal(self) -> str:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass


class Statement(Node):
    @abstractmethod
    def statement_node(self):
        pass


class Expression(Node):
    @abstractmethod
    def expression_node(self):
        pass


class Program(Node):
    def __init__(self):
        self.statements: list[Statement] = []

    def token_literal(self) -> str:
        if len(self.statements) > 0:
            return self.statements[0].token_literal()
        else:
            return ""

    def __str__(self) -> str:
        out = []
        for statement in self.statements:
            out.append(str(statement))
        return "".join(out)


class Identifier(Expression):
    def __init__(self, token: Token, value: str):
        self.token = token
        self.value = value

    def expression_node(self):
        pass

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return self.value


class IntegerLiteral(Expression):
    def __init__(self, token: Token, value: int):
        self.token = token
        self.value = value

    def expression_node(self):
        pass

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return str(self.value)


class PrefixExpression(Expression):
    def __init__(self, token: Token, operator: str, right: Expression):
        self.token = token
        self.operator = operator
        self.right = right

    def expression_node(self):
        pass

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return f"({self.operator}{self.right})"


class InfixExpression(Expression):
    def __init__(self, token: Token, left: Expression, operator: str, right: Expression):
        self.token = token
        self.left = left
        self.operator = operator
        self.right = right

    def expression_node(self):
        pass

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return f"({self.left} {self.operator} {self.right})"


class BooleanLiteral(Expression):
    def __init__(self, token: Token, value: bool):
        self.token = token
        self.value = value

    def expression_node(self):
        pass

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return str(self.value).lower()


class IfExpression(Expression):
    def __init__(
        self,
        token: Token,
        condition: Expression,
        consequence: "BlockStatement",
        alternative: Optional["BlockStatement"],
    ):
        self.token = token
        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative

    def expression_node(self):
        pass

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        out = []
        out.append("if")
        out.append(str(self.condition))
        out.append(" ")
        out.append(str(self.consequence))
        if self.alternative is not None:
            out.append("else ")
            out.append(str(self.alternative))
        return "".join(out)


class FunctionLiteral(Expression):
    def __init__(self, token: Token, parameters: list[Identifier], body: "BlockStatement"):
        self.token = token
        self.parameters = parameters
        self.body = body

    def expression_node(self):
        pass

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        params = [str(param) for param in self.parameters]
        return f"{self.token_literal()}({', '.join(params)}) {str(self.body)}"


class CallExpression(Expression):
    def __init__(self, token: Token, function: Expression, arguments: list[Expression]):
        self.token = token
        self.function = function
        self.arguments = arguments

    def expression_node(self):
        pass

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        args = [str(arg) for arg in self.arguments]
        return f"{str(self.function)}({', '.join(args)})"


class StringLiteral(Expression):
    def __init__(self, token: Token, value: str):
        self.token = token
        self.value = value

    def expression_node(self):
        pass

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return self.token.literal


class ArrayLiteral(Expression):
    def __init__(self, token: Token, elements: list[Expression]):
        self.token = token
        self.elements = elements

    def expression_node(self):
        pass

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        elements = [str(element) for element in self.elements]
        return f"[{', '.join(elements)}]"


class IndexExpression(Expression):
    def __init__(self, token: Token, left: Expression, index: Expression):
        self.token = token
        self.left = left
        self.index = index

    def expression_node(self):
        pass

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return f"({str(self.left)}[{str(self.index)}])"


class HashLiteral(Expression):
    def __init__(self, token: Token, pairs: dict[Expression, Expression]):
        self.token = token
        self.pairs = pairs

    def expression_node(self):
        pass

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        pairs = [f"{str(key)}:{str(value)}" for key, value in self.pairs.items()]
        return f"{{{', '.join(pairs)}}}"


class LetStatement(Statement):
    def __init__(self, token: Token, name: Identifier, value: Expression):
        self.token = token
        self.name = name
        self.value = value

    def statement_node(self):
        pass

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        out = []
        out.append(self.token_literal() + " ")
        out.append(str(self.name))
        out.append(" = ")
        if self.value:
            out.append(str(self.value))
        out.append(";")
        return "".join(out)


class ReturnStatement(Statement):
    def __init__(self, token: Token, return_value: Expression):
        self.token = token
        self.return_value = return_value

    def statement_node(self):
        pass

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        out = []
        out.append(self.token_literal() + " ")
        if self.return_value:
            out.append(str(self.return_value))
        out.append(";")
        return "".join(out)


class ExpressionStatement(Statement):
    def __init__(self, token: Token, expression: Expression):
        self.token = token
        self.expression = expression

    def statement_node(self):
        pass

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        if self.expression:
            return str(self.expression)
        return ""


class BlockStatement(Statement):
    def __init__(self, token: Token):
        self.token = token
        self.statements: list[Statement] = []

    def statement_node(self):
        pass

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        out = []
        for statement in self.statements:
            out.append(str(statement))
        return "".join(out)
