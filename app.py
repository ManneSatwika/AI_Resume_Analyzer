import streamlit as st
import pdfplumber
import matplotlib.pyplot as plt
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ---------------- TITLE ----------------
st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")
st.title("📄 AI Resume Analyzer")
st.write("Upload a resume and compare it with the Job Description")

# ---------------- INPUT ----------------
uploaded_file = st.file_uploader("Upload Resume PDF", type=["pdf"])
job_description = st.text_area("Paste Job Description", height=200)

# ---------------- SKILLS ----------------
skills_list = [
    "python", "java", "c", "c++", "sql", "html", "css", "javascript", 
    "react", "nodejs", "git", "github", "streamlit", "machine learning", 
    "deep learning", "data science", "tensorflow", "pandas", "numpy", 
    "opencv", "docker", "aws", "kubernetes", "linux", "excel", "power bi"
]

def generate_pdf(found_skills, job_skills, matching_skills, missing_skills, ats_score):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []
    
    # PDF Header Elements
    story.append(Paragraph("<b>AI Resume Analyzer Report</b>", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>ATS Score:</b> {ats_score:.2f}%", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Skills Summary Sections
    story.append(Paragraph(f"<b>Resume Skills:</b> {', '.join(found_skills) if found_skills else 'None'}", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(f"<b>Job Skills:</b> {', '.join(job_skills) if job_skills else 'None'}", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(f"<b>Matching Skills:</b> {', '.join(matching_skills) if matching_skills else 'None'}", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(f"<b>Missing Skills:</b> {', '.join(missing_skills) if missing_skills else 'None'}", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Actionable AI suggestions in the document
    if missing_skills:
        story.append(Paragraph("<b>AI Suggestions:</b>", styles['Heading2']))
        for skill in missing_skills:
            story.append(Paragraph(f"• Add projects and experience demonstrating <b>{skill.title()}</b>.", styles['Normal']))
    else:
        story.append(Paragraph("Excellent! Your resume matches the job requirements well.", styles['Normal']))
        
    doc.build(story)
    buffer.seek(0)
    return buffer

# ---------------- MAIN ----------------
if uploaded_file and job_description:
    # -------- PDF TEXT --------
    text = ""
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        st.error(f"Error reading the PDF: {e}")

    resume_text = text.lower()
    jd_text = job_description.lower()

    # -------- SKILLS --------
    found_skills = [s for s in skills_list if s in resume_text]
    job_skills = [s for s in skills_list if s in jd_text]
    matching_skills = [s for s in found_skills if s in job_skills]
    missing_skills = [s for s in job_skills if s not in found_skills]

    # -------- DISPLAY --------
    st.subheader("📄 Extracted Resume Text")
    st.text_area("Extracted Text", text, height=200)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎯 Resume Skills")
        st.write(found_skills)
        st.subheader("📝 Job Skills")
        st.write(job_skills)

    with col2:
        st.subheader("🤝 Matching Skills")
        st.write(matching_skills)
        st.subheader("❌ Missing Skills")
        st.write(missing_skills)

    # -------- ATS SCORE --------
    st.subheader("📊 ATS Score")
    if len(job_skills) > 0:
        ats_score = (len(matching_skills) / len(job_skills)) * 100
    else:
        ats_score = 0
        
    st.progress(ats_score / 100)
    st.write(f"**{ats_score:.2f}%**")

    # -------- DOWNLOAD PDF --------
    pdf_file = generate_pdf(found_skills, job_skills, matching_skills, missing_skills, ats_score)
    st.download_button(
        label="📥 Download PDF Report",
        data=pdf_file,
        file_name="resume_report.pdf",
        mime="application/pdf"
    )

    # -------- PIE CHART --------
    st.subheader("📈 Skill Match Chart")
    if job_skills:
        fig, ax = plt.subplots()
        ax.pie([len(matching_skills), len(missing_skills)], labels=['Matched', 'Missing'], autopct='%1.1f%%', colors=['#4CAF50', '#F44336'])
        ax.axis('equal')
        st.pyplot(fig)

    # -------- SUGGESTIONS --------
    st.subheader("💡 Suggestions")
    if missing_skills:
        for skill in missing_skills:
            st.write(f"✔ Add **{skill.title()}** to your resume")
    else:
        st.success("Perfect Resume 🎉")

    # -------- SUMMARY --------
    st.subheader("📋 Summary")
    st.write(f"Resume Skills: **{len(found_skills)}**")
    st.write(f"Job Skills: **{len(job_skills)}**")
    st.write(f"Matching Skills: **{len(matching_skills)}**")
    st.write(f"Missing Skills: **{len(missing_skills)}**")

else:
    st.info("Upload a resume PDF and paste the job description to get started.")