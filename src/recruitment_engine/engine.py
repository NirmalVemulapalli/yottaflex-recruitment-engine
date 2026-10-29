from __future__ import annotations
import argparse, csv, hashlib, json, random, sqlite3
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

SEED_DEFAULT = 20261022
TABLES = ["Department", "JobRequisition", "Candidate", "Skill", "CandidateSkill", "RequisitionSkill", "ResumeArtifact", "ScreeningRule", "Application", "Interviewer", "Interview", "Feedback", "Offer", "ApplicationEvent"]
DEPARTMENTS = ["Engineering", "Data", "Product", "Operations", "Finance", "Customer Success", "Security"]
SKILLS = ["Python", "SQL", "Java", "React", "Data Analysis", "Power BI", "Machine Learning", "AWS", "Communication", "Project Management", "Excel", "Spring Boot", "Statistics", "ETL", "Linux"]
ROLES = ["Data Analyst", "Software Engineer", "AI Engineer", "Backend Engineer", "BI Analyst", "ML Engineer", "Data Engineer", "QA Engineer", "Product Analyst", "Cloud Engineer"]
STAGES = ["applied", "screened", "interview", "interview_passed", "offer", "hired", "rejected", "withdrawn"]


def iso(d): return d.isoformat() if isinstance(d, (date, datetime)) else d

def write_csv(path: Path, rows):
    rows = list(rows)
    if not rows:
        path.write_text("", encoding="utf-8"); return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

def checksum(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""): h.update(chunk)
    return h.hexdigest()


