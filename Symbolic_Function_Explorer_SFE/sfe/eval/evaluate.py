"""Evaluate the curated function set. Expected values may be filled after manual verification."""
import json, time, sys
from pathlib import Path
import pandas as pd
import sympy as sp
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sfe.analyzer import analyze_function

def main():
    data = json.loads((ROOT/"data/functions_dataset.json").read_text(encoding="utf-8"))
    rows=[]
    for item in data:
        start=time.perf_counter()
        try:
            result=analyze_function(item["expr"])
            latency=(time.perf_counter()-start)*1000
            rows.append({"id":item["id"],"category":item["category"],"status":"ok",
                         "latency_ms":round(latency,3),"derivative":str(result["derivative"]),
                         "roots":result["roots_display"],"domain":result["domain"],
                         "fully_analyzed":bool(result["domain"] and result["derivative"] is not None)})
        except Exception as exc:
            rows.append({"id":item["id"],"category":item["category"],"status":f"error: {exc}",
                         "latency_ms":round((time.perf_counter()-start)*1000,3),
                         "derivative":"","roots":"","domain":"","fully_analyzed":False})
    out=ROOT/"eval/results"; out.mkdir(parents=True,exist_ok=True)
    df=pd.DataFrame(rows); df.to_csv(out/"results.csv",index=False)
    summary=df.groupby("category").agg(count=("id","count"),coverage=("fully_analyzed","mean"),
                                      mean_latency_ms=("latency_ms","mean")).reset_index()
    summary.to_csv(out/"summary.csv",index=False)
    print(df.to_string(index=False)); print("\nSummary\n",summary.to_string(index=False))
    print(f"\nOverall coverage: {df.fully_analyzed.mean()*100:.1f}%")
    print(f"Mean latency: {df.latency_ms.mean():.2f} ms")
if __name__=="__main__": main()
