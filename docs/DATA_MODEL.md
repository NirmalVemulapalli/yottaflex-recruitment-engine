# Data model and relationship guide

This document describes the relational shape of the synthetic recruitment dataset. The authoritative field-level reference is [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md); the SQL definitions are exported to [`../data/generated/schema.sql`](../data/generated/schema.sql).

## Entity groups

### Master/reference data
- **Department** — organizational unit referenced by requisitions.
- **Skill** — normalized skill vocabulary.
- **JobRequisition** — approved or otherwise lifecycle-tracked opening, including department, date window, headcount, and salary band.
- **Candidate** — synthetic candidate profile with no real-person data.
- **Interviewer** — synthetic interviewer and availability attributes.

### Bridge and supporting records
- **RequisitionSkill** — bridge between requisitions and required skills (many-to-many).
- **CandidateSkill** — bridge between candidates and skills, with a proficiency/experience representation.
- **ResumeArtifact** — synthetic resume metadata associated with a candidate; no real resume files are embedded.
- **ScreeningRule** — rule configuration associated with a requisition and its screening criteria.

### Transaction and history records
- **Application** — candidate's application to a requisition. A candidate may apply to multiple requisitions, and a requisition may receive multiple candidates.
- **Interview** — scheduled round for an application, with an assigned interviewer and time interval.
- **Feedback** — structured interviewer feedback associated with an interview.
- **Offer** — offer proposal/outcome associated with an application and its requisition salary band.
- **ApplicationEvent** — append-style stage transition history used to retain a trace of progression.

## Cardinality summary

| Relationship | Cardinality | Notes |
|---|---|---|
| Department → JobRequisition | 1:N | A requisition references one department. |
| JobRequisition ↔ Skill | N:M | Represented by RequisitionSkill. |
| Candidate ↔ Skill | N:M | Represented by CandidateSkill. |
| Candidate → ResumeArtifact | 1:N in schema/data model | Candidate metadata may have one or more artifacts over time. |
| Candidate → Application | 1:N | A candidate can submit applications to different roles. |
| JobRequisition → Application | 1:N | Each application targets one requisition. |
| Application → Interview | 1:N | Interviews are separate rounds. |
| Interview → Feedback | 1:N | Multiple panel members can provide feedback. |
| Application → Offer | 1:N optional | An application may have no offer or multiple offer records over its lifecycle. |
| Application → ApplicationEvent | 1:N | Events preserve stage history. |

## Integrity expectations

1. Primary identifiers are deterministic, zero-padded where specified, and treated as immutable.
2. Child rows must reference existing parent IDs.
3. Intentional negative scenarios remain identifiable in ground truth and audit outputs; do not delete them merely to make all business checks appear clean.
4. Ground truth is an evaluation label set, not an input feature for screening.
5. Run SQLite `PRAGMA foreign_key_check` after generation.

## Known modeling boundaries

This is a synthetic evaluation model, not a complete ATS production schema. The data generator and SQL schema are the source of truth for exact constraints. Review optional fields and lifecycle semantics against the code before extending the model.
