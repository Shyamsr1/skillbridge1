
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
from datetime import datetime
from app import (
    db_dl_integration as db,
    resume_parser_dl,
    readiness_eval_updated as readiness_eval,
    skill_extractor_dl,
    skill_recommender_dl,
    quiz_bank,
    skill_gap_dl,
    dashboard_dl,
    resume_classifier,
    extract_skills_dl_v2
)

from app.dashboard_dl import plot_skill_coverage_dl, plot_readiness_bar_dl, generate_pdf_with_reportlab
from app.resume_parser_dl import extract_text_from_pdf
from app.skill_extractor_dl import detect_job_role
from app.skill_gap_dl import identify_skill_gaps_dl
from app.skill_recommender_dl import recommend_learning_paths, recommend_missing_skills, recommend_skills
from app.extract_skills_dl_v2 import extract_skills_dl_v2, load_alias_map

st.set_page_config(page_title="SkillBridge DL", layout="wide")

# --- Session State Initialization ---
def initialize_session():
    keys_defaults = {
        "logged_in": False,
        "quiz_completed": False,
        "quiz_submitted": False,
        "skill_ratings": {},
        "quiz_score": 0,
        "username": "",
        "resume_file": None,
        "extracted_skills": [],
        "predicted_role": None
    }
    for k, v in keys_defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
st.title("🤖 SkillBridge DL Edition")

initialize_session()
if not st.session_state.get("logged_in", False):
        
        st.markdown("### 🧠 AI + Data Science Career Readiness Platform")
        st.markdown("### ⚠️ Kindly Login or Register to access the platform features. ")

# --- Auth ---
if not st.session_state.logged_in:
    st.sidebar.header("Login or Register")
    username = st.sidebar.text_input("Username")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    language = st.sidebar.selectbox("Language Preference", ["en"])

    if st.sidebar.button("Register"):
        if not username or not email or not password:
            st.warning("Fill all fields.")
        else:
            if db.create_user(username, email, password, language):
                st.success("Registered!")
            else:
                st.error("Username exists.")

    if st.sidebar.button("Login"):
        if not username or not password:
            st.warning("Enter credentials.")
        else:
            user = db.get_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid login.")
