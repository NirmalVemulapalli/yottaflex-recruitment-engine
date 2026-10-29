# Reviewer guide

## Suggested 10-minute review

1. Read the project summary and run commands in [`../README.md`](../README.md).
2. Inspect [`ARCHITECTURE.md`](ARCHITECTURE.md) and [`DATA_MODEL.md`](DATA_MODEL.md).
3. Run the test suite and note the actual local result.
4. Inspect `data/generated/manifest.json` for seed, scale, counts, and checksums.
5. Compare `data/generated/anomaly_report.csv` with `data/generated/ground_truth.csv`.
6. Open `data/generated/schema.sql` or the SQLite database and check foreign-key integrity.
7. Read [`BUSINESS_RULES.md`](BUSINESS_RULES.md), [`VALIDATION.md`](VALIDATION.md), and [`DECISIONS.md`](DECISIONS.md) for the rationale and boundaries.

## Evidence interpretation

- `evidence/` contains reports generated from the local code and checked-in snapshot.
- The anomaly report is expected to contain the intentionally injected cases.
- Structural validation and business-rule audit answer different questions: a dataset can be relationally valid and still contain deliberate policy exceptions.
- The evidence is not an independent external audit or production certification.

## Reproduction

Use a fresh output directory for each generation and follow the reproducibility commands in the README. Confirm the report is generated from the code revision under review.
