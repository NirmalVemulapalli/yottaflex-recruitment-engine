# Project Walkthrough

This walkthrough gives a reviewer a short, reproducible route through the Recruitment Workflow & Data Quality Engine.

## 1. Requirements

- Python 3.10 or newer
- A terminal opened at the repository root
- Internet access only if pip needs to download the test dependency during setup

The project has no runtime dependencies declared. `pytest` is installed through the optional `test` extra.

## 2. Install

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[test]"
```

If PowerShell blocks activation, use `.\.venv\Scripts\python.exe` and `.\.venv\Scripts\python.exe -m pip` instead.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[test]"
```

## 3. Generate the synthetic dataset

```bash
python -m recruitment_engine.engine generate --out data/generated --seed 20261022 --scale 1
```

The output directory contains CSV and JSON exports for the recruitment entities, a SQLite seed database, SQL schema, a manifest, source manifest, metrics summary, validation summary, anomaly report, and separate ground-truth labels.

At scale 1, the baseline targets include 100 requisitions, 2,000 candidates, 3,000 applications, 600 interviews, and 150 offers. Some observed totals are intentionally higher because exception records are injected; for example, the expected generated snapshot has 3,002 applications and 601 interviews. Consult `data/generated/manifest.json` for the actual output counts.

## 4. Run the audit and tests

```bash
python -m recruitment_engine.engine audit --data data/generated
pytest -q
```

The audit writes/prints its findings for the dataset. The test suite checks deterministic output, required anomaly categories, SQLite foreign-key integrity, and selected lifecycle rules. The recorded local run is in `evidence/test-run.txt`; rerun it locally to verify the current checkout.

## 5. Inspect key outputs

1. `data/generated/manifest.json` — record counts and generation metadata.
2. `data/generated/validation_summary.json` — structural validation status and errors.
3. `data/generated/anomaly_report.csv` and `.json` — audit findings for the seeded edge cases.
4. `data/generated/metrics_summary.json` — descriptive metrics derived from the synthetic records.
5. `data/generated/ground_truth.csv` and `.json` — labelled injected issues for evaluation. These are evaluation labels, not operational screening features.
6. `data/generated/recruitment_seed.sqlite` — relational seed database.
7. `evidence/` — saved verification snapshots and checksums.

## 6. Verify reproducibility

```bash
python -m recruitment_engine.engine generate --out data/run_a --seed 20261022 --scale 1
python -m recruitment_engine.engine generate --out data/run_b --seed 20261022 --scale 1
python scripts/verify_reproducibility.py data/run_a data/run_b
```

Use separate output directories so the first run is not overwritten. The verifier compares generated artifacts; identical output is expected for the same seed and scale in the same implementation/version.

## 7. Read next

- `DATA_MODEL.md` and `DATA_DICTIONARY.md` for the schema
- `BUSINESS_RULES.md` and `LIFECYCLE.md` for recruitment constraints
- `VALIDATION.md` and `QA_TEST_PLAN.md` for quality checks and their limits
- `DATA_PROVENANCE.md` for synthetic-data boundaries
- `PROMPT_HISTORY.md` for the AI-use record; complete it with your actual prompts and review notes before submission

## Known boundaries

This is a local synthetic-data generator and audit CLI, not a production ATS or a web dashboard. It does not integrate with live calendars, real candidates, or external recruitment services.
