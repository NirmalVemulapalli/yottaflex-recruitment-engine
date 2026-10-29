# Data Dictionary

All records are synthetic. Dates use ISO 8601 (`YYYY-MM-DD`); timestamps use local ISO format. INR salary fields are annual gross salary in rupees. `*_id` values are immutable identifiers. Empty strings represent optional values in CSV exports.

| Entity | Primary key | Required fields / validation | Relationship and cardinality |
|---|---|---|---|
| Department | `department_id` | `name` unique; `active` boolean | Department 1:N requisitions and interviewers |
| JobRequisition | `requisition_id` | approved status; valid department; `salary_min_inr <= salary_max_inr`; created date <= close date; headcount >= 1 | Department N:1; requisition 1:N applications and screening rules |
| Candidate | `candidate_id` | unique synthetic email; experience >= 0 | Candidate 1:N resume artifacts and applications |
| Application | `application_id` | valid requisition and candidate; stage in `applied, screened, interview, interview_passed, offer, hired, rejected, withdrawn`; score 0–100 | Requisition N:1; candidate N:1; application 1:N interviews, offers, events |
| ResumeArtifact | `resume_id` | candidate FK; content hash; metadata-only URI | Candidate N:1; resume contents intentionally not generated |
| Skill | `skill_id` | unique skill name | Skill 1:N CandidateSkill and RequisitionSkill rows |
| RequisitionSkill | composite (`requisition_id`, `skill_id`) | both FKs; positive priority; required flag | Requisition N:M Skill bridge for required job skills |
| CandidateSkill | composite (`candidate_id`, `skill_id`) | both FKs; proficiency enum; years >= 0 | Candidate N:M Skill bridge |
| ScreeningRule | `screening_rule_id` | requisition FK; weights total 1.0; minimum match 0–100; effective dates | Requisition N:1; effective-dated rule |
| Interview | `interview_id` | application/interviewer FKs; start < end; round >= 1; status enum | Application 1:N interviews; interviewer 1:N interviews |
| Interviewer | `interviewer_id` | department FK; active flag; weekly capacity > 0 | Department N:1; interviewer 1:N interviews and feedback |
| Feedback | `feedback_id` | interview/interviewer FKs; each score 1–5; recommendation `hire, hold, no_hire` | Interview 1:N feedback (supports panel interviews); interviewer 1:N feedback |
| Offer | `offer_id` | application FK; salary > 0; approval status; offer status enum | Application 1:N offers; salary should fit approved requisition band |
| ApplicationEvent | `event_id` | application ID; event timestamp; actor and reason | Application 1:N lifecycle events |

## Lifecycle values

- Requisition status: `approved`, `closed`.
- Candidate profile status: `active`, `inactive`.
- Application stages: `applied`, `screened`, `interview`, `interview_passed`, `offer`, `hired`, `rejected`, `withdrawn`.
- Interview status: `completed`, `scheduled`, `cancelled`.
- Offer status: `accepted`, `rejected`, `pending`, `expired`.
- Resume parse status: `parsed`, `needs_review`.

## ID conventions

`REQ-2026-000001`, `CAND-000001`, `APP-<requisition-id>-<candidate-id>`, `INT-2026-000001`, `FB-<interview-id>-<interviewer-id>`, `OFF-2026-000001`. Deliberate duplicate-pair and closed-role exception rows use explicit suffixes and `issue_type` labels to preserve traceability. Expected decisions are stored only in the separate ground-truth file.

## Notes

`ground_truth.csv/json` is separate evaluation metadata, not a feature table. The expected labels are not present in operational table exports. The optional `issue_type` marker identifies deliberate anomaly rows; exclude it too when building model features.

## Field-level specification

In the tables below, `R` = required and `O` = optional. Unless stated otherwise, string identifiers are required and immutable; IDs are unique primary keys or foreign keys as indicated above.

### Department

| Field | Type | Req. | Allowed values / uniqueness / validation |
|---|---|---:|---|
| `department_id` | string | R | PK; `DEP-` plus zero-padded counter |
| `name` | string | R | Unique; one of the synthetic department names |
| `active` | boolean | R | `true` or `false` |

