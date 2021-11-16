class BaseNode:
    def is_err(self):
        return isinstance(self, NodeType.ErrorNode)

    def is_var(self):
        return isinstance(self, NodeType.VariableNode)

    def is_func(self):
        return isinstance(self, NodeType.FuncNode)

    def is_val(self):
        return isinstance(self, NodeType.ValueNode)

    def __bool__(self):
        return not self.is_err()

class NodeType:
    class ValueNode(BaseNode):
        def __init__(self, value):
            self.value = value

        def eval(self, env):
            return (env, self)

        def __repr__(self):
            return str(self.value)

    class VariableNode(BaseNode):
        def __init__(self, name):
            self.name = name

        def eval(self, env):
            if self.name in env:
                return (env, env[self.name])
            return (env, NodeType.ErrorNode(f"Variable named '{self.name}' does not exist"))

    class FuncNode(BaseNode):
        def __init__(self, arg, expr):
            self.arg = arg
            self.expr = expr

        def eval(self, env):
            return (env, self)

        def __repr__(self):
            return f"[function of '{self.arg}']"

    class CallNode(BaseNode):
        def __init__(self, func, arg):
            self.func = func
            self.arg = arg

        def eval(self, env):
            (env, func) = self.func.eval(env)
            if func.is_err():
                return (env, func)
            elif not func.is_func():
                return (env, NodeType.ErrorNode("Cannot call a non-function value"))
            (env, arg) = self.arg.eval(env)
            save_var = env.get(func.arg, None)
            (env, result) = func.expr.eval({**env, func.arg : arg})
            if save_var is None:
                del env[func.arg]
                return (env, result)
            env[func.arg] = save_var
            return (env, result)

    class OperationNode(BaseNode):
        def __init__(self, left, op, right):
            self.left = left
            self.op = op
            self.right = right

        def eval(self, env):
            if self.left.is_var() and self.op == "=":
                (env, right) = self.right.eval(env)
                if right.is_err():
                    return (env, right)
                if self.left.name in env:
                    env[self.left.name] = right
                    return (env, right)
                else:
                    return (env, NodeType.ErrorNode(f"Variable '{self.left.name}' has not been declared"))
            elif self.op == "=":
                return (env, NodeType.ErrorNode(f"Cannot assign to a literal value"))
            (env, left) = self.left.eval(env)
            if left.is_err():
                return (env, left)
            (env, right) = self.right.eval(env)
            if right.is_err():
                return (env, right)
            if self.op == "+":
                return (env, NodeType.ValueNode(left.value + right.value))
            elif self.op == "-":
                return (env, NodeType.ValueNode(left.value - right.value))
            elif self.op == "*":
                return (env, NodeType.ValueNode(left.value * right.value))
            elif self.op == "/":
                if right.value == 0:
                    return (env, NodeType.ErrorNode("Cannot divide by zero"))
                return (env, NodeType.ValueNode(int(left.value / right.value)))
            elif self.op == "==":
                return (env, NodeType.ValueNode(int(right.value == left.value))) 
            raise ValueError(f"Operator '{self.op}' is not implemented")

    class IfNode(BaseNode):
        def __init__(self, case, left, right):
            self.case = case
            self.left = left
            self.right = right

        def eval(self, env):
            (env, case) = self.case.eval(env)
            if case.is_err():
                return (env, case)
            if case.is_val() and case.value == 0:
                return self.right.eval(env)
            return self.left.eval(env)

    class BindNode(BaseNode):
        def __init__(self, name, expr):
            self.name = name
            self.expr = expr

        def eval(self, env):
            if self.name in env:
                return (env, NodeType.ErrorNode(f"Variable '{self.name}' already exists"))
            (env, result) = self.expr.eval(env)
            if result.is_err():
                return (env, result)
            env[self.name] = result
            return (env, result)

    class ErrorNode(BaseNode):
        def __init__(self, message):
            self.message = message

        def eval(self, env):
            return (env, self)

        def __repr__(self):
            return self.message
