# Data provenance and privacy

## Provenance

The checked-in generated dataset is synthetic and created by this repository's deterministic generator. No external candidate dataset or real resume files are used in the generated sample. The `source_manifest.json` file records the provenance statement for the generated snapshot.

## Synthetic-data safeguards

- Candidate identifiers and profiles are generated for demonstration.
- Resume artifacts represent metadata, not copies of actual resumes.
- Screening features are job-related skill and experience fields.
- Demographic characteristics and demographic proxies are not intended as screening features.
- Ground-truth anomaly labels are stored separately from operational features.

## Safe publication checklist

- Do not add real applicant names, contact details, resumes, interview notes, or recruiter correspondence.
- Do not commit access tokens, passwords, local environment files, or personal paths.
- Keep generated artifacts reproducible and identify the seed and scale.
- If future versions use external data, document source URL, dataset/version, retrieval date, license/terms, attribution, transformations, and discarded fields before redistributing it.

## Limitation

Synthetic records reduce privacy risk but do not make this project a validated hiring system. It is intended for software evaluation and data-quality demonstration only.
