
import json
import streamlit as st
from app.skill_extractor_dl import load_alias_map, detect_job_role

def skill_importance_weights(required_skills, job_role, skill_master_path="data/skill_master.json"):
    with open(skill_master_path, "r") as f:
        master = json.load(f)

    if "skills" in master:
        master = master["skills"]

    alias_map = {}
    for skill, meta in master.items():
        alias_map[skill.lower()] = skill
        for alias in meta.get("alias", []):
            alias_map[alias.lower()] = skill

    weights = {}
    for s in required_skills:
        normalized = alias_map.get(s.lower().strip(), s.strip())
        weights[normalized] = master.get(normalized, {}).get("weight", 1)
    return weights

def calculate_readiness(resume_text, quiz_score=0, total_quiz_questions=10, matched_resume_skills=None, skill_master_path="data/skill_master.json"):
    # Step 1: Detect job role, fallback to Data Scientist
    try:
        job_role = detect_job_role(resume_text, skill_master_path)
    except Exception:
        job_role = "Data Scientist"

    # Step 2: Load role-specific skills from skill_master.json
    with open(skill_master_path, "r") as f:
        skill_master = json.load(f)
    required_skills = skill_master.get("roles", {}).get(job_role, [])

    # Step 3: Normalize and compute skill match
    alias_map = load_alias_map(skill_master_path)
    normalized_required = [alias_map.get(s.lower(), s) for s in required_skills]
    normalized_matched = set(alias_map.get(s.lower(), s) for s in (matched_resume_skills or []))
    matched_skills = set(normalized_required) & normalized_matched

    # Step 4: Use WEIGHTED coverage and boost formula
    weights = skill_importance_weights(required_skills, job_role, skill_master_path)
    total_weight = sum(weights.get(skill, 1) for skill in normalized_required)
    weighted_score = sum(weights.get(skill, 1) for skill in matched_skills)
    coverage = weighted_score / total_weight if total_weight else 0
    resume_component = 7 * min(1.0, coverage * 2.5)

    # Step 5: Quiz contribution
    # Convert 10-scaled quiz score to raw correct count
    quiz_score = (st.session_state.quiz_score / 10) * st.session_state.total_quiz_questions

    quiz_component = (quiz_score / total_quiz_questions) * 3 if total_quiz_questions else 0
    final_score = resume_component + quiz_component

    return {
        "final_score": round(min(final_score, 10), 2),
        "skill_component": round(resume_component, 2),
        "quiz_component": round(quiz_component, 2),
        "resume_component": round(resume_component, 2),
        "job_role": job_role
    }
