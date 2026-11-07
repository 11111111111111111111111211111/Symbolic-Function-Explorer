import streamlit as st
import sympy as sp
import pandas as pd
from sfe.analyzer import analyze_function, AnalysisError
from sfe.plotter import build_plot
from sfe.exporter import to_markdown, to_pdf

st.set_page_config(page_title="Symbolic Function Explorer", page_icon="∑", layout="wide")
st.title("∑ Symbolic Function Explorer")
st.caption("Explainable single-variable symbolic mathematics — powered by SymPy")

with st.sidebar:
    st.header("Function")
    expression = st.text_input("Enter f(x)", value="sin(x)*x", help="Use x, optional parameter a, ^ or ** for powers.")
    st.markdown("**Supported:** arithmetic, sin/cos/tan, exp, log, sqrt, abs and constants pi/e.")
    st.markdown("**Examples:** `x^2 - 4`, `exp(-x^2)`, `log(x)/x`")
    st.divider()
    st.subheader("Plot range")
    xmin, xmax = st.slider("x range", -30.0, 30.0, (-10.0, 10.0), 0.5)
    st.subheader("Overlays")
    show_derivative = st.checkbox("Derivative", True)
    show_roots = st.checkbox("Real roots", True)
    show_critical = st.checkbox("Critical points", True)

    use_parameter = st.checkbox("Enable parameter a")
    parameter = st.slider("a", -5.0, 5.0, 1.0, 0.1, disabled=not use_parameter)

parameter_value = parameter if use_parameter else None

try:
    result = analyze_function(expression, parameter_value=parameter_value)
except AnalysisError as exc:
    st.error(str(exc))
    st.info("Check the syntax and use only the supported single-variable functions.")
    st.stop()
except Exception:
    st.error("The expression could not be analyzed safely. Try a simpler expression.")
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("Variable", "x")
c2.metric("Expression", str(result["expression"]))
c3.metric("Parity", result["parity"])

tabs = st.tabs(["Overview", "Plot", "Details", "Export"])
with tabs[0]:
    left, right = st.columns(2)
    with left:
        st.subheader("Symbolic results")
        st.latex("f(x) = " + sp.latex(result["expression"]))
        st.latex("f'(x) = " + sp.latex(result["derivative"]))
        st.latex(r"\int f(x)\,dx = " + sp.latex(result["integral"]))
        st.write("**Real roots:**", result["roots_display"])
        st.write("**Domain:**", result["domain"])
    with right:
        st.subheader("Critical points")
        if result["critical_points"]:
            st.dataframe(pd.DataFrame(result["critical_points"]), use_container_width=True, hide_index=True)
        else:
            st.write("No real critical points found (or none could be represented exactly).")
        st.subheader("Limits")
        st.dataframe(pd.DataFrame(result["limits"]), use_container_width=True, hide_index=True)
    st.subheader("Explanation")
    for item in result["explanations"]:
        with st.expander(item["title"], expanded=item["title"] == "Derivative"):
            st.write(item["steps"])
            st.caption(item["summary"])

with tabs[1]:
    st.plotly_chart(build_plot(result, xmin, xmax, show_derivative, show_roots, show_critical),
                    use_container_width=True, theme="streamlit")
with tabs[2]:
    st.subheader("Analysis table")
    rows = [
        ("Simplified", str(result["expression"])),
        ("First derivative", str(result["derivative"])),
        ("Indefinite integral", str(result["integral"])),
        ("Domain", result["domain"]),
        ("Parity", result["parity"]),
        ("Real roots", result["roots_display"]),
        ("Singular points", result["singular_points"]),
    ]
    st.dataframe(pd.DataFrame(rows, columns=["Property", "Result"]), use_container_width=True, hide_index=True)
    st.subheader("Method notes")
    st.write("Domain and roots are best-effort symbolic results. Some transcendental equations cannot be solved in closed form.")
    st.write("Critical-point classification uses the second-derivative test where possible; inconclusive cases are labelled accordingly.")

with tabs[3]:
    md = to_markdown(result)
    st.download_button("Download Markdown report", md, file_name="sfe-analysis.md", mime="text/markdown")
    try:
        pdf = to_pdf(result)
        st.download_button("Download PDF report", pdf, file_name="sfe-analysis.pdf", mime="application/pdf")
    except ImportError:
        st.warning("Install reportlab to enable PDF export.")
    st.code(md, language="markdown")

st.caption("SFE is an educational research prototype. Always verify results for high-stakes mathematical work.")
