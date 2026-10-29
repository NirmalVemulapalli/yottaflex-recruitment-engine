# QA test plan

## Objective

Show that the generated dataset is reproducible, structurally coherent, and capable of surfacing the five required labelled exception classes.

## Test layers

| Layer | Check | Evidence artifact |
|---|---|---|
| Generator | Same seed and scale produce byte-identical outputs | `evidence/reproducibility-report.json` |
| Volume | Baseline volumes plus deliberate exception additions | `evidence/row-counts.csv` |
| Relational | SQLite foreign-key check | `evidence/verification-summary.json` |
| Business audit | Five required issue types appear in audit output | `evidence/anomaly-coverage.csv` |
| Metrics | Derived metrics exported with the generated snapshot | `data/generated/metrics_summary.json` |
| Regression | Automated test suite passes | `evidence/test-run.txt` |

## Expected negative cases

1. Duplicate application pair: should be reported by duplicate-pair rule.
2. Interviewer overlap: should be reported by scheduling audit.
3. Stage advanced without required feedback: should be reported.
4. Offer salary outside approved band: should be reported.
5. Active application for closed role: should be reported.

## Exit criteria

- Test command exits successfully.
- Structural validation reports zero structural errors.
- SQLite foreign-key check returns no rows.
- Each required exception type has a ground-truth label and a corresponding audit finding.
- Two independent output directories compare byte-for-byte under the same seed and scale.

## Limitations

Passing this plan does not prove all conceivable lifecycle cases, concurrency behavior, security, accessibility, or production readiness. It demonstrates the documented checks for this local synthetic challenge.
