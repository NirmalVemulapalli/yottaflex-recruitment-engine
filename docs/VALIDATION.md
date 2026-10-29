# Validation and evidence guide

## Run checks

```powershell
python -m pytest -q
python -m recruitment_engine.engine audit --data data/generated
python -m recruitment_engine.engine generate --out data/run_a --seed 20261022 --scale 1
python -m recruitment_engine.engine generate --out data/run_b --seed 20261022 --scale 1
python scripts/verify_reproducibility.py data/run_a data/run_b
```

## What the current tests check

- Two independent generations with the same seed have matching file names and byte contents.
- Required baseline counts are met (applications and interviews may include extra labelled cases).
- Ground-truth labels remain separate from operational application records.
- All five requested issue types are represented in ground truth.
- All five required anomaly categories appear in ground truth and the audit output.
- SQLite foreign-key integrity passes.
- Application event records follow the documented allowed transition graph.

## Interpreting audit findings

The generated data deliberately includes exception cases. A non-zero anomaly count is expected and should be compared with the separate ground-truth labels. A useful review checks that each expected issue is found, unrelated valid rows remain structurally valid, and reports point to the affected record IDs.

## Evidence honesty

Do not publish a passing status, benchmark, coverage percentage, or test count unless it was produced by a run you can reproduce. Record the command, Python version, date, exit code, and output artifact when preparing final evidence. A passing test suite does not prove every lifecycle rule or all foreign-key constraints are exhaustive; inspect the implementation and state limitations clearly.


## Lifecycle and relational checks

The validator checks primary-key uniqueness for each entity with a declared single-column key, required parent joins, supported enum values, date ordering, score/salary bounds, approval presence, and the allowed application-stage transition graph. The automated tests also execute SQLite's `PRAGMA foreign_key_check` and verify the event transitions. Duplicate `(requisition_id, candidate_id)` pairs are intentionally retained as a labelled exception so the audit can demonstrate detection rather than silently dropping the record.

The known exception set is expected to produce one finding for each required anomaly category with the default seed. This is a fixture-coverage check, not evidence that all possible production anomalies are detected.
