import json
import os
from pathlib import Path
path = Path('outputs/evaluation-results.json')
if not path.exists():
    raise SystemExit('BLOCK: Evaluation results are missing.')
rows = json.loads(path.read_text()).get('builtin.task_adherence')
expected = len(json.loads(Path('evaluation/evaluation.json').read_text())['data'])
if not isinstance(rows, list) or len(rows) != expected or expected == 0:
    raise SystemExit('BLOCK: Evaluation results are incomplete.')
if any(not isinstance(row, dict) or not isinstance(row.get('passed'), bool) for row in rows):
    raise SystemExit('BLOCK: Evaluator pass/fail results are missing.')
passed = sum(row['passed'] for row in rows)
rate = passed / expected
threshold = 0.85
decision = 'PASS' if rate >= threshold else 'BLOCK'
summary = f'Quality gate: {decision}\nTask-adherence passing rate: {rate:.0%}\nRequired threshold: {threshold:.0%}\nPassing cases: {passed}/{expected}\n'
print(summary)
Path('outputs/quality-gate.json').write_text(json.dumps({'decision': decision, 'passing_rate': rate,
    'threshold': threshold, 'passed': passed, 'total': expected}, indent=2))
if os.environ.get('GITHUB_STEP_SUMMARY'):
    with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as handle:
        handle.write('## Enterprise platform quality gate\n\n' + summary)
raise SystemExit(0 if decision == 'PASS' else 1)
