class TokenType:
    Error = 0
    Eof = 1
    Paren = 2
    Operator = 3
    Number = 4
    Identifier = 5
    Keyword = 6

type_to_string = {
    TokenType.Error      : "Error",
    TokenType.Eof        : "Eof",
    TokenType.Paren      : "Paren",
    TokenType.Operator   : "Operator",
    TokenType.Number     : "Number",
    TokenType.Identifier : "Identifier",
    TokenType.Keyword    : "Keyword",
}

class Token:
    def __init__(self, _type, text=""):
        self.type = _type
        self.text = text

    def __repr__(self):
        return f"Token({type_to_string[self.type]}, \"{self.text}\")"
