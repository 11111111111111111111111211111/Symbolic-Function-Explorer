# Symbolic Function Explorer (SFE)

SFE is an open-source, single-variable symbolic mathematics explorer. It combines SymPy analysis, interactive Plotly visualization, and deterministic rule-based explanations in a Streamlit application.

## Features

- Simplification, first derivative, indefinite integral, real roots, best-effort real domain, limits and singularities
- Critical-point candidates with a second-derivative classification when possible
- Even/odd parity check
- Interactive function/derivative plots and root/critical-point overlays
- Optional parameter `a` slider
- Markdown and PDF report export
- Whitelist-based expression parser; no arbitrary Python evaluation
- Offline symbolic analysis after dependencies are installed

## Quick start

Python 3.11 or 3.12 is recommended.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit.

## Supported syntax

Use `x` as the independent variable and optionally `a` as a parameter. Supported operators: `+ - * / ^ **`. Supported functions: `sin`, `cos`, `tan`, inverse trig functions, hyperbolic functions, `exp`, `log`, `sqrt`, `abs`/`Abs`. Constants: `pi`, `e`.

Examples: `sin(x)*x`, `x^2 - 4`, `exp(-x^2)`, `log(x)/x`, `x^2-a`.

## Repository layout

```text
sfe/
├── app.py
├── sfe/
│   ├── __init__.py
│   ├── parser.py
│   ├── analyzer.py
│   ├── explainer.py
│   ├── plotter.py
│   └── exporter.py
├── data/functions_dataset.json
├── eval/evaluate.py
├── eval/results/
├── paper/main.tex
├── tests/test_analyzer.py
├── requirements.txt
└── LICENSE
```

The explanation logic currently lives in `sfe/analyzer.py` to keep the prototype compact. `sfe/explainer.py` is reserved for a future dedicated rule engine.

## Tests and evaluation

```bash
python -m unittest discover -s tests -v
python eval/evaluate.py
```

The evaluation script writes per-function and category-level CSV files under `eval/results/`. The included dataset contains 43 curated expressions. Expected outputs are intentionally marked for manual verification; do not report correctness scores until ground truth has been independently checked.

## Deployment

1. Push this repository to GitHub.
2. In Streamlit Community Cloud, create an app from the repository.
3. Set the main file path to `app.py`.
4. Deploy. The app does not require API keys or a database.

## Research status and limitations

This is a research prototype, not a certified computer algebra system. Domain computation, roots for transcendental functions, limits at singularities, and classification of degenerate critical points are best-effort. A displayed `ConditionSet` or unevaluated integral means SymPy could not produce a closed-form result. The derivative explanation is deterministic and rule-hinted, but it is not a complete formal derivation tree. The current evaluation script measures coverage and latency; correctness requires manually populated ground truth and comparison logic before a valid accuracy percentage can be claimed.

## License

MIT. See `LICENSE`.
