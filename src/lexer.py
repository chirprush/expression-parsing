from ltoken import Token, TokenType
from itertools import takewhile

class Lexer:
    def __init__(self, inp):
        self.inp = inp.strip()
        self.index = 0
        self.failed = False

    def startswith(self, *strings):
        return self.inp[self.index:].startswith(strings)

    def next(self):
        whitespace = len(self.inp[self.index:]) - len(self.inp[self.index:].strip())
        self.index += whitespace
        if self.index >= len(self.inp):
            return Token(TokenType.Eof)
        elif self.startswith("(", ")"):
            self.index += 1
            return Token(TokenType.Paren, self.inp[self.index - 1])
        elif self.startswith("=="):
            self.index += 2
            return Token(TokenType.Operator, self.inp[self.index - 2 : self.index])
        elif self.startswith("+", "-", "*", "/", "=", "'"):
            self.index += 1
            return Token(TokenType.Operator, self.inp[self.index - 1])
        word = ''.join(takewhile(lambda c : c == "_" or c.isalnum(), self.inp[self.index:]))
        if word in ["let", "func", "if", "then", "else"]:
            self.index += len(word)
            return Token(TokenType.Keyword, word)
        elif word.isnumeric():
            self.index += len(word)
            return Token(TokenType.Number, word)
        elif word.isidentifier():
            self.index += len(word)
            return Token(TokenType.Identifier, word)
        return Token(TokenType.Error, f"Unexpected character '{self.inp[self.index]}'")

    def collect(self):
        tokens = []
        token = self.next()
        while token.type != TokenType.Eof:
            tokens.append(token)
            if token.type == TokenType.Error:
                self.failed = True
                return token
            token = self.next()
        return tokens
