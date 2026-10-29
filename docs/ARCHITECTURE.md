# Architecture and design notes

## Components

- `src/recruitment_engine/engine.py`: deterministic synthetic record generation, relational seed export, structural checks, and business-rule audit.
- `data/generated/`: generated outputs. Regenerate these from source rather than hand-editing individual files.
- `tests/`: repeatability and acceptance-focused checks.
- `docs/DATA_DICTIONARY.md`: entity fields and relationships.
- `docs/PROMPT_HISTORY.md`: AI prompt record and disclosure checklist.

## Generation order

The generator creates parent/master records before dependent records. Applications refer to generated requisitions and candidates; interviews refer to applications and interviewers; feedback refers to interviews and interviewers; offers refer to applications. Candidate-to-skill relationships use a bridge table. Deterministic ID conventions and a fixed random seed make runs comparable.

## Separation of operational data and evaluation labels

Operational tables contain the records a downstream process would evaluate. `ground_truth.csv/json` stores the known injected exception labels separately. The audit recomputes findings from operational tables; it should not use ground-truth labels as input features. This separation supports checking whether the rules detect the intended exceptions.

## Validation layers

1. Structural checks: primary-key uniqueness, parent foreign keys, enum values, date ordering, score/salary bounds, approval presence, and allowed lifecycle transitions.
2. Relational check: SQLite `PRAGMA foreign_key_check` verifies the persisted seed database.
3. Business audit: duplicate application pairs, overlapping interviewer slots, missing feedback before progression, salary outside the approved band, and active applications on closed roles.
4. Metrics: summary values are derived from generated operational records rather than assigned independently.
5. Reproducibility: same seed and scale should produce byte-identical generated files in separate output directories.

## Trade-offs

The solution favors a locally runnable and inspectable Python implementation over a hosted web application. SQLite provides a portable relational artifact; CSV/JSON make generated records easy to inspect with common tools. The current three automated tests are focused acceptance checks, not proof of exhaustive correctness. See `VALIDATION.md` for scope and limitations.
