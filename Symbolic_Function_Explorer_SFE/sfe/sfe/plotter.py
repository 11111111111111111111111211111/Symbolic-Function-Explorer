import numpy as np
import sympy as sp
import plotly.graph_objects as go
from .parser import x

def build_plot(result, xmin, xmax, show_derivative=True, show_roots=True, show_critical=True):
    fig = go.Figure()
    xx = np.linspace(xmin, xmax, 1000)
    def sample(expr):
        fn = sp.lambdify(x, expr, modules=["numpy"])
        with np.errstate(all="ignore"):
            yy = np.asarray(fn(xx), dtype=float)
        if yy.ndim == 0: yy = np.full_like(xx, float(yy))
        yy[~np.isfinite(yy)] = np.nan
        yy[np.abs(yy) > 1e6] = np.nan
        return yy
    fig.add_trace(go.Scatter(x=xx, y=sample(result["expression"]), name="f(x)", mode="lines"))
    if show_derivative:
        fig.add_trace(go.Scatter(x=xx, y=sample(result["derivative"]), name="f′(x)", mode="lines", line={"dash":"dash"}))
    if show_roots and result["roots"]:
        rx, ry = [], []
        for root in result["roots"]:
            try:
                rv = float(sp.N(root))
                if xmin <= rv <= xmax: rx.append(rv); ry.append(0)
            except Exception: pass
        if rx: fig.add_trace(go.Scatter(x=rx, y=ry, name="Roots", mode="markers", marker={"size":10,"symbol":"x"}))
    if show_critical and result["critical_points"]:
        cx, cy = [], []
        for p in result["critical_points"]:
            try:
                xv, yv = float(sp.N(sp.sympify(p["x"]))), float(sp.N(sp.sympify(p["f(x)"])))
                if xmin <= xv <= xmax and np.isfinite(yv): cx.append(xv); cy.append(yv)
            except Exception: pass
        if cx: fig.add_trace(go.Scatter(x=cx, y=cy, name="Critical points", mode="markers", marker={"size":9,"symbol":"diamond"}))
    fig.update_layout(title="Interactive function explorer", xaxis_title="x", yaxis_title="y",
                      hovermode="x unified", legend={"orientation":"h"}, margin={"l":20,"r":20,"t":50,"b":20})
    return fig