### JobRequisition

| Field | Type | Req. | Allowed values / uniqueness / validation |
|---|---|---:|---|
| `requisition_id` | string | R | PK; `REQ-2026-` plus six digits |
| `title` | string | R | Synthetic role title |
| `department_id` | string | R | FK to Department |
| `level` | string | R | `junior`, `mid`, `senior` |
| `status` | string | R | `approved`, `closed` |
| `created_date` | date | R | ISO date; <= `close_date` |
| `close_date` | date | R | ISO date; >= `created_date` |
| `headcount` | integer | R | >= 1 |
| `salary_min_inr` | integer | R | INR/year; > 0 and <= maximum |
| `salary_max_inr` | integer | R | INR/year; >= minimum |
| `approved_by` | string | R | Synthetic user ID |
| `approval_status` | string | R | `approved` in baseline data |

### Candidate

| Field | Type | Req. | Allowed values / uniqueness / validation |
|---|---|---:|---|
| `candidate_id` | string | R | PK; `CAND-` plus six digits |
| `full_name` | string | R | Synthetic name; not guaranteed unique |
| `email` | string | R | Unique; reserved `.test` domain |
| `city` | string | R | Synthetic city / `Remote` |
| `experience_years` | integer | R | 0–12 years |
| `created_date` | date | R | ISO date |
| `profile_status` | string | R | `active`, `inactive` |

### Application

| Field | Type | Req. | Allowed values / uniqueness / validation |
|---|---|---:|---|
| `application_id` | string | R | PK; `APP-<requisition-id>-<candidate-id>`; deliberate duplicate uses suffix |
| `requisition_id` | string | R | FK to JobRequisition |
| `candidate_id` | string | R | FK to Candidate |
| `applied_at` | date | R | ISO date |
| `stage` | string | R | Lifecycle enum above |
| `screening_score` | decimal | R | 0–100; derived from skills and experience |
| `screening_decision` | string | R | `pass`, `review_or_reject` |
| `withdrawn_at` | date/string | O | Blank unless withdrawn |
| `issue_type` | string | O | Blank for normal row; known anomaly type for injected row |

### ResumeArtifact

| Field | Type | Req. | Allowed values / uniqueness / validation |
|---|---|---:|---|
| `resume_id` | string | R | PK; `RES-` plus six digits |
| `candidate_id` | string | R | FK to Candidate |
| `artifact_type` | string | R | `synthetic_resume_metadata` |
| `file_name` | string | R | Synthetic filename |
| `storage_uri` | string | R | Local synthetic URI; no real resume content |
| `content_hash` | string | R | SHA-256-shaped hex digest |
| `created_at` | date | R | ISO date |
| `parsed_status` | string | R | `parsed`, `needs_review` |
| `source` | string | R | `synthetic_generator` |

### RequisitionSkill

| Field | Type | Req. | Allowed values / uniqueness / validation |
|---|---|---:|---|
| `requisition_id` | string | R | FK to JobRequisition; composite PK part |
| `skill_id` | string | R | FK to Skill; composite PK part |
| `requirement_priority` | integer | R | Positive integer; deterministic order of job requirements |
| `is_required` | boolean | R | `true` for generated mandatory role skills |

### Skill and CandidateSkill

| Field | Type | Req. | Allowed values / uniqueness / validation |
|---|---|---:|---|
| `Skill.skill_id` | string | R | PK; `SKL-` plus three digits |
| `Skill.name` | string | R | Unique skill name |
| `Skill.category` | string | R | `technical`, `professional` |
| `CandidateSkill.candidate_id` | string | R | FK to Candidate; part of composite PK |
| `CandidateSkill.skill_id` | string | R | FK to Skill; part of composite PK |
| `CandidateSkill.proficiency` | string | R | `beginner`, `intermediate`, `advanced` |
| `CandidateSkill.years_experience` | decimal | R | >= 0; years |

### ScreeningRule

| Field | Type | Req. | Allowed values / uniqueness / validation |
|---|---|---:|---|
| `screening_rule_id` | string | R | PK; `SCR-` plus six digits |
| `requisition_id` | string | R | FK to JobRequisition |
| `minimum_match_pct` | integer | R | 0–100 |
| `required_skill_weight` | decimal | R | 0–1 |
| `experience_weight` | decimal | R | 0–1; weights sum to 1 |
| `effective_from` | date | R | ISO date |
| `effective_to` | date | O | Blank for currently effective; otherwise >= start |

### Interviewer and Interview

| Field | Type | Req. | Allowed values / uniqueness / validation |
|---|---|---:|---|
| `Interviewer.interviewer_id` | string | R | PK; `IVR-` plus four digits |
| `Interviewer.department_id` | string | R | FK to Department |
| `Interviewer.active` | boolean | R | `true`, `false` |
| `Interviewer.timezone` | string | R | IANA-style timezone string |
| `Interviewer.weekly_capacity` | integer | R | >= 1 interviews/week |
| `Interview.interview_id` | string | R | PK; `INT-2026-` plus six digits; injected conflict uses reserved high ID |
| `Interview.application_id` | string | R | FK to Application |
| `Interview.round_number` | integer | R | >= 1 |
| `Interview.interviewer_id` | string | R | FK to Interviewer |
| `Interview.scheduled_start` | timestamp | R | ISO local timestamp |
| `Interview.scheduled_end` | timestamp | R | Must be later than start |
| `Interview.status` | string | R | `completed`, `scheduled`, `cancelled` |
| `Interview.availability_checked` | boolean | R | False for the injected conflict |
| `Interview.issue_type` | string | O | Blank normally; `interviewer_conflict` for injected conflict |

### Feedback

| Field | Type | Req. | Allowed values / uniqueness / validation |
|---|---|---:|---|
| `feedback_id` | string | R | PK; `FB-<interview-id>-<interviewer-id>` |
| `interview_id` | string | R | FK to Interview |
| `interviewer_id` | string | R | FK to Interviewer |
| `technical_score` | integer | R | 1–5 |
| `communication_score` | integer | R | 1–5 |
| `problem_solving_score` | integer | R | 1–5 |
| `recommendation` | string | R | `hire`, `hold`, `no_hire` |
| `comments` | string | R | Synthetic comment; no sensitive details |
| `submitted_at` | timestamp | R | ISO local timestamp |
| `issue_type` | string | O | Blank normally |

### Offer and ApplicationEvent

| Field | Type | Req. | Allowed values / uniqueness / validation |
|---|---|---:|---|
| `Offer.offer_id` | string | R | PK; `OFF-2026-` plus six digits |
| `Offer.application_id` | string | R | FK to Application |
| `Offer.annual_salary_inr` | integer | R | INR/year; should be within requisition band |
| `Offer.currency` | string | R | `INR` |
| `Offer.created_at` | date | R | ISO date |
| `Offer.approval_status` | string | R | `approved`, `pending`, `rejected`; baseline offers are approved |
| `Offer.approved_by` | string | R | Synthetic approver ID |
| `Offer.offer_status` | string | R | `accepted`, `rejected`, `pending`, `expired` |
| `Offer.valid_until` | date | R | ISO date; should follow creation date |
| `Offer.issue_type` | string | O | `salary_outside_approved_band` for injected anomaly |
| `ApplicationEvent.event_id` | string | R | PK; `EVT-` plus seven digits |
| `ApplicationEvent.application_id` | string | R | References an application ID; includes deliberate edge-case IDs |
| `ApplicationEvent.from_stage` | string | O | Blank for initial event; otherwise valid prior stage |
| `ApplicationEvent.to_stage` | string | R | Valid application stage |
| `ApplicationEvent.event_at` | timestamp/date | R | ISO timestamp/date; should be chronological |
| `ApplicationEvent.actor` | string | R | Synthetic actor or workflow component |
| `ApplicationEvent.reason` | string | R | Human-readable transition reason |
