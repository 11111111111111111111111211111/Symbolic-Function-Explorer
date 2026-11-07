import sympy as sp
from .parser import parse_expression, x, a, ExpressionError

class AnalysisError(ValueError):
    pass

def _safe_string(value):
    try: return str(value)
    except Exception: return "Unavailable"

def _real_roots(expr):
    try:
        solution = sp.solveset(expr, x, domain=sp.S.Reals)
        if solution is sp.S.EmptySet: return [], "None"
        if isinstance(solution, sp.FiniteSet):
            vals = sorted(list(solution), key=lambda v: float(sp.N(v)) if v.is_real else 0)
            return vals, ", ".join(map(str, vals))
        return [], _safe_string(solution)
    except Exception:
        try:
            poly = sp.Poly(expr, x)
            vals = sp.nroots(poly)
            real = [sp.re(v) for v in vals if abs(float(sp.im(v))) < 1e-9]
            return real, ", ".join(map(str, real)) if real else "No real roots found"
        except Exception:
            return [], "Could not determine symbolically"

def _domain(expr):
    try: return sp.calculus.util.continuous_domain(expr, x, sp.S.Reals)
    except Exception: return "Could not determine exactly"

def _singularities(expr):
    try:
        s = sp.singularities(expr, x)
        if s is sp.S.EmptySet: return []
        if isinstance(s, sp.FiniteSet): return sorted(list(s), key=lambda v: float(sp.N(v)))
        return [s]
    except Exception: return []

def _limits(expr, singular):
    out = []
    for label, point, direction in [
        ("x → +∞", sp.oo, "+"), ("x → −∞", -sp.oo, "-")]:
        try: val = sp.limit(expr, x, point)
        except Exception: val = "Undetermined"
        out.append({"Location": label, "Limit": _safe_string(val)})
    for point in singular[:8]:
        for direction in ["-", "+"]:
            try: val = sp.limit(expr, x, point, dir=direction)
            except Exception: val = "Undetermined"
            out.append({"Location": f"x → {point} ({direction})", "Limit": _safe_string(val)})
    return out

def _critical(expr, derivative):
    points = []
    try: sols = sp.solveset(derivative, x, domain=sp.S.Reals)
    except Exception: return points
    if not isinstance(sols, sp.FiniteSet): return points
    second = sp.diff(expr, x, 2)
    for point in sols:
        try:
            if point.is_real is False: continue
            test = sp.simplify(second.subs(x, point))
            if test.is_positive: kind = "Local minimum"
            elif test.is_negative: kind = "Local maximum"
            elif test == 0 or test.is_zero: kind = "Inconclusive (possible inflection)"
            else: kind = "Inconclusive"
            yval = sp.simplify(expr.subs(x, point))
            points.append({"x": _safe_string(point), "f(x)": _safe_string(yval), "classification": kind})
        except Exception: continue
    return points[:30]

def _parity(expr):
    try:
        even = sp.simplify(expr.subs(x, -x) - expr) == 0
        odd = sp.simplify(expr.subs(x, -x) + expr) == 0
        if even: return "Even"
        if odd: return "Odd"
    except Exception: pass
    return "Neither / undetermined"

def _derivative_explanation(expr, derivative):
    steps = []
    if expr.is_Add:
        steps.append("Apply the sum/difference rule: differentiate each term separately.")
    if expr.is_Mul:
        steps.append("Apply the product rule to the multiplicative factors.")
    if expr.is_Pow and expr.exp.is_number:
        steps.append("Apply the power rule: d(x^n)/dx = n·x^(n−1), with the chain rule if needed.")
    if expr.func in (sp.sin, sp.cos, sp.tan, sp.exp, sp.log):
        steps.append(f"Apply the standard derivative rule for {expr.func.__name__}.")
    if expr.has(sp.Function):
        steps.append("Use the chain rule for nested functions.")
    if not steps:
        steps.append("Differentiate the expression using SymPy's symbolic differentiation engine.")
    steps.append(f"Symbolic result: f'(x) = {sp.sstr(derivative)}")
    return steps

def analyze_function(source, parameter_value=None):
    try:
        expr = parse_expression(source)
        if parameter_value is not None:
            expr = expr.subs(a, sp.Float(parameter_value))
        expr = sp.simplify(expr)
        derivative = sp.simplify(sp.diff(expr, x))
        try: integral = sp.integrate(expr, x)
        except Exception: integral = sp.Integral(expr, x)
        roots, roots_display = _real_roots(expr)
        domain = _domain(expr)
        singular = _singularities(expr)
        critical = _critical(expr, derivative)
        parity = _parity(expr)
        limits = _limits(expr, singular)
        explanations = [
            {"title": "Derivative", "steps": "\n\n".join(_derivative_explanation(expr, derivative)),
             "summary": "The derivative describes the instantaneous rate of change of the function."},
            {"title": "Integral", "steps": f"Find an antiderivative F such that F'(x) = f(x).\n\nResult: {sp.sstr(integral)}",
             "summary": "The indefinite integral represents a family of antiderivatives, differing by a constant."},
            {"title": "Roots", "steps": f"Solve f(x) = 0 over the real numbers.\n\nResult: {roots_display}",
             "summary": "Roots are input values where the graph intersects the x-axis."},
            {"title": "Domain", "steps": f"Determine where the expression is real-valued and continuous.\n\nResult: {domain}",
             "summary": "The domain contains all real input values for which the expression is defined."},
            {"title": "Critical points", "steps": "Solve f'(x) = 0, then use the second-derivative test where possible.",
             "summary": "Critical points are candidates for local extrema; an inconclusive test needs further analysis."},
        ]
        return {"source": source, "expression": expr, "derivative": derivative, "integral": integral,
                "roots": roots, "roots_display": roots_display, "domain": _safe_string(domain),
                "singular_points": ", ".join(map(str, singular)) if singular else "None detected",
                "critical_points": critical, "parity": parity, "limits": limits,
                "explanations": explanations}
    except ExpressionError as exc:
        raise AnalysisError(str(exc)) from exc
    except Exception as exc:
        raise AnalysisError("Unable to analyze this expression. Try a simpler function.") from exc
