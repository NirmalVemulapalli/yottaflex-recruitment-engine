# Design decisions and trade-offs

## ADR-001: Python for deterministic generation
**Decision:** Use Python for synthetic data generation and validation.
**Reason:** It supports seeded generation, CSV/JSON handling, relational checks, and tests with a small local setup.
**Trade-off:** A command-line engine is less visually interactive than a web dashboard, but keeps effort focused on the challenge's data and workflow rules.

## ADR-002: SQLite for portable relational storage
**Decision:** Export a SQLite database and SQL schema alongside flat files.
**Reason:** Reviewers can inspect real foreign-key relationships locally without setting up a server.
**Trade-off:** SQLite is appropriate for a single-machine evaluation, not a claim of a production multi-user deployment.

## ADR-003: Keep operational records separate from ground truth
**Decision:** Export known injected anomaly labels to separate ground-truth files.
**Reason:** Evaluation labels must not leak into input features or influence screening scores.
**Trade-off:** Reviewers must compare audit results and labels explicitly rather than expecting the input table to mark its own defects.

## ADR-004: Preserve intentional negative scenarios
**Decision:** Keep deliberate anomalies as labelled fixtures instead of silently cleaning them away.
**Reason:** The challenge explicitly evaluates exception detection and traceability.
**Trade-off:** The business audit is expected to report findings even when structural validation passes.

## ADR-005: Synthetic-only provenance
**Decision:** Use synthetic profiles and metadata, with no external personal dataset.
**Reason:** This avoids redistribution and privacy uncertainty while keeping the data generator reproducible.
**Trade-off:** Synthetic distributions are illustrative and should not be interpreted as representative of a real hiring market.
