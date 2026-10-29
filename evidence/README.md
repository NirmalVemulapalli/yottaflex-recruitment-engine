# Verification evidence

This directory contains machine-readable or text evidence produced from the checked-in generated snapshot and local verification run. These artifacts document what was run, not a claim of independent audit or production certification.

| Artifact | What it records |
|---|---|
| `verification-summary.json` | Consolidated checks, counts, metrics, and stated limitations |
| `test-run.txt` | Actual pytest command, runtime, timestamp, exit code, and output |
| `sqlite-integrity.json` | SQLite foreign-key check result for the checked-in database |
| `row-counts.csv` | Observed generated row counts from the manifest |
| `anomaly-coverage.csv` | Ground-truth issue types mapped to observed audit rules |
| `metrics-snapshot.json` | Copy of the generated operational metrics snapshot |
| `validation-snapshot.json` | Copy of the generated structural validation summary |
| `SHA256SUMS.json` | SHA-256 hashes for the evidence files (excluding this checksum file) |

## Reproduce

From the project root, run:

```powershell
python -m pytest -q
python -m recruitment_engine.engine audit --data data/generated
python -m recruitment_engine.engine generate --out data/run_a --seed 20261022 --scale 1
python -m recruitment_engine.engine generate --out data/run_b --seed 20261022 --scale 1
python scripts/verify_reproducibility.py data/run_a data/run_b
```

Regenerate evidence after changing the code or generated snapshot. Do not keep a stale PASS report after a failed test run. Record environment differences when comparing runs across machines.
