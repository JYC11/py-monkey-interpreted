import sys

from src.repl.repl import monkey_repl

if __name__ == "__main__":
    monkey_repl(sys.stdin, sys.stdout)
