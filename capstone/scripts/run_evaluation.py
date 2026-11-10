import json
import os
import runpy
import sys
from pathlib import Path
source = Path(os.environ['EVAL_ACTION_PATH']).resolve()
sys.path.insert(0, str(source))
import analysis
original = analysis.process_evaluation_results

def capture_results(*args, **kwargs):
    results = original(*args, **kwargs)
    scores = {name: score.result_items for name, score in results['evaluation_scores'].items()}
    Path('outputs').mkdir(exist_ok=True)
    Path('outputs/evaluation-results.json').write_text(json.dumps(scores))
    return results

analysis.process_evaluation_results = capture_results
runpy.run_path(str(source / 'action.py'), run_name='__main__')
