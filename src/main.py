from lexer import Lexer
from parser import Parser

env = {}

# TODO:
#   - Fix parsing error in which you cannot call the output of a function
#   - Add if else expression

while True:
    try:
        inp = input("> ")
    except EOFError:
        print()
        break
    except KeyboardInterrupt:
        print()
        continue
    lexer = Lexer(inp)
    output = lexer.collect()
    if lexer.failed:
        print(output.text)
        continue
    elif len(output) == 0:
        continue
    tokens = output
    parser = Parser(tokens)
    node = parser.parse_all()
    try:
        (env, result) = node.eval(env)
    except RecursionError:
        print("Recursion limit exceeded")
        continue
    if result.is_err():
        print(result.message)
    else:
        print(result)