def generate(out_dir: str | Path, seed=SEED_DEFAULT, scale=1):
    """Generate deterministic CSV/JSON data. scale=1 creates the required challenge volume."""
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    n_req, n_cand, n_apps, n_int, n_offers = 100*scale, 2000*scale, 3000*scale, 600*scale, 150*scale
    today = date(2026, 10, 28)
    departments = [{"department_id": f"DEP-{i:03d}", "name": name, "active": True} for i, name in enumerate(DEPARTMENTS, 1)]
    skills = [{"skill_id": f"SKL-{i:03d}", "name": name, "category": "technical" if name not in ("Communication", "Project Management") else "professional"} for i, name in enumerate(SKILLS, 1)]
    skill_id = {r["name"]: r["skill_id"] for r in skills}

    reqs=[]; req_skill_map={}; requisition_skills=[]; screening=[]
    for i in range(1, n_req+1):
        role = rng.choice(ROLES); dept = rng.choice(departments); level = rng.choice(["junior", "mid", "senior"])
        low = rng.choice([400000, 500000, 600000, 800000]); high = low + rng.choice([200000, 300000, 400000, 600000])
        created = today - timedelta(days=rng.randint(5, 300)); close = created + timedelta(days=rng.randint(30, 120))
        status = "closed" if i % 17 == 0 or close < today else "approved"
        rid=f"REQ-2026-{i:06d}"
        required = rng.sample(SKILLS, k=rng.randint(3, 5))
        reqs.append({"requisition_id":rid,"title":role,"department_id":dept["department_id"],"level":level,"status":status,"created_date":iso(created),"close_date":iso(close),"headcount":rng.randint(1,4),"salary_min_inr":low,"salary_max_inr":high,"approved_by":f"USR-{rng.randint(1,25):03d}","approval_status":"approved"})
        req_skill_map[rid]=required
        for priority, required_name in enumerate(required, 1):
            requisition_skills.append({"requisition_id":rid,"skill_id":skill_id[required_name],"requirement_priority":priority,"is_required":True})
        screening.append({"screening_rule_id":f"SCR-{i:06d}","requisition_id":rid,"minimum_match_pct":60,"required_skill_weight":0.8,"experience_weight":0.2,"effective_from":iso(created),"effective_to":""})

    candidates=[]; candidate_skills=[]; resumes=[]
    first_names=["Aarav","Diya","Ishaan","Anaya","Kabir","Meera","Arjun","Sana","Rohan","Tara","Dev","Mira","Kiran","Aditi","Nikhil","Ira"]
    last_names=["Shah","Rao","Patel","Reddy","Iyer","Khan","Das","Nair","Kapoor","Joshi","Sen","Mehta"]
    cand_skill_map={}
    for i in range(1,n_cand+1):
        cid=f"CAND-{i:06d}"; candidates.append({"candidate_id":cid,"full_name":f"{rng.choice(first_names)} {rng.choice(last_names)}","email":f"candidate{i:06d}@example.test","city":rng.choice(["Hyderabad","Bengaluru","Pune","Chennai","Vijayawada","Delhi","Remote"]),"experience_years":rng.randint(0,12),"created_date":iso(today-timedelta(days=rng.randint(1,400))),"profile_status":rng.choice(["active","active","active","inactive"])})
        owned=rng.sample(SKILLS,k=rng.randint(2,9)); cand_skill_map[cid]=set(owned)
        for sk in owned: candidate_skills.append({"candidate_id":cid,"skill_id":skill_id[sk],"proficiency":rng.choice(["beginner","intermediate","advanced"]),"years_experience":round(rng.uniform(0,6),1)})
        resumes.append({"resume_id":f"RES-{i:06d}","candidate_id":cid,"artifact_type":"synthetic_resume_metadata","file_name":f"resume_{i:06d}.pdf","storage_uri":f"local://synthetic/resume_{i:06d}.pdf","content_hash":hashlib.sha256(f"resume-{seed}-{i}".encode()).hexdigest(),"created_at":iso(today-timedelta(days=rng.randint(0,180))),"parsed_status":rng.choice(["parsed","parsed","parsed","needs_review"]),"source":"synthetic_generator"})

    interviewers=[]
    for i in range(1,121):
        interviewers.append({"interviewer_id":f"IVR-{i:04d}","department_id":rng.choice(departments)["department_id"],"active":True,"timezone":"Asia/Kolkata","weekly_capacity":rng.randint(3,8)})
    interviewer_ids=[x["interviewer_id"] for x in interviewers]

    # Choose 3,000 distinct application pairs first; a labelled duplicate is injected below.
    pairs=set(); apps=[]
    req_ids=[r["requisition_id"] for r in reqs]
    while len(pairs)<n_apps:
        pair=(rng.choice(req_ids),f"CAND-{rng.randint(1,n_cand):06d}")
        if pair not in pairs: pairs.add(pair)
    for i,(rid,cid) in enumerate(sorted(pairs),1):
        req=next(r for r in reqs if r["requisition_id"]==rid)
        owned=cand_skill_map[cid]; needed=req_skill_map[rid]
        match=sum(s in owned for s in needed)/len(needed)
        score=round(100*(0.8*match+0.2*min(1, next(c["experience_years"] for c in candidates if c["candidate_id"]==cid)/6)),2)
        status="applied" if req["status"]=="approved" else rng.choice(["rejected","withdrawn"])
        if status=="applied": status=rng.choices(["screened","interview","interview_passed","rejected","withdrawn"],[30,25,8,25,12])[0]
        appid=f"APP-{rid}-{cid}"
        apps.append({"application_id":appid,"requisition_id":rid,"candidate_id":cid,"applied_at":iso(today-timedelta(days=rng.randint(0,150))),"stage":status,"screening_score":score,"screening_decision":"pass" if score>=60 else "review_or_reject","withdrawn_at":iso(today-timedelta(days=rng.randint(0,10))) if status=="withdrawn" else "","issue_type":"","ground_truth":""})
    # Re-index app event IDs follow stable application IDs.
    app_by_id={a["application_id"]:a for a in apps}
    events=[]
    for a in apps:
        events.append({"event_id":f"EVT-{len(events)+1:07d}","application_id":a["application_id"],"from_stage":"","to_stage":"applied","event_at":a["applied_at"],"actor":"system","reason":"application_created"})
        if a["stage"]!="applied": events.append({"event_id":f"EVT-{len(events)+1:07d}","application_id":a["application_id"],"from_stage":"applied","to_stage":a["stage"],"event_at":a["applied_at"],"actor":"workflow_engine","reason":"synthetic_lifecycle"})

    interviews=[]; feedback=[]
    interview_apps=rng.sample(apps,k=min(n_int,len(apps)))
    # Spread interview start times across dates and use 45-minute slots.
    for i,a in enumerate(interview_apps,1):
        # Baseline scheduling is conflict-free: each interviewer is assigned at most
        # one interview per generated day. A labelled overlap is injected afterward.
        day=today-timedelta(days=(i-1)//len(interviewer_ids)); start=datetime.combine(day,datetime.min.time()).replace(hour=rng.choice([9,10,11,13,14,15,16]))
        interviewer=interviewer_ids[(i-1)%len(interviewer_ids)]
        interviews.append({"interview_id":f"INT-2026-{i:06d}","application_id":a["application_id"],"round_number":rng.choice([1,1,1,2,3]),"interviewer_id":interviewer,"scheduled_start":start.isoformat(timespec="minutes"),"scheduled_end":(start+timedelta(minutes=45)).isoformat(timespec="minutes"),"status":rng.choice(["completed","completed","scheduled","cancelled"]),"availability_checked":True,"issue_type":"","ground_truth":""})
        if interviews[-1]["status"]=="completed":
            score=rng.randint(1,5)
            feedback.append({"feedback_id":f"FB-{interviews[-1]['interview_id']}-{interviewer}","interview_id":interviews[-1]["interview_id"],"interviewer_id":interviewer,"technical_score":score,"communication_score":rng.randint(1,5),"problem_solving_score":rng.randint(1,5),"recommendation": "hire" if score>=4 else ("no_hire" if score<=2 else "hold"),"comments":"Synthetic structured feedback","submitted_at":(start+timedelta(hours=2)).isoformat(timespec="minutes"),"issue_type":"","ground_truth":""})

    offers=[]
    approved_requisition_ids={r["requisition_id"] for r in reqs if r["status"]=="approved" and r["approval_status"]=="approved"}
    eligible_offer_apps=[a for a in apps if a["requisition_id"] in approved_requisition_ids and a["stage"] not in ("rejected","withdrawn") and a.get("issue_type","")=="" and date.fromisoformat(a["applied_at"]) <= today-timedelta(days=30)]
    offer_apps=rng.sample(eligible_offer_apps,k=min(n_offers,len(eligible_offer_apps)))
    for i,a in enumerate(offer_apps,1):
        req=next(r for r in reqs if r["requisition_id"]==a["requisition_id"])
        salary=rng.randint(req["salary_min_inr"],req["salary_max_inr"])
        offer_status=rng.choice(["accepted","rejected","pending","expired"])
        previous_stage=a["stage"]
        a["stage"] = "hired" if offer_status=="accepted" else ("rejected" if offer_status=="rejected" else "offer")
        applied_date=date.fromisoformat(a["applied_at"])
        offer_created_date=applied_date+timedelta(days=rng.randint(1,min(20,(today-applied_date).days)))
        offer_created=iso(offer_created_date)
        if previous_stage != a["stage"]:
            events.append({"event_id":f"EVT-{len(events)+1:07d}","application_id":a["application_id"],"from_stage":previous_stage,"to_stage":a["stage"],"event_at":offer_created,"actor":"offer_workflow","reason":"approved_offer_"+offer_status})
        offers.append({"offer_id":f"OFF-2026-{i:06d}","application_id":a["application_id"],"annual_salary_inr":salary,"currency":"INR","created_at":offer_created,"approval_status":"approved","approved_by":f"USR-{rng.randint(1,25):03d}","offer_status":offer_status,"valid_until":iso(offer_created_date+timedelta(days=rng.randint(7,30))),"issue_type":"","ground_truth":""})

    # Labelled exception injections: intentionally visible in data and ground_truth.
    truth=[]
    def label(issue, entity, entity_id, expected, detail): truth.append({"issue_type":issue,"entity_type":entity,"entity_id":entity_id,"expected_decision":expected,"description":detail})
    if apps:
        src=apps[0]; dup=dict(src); dup["issue_type"]="duplicate_application"; dup["ground_truth"]="duplicate_of:"+src["application_id"]; dup["application_id"] += "-DUP01"; apps.append(dup)
        label("duplicate_application","Application",dup["application_id"],"flag_duplicate","Same requisition-candidate pair as "+src["application_id"])
    if interviews:
        # Add a clearly labelled conflicting event without rewriting a valid baseline interview.
        x=interviews[0]
        x_start=datetime.fromisoformat(x["scheduled_start"])
        y=dict(x)
        y["interview_id"]="INT-2026-999999"
        y["application_id"]=interviews[1]["application_id"] if len(interviews)>1 else x["application_id"]
        y["scheduled_start"]=(x_start+timedelta(minutes=15)).isoformat(timespec="minutes")
        y["scheduled_end"]=(x_start+timedelta(minutes=60)).isoformat(timespec="minutes")
        y["availability_checked"]=False
        y["issue_type"]="interviewer_conflict"
        y["ground_truth"]="conflict_with:"+x["interview_id"]
        interviews.append(y)
        label("interviewer_conflict","Interview",y["interview_id"],"flag_schedule_conflict","Overlaps another interview for the same interviewer; baseline interview remains unchanged")
    if apps and interviews:
        approved_req_ids={r["requisition_id"] for r in reqs if r["status"]=="approved"}
        missing_interview=next((it for it in interviews if next(a for a in apps if a["application_id"]==it["application_id"])["requisition_id"] in approved_req_ids), interviews[0])
        missing_interview["status"]="completed"
        missing_app=next(a for a in apps if a["application_id"]==missing_interview["application_id"])
        feedback[:]=[f for f in feedback if f["interview_id"]!=missing_interview["interview_id"]]
        old_stage=missing_app["stage"]
        missing_app["stage"]="interview_passed"; missing_app["issue_type"]="missing_feedback_stage_advanced"; missing_app["ground_truth"]="feedback_required"
        events.append({"event_id":f"EVT-{len(events)+1:07d}","application_id":missing_app["application_id"],"from_stage":old_stage,"to_stage":"interview_passed","event_at":iso(today),"actor":"synthetic_edge_case","reason":"deliberate_missing_feedback_transition"})
        label("missing_feedback_stage_advanced","Application",missing_app["application_id"],"block_transition","Stage advanced without required structured feedback")
    if offers:
        o=offers[0]; req=next(r for r in reqs if r["requisition_id"]==app_by_id[o["application_id"]]["requisition_id"]); o["annual_salary_inr"]=req["salary_max_inr"]+500000; o["issue_type"]="salary_outside_approved_band"; o["ground_truth"]="salary_exceeds_max"
        label("salary_outside_approved_band","Offer",o["offer_id"],"reject_or_escalate","Salary exceeds requisition approved maximum")
    closed=next((r for r in reqs if r["status"]=="closed"),None)
    if closed:
        active=next((a for a in apps if a["requisition_id"]==closed["requisition_id"] and a["stage"] not in ("rejected","withdrawn")),None)
        if active is None:
            candidate=next(c for c in candidates if c["candidate_id"] not in {a["candidate_id"] for a in apps if a["requisition_id"]==closed["requisition_id"]})
            active={"application_id":f"APP-{closed['requisition_id']}-{candidate['candidate_id']}-EDGE01","requisition_id":closed["requisition_id"],"candidate_id":candidate["candidate_id"],"applied_at":iso(today-timedelta(days=1)),"stage":"interview","screening_score":75.0,"screening_decision":"pass","withdrawn_at":"","issue_type":"closed_role_active_application","ground_truth":"role_closed"}; apps.append(active)
            events.append({"event_id":f"EVT-{len(events)+1:07d}","application_id":active["application_id"],"from_stage":"","to_stage":"interview","event_at":active["applied_at"],"actor":"synthetic_edge_case","reason":"deliberate_active_application_on_closed_role"})
        else: active["issue_type"]="closed_role_active_application"; active["ground_truth"]="role_closed"
        label("closed_role_active_application","Application",active["application_id"],"flag_or_close_application","Application remains active after requisition closure")

    # Rebuild lifecycle history from each application's final state so events tell a coherent story.
    # Ground-truth labels remain separate and are not copied into event features.
    events=[]
    stage_path={
        "applied":[],
        "screened":["screened"],
        "interview":["screened","interview"],
        "interview_passed":["screened","interview","interview_passed"],
        "offer":["screened","interview","interview_passed","offer"],
        "hired":["screened","interview","interview_passed","offer","hired"],
        "rejected":["rejected"],
        "withdrawn":["withdrawn"],
    }
    for app in apps:
        applied_day=date.fromisoformat(app["applied_at"])
        sequence=["applied"]+stage_path[app["stage"]]
        previous=""
        for step, stage in enumerate(sequence):
            # Keep event time on/after application date and no later than the fixed dataset date.
            event_day=min(today, applied_day+timedelta(days=min(step, max(0,(today-applied_day).days))))
            event_time=datetime.combine(event_day,datetime.min.time()).replace(hour=9+step)
            if step==0:
                actor,reason="system","application_created"
            else:
                actor,reason="workflow_engine","valid_lifecycle_transition"
            if step==len(sequence)-1 and app.get("issue_type")=="missing_feedback_stage_advanced":
                actor,reason="synthetic_edge_case","deliberate_missing_feedback_transition"
            events.append({"event_id":f"EVT-{len(events)+1:07d}","application_id":app["application_id"],"from_stage":previous,"to_stage":stage,"event_at":event_time.isoformat(timespec="minutes"),"actor":actor,"reason":reason})
            previous=stage

    data={"Department":departments,"JobRequisition":reqs,"Candidate":candidates,"Skill":skills,"RequisitionSkill":requisition_skills,"CandidateSkill":candidate_skills,"ResumeArtifact":resumes,"ScreeningRule":screening,"Application":apps,"Interviewer":interviewers,"Interview":interviews,"Feedback":feedback,"Offer":offers,"ApplicationEvent":events}
    # Export CSV and JSON; data rows contain no ground_truth table in operational inputs.
    operational_data = {name: [{k: v for k, v in row.items() if k != "ground_truth"} for row in rows] for name, rows in data.items()}
    for name, rows in operational_data.items():
        write_csv(out/f"{name}.csv", rows)
        (out/f"{name}.json").write_text(json.dumps(rows,indent=2),encoding="utf-8")
    (out/"ground_truth.json").write_text(json.dumps(truth,indent=2),encoding="utf-8")
    write_csv(out/"ground_truth.csv",truth)
    schema_sql = """PRAGMA foreign_keys=ON;
CREATE TABLE Department(department_id TEXT PRIMARY KEY, name TEXT UNIQUE NOT NULL, active INTEGER NOT NULL);
CREATE TABLE JobRequisition(requisition_id TEXT PRIMARY KEY, title TEXT NOT NULL, department_id TEXT NOT NULL REFERENCES Department(department_id), level TEXT NOT NULL, status TEXT NOT NULL, created_date TEXT NOT NULL, close_date TEXT NOT NULL, headcount INTEGER NOT NULL, salary_min_inr INTEGER NOT NULL, salary_max_inr INTEGER NOT NULL, approved_by TEXT NOT NULL, approval_status TEXT NOT NULL);
CREATE TABLE Candidate(candidate_id TEXT PRIMARY KEY, full_name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, city TEXT NOT NULL, experience_years INTEGER NOT NULL, created_date TEXT NOT NULL, profile_status TEXT NOT NULL);
CREATE TABLE Skill(skill_id TEXT PRIMARY KEY, name TEXT UNIQUE NOT NULL, category TEXT NOT NULL);
CREATE TABLE RequisitionSkill(requisition_id TEXT NOT NULL REFERENCES JobRequisition(requisition_id), skill_id TEXT NOT NULL REFERENCES Skill(skill_id), requirement_priority INTEGER NOT NULL CHECK(requirement_priority > 0), is_required INTEGER NOT NULL CHECK(is_required IN (0,1)), PRIMARY KEY(requisition_id,skill_id));
CREATE TABLE CandidateSkill(candidate_id TEXT REFERENCES Candidate(candidate_id), skill_id TEXT REFERENCES Skill(skill_id), proficiency TEXT NOT NULL, years_experience REAL NOT NULL, PRIMARY KEY(candidate_id,skill_id));
CREATE TABLE ResumeArtifact(resume_id TEXT PRIMARY KEY, candidate_id TEXT NOT NULL REFERENCES Candidate(candidate_id), artifact_type TEXT NOT NULL, file_name TEXT NOT NULL, storage_uri TEXT NOT NULL, content_hash TEXT NOT NULL, created_at TEXT NOT NULL, parsed_status TEXT NOT NULL, source TEXT NOT NULL);
CREATE TABLE ScreeningRule(screening_rule_id TEXT PRIMARY KEY, requisition_id TEXT NOT NULL REFERENCES JobRequisition(requisition_id), minimum_match_pct INTEGER NOT NULL, required_skill_weight REAL NOT NULL, experience_weight REAL NOT NULL, effective_from TEXT NOT NULL, effective_to TEXT);
CREATE TABLE Application(application_id TEXT PRIMARY KEY, requisition_id TEXT NOT NULL REFERENCES JobRequisition(requisition_id), candidate_id TEXT NOT NULL REFERENCES Candidate(candidate_id), applied_at TEXT NOT NULL, stage TEXT NOT NULL, screening_score REAL NOT NULL, screening_decision TEXT NOT NULL, withdrawn_at TEXT, issue_type TEXT);
CREATE TABLE Interviewer(interviewer_id TEXT PRIMARY KEY, department_id TEXT NOT NULL REFERENCES Department(department_id), active INTEGER NOT NULL, timezone TEXT NOT NULL, weekly_capacity INTEGER NOT NULL);
CREATE TABLE Interview(interview_id TEXT PRIMARY KEY, application_id TEXT NOT NULL REFERENCES Application(application_id), round_number INTEGER NOT NULL, interviewer_id TEXT NOT NULL REFERENCES Interviewer(interviewer_id), scheduled_start TEXT NOT NULL, scheduled_end TEXT NOT NULL, status TEXT NOT NULL, availability_checked INTEGER NOT NULL, issue_type TEXT);
CREATE TABLE Feedback(feedback_id TEXT PRIMARY KEY, interview_id TEXT NOT NULL REFERENCES Interview(interview_id), interviewer_id TEXT NOT NULL REFERENCES Interviewer(interviewer_id), technical_score INTEGER NOT NULL, communication_score INTEGER NOT NULL, problem_solving_score INTEGER NOT NULL, recommendation TEXT NOT NULL, comments TEXT NOT NULL, submitted_at TEXT NOT NULL, issue_type TEXT);
CREATE TABLE Offer(offer_id TEXT PRIMARY KEY, application_id TEXT NOT NULL REFERENCES Application(application_id), annual_salary_inr INTEGER NOT NULL, currency TEXT NOT NULL, created_at TEXT NOT NULL, approval_status TEXT NOT NULL, approved_by TEXT NOT NULL, offer_status TEXT NOT NULL, valid_until TEXT NOT NULL, issue_type TEXT);
CREATE TABLE ApplicationEvent(event_id TEXT PRIMARY KEY, application_id TEXT NOT NULL REFERENCES Application(application_id), from_stage TEXT, to_stage TEXT NOT NULL, event_at TEXT NOT NULL, actor TEXT NOT NULL, reason TEXT NOT NULL);
"""
    (out/"schema.sql").write_text(schema_sql,encoding="utf-8")
    # Build a portable SQLite seed database from the same generated rows.
    db_path = out / "recruitment_seed.sqlite"
    if db_path.exists(): db_path.unlink()
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(schema_sql)
        for table, rows in operational_data.items():
            if not rows: continue
            columns = list(rows[0].keys())
            placeholders = ",".join(["?"] * len(columns))
            quoted_cols = ",".join('"' + c + '"' for c in columns)
            # Keep the intentionally labelled anomaly records available for audit.
            conn.executemany(f'INSERT INTO "{table}" ({quoted_cols}) VALUES ({placeholders})', [[r.get(c) for c in columns] for r in rows])
        conn.commit()
    finally: conn.close()
    validation=validate_data(data)
    (out/"validation_summary.json").write_text(json.dumps(validation,indent=2),encoding="utf-8")
    # Produce an audit report and derived operational metrics from source records.
    audit(out)
    req_by_id={r["requisition_id"]:r for r in reqs}
    app_by_id_final={r["application_id"]:r for r in apps}
    completed_interviews=[r for r in interviews if r["status"]=="completed"]
    feedback_interview_ids={r["interview_id"] for r in feedback}
    in_band=0
    for offer in offers:
        app=app_by_id_final.get(offer["application_id"])
        req=req_by_id.get(app["requisition_id"]) if app else None
        if req and req["salary_min_inr"]<=offer["annual_salary_inr"]<=req["salary_max_inr"]: in_band+=1
    stage_counts=dict(Counter(a["stage"] for a in apps))
    metrics={
        "application_count":len(apps),
        "screening_pass_rate_pct":round(100*sum(a["screening_decision"]=="pass" for a in apps)/max(1,len(apps)),2),
        "average_screening_score":round(sum(a["screening_score"] for a in apps)/max(1,len(apps)),2),
        "application_stage_distribution":stage_counts,
        "withdrawn_application_rate_pct":round(100*sum(a["stage"]=="withdrawn" for a in apps)/max(1,len(apps)),2),
        "interview_count":len(interviews),
        "completed_interview_count":len(completed_interviews),
        "completed_interview_feedback_coverage_pct":round(100*sum(i["interview_id"] in feedback_interview_ids for i in completed_interviews)/max(1,len(completed_interviews)),2),
        "offer_count":len(offers),
        "offer_acceptance_rate_pct":round(100*sum(o["offer_status"]=="accepted" for o in offers)/max(1,len(offers)),2),
        "offers_within_salary_band_pct":round(100*in_band/max(1,len(offers)),2),
        "currency":"INR",
        "notes":["Metrics are derived from generated operational records.","The deliberately injected salary-band exception is included in offers_within_salary_band_pct.","These are synthetic demonstration metrics, not real-world hiring benchmarks."]
    }
    (out/"metrics_summary.json").write_text(json.dumps(metrics,indent=2),encoding="utf-8")
    source_manifest={
        "provenance":"fully synthetic data generated by this repository",
        "external_datasets_used":False,
        "source_urls":[],
        "license_or_terms":"Not applicable; no external dataset used",
        "retrieval_date":"Not applicable",
        "seed":seed,
        "scale":scale,
        "generator_version":"1.1.0",
        "generation_command":f"python -m recruitment_engine.engine generate --out data/generated --seed {seed} --scale {scale}",
        "synthetic_fields":["names","emails using example.test","cities","experience","skills","applications","interviews","feedback","offers","approval identifiers","resume metadata"],
        "sensitive_or_real_candidate_data_included":False
    }
    (out/"source_manifest.json").write_text(json.dumps(source_manifest,indent=2),encoding="utf-8")
    manifest={"seed":seed,"scale":scale,"generator_version":"1.1.0","counts":{k:len(v) for k,v in data.items()},"ground_truth_count":len(truth),"checksums":{p.name:checksum(p) for p in sorted(out.iterdir()) if p.is_file() and p.name not in ("manifest.json",)}}
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    return manifest


def validate_data(data):
    """Validate keys, joins, enums, date ordering, derived-value bounds and lifecycle basics."""
    errors=[]; warnings=[]
    pk_fields={"Department":"department_id","JobRequisition":"requisition_id","Candidate":"candidate_id","Skill":"skill_id","ResumeArtifact":"resume_id","ScreeningRule":"screening_rule_id","Application":"application_id","Interviewer":"interviewer_id","Interview":"interview_id","Feedback":"feedback_id","Offer":"offer_id","ApplicationEvent":"event_id"}
    ids={}
    for table, field in pk_fields.items():
        rows=data.get(table,[]); vals=[r.get(field) for r in rows]
        if any(v in (None,"") for v in vals): errors.append(f"{table}: missing primary key")
        if len(vals)!=len(set(vals)): errors.append(f"{table}: duplicate primary key")
        ids[table]=set(vals)

    departments={r["department_id"] for r in data.get("Department",[])}
    reqs={r["requisition_id"]:r for r in data.get("JobRequisition",[])}
    candidates={r["candidate_id"]:r for r in data.get("Candidate",[])}
    skills={r["skill_id"] for r in data.get("Skill",[])}
    apps={r["application_id"]:r for r in data.get("Application",[])}
    interviewers={r["interviewer_id"]:r for r in data.get("Interviewer",[])}
    interviews={r["interview_id"]:r for r in data.get("Interview",[])}
    allowed_stages=set(STAGES)
    allowed_requisition_status={"approved","closed"}
    allowed_interview_status={"completed","scheduled","cancelled"}
    allowed_offer_status={"accepted","rejected","pending","expired"}
    allowed_feedback_recommendations={"hire","hold","no_hire"}

    for r in data.get("JobRequisition",[]):
        if r.get("department_id") not in departments: errors.append("JobRequisition: invalid department FK")
        if r.get("salary_min_inr",0)<=0 or r.get("salary_min_inr",0)>r.get("salary_max_inr",0): errors.append("JobRequisition: invalid salary band")
        if r.get("created_date","")>r.get("close_date",""): errors.append("JobRequisition: invalid date ordering")
        if r.get("status") not in allowed_requisition_status: errors.append("JobRequisition: invalid status")
        if r.get("approval_status")!="approved": errors.append("JobRequisition: requisition is not approved")
        if r.get("headcount",0)<1: errors.append("JobRequisition: headcount must be positive")
    for r in data.get("Candidate",[]):
        if not 0<=r.get("experience_years",-1)<=60: errors.append("Candidate: experience outside supported bounds")
    for r in data.get("CandidateSkill",[]):
        if r.get("candidate_id") not in candidates or r.get("skill_id") not in skills: errors.append("CandidateSkill: invalid FK")
        if r.get("proficiency") not in {"beginner","intermediate","advanced"}: errors.append("CandidateSkill: invalid proficiency")
        if r.get("years_experience",-1)<0: errors.append("CandidateSkill: negative skill experience")
    seen_requisition_skills=set()
    for r in data.get("RequisitionSkill",[]):
        pair=(r.get("requisition_id"),r.get("skill_id"))
        if pair in seen_requisition_skills: errors.append("RequisitionSkill: duplicate requisition-skill pair")
        seen_requisition_skills.add(pair)
        if r.get("requisition_id") not in reqs or r.get("skill_id") not in skills: errors.append("RequisitionSkill: invalid parent FK")
        if r.get("requirement_priority",0)<=0: errors.append("RequisitionSkill: priority must be positive")
    for r in data.get("ResumeArtifact",[]):
        if r.get("candidate_id") not in candidates: errors.append("ResumeArtifact: invalid candidate FK")
        if not r.get("content_hash"): errors.append("ResumeArtifact: missing content hash")
    for r in data.get("ScreeningRule",[]):
        if r.get("requisition_id") not in reqs: errors.append("ScreeningRule: invalid requisition FK")
        if not 0<=r.get("minimum_match_pct",-1)<=100: errors.append("ScreeningRule: minimum match outside 0..100")
        if abs(r.get("required_skill_weight",0)+r.get("experience_weight",0)-1.0)>1e-9: errors.append("ScreeningRule: weights must sum to 1")
        if r.get("effective_to") and r.get("effective_from","")>r["effective_to"]: errors.append("ScreeningRule: invalid effective dates")
    for r in data.get("Application",[]):
        if r.get("requisition_id") not in reqs or r.get("candidate_id") not in candidates: errors.append("Application: invalid parent FK")
        if r.get("stage") not in allowed_stages: errors.append("Application: invalid stage")
        if not 0<=r.get("screening_score",-1)<=100: errors.append("Application: screening score outside 0..100")
        if r.get("screening_decision") not in {"pass","review_or_reject"}: errors.append("Application: invalid screening decision")
        if r.get("stage")=="withdrawn" and not r.get("withdrawn_at"): warnings.append("Application: withdrawn stage has no withdrawn_at date")
    for r in data.get("Interviewer",[]):
        if r.get("department_id") not in departments: errors.append("Interviewer: invalid department FK")
        if r.get("weekly_capacity",0)<=0: errors.append("Interviewer: weekly capacity must be positive")
    for r in data.get("Interview",[]):
        if r.get("application_id") not in apps or r.get("interviewer_id") not in interviewers: errors.append("Interview: invalid parent FK")
        if r.get("scheduled_start","")>=r.get("scheduled_end",""): errors.append("Interview: invalid date ordering")
        if r.get("round_number",0)<1: errors.append("Interview: round number must be positive")
        if r.get("status") not in allowed_interview_status: errors.append("Interview: invalid status")
    for r in data.get("Feedback",[]):
        if r.get("interview_id") not in interviews or r.get("interviewer_id") not in interviewers: errors.append("Feedback: invalid parent FK")
        for field in ("technical_score","communication_score","problem_solving_score"):
            if not 1<=r.get(field,0)<=5: errors.append("Feedback: score outside 1..5")
        if r.get("recommendation") not in allowed_feedback_recommendations: errors.append("Feedback: invalid recommendation")
        if r.get("interview_id") in interviews and r.get("interviewer_id")!=interviews[r["interview_id"]].get("interviewer_id"):
            warnings.append("Feedback: interviewer differs from the single assigned interviewer; verify panel mapping")
    for r in data.get("Offer",[]):
        if r.get("application_id") not in apps: errors.append("Offer: invalid application FK")
        if r.get("annual_salary_inr",0)<=0: errors.append("Offer: salary must be positive")
        if r.get("approval_status")!="approved" or not r.get("approved_by"): errors.append("Offer: missing required approval")
        if r.get("offer_status") not in allowed_offer_status: errors.append("Offer: invalid status")
        if r.get("created_at","")>r.get("valid_until",""): errors.append("Offer: validity ends before creation")
    transitions={
        "applied":{"screened","rejected","withdrawn"},
        "screened":{"interview","rejected","withdrawn"},
        "interview":{"interview_passed","rejected","withdrawn"},
        "interview_passed":{"offer","rejected","withdrawn"},
        "offer":{"hired","rejected","withdrawn"},
        "hired":set(),"rejected":set(),"withdrawn":set(),
    }
    for r in data.get("ApplicationEvent",[]):
        if r.get("application_id") not in apps: errors.append("ApplicationEvent: invalid application FK")
        if r.get("to_stage") not in allowed_stages: errors.append("ApplicationEvent: invalid target stage")
        if r.get("from_stage") and r.get("from_stage") not in allowed_stages: errors.append("ApplicationEvent: invalid source stage")
        if r.get("from_stage") and r.get("to_stage") not in transitions.get(r["from_stage"],set()):
            errors.append("ApplicationEvent: disallowed lifecycle transition")

    pair_counts=Counter((a["requisition_id"],a["candidate_id"]) for a in data.get("Application",[]))
    duplicate_pairs=sum(1 for n in pair_counts.values() if n>1)
    return {"status":"PASS" if not errors else "FAIL","errors":errors,"warnings":warnings,"checks":{"primary_key_uniqueness":"completed","foreign_key_integrity":"completed","allowed_enums":"completed","date_ordering":"completed","salary_and_score_bounds":"completed","approval_presence":"completed","duplicate_application_pairs_detected":duplicate_pairs},"notes":["Known injected anomalies are expected and listed separately in ground_truth.csv/json.","Business-rule findings are computed separately by the audit command.","Warnings identify expected or reviewable edge-case conditions; validation errors indicate structural or invariant failures."]}


def audit(out_dir: str | Path):
    out=Path(out_dir)
    def read(name):
        with (out/f"{name}.json").open(encoding="utf-8") as f:return json.load(f)
    apps=read("Application"); reqs={r["requisition_id"]:r for r in read("JobRequisition")}; interviews=read("Interview"); feedback=read("Feedback"); offers=read("Offer")
    feedback_interviews={f["interview_id"] for f in feedback}
    findings=[]
    seen=defaultdict(list)
    for a in apps: seen[(a["requisition_id"],a["candidate_id"])].append(a["application_id"])
    for pair, ids in seen.items():
        if len(ids)>1: findings.append({"rule":"duplicate_application_pair","severity":"high","entity_ids":ids,"details":f"Duplicate pair {pair[0]} / {pair[1]}"})
    by_interviewer=defaultdict(list)
    for it in interviews: by_interviewer[it["interviewer_id"]].append(it)
    for iid, items in by_interviewer.items():
        items.sort(key=lambda x:x["scheduled_start"])
        active=[]
        for current in items:
            active=[prior for prior in active if prior["scheduled_end"]>current["scheduled_start"]]
            for prior in active:
                findings.append({"rule":"interviewer_time_conflict","severity":"high","entity_ids":[prior["interview_id"],current["interview_id"]],"details":f"Overlapping slots for {iid}"})
            active.append(current)
    for a in apps:
        if a["stage"]=="interview_passed":
            related=[it for it in interviews if it["application_id"]==a["application_id"] and it["status"]=="completed"]
            if related and any(it["interview_id"] not in feedback_interviews for it in related): findings.append({"rule":"missing_feedback_before_progression","severity":"high","entity_ids":[a["application_id"]],"details":"Application advanced despite missing feedback"})
        if reqs[a["requisition_id"]]["status"]=="closed" and a["stage"] not in ("rejected","withdrawn"):
            findings.append({"rule":"active_application_on_closed_role","severity":"medium","entity_ids":[a["application_id"]],"details":"Application is active while requisition is closed"})
    for o in offers:
        a=next((x for x in apps if x["application_id"]==o["application_id"]),None)
        if a and (o["annual_salary_inr"]<reqs[a["requisition_id"]]["salary_min_inr"] or o["annual_salary_inr"]>reqs[a["requisition_id"]]["salary_max_inr"]): findings.append({"rule":"offer_salary_outside_band","severity":"high","entity_ids":[o["offer_id"]],"details":"Offer salary outside approved requisition band"})
    report={"findings_count":len(findings),"by_rule":dict(Counter(x["rule"] for x in findings)),"by_severity":dict(Counter(x["severity"] for x in findings)),"findings":findings}
    (out/"anomaly_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    (out/"anomaly_report.csv").write_text("rule,severity,entity_ids,details\n"+"".join(f'"{x["rule"]}","{x["severity"]}","{";".join(x["entity_ids"])}","{x["details"]}"\n' for x in findings),encoding="utf-8")
    return report


def main():
    p=argparse.ArgumentParser(description="Generate and audit synthetic recruitment workflow data")
    sub=p.add_subparsers(dest="cmd",required=True)
    g=sub.add_parser("generate");g.add_argument("--out",default="data/generated");g.add_argument("--seed",type=int,default=SEED_DEFAULT);g.add_argument("--scale",type=int,default=1)
    a=sub.add_parser("audit");a.add_argument("--data",default="data/generated")
    args=p.parse_args()
    if args.cmd=="generate":
        m=generate(args.out,args.seed,args.scale); print(json.dumps({"generated":args.out,"seed":args.seed,"counts":m["counts"]},indent=2))
    else: print(json.dumps(audit(args.data),indent=2))
if __name__=="__main__": main()
