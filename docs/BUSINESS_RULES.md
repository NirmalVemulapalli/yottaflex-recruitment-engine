# Business rules and decision policy

This page states the intended policies used by the synthetic generator and audit checks. Where the implementation is a simplified simulation, that is called out explicitly.

## Requisition policy
- Requisitions carry department, lifecycle state, opening/closing dates, headcount and salary-band values.
- The baseline generator creates valid parent/master data before dependent records.
- A closed role with an active application is retained as a deliberate exception and should be reported, not silently rewritten.

## Screening policy
- Screening scores use job-related skill match and experience-related fields only.
- Demographic attributes and demographic proxies are excluded from the scoring features.
- The score is derived from source criteria; it is not independently randomized.
- The scoring output is a synthetic demonstration and must not be used to make real hiring decisions.

## Interview policy
- Each interview references an existing application and interviewer.
- Interview time intervals must be ordered and fit the documented synthetic schedule.
- An interviewer cannot be scheduled for overlapping intervals.
- The intentionally injected unavailable/conflicting schedule is expected to appear in the audit report.

## Feedback and stage policy
- Feedback is structured and linked to an interview and interviewer.
- Progression beyond a stage requiring feedback should be supported by the required feedback records.
- The injected missing-feedback case is preserved as a negative scenario so the auditor can detect it.
- ApplicationEvent rows provide traceability for stage transitions; do not treat the latest stage alone as complete history.

## Offer policy
- Offer records reference valid application/requisition context.
- Proposed salary should fall within the approved requisition band.
- Offers should only be generated when the simulated approval prerequisites are satisfied.
- The out-of-band offer is a deliberate labelled exception and must remain separately identifiable.

## Exception policy

| Exception | Expected system response |
|---|---|
| Duplicate application pair | Flag duplicate candidate/requisition pair; preserve both rows for audit. |
| Interviewer conflict | Flag overlapping interviewer schedule. |
| Missing feedback before progression | Flag stage advancement lacking required feedback. |
| Salary outside band | Flag offer salary against requisition bounds. |
| Active application on closed role | Flag lifecycle mismatch between role and application. |

## Important limitation

These policies describe a synthetic challenge implementation, not a legally reviewed recruitment policy. Before production use, a hiring organization would need policy owners, audit controls, accessibility review, security controls, and validation against applicable law.
