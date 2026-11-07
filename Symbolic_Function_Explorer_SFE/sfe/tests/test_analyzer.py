import unittest
from sfe.analyzer import analyze_function, AnalysisError

class AnalyzerTests(unittest.TestCase):
    def test_polynomial_derivative(self):
        r=analyze_function("x^2 - 4")
        self.assertEqual(str(r["derivative"]), "2*x")
        self.assertEqual(set(map(str,r["roots"])), {"-2","2"})
    def test_log_domain(self):
        r=analyze_function("log(x)")
        self.assertIn("Interval.open(0", r["domain"])
    def test_reject_unknown_name(self):
        with self.assertRaises(AnalysisError): analyze_function("__import__('os')")
    def test_parameter(self):
        r=analyze_function("x^2-a", parameter_value=4)
        self.assertEqual(sorted(round(float(v), 6) for v in r["roots"]), [-2.0, 2.0])
if __name__=="__main__": unittest.main()
