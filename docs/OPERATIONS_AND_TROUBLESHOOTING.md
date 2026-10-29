# Operations and troubleshooting

## Supported workflow

1. Create and activate a virtual environment.
2. Install the package and test dependencies.
3. Generate the dataset into a chosen output directory.
4. Run structural validation and business-rule audit.
5. Run tests.
6. If reproducibility is being checked, generate to two clean output directories and compare them.

## Windows quick commands

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[test]"
python -m recruitment_engine.engine generate --out data/generated --seed 20261022 --scale 1
python -m recruitment_engine.engine audit --data data/generated
python -m pytest -q
```

## Common issues

### `No module named recruitment_engine`
Run commands from the repository root after `pip install -e ".[test]"`, or set `PYTHONPATH=src` for direct local test execution.

### PowerShell refuses to activate the environment
Use `.\.venv\Scripts\python.exe -m pip install -e ".[test]"` and run the project with `.\.venv\Scripts\python.exe -m recruitment_engine.engine ...`; activation is optional.

### Reproducibility comparison differs
Use the same seed, scale, code revision, Python version, and clean output directories. Check whether the compared paths contain unrelated files or prior outputs. Do not edit generated outputs between runs.

### Audit reports findings
The default fixture intentionally includes five required anomaly classes. Compare findings to `ground_truth.csv` / `ground_truth.json`; a non-zero expected-anomaly count is not the same as a structural validation failure.

### SQLite foreign-key check fails
Preserve the failing database for diagnosis, inspect parent/child IDs and generation order, then rerun generation into a fresh output directory. Do not suppress the failure by disabling constraints.

## Data handling

All generated people and resume metadata are synthetic. Do not add real candidate data, credentials, tokens, private recruitment correspondence, or assessment PDFs to this public repository.
