"""Deterministic explanation helpers."""
from .analyzer import _derivative_explanation

def explain_derivative(expression, derivative):
    return _derivative_explanation(expression, derivative)
