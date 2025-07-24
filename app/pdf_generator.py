import json
# Generate PDF readiness reports
# app/pdf_generator.py
import logging
logging.getLogger("transformers").setLevel(logging.ERROR)# Suppress transformers warnings


from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

def generate_pdf_report(filename, user_info, gaps, courses):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    textobject = c.beginText(40, height - 50)

    textobject.setFont("Helvetica-Bold", 14)
    textobject.textLine("SkillBridge Career Guidance Report")
    textobject.setFont("Helvetica", 11)
    textobject.textLine(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    textobject.textLine("")

    # Resume Info
    textobject.setFont("Helvetica-Bold", 12)
    textobject.textLine("Resume Summary:")
    textobject.setFont("Helvetica", 11)
    for key in ["Email", "Phone", "Detected Language"]:
        if user_info.get(key):
            textobject.textLine(f"{key}: {user_info[key]}")
    textobject.textLine("")

    # Skills
    textobject.setFont("Helvetica-Bold", 12)
    textobject.textLine("Extracted Skills:")
    textobject.setFont("Helvetica", 11)
    for skill in user_info["Skills"]:
        textobject.textLine(f"- {skill}")
    textobject.textLine("")

    # Gaps
    textobject.setFont("Helvetica-Bold", 12)
    textobject.textLine("Skill Gaps:")
    textobject.setFont("Helvetica", 11)
    if gaps:
        for gap in gaps:
            textobject.textLine(f"- {gap}")
    else:
        textobject.textLine("No major gaps detected.")
    textobject.textLine("")

    # Recommendations
    textobject.setFont("Helvetica-Bold", 12)
    textobject.textLine("Recommended Courses:")
    textobject.setFont("Helvetica", 11)
    if not courses.empty:
        for _, row in courses.iterrows():
            textobject.textLine(f"- {row['Skill']}: {row['Course Title']} ({row['Platform']})")
            textobject.textLine(f"  {row['URL']}")
    else:
        textobject.textLine("You're all set. No courses recommended.")

    c.drawText(textobject)
    c.showPage()
    c.save()
