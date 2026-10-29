# Submission Checklist

Use this list immediately before creating or sharing the submission repository. Mark an item complete only after checking it in the current checkout.

## Challenge outputs

- [ ] Generate the dataset from a clean checkout using the documented command and fixed seed.
- [ ] Confirm baseline targets: 100 requisitions, 2,000 candidates, 3,000 applications, 600 interviews, and 150 offers.
- [ ] Check observed totals against `data/generated/manifest.json`; document that injected exceptions make some observed totals higher than the baseline targets.
- [ ] Confirm CSV and JSON outputs exist for the required entities and that the SQLite database and `schema.sql` are present.
- [ ] Confirm `source_manifest.json`, `metrics_summary.json`, and `validation_summary.json` are present.
- [ ] Confirm `ground_truth.csv` and `ground_truth.json` are separate from operational feature data.
- [ ] Confirm `anomaly_report.csv` and `anomaly_report.json` are generated.

## Quality checks

- [ ] Run `pytest -q` and review every failure; do not rely solely on a previously saved test report.
- [ ] Run the audit command and inspect the validation status and findings.
- [ ] Verify all five intended anomaly categories are represented: duplicate application, interviewer conflict, missing feedback before progression, salary outside approved band, and active application on a closed role.
- [ ] Run the two-directory reproducibility check using the same seed and scale.
- [ ] Verify SQLite foreign-key integrity and inspect the evidence snapshots.
- [ ] Review metric definitions and ensure no synthetic metric is presented as a real-world benchmark.

## Documentation and disclosure

- [ ] Read the root `README.md`, `docs/README.md`, `docs/WALKTHROUGH.md`, and `docs/TEST_REPORT.md` from the perspective of a first-time reviewer.
- [ ] Complete `docs/PROMPT_HISTORY.md` with the actual prompts and meaningful iterations you used. Do not invent prompts or claim the history is exhaustive if it is not.
- [ ] Be prepared to explain the generator, schema, seed behavior, validation rules, anomaly injection, and limitations in your own words.
- [ ] Ensure the README accurately describes the project as a synthetic-data generator and audit CLI, not a production ATS or live integration.

## Repository hygiene and confidentiality

- [ ] Do not commit the original confidential challenge email, assessment PDF, or other restricted assessment materials.
- [ ] Remove credentials, tokens, personal data, local virtual environments, caches, and temporary output directories.
- [ ] Review `.gitignore`, staged files, commit history, and the final public repository contents.
- [ ] Check that all paths and commands in the README work from a fresh clone.
- [ ] Confirm the license is appropriate for the files you are publishing and does not imply rights to confidential third-party materials.
- [ ] Push to your own repository and open the GitHub page to confirm the README, documentation links, and expected files render correctly.

## Final status

- [ ] All checks above are complete, or any unchecked item is explicitly recorded as a limitation.
- [ ] Final submission is uploaded before the challenge deadline.
