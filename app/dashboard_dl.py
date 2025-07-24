import json
import datetime
import textwrap
import streamlit as st
import plotly.graph_objects as go
from sentence_transformers import SentenceTransformer, util
from app.skill_recommender_dl import recommend_skills, recommend_missing_skills, recommend_learning_paths
from app.skill_extractor_dl import load_alias_map

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black, green, red
from datetime import datetime
import io


# Load DL model
model = SentenceTransformer("all-MiniLM-L6-v2")

# --- Semantic Skill Match via DL ---
def compute_semantic_match(user_skills, required_skills, threshold=0.75):
    user_embeddings = model.encode(user_skills, convert_to_tensor=True)
    required_embeddings = model.encode(required_skills, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(required_embeddings, user_embeddings)

    matched, gaps = [], []
    for i, row in enumerate(similarity):
        max_score = max(row).item()
        if max_score >= threshold:
            matched.append(required_skills[i])
        else:
            gaps.append(required_skills[i])
    return matched, gaps


# --- Generate PDF Report with ReportLab ---
def generate_pdf_with_reportlab(matched, missing, result):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50

    def check_page_end():
        nonlocal y
        if y < 50:
            c.showPage()
            y = height - 50

    # ---- Title ----
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, y, "SkillBridge - Readiness Report")
    y -= 40

    # ---- User Info ----
    c.setFont("Helvetica", 11)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(50, y, f"Username: {st.session_state.username}")
    y -= 20
    check_page_end()

    # ---- Matched Skills ----
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(green)
    c.drawString(40, y, f"Matched Skills ({len(matched)}):")
    y -= 20
    c.setFillColor(black)
    c.setFont("Helvetica", 11)
    for skill in matched:
        c.drawString(50, y, f"- {skill}")
        y -= 15
        check_page_end()

    y -= 10
    check_page_end()

    # ---- Missing Skills ----
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(red)
    c.drawString(40, y, f"Missing Skills ({len(missing)}):")
    y -= 20
    c.setFillColor(black)
    c.setFont("Helvetica", 11)
    for skill in missing:
        c.drawString(50, y, f"- {skill}")
        y -= 15
        check_page_end()

    y -= 20
    check_page_end()

    # ---- Readiness Summary (Centered) ----
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, y, f"Resume Readiness Report - {datetime.now().strftime('%Y-%m-%d')}")
    y -= 25
    c.setFont("Helvetica", 11)
    c.drawString(30, y, f"Job Role: {result['job_role']}")
    y -= 20
    c.drawString(30, y, f"Resume Score: {result['resume_component']} / 7")
    y -= 20
    c.drawString(30, y, f"Quiz Score: {result['quiz_component']} / 3")
    y -= 20
    c.drawString(30, y, f"Final Score: {result['final_score']} / 10")
    y -= 30
    check_page_end()

    # ---- Explanation ----
    explanation = (
        "NOTE: Your DL-based readiness score is driven by both resume and quiz performance. "
        "However, some required job-specific skills were not matched directly from your resume. "
        "This can happen if the skills are implied but not explicitly written, or if they are phrased differently. "
        "The list of 'Missing skills' is provided so that you can consider incorporating them into your resume. "
        "Doing so will improve keyword clarity and boost matching accuracy, especially when your resume is parsed by ATS (Applicant Tracking System) tools."
    )

    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "ℹ️ Why Readiness = 10 but Skills are Missing:")
    y -= 20
    c.setFont("Helvetica", 11)
    wrapped_lines = textwrap.wrap(explanation, width=100)
    for line in wrapped_lines:
        c.drawString(30, y, line)
        y -= 15
        check_page_end()

    c.save()
    buffer.seek(0)
    return buffer



def plot_skill_coverage_dl(matched_skills, job_role, skill_master_path="data/skill_master.json"):
    with open(skill_master_path) as f:
        skills_data = json.load(f)

    required = skills_data["roles"].get(job_role, [])
    alias_map = load_alias_map(skill_master_path)
    required_canonical = set(alias_map.get(s.lower(), s) for s in required)
    matched_canonical = set(alias_map.get(s.lower(), s) for s in matched_skills)
    missing = list(required_canonical - matched_canonical)
    
    data = go.Figure(data=[go.Pie(
        labels=["Matched Skills", "Missing Skills"],
        values=[len(matched_canonical), len(missing)],
        hole=0.6,
        hoverinfo="label+percent+value"
        # text=[f"{len(missing)} skills", f"Missing ({len(missing)} skills): " + ", ".join(missing),
        #       f"{len(matched_canonical)} skills", f"Missing ({len(missing)} skills): " + ", ".join(matched_skills)]
        # # textinfo="label+text"
    )])
    data.update_layout(title="🔍 DL-Based Skill Coverage")
    return data


# --- DL-Based Readiness Score Gauge ---
def plot_readiness_bar_dl(dl_score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=dl_score,
        title={'text': "🤖 DL Job Readiness"},
        gauge={'axis': {'range': [0, 10]},
               'bar': {'color': "blue"}}
    ))
    return fig
