from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from core.database import add_job, STATUSES
from core.matcher import compute_match, score_label
from core.parser import extract_pdf_text

st.set_page_config(page_title="Add Job", page_icon="", layout="wide")

st.title("Add Application")
st.caption("Paste the job description and your resume to get an match score.")
st.divider()

#  Helper 
def badge(text: str, color: str) -> str:
    return (
        f"<span style='background:{color}22; color:{color}; padding:3px 9px;"
        f" border-radius:12px; font-size:13px; font-weight:500'>{text}</span>"
    )


#  Form 
with st.form("add_job_form", clear_on_submit=False):
    st.subheader("Job Details")

    col1, col2 = st.columns(2)
    company = col1.text_input("Company *", placeholder="e.g. Stripe")
    role = col2.text_input("Role / Title *", placeholder="e.g. Data Analyst")

    col3, col4 = st.columns(2)
    location = col3.text_input("Location", placeholder="e.g. Remote / Bangalore")
    job_url = col4.text_input("Job Posting URL", placeholder="https://...")

    col5, col6, col7 = st.columns(3)
    status = col5.selectbox("Status", STATUSES, index=0)
    applied_date = col6.date_input("Applied Date", value=date.today())
    deadline_date = col7.date_input("Deadline (optional)", value=None)

    st.markdown("---")
    st.subheader("Job Description")
    jd_text = st.text_area(
        "Paste the full job description here",
        height=220,
        placeholder="Copy and paste the entire job posting including requirements, responsibilities, and qualifications…",
    )

    st.markdown("---")
    st.subheader("Your Resume")
    resume_tab1, resume_tab2 = st.tabs(["Upload PDF", "Paste Text"])

    with resume_tab1:
        uploaded_file = st.file_uploader(
            "Upload your resume as PDF",
            type=["pdf"],
            help="Text-based PDFs work best. Scanned/image PDFs may not extract correctly.",
        )

    with resume_tab2:
        resume_text_input = st.text_area(
            "Or paste your resume text here",
            height=200,
            placeholder="Paste your resume content…",
        )

    st.markdown("---")
    notes = st.text_area("Notes (optional)", height=80, placeholder="Referral contact, salary range, anything worth remembering…")

    submitted = st.form_submit_button("🔍 Analyze & Save", use_container_width=True, type="primary")


#  On submit 
if submitted:
    errors = []
    if not company.strip():
        errors.append("Company name is required.")
    if not role.strip():
        errors.append("Role / Title is required.")
    if not jd_text.strip():
        errors.append("Job description is required for scoring.")

    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    # Resolve resume text
    resume_text = ""
    if uploaded_file is not None:
        with st.spinner("Extracting text from PDF…"):
            try:
                resume_text = extract_pdf_text(uploaded_file.read())
            except Exception as exc:
                st.error(f"PDF extraction failed: {exc}")
                st.stop()
    elif resume_text_input.strip():
        resume_text = resume_text_input.strip()

    # Run the AI matcher
    match_result: dict = {"score": 0.0, "missing_keywords": [], "matched_keywords": []}
    if jd_text.strip() and resume_text:
        with st.spinner("Running AI match analysis…"):
            match_result = compute_match(jd_text, resume_text)

    # Persist
    saved = add_job({
        "company": company.strip(),
        "role": role.strip(),
        "location": location.strip(),
        "job_url": job_url.strip(),
        "jd_text": jd_text.strip(),
        "resume_text": resume_text,
        "match_score": match_result["score"],
        "missing_keywords": match_result["missing_keywords"],
        "matched_keywords": match_result["matched_keywords"],
        "status": status,
        "applied_date": str(applied_date),
        "deadline": str(deadline_date) if deadline_date else "",
        "notes": notes.strip(),
    })

    st.success(f"**{company}** — {role} saved successfully!")
    st.divider()

    #  Results 
    if match_result["score"] > 0:
        label, color = score_label(match_result["score"])

        st.subheader("AI Match Analysis")

        score_col, label_col = st.columns([1, 3])
        score_col.metric("Match Score", f"{match_result['score']:.1f}%")
        with label_col:
            st.markdown(badge(label, color), unsafe_allow_html=True)
            if not match_result.get("spacy_used", True):
                st.caption("spaCy model not found — using basic keyword extraction. Run `python -m spacy download en_core_web_sm` for better results.")

        kw_col1, kw_col2 = st.columns(2)

        with kw_col1:
            st.markdown("**Keywords you already have**")
            if match_result["matched_keywords"]:
                tags_html = " ".join(
                    badge(kw, "#1D9E75") for kw in match_result["matched_keywords"][:20]
                )
                st.markdown(tags_html, unsafe_allow_html=True)
            else:
                st.caption("No overlapping keywords found.")

        with kw_col2:
            st.markdown("**Keywords missing from your resume**")
            if match_result["missing_keywords"]:
                tags_html = " ".join(
                    badge(kw, "#A32D2D") for kw in match_result["missing_keywords"][:20]
                )
                st.markdown(tags_html, unsafe_allow_html=True)
                st.caption(
                    f"Consider adding these to your resume to improve your chances."
                )
            else:
                st.caption("Great — no major keyword gaps detected!")

    else:
        if not resume_text:
            st.info("Upload a resume or paste resume text to get an AI match score next time.")
        st.caption(f"Application saved with ID #{saved['id']}.")
