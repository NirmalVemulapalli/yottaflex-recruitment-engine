# AI Use and Prompt History

## 1. AI Assistance Disclosure

ChatGPT was used to support project planning, implementation guidance, Python environment troubleshooting, test execution, reproducibility verification, documentation review, and local repository preparation.

The project is a synthetic recruitment-data generator and workflow-audit command-line application. AI assistance supported the development and verification process. The candidate remains responsible for reviewing the source code, understanding the design decisions, validating the outputs, and accurately explaining the implementation.

This document records the prompts and requests currently documented in the available project notes. It is a **summary of AI interactions, not a complete verbatim transcript**.

## 2. Chronological User Requests

### User Request 1 — Initial Project and Assessment Requirements

**Date:** 28 October 2026  
**Tool:** ChatGPT

**Request summary:**  
Assistance was requested with interpreting the recruitment workflow and synthetic-data generation requirements, including the relational data model, deterministic data generation, validation rules, workflow auditing, intentional edge cases, output formats, documentation, and automated testing.

**How the assistance was used:**  
Planning and implementation guidance for the recruitment-data generator and its validation workflow.

**Record limitation:**  
The original request contained assessment material and is summarized here rather than reproduced verbatim because of the stated confidentiality concern. This summary should be reconciled with the assessment's prompt-recording requirements and confidentiality instructions.

### User Request 2 — Python Environment and Local Execution

**Date:** 29 October 2026  
**Tool:** ChatGPT

**Request summary:**  
Assistance was requested with troubleshooting the Python environment and running the project on Windows using PowerShell.

**How the assistance was used:**  
Followed guidance to create a fresh virtual environment, install the project and its testing dependencies, and execute the generator and audit commands.

**Verification recorded:**  
The project was executed successfully using Python 3.14.2.

### User Request 3 — Automated Testing, Audit, and Reproducibility

**Date:** 29 October 2026  
**Tool:** ChatGPT

**Request summary:**  
Assistance was requested with checking generated data, automated tests, audit findings, reproducibility, and project verification.

**How the assistance was used:**  
Followed a step-by-step verification process and inspected the generated artifacts and audit results.

**Verification recorded from previous runs:**

- **Automated tests:** 3 tests passed.
- **Audit findings:** 5 intended anomaly categories were detected:
  1. Duplicate application.
  2. Interviewer scheduling conflict.
  3. Missing feedback before progression.
  4. Active application on a closed requisition.
  5. Offer salary outside the approved band.
- **Reproducibility:** 38 files matched byte-for-byte between two generated output directories using the same seed and scale.

These results describe previous executions. They do not guarantee future results after code or configuration changes, establish production readiness, or guarantee an assessment outcome.

### User Request 4 — Git and Repository Preparation

**Date:** 29 October 2026  
**Tool:** ChatGPT

**Request summary:**  
Assistance was requested with preparing the local project for version control and potential GitHub publication.

**How the assistance was used:**  
Initialized a local Git repository, configured a repository-specific commit identity, reviewed ignore rules, and checked that temporary reproducibility outputs and development-environment files were excluded from version control.

**Verification recorded:**  
Local Git repository initialization succeeded. The virtual environment, Python caches, and temporary reproducibility outputs were identified as ignored files.

**Repository status at the time of recording:**  
The repository was initialized locally. A successful commit, GitHub publication, and assessment submission must only be reported after each action has actually occurred.

### User Request 5 — Prompt History Documentation

**Date:** 29 October 2026  
**Tool:** ChatGPT

**Request summary:**  
Assistance was requested with making the AI prompt-history documentation more professional, chronological, readable, and suitable for project review.

**How the assistance was used:**  
The document structure and disclosure wording were refined to distinguish summarized requests from verbatim prompts, record verification results, and describe the limitations of the available prompt record.

**Candidate responsibility:**  
The candidate must review the actual conversation history and any other AI tools used, then add the required prompts and correct any incomplete or inaccurate entries before submission.

## 3. Implementation and Verification Summary

The project currently includes the following documented components:

- A deterministic synthetic recruitment-data generator using a fixed seed.
- CSV and JSON exports.
- A SQLite database and SQL schema.
- Recruitment entities covering requisitions, departments, candidates, applications, skills, resumes, screening rules, interviews, interviewers, feedback, offers, and application events.
- Separate ground-truth labels for intentionally injected cases.
- Structural validation and workflow-audit findings.
- Metrics, manifests, and generated data summaries.
- Automated tests and a reproducibility verification script.
- Documentation covering the data model, business rules, lifecycle, validation, provenance, operations, and reviewer guidance.

The generated dataset intentionally includes edge cases for audit verification. These findings are expected test scenarios and should be interpreted alongside the documented business rules and ground-truth labels.

## 4. Record Limitations and Redactions

This document records the AI interactions currently documented in the available project notes. It does not claim to contain every message, exact prompt, AI response, or tool interaction.

Before submission, the candidate should:

1. Review the available conversation history.
2. Include the actual prompts required by the assessment.
3. Record any other AI tools used, including IDE assistants, if applicable.
4. Clearly label summaries, omissions, and redactions.
5. Avoid inventing prompts or presenting an incomplete record as exhaustive.

The original confidential assessment email and restricted assessment document should not be copied into a public repository. If the requirement to reproduce prompts conflicts with the confidentiality instructions, request clarification from the recruiter.

## 5. Candidate Review and Responsibility

The candidate is responsible for understanding and reviewing the submitted implementation, including:

- The relational data model and entity relationships.
- Seed-based deterministic generation.
- Synthetic-data generation and anomaly injection.
- Validation and audit rules.
- Export formats, manifests, and ground-truth separation.
- Test coverage, reproducibility checks, and known limitations.

Only work personally reviewed or verified should be described as such. AI-assisted work should be disclosed accurately. Test results should reflect actual executions, and no GitHub publication, submission, or evaluation outcome should be claimed without evidence.

## 6. Final Review Checklist

- [ ] Review all available AI conversations and other AI tools used.
- [ ] Add the actual prompts required by the assessment.
- [ ] Identify summaries and redactions explicitly.
- [ ] Verify that the recorded test and reproducibility results are current.
- [ ] Review source code, generated outputs, and documentation.
- [ ] Confirm that no credentials, private information, or restricted assessment files are included in the public repository.
- [ ] Confirm the repository status before describing it as committed or published.
- [ ] Ensure the candidate can explain the implementation and its limitations independently.
