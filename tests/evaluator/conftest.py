from src.ast.ast import Program
from src.evaluator.evaluator import evaluate
from src.lexer.lexer import Lexer
from src.object.environment import Environment, new_environment
from src.object.object import Boolean, Integer, Null, Object
from src.parser.parser import Parser


def eval_factory_for_test(input: str) -> Object:
    lexer = Lexer(input=input)
    parser = Parser(lexer=lexer)
    assert len(parser.get_errors()) == 0
    program: Program = parser.parse_program()
    env: Environment = new_environment()
    return evaluate(node=program, env=env)


def check_integer_object(obj: Object, expected: int):
    assert isinstance(obj, Integer)
    assert obj.value == expected


def check_boolean_object(obj: Object, expected: bool):
    assert isinstance(obj, Boolean)
    assert obj.value == expected


def check_null_object(obj: Object):
    assert isinstance(obj, Null)
