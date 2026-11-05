# GenAI CI Evaluation Quality Gate

This working GitHub Actions example automatically checks supplied evaluation results against a quality threshold.

**Scope:** The included evaluation scores are synthetic, not actual Microsoft Foundry results. This workflow does NOT run Foundry evaluations or deploy an application. For a fully automated Foundry evaluation pipeline, add a supported Foundry evaluation SDK/API invocation and an adapter that converts the actual results to the normalized JSON format used here.

## Files
- `.github/workflows/evaluate.yml`: GitHub Actions workflow
- `data/foundry_evaluation_results.json`: sample normalized scores
- `scripts/check_quality_gate.py`: threshold check

## Run locally (PowerShell)

```powershell
python scripts/check_quality_gate.py --threshold 0.85
```

Expected: `QUALITY GATE: PASS`.

```powershell
python scripts/check_quality_gate.py --threshold 0.95
```

Expected: `QUALITY GATE: FAIL` (exit code 1).

## GitHub
Upload the whole folder including hidden `.github` to a GitHub repository. Open **Actions > GenAI Quality Gate > Run workflow**. Configure a branch ruleset for `main` requiring the `evaluation-gate` status check to prevent merges when it fails.

## Actual Foundry evaluation data
Run an evaluation in Foundry, export its numeric scores, and normalize them to the structure of `data/foundry_evaluation_results.json`: `score_scale` is `0_to_5` and `results` contains at least 3 objects with numeric `score` values. Raw Foundry exports may use a different schema. The mean score divided by five is an illustrative policy, not an official Foundry pass-rate metric.
