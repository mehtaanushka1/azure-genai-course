import argparse, json, math, sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument("--input",default="data/foundry_evaluation_results.json");p.add_argument("--threshold",type=float,default=0.85);a=p.parse_args()
try:
 d=json.loads(Path(a.input).read_text());s=[r["score"] for r in d["results"]]
 if d.get("score_scale")!="0_to_5" or len(s)<3 or not all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) and 0<=v<=5 for v in s):raise ValueError("Expected at least 3 scores between 0 and 5")
 if not 0<=a.threshold<=1:raise ValueError("Invalid threshold")
 score=sum(s)/len(s)/5;print(f"Normalized score: {score:.1%}; threshold: {a.threshold:.1%}");ok=score>=a.threshold;print("QUALITY GATE: PASS" if ok else "QUALITY GATE: FAIL");sys.exit(0 if ok else 1)
except (OSError,ValueError,KeyError,TypeError) as e:print(f"QUALITY GATE: ERROR - {e}",file=sys.stderr);sys.exit(2)
