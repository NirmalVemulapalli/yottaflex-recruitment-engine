# Test Report

## Purpose

This report records the checks currently implemented in the repository. It distinguishes automated test results from expected anomaly findings in the intentionally seeded synthetic dataset.

## Reproduce the test run

From the repository root, after installing the project and test extra:

```bash
python -m pip install -e ".[test]"
pytest -q
python -m recruitment_engine.engine audit --data data/generated
```

To validate reproducibility independently, generate two outputs and compare them:

```bash
python -m recruitment_engine.engine generate --out data/run_a --seed 20261022 --scale 1
python -m recruitment_engine.engine generate --out data/run_b --seed 20261022 --scale 1
python scripts/verify_reproducibility.py data/run_a data/run_b
```

## Automated test coverage

The current test suite contains three pytest tests covering:

1. **Deterministic generation and baseline counts** — two generated directories with the same seed must have identical filenames and byte-for-byte identical file contents. Key baseline targets and generated artifacts are checked.
2. **Known anomaly detection** — the audit must report the five expected injected issue categories: duplicate application, interviewer time conflict, missing feedback before progression, active application on a closed requisition, and offer salary outside the approved band.
3. **SQLite integrity and lifecycle transitions** — SQLite foreign-key checks must be clean, required tables must exist, and application-event transitions must follow the configured allowed-transition map.

Additional assertions check that the validation summary has `PASS` status with no validation errors, metrics match generated record counts, no external datasets are declared, and ground-truth labels are not embedded in operational application records.

## Recorded local result

The latest recorded local run in `evidence/test-run.txt` reports **3 passed**. The accompanying `evidence/` files preserve the row-count snapshot, anomaly coverage, validation summary, SQLite integrity result, metrics snapshot, and checksum information for that run.

Re-run the commands above in your own environment before submission. Python versions, operating systems, and dependency versions can differ; do not interpret a past local result as proof that every untested environment will behave identically.

## Expected anomalies versus test failures

The generator intentionally injects known edge cases so the audit can demonstrate detection behavior. Seeing these findings in `anomaly_report.csv` is expected. A failed validation summary, unexpected exception, failing test, or non-reproducible output is a separate issue that should be investigated.

## Scope and limitations

- The tests cover the current generator, audit rules, SQLite integrity, and selected lifecycle constraints; they are not exhaustive property-based or load tests.
- Interviewer availability is simulated. No live calendar, applicant-tracking system, email service, or external API is connected.
- The test suite does not establish that synthetic metrics represent a real employer or hiring population.