else:
    st.sidebar.success(f"Logged in as {st.session_state.username}")
    if st.sidebar.button("Logout"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

    st.subheader("📊 Rate Your Skills")
    core_skills = ["Python", "SQL", "Machine Learning", "Power BI", "Deep Learning"]
    for s in core_skills:
        st.session_state.skill_ratings[s] = st.slider(f"{s}", 1, 5, 3)
## Clear skill ratings if not logged in
    if st.button("Submit Ratings"):
        st.session_state.quiz_completed = True

    if st.session_state.quiz_completed:
        st.subheader("🧠 Skill Quiz")
        for skill, rating in st.session_state.skill_ratings.items():
            level = "basic" if rating <= 1 else "intermediate" if rating <= 3 else "advanced"
            questions = quiz_bank.get_question_by_difficulty(skill, level)
            if not questions:
                continue
            st.markdown(f"### {skill} Quiz ({level.title()})")
            for i, q in enumerate(questions[:5]):
                st.radio(f"Q{i+1}: {q['question']}", q['options'], key=f"{skill}_{i}_{level}")

        if st.button("Submit Quiz"):
           
            score, total = 0, 0
            for skill, rating in st.session_state.skill_ratings.items():
                level = "basic" if rating <= 1 else "intermediate" if rating <= 3 else "advanced"
                questions = quiz_bank.get_question_by_difficulty(skill, level)
                for i, q in enumerate(questions[:5]):
                    key = f"{skill}_{i}_{level}"
                    if st.session_state.get(key) == q["answer"]:
                        score += 1
                    total += 1
            score = round((score / total) * 10, 2) if total else 0
            st.session_state.quiz_score = score
            st.session_state.total_quiz_questions = total
            st.session_state.quiz_submitted = True
            st.success(f"Quiz submitted!")

    # --- Resume Upload ---
    st.subheader("📄 Upload Resume")
    resume = st.file_uploader("Upload (PDF only)", type=["pdf"])

    if "resume_file" in st.session_state and st.session_state.resume_file and resume is None:
        for key in ["resume_file", "resume_text", "extracted_skills", "resume_score", "predicted_role"]:
            st.session_state.pop(key, None)
        st.rerun()

    if resume:
        save_path = os.path.join("data", resume.name)
        with open(save_path, "wb") as f:
            f.write(resume.read())
        st.session_state.resume_file = save_path
        st.success(f"✅ Uploaded: {resume.name}")
    else:
        st.warning("⚠️ Upload your resume to proceed.")

    if st.session_state.resume_file:
        try:
            if "resume_text" not in st.session_state:
                resume_text = extract_text_from_pdf(st.session_state.resume_file)
                st.session_state.resume_text = resume_text
            else:
                resume_text = st.session_state.resume_text

            if not resume_text.strip():
                st.warning("Empty or unreadable resume.")
                st.session_state.extracted_skills = []
            else:
                if not st.session_state.extracted_skills:
                    known_skills = resume_parser_dl.load_skill_list()
                    dl_skills = skill_extractor_dl.extract_skills_dl(resume_text, known_skills)
                    st.session_state.extracted_skills = dl_skills
                else:
                    dl_skills = st.session_state.extracted_skills

                try:
                    role = detect_job_role(resume_text)
                    st.session_state.predicted_role = role
                except Exception:
                    role = "Data Scientist"
                    st.session_state.predicted_role = role
                st.success(f"🧠 Predicted Role: {role}")

        except Exception as e:
            st.warning(f"⚠️ Resume analysis failed. Please try again. Error: {e}")

    if st.session_state.quiz_submitted and st.session_state.resume_file and st.session_state.resume_text:
        st.subheader("📈 Final Readiness Score")

        result = readiness_eval.calculate_readiness(
            resume_text=st.session_state.resume_text,
            quiz_score=st.session_state.quiz_score,
            total_quiz_questions=st.session_state.total_quiz_questions,
            matched_resume_skills=st.session_state.extracted_skills
        )

        st.markdown(f"**Final Score:** {result['final_score']} / 10")

        st.subheader("📊 Score Breakdown")
        st.markdown(f"""
        📄 **Resume Match Score:**
        - 🔸 **Skill Match (Readiness Model):** `{result.get('skill_component', 0.0):.2f} / 7`
        - 📝 **Quiz Score:** `{result.get('quiz_component', 0)} / 3`
        - 🎯 **Final Score:** `{result.get('final_score', 0)} / 10`
        """)

        st.plotly_chart(plot_readiness_bar_dl(result['final_score']))

        st.markdown("### 🧠 Readiness Analysis")
        alias_map = load_alias_map("data/skill_master.json")
        
        with open("data/skill_master.json") as f:
            skills_data = json.load(f)
        role = detect_job_role(resume_text)
        st.session_state.predicted_role = role
        required = skills_data["roles"].get(role, [])
        required_canonical = set(alias_map.get(s.lower(), s) for s in required)
        matched_canonical = set(alias_map.get(s.lower(), s) for s in st.session_state.extracted_skills)
        missing = list(required_canonical - matched_canonical)

        # Display above the chart
        st.markdown(f"### ✅ Matched Skills ({len(matched_canonical)}):")
        st.markdown(", ".join(sorted(matched_canonical)) or "None")

        st.markdown(f"### ❌ Missing Skills ({len(missing)}):")
        st.markdown(", ".join(sorted(missing)) or "None")

        st.plotly_chart(plot_skill_coverage_dl(st.session_state.extracted_skills, result['job_role']))
        if result['final_score'] >= 8:
            st.success("✅ You are highly prepared!")
        elif result['final_score'] >= 6:
            st.info("🟡 You have moderate readiness.")
        else:
            st.warning("🔴 Your readiness is low.")

        st.subheader("📚 Learning Recommendations")

 
        alias_map = load_alias_map("data/skill_master.json")
                
        with open("data/skill_master.json") as f:   
            skills_data = json.load(f)
            role = detect_job_role(resume_text)
            st.session_state.predicted_role = role
            required = skills_data["roles"].get(role, [])
            required_canonical = set(alias_map.get(s.lower(), s) for s in required)
            matched_canonical = set(alias_map.get(s.lower(), s) for s in st.session_state.extracted_skills)
            matched = matched_canonical
            missing = list(required_canonical - matched_canonical)
            if st.session_state.quiz_submitted and st.session_state.resume_file and st.session_state.resume_text:
                result = readiness_eval.calculate_readiness(
                    resume_text=st.session_state.resume_text,
                    quiz_score=st.session_state.quiz_score,
                    total_quiz_questions=st.session_state.total_quiz_questions,
                    matched_resume_skills=st.session_state.extracted_skills
                )
        pdf_buffer = generate_pdf_with_reportlab(matched, missing, result)

        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_buffer,
            file_name="readiness_report.pdf",
            mime="application/pdf"
        )
        
        recommendations = recommend_learning_paths(
            skill_ratings=st.session_state.skill_ratings,
            resume_skills=st.session_state.extracted_skills
        )
        for skill, url in recommendations:
            st.markdown(f"- **{skill}**: [Learn here]({url})")