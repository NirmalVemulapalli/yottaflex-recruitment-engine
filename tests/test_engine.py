import json
from pathlib import Path
from recruitment_engine.engine import generate, validate_data, audit


def test_generator_reproducible_counts_and_ground_truth(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    ma = generate(a, seed=20261022, scale=1)
    mb = generate(b, seed=20261022, scale=1)
    assert ma["counts"] == mb["counts"]
    files_a = {p.name for p in a.iterdir() if p.is_file()}
    files_b = {p.name for p in b.iterdir() if p.is_file()}
    assert files_a == files_b
    for filename in sorted(files_a):
        assert (a / filename).read_bytes() == (b / filename).read_bytes(), filename
    assert ma["counts"]["JobRequisition"] == 100
    assert ma["counts"]["Candidate"] == 2000
    assert ma["counts"]["Application"] >= 3000
    assert ma["counts"]["Interview"] >= 600
    assert ma["counts"]["Offer"] == 150
    assert ma["counts"]["Department"] >= 1
    assert ma["counts"]["ResumeArtifact"] == 2000
    assert ma["counts"]["RequisitionSkill"] >= 300
    assert ma["counts"]["ApplicationEvent"] >= ma["counts"]["Application"]
    validation = json.loads((a / "validation_summary.json").read_text())
    assert validation["status"] == "PASS", validation["errors"]
    assert validation["errors"] == []
    metrics = json.loads((a / "metrics_summary.json").read_text())
    assert metrics["application_count"] == ma["counts"]["Application"]
    assert 0 <= metrics["screening_pass_rate_pct"] <= 100
    source_manifest = json.loads((a / "source_manifest.json").read_text())
    assert source_manifest["external_datasets_used"] is False
    operational_app = json.loads((a / "Application.json").read_text())
    assert all("ground_truth" not in row for row in operational_app)
    truth = json.loads((a / "ground_truth.json").read_text())
    assert {x["issue_type"] for x in truth} >= {
        "duplicate_application", "interviewer_conflict", "missing_feedback_stage_advanced",
        "salary_outside_approved_band", "closed_role_active_application"
    }


def test_validation_and_audit_find_known_issues(tmp_path):
    out = tmp_path / "data"
    generate(out)
    report = audit(out)
    assert report["findings_count"] > 0
    assert {
        "offer_salary_outside_band",
        "duplicate_application_pair",
        "interviewer_time_conflict",
        "missing_feedback_before_progression",
        "active_application_on_closed_role",
    } <= set(report["by_rule"])
    assert report["findings_count"] >= 5



def test_sqlite_integrity_and_lifecycle_transitions(tmp_path):
    import sqlite3
    out = tmp_path / "data"
    generate(out)
    conn = sqlite3.connect(out / "recruitment_seed.sqlite")
    try:
        assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
        table_names = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert {"Department", "JobRequisition", "Candidate", "Skill", "RequisitionSkill", "CandidateSkill", "Application", "Interview", "Feedback", "Offer", "ApplicationEvent"} <= table_names
    finally:
        conn.close()

    events = json.loads((out / "ApplicationEvent.json").read_text())
    allowed = {
        "applied": {"screened", "rejected", "withdrawn"},
        "screened": {"interview", "rejected", "withdrawn"},
        "interview": {"interview_passed", "rejected", "withdrawn"},
        "interview_passed": {"offer", "rejected", "withdrawn"},
        "offer": {"hired", "rejected", "withdrawn"},
        "hired": set(), "rejected": set(), "withdrawn": set(),
    }
    for event in events:
        if event["from_stage"]:
            assert event["to_stage"] in allowed[event["from_stage"]], event
