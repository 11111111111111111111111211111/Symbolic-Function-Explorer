"""A small whitelist-based expression parser. No eval/exec or arbitrary names."""
import ast
import sympy as sp

x, a = sp.symbols("x a", real=True)
FUNCTIONS = {
    "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
    "asin": sp.asin, "acos": sp.acos, "atan": sp.atan,
    "sinh": sp.sinh, "cosh": sp.cosh, "tanh": sp.tanh,
    "exp": sp.exp, "log": sp.log, "sqrt": sp.sqrt,
    "Abs": sp.Abs, "abs": sp.Abs,
}
CONSTANTS = {"pi": sp.pi, "E": sp.E, "e": sp.E}
MAX_LENGTH = 250
MAX_NODES = 100

class ExpressionError(ValueError):
    pass

def parse_expression(source: str):
    if not isinstance(source, str) or not source.strip():
        raise ExpressionError("Please enter a mathematical expression.")
    if len(source) > MAX_LENGTH:
        raise ExpressionError(f"Input is too long (maximum {MAX_LENGTH} characters).")
    source = source.replace("^", "**").replace("π", "pi")
    try:
        tree = ast.parse(source, mode="eval")
    except SyntaxError as exc:
        raise ExpressionError("Invalid syntax. Example: sin(x)*x or x^2 - 4.") from exc
    nodes = list(ast.walk(tree))
    if len(nodes) > MAX_NODES:
        raise ExpressionError("Expression is too complex.")
    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return sp.Integer(node.value) if isinstance(node.value, int) else sp.Float(node.value)
        if isinstance(node, ast.Name):
            if node.id == "x": return x
            if node.id == "a": return a
            if node.id in CONSTANTS: return CONSTANTS[node.id]
            raise ExpressionError(f"Unknown symbol '{node.id}'. Only x, a, pi and e are allowed.")
        if isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            ops = {ast.Add: lambda: left + right, ast.Sub: lambda: left-right,
                   ast.Mult: lambda: left*right, ast.Div: lambda: left/right,
                   ast.Pow: lambda: left**right}
            for typ, fn in ops.items():
                if isinstance(node.op, typ): return fn()
            raise ExpressionError("Unsupported operator.")
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = visit(node.operand)
            return value if isinstance(node.op, ast.UAdd) else -value
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            fn = FUNCTIONS.get(node.func.id)
            if fn is None or node.keywords or len(node.args) != 1:
                raise ExpressionError("Unsupported function. Use a supported one-argument function.")
            return fn(visit(node.args[0]))
        raise ExpressionError("Unsupported syntax. Use arithmetic and supported one-variable functions.")
    expr = visit(tree)
    if expr.has(sp.Derivative) or expr.has(sp.Integral):
        raise ExpressionError("Derivatives and integrals are not accepted as input.")
    return sp.sympify(expr)
