from node import NodeType
from ltoken import TokenType

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def advance(self):
        self.index += 1
        
    def peek(self):
        if self.index >= len(self.tokens):
            return None
        return self.tokens[self.index]

    def expect(self, _type, text=[]):
        current = self.peek()
        if current is None or current.type != _type or (text and current.text not in text):
            return None
        self.advance()
        return current

    def parse_number(self):
        if (current := self.expect(TokenType.Number)) is not None:
            return NodeType.ValueNode(int(current.text))
        return NodeType.ErrorNode("Expected number")

    def parse_variable(self):
        if (current := self.expect(TokenType.Identifier)) is not None:
            return NodeType.VariableNode(current.text)
        return NodeType.ErrorNode("Expected variable")

    def parse_paren(self):
        save_index = self.index
        if (_ := self.expect(TokenType.Paren, ["("])) is None:
            return NodeType.ErrorNode("Expected parenthesized expression")
        result = self.parse_expr()
        if (_ := self.expect(TokenType.Paren, [")"])) is None:
            self.index = save_index
            return NodeType.ErrorNode("Expected closing parentheses")
        return result

    def parse_func(self):
        save_index = self.index
        if (_ := self.expect(TokenType.Keyword, ["func"])) is None:
            return NodeType.ErrorNode("Expected keyword 'func'")
        if (ident := self.expect(TokenType.Identifier)) is None:
            self.index = save_index
            return NodeType.ErrorNode("Expected identifier after 'func' keyword")
        if (_ := self.expect(TokenType.Operator, ["'"])) is None:
            self.index = save_index
            return NodeType.ErrorNode("Expected quote after function arguments")
        expr = self.parse_expr()
        if expr.is_err():
            self.index = save_index
            return expr
        return NodeType.FuncNode(ident.text, expr)

    def parse_if(self):
        save_index = self.index
        if (_ := self.expect(TokenType.Keyword, "if")) is None:
            return NodeType.ErrorNode("Expected keyword 'if'")
        case = self.parse_expr()
        if case.is_err():
            self.index = save_index
            return case
        if (_ := self.expect(TokenType.Keyword, "then")) is None:
            return NodeType.ErrorNode("Expected keyword 'then' in if statement")
        left = self.parse_expr()
        if left.is_err():
            self.index = save_index
            return left
        if (_ := self.expect(TokenType.Keyword, "else")) is None:
            return NodeType.ErrorNode("Expected keyword 'else' in if statement")
        right = self.parse_expr()
        if right.is_err():
            self.index = save_index
            return right
        return NodeType.IfNode(case, left, right)

    def parse_call(self):
        save_index = self.index
        func = self.parse_variable() or self.parse_paren()
        first = True
        if func.is_err():
            self.index = save_index
            return NodeType.ErrorNode("Invalid function call")
        while True:
            if (_ := self.expect(TokenType.Paren, "(")) is None:
                if first:
                    self.index = save_index
                    return NodeType.ErrorNode("Expected opening parentheses in function call")
                else:
                    break
            arg = self.parse_expr()
            if arg.is_err():
                self.index = save_index
                return arg
            if (_ := self.expect(TokenType.Paren, ")")) is None:
                self.index = save_index
                return NodeType.ErrorNode("Expected closing parentheses in function call")
            if first:
                result = NodeType.CallNode(func, arg)
            else:
                result = NodeType.CallNode(result, arg)
            first = False
        return result

    def parse_expr(self):
        save_index = self.index
        result = self.parse_level1()
        if result.is_err():
            self.index = save_index
            return result
        while True:
            if (op := self.expect(TokenType.Operator, ["="])) is None:
                break
            right = self.parse_level1()
            if right.is_err():
                self.index = save_index
                return right
            result = NodeType.OperationNode(result, op.text, right)
        return result

    def parse_level1(self):
        save_index = self.index
        result = self.parse_level2()
        if result.is_err():
            self.index = save_index
            return result
        while True:
            if (op := self.expect(TokenType.Operator, ["=="])) is None:
                break
            right = self.parse_level2()
            if right.is_err():
                self.index = save_index
                return right
            result = NodeType.OperationNode(result, op.text, right)
        return result

    def parse_level2(self):
        save_index = self.index
        result = self.parse_level3()
        if result.is_err():
            self.index = save_index
            return result
        while True:
            if (op := self.expect(TokenType.Operator, ["+", "-"])) is None:
                break
            right = self.parse_level3()
            if right.is_err():
                self.index = save_index
                return right
            result = NodeType.OperationNode(result, op.text, right)
        return result

    def parse_level3(self):
        save_index = self.index
        result = self.parse_factor()
        if result.is_err():
            self.index = save_index
            return result
        while True:
            if (op := self.expect(TokenType.Operator, ["*", "/"])) is None:
                break
            right = self.parse_factor()
            if right.is_err():
                self.index = save_index
                return right
            result = NodeType.OperationNode(result, op.text, right)
        return result

    def parse_factor(self):
        current = self.peek()
        if current is None:
            return NodeType.ErrorNode("Expected expression")
        elif current.type == TokenType.Paren and current.text == "(":
            return self.parse_call() or self.parse_paren()
        elif current.type == TokenType.Number:
            return self.parse_number()
        elif current.type == TokenType.Identifier:
            return self.parse_call() or self.parse_variable()
        elif current.type == TokenType.Keyword and current.text == "func":
            return self.parse_func()
        elif current.type == TokenType.Keyword and current.text == "if":
            return self.parse_if()
        return NodeType.ErrorNode("Expected expression")

    def parse_bind(self):
        save_index = self.index
        if (_ := self.expect(TokenType.Keyword, ["let"])) is None:
            return NodeType.ErrorNode("Expected keyword 'let'")
        if (ident := self.expect(TokenType.Identifier)) is None:
            self.index = save_index
            return NodeType.ErrorNode("Expected identifier after keyword 'let'")
        if (_ := self.expect(TokenType.Operator, "=")) is None:
            self.index = save_index
            return NodeType.ErrorNode("Expected '=' operator in binding statement")
        expr = self.parse_expr()
        return NodeType.BindNode(ident.text, expr)

    def parse_all(self):
        return self.parse_bind() or self.parse_expr()

    def __repr__(self):
        return f"Parser({self.tokens[self.index:]})"
