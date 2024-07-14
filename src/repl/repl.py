from typing import TextIO

from src.evaluator.evaluator import evaluate
from src.lexer.lexer import Lexer
from src.object.environment import new_environment
from src.parser.parser import Parser

PROMPT = ">> "


def monkey_repl(in_stream: TextIO, out_stream: TextIO):
    env = new_environment()
    out_stream.write("py monkey v0.0.1\n")
    while True:
        out_stream.write(PROMPT)
        out_stream.flush()
        line = in_stream.readline()
        if not line:
            return

        lexer = Lexer(line)
        parser = Parser(lexer)

        program = parser.parse_program()
        if len(parser.get_errors()) != 0:
            print_parser_errors(out_stream, parser.get_errors())
            continue

        evaluated = evaluate(program, env)
        if evaluated is not None:
            out_stream.write(evaluated.inspect())
            out_stream.write("\n")
            out_stream.flush()


MONKEY_FACE = (
    """            __,__
   .--.  .-"     "-.  .--.
  / .. \\/  .-. .-.  \\/ .. \\
 | |  '|  /   Y   \\  |'  | |
 | \\   \\  \\ 0 | 0 /  /   / |
  \\ '- ,\\.-"""
    """"-./, -' /
   ''-' /_   ^ ^   _\\ '-''
       |  \\._   _./  |
       \\   \\ '~' /   /
        '._ '-=-' _.'
           '-----'
"""
)


def print_parser_errors(out_stream: TextIO, errors: TextIO):
    out_stream.write(MONKEY_FACE)
    out_stream.write("Woops! We ran into some monkey business here!\n")
    out_stream.write(" parser errors:\n")
    for msg in errors:
        out_stream.write("\t" + msg + "\n")
    out_stream.flush()
