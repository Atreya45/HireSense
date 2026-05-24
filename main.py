from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
from core.database import get_all_jobs, STATUSES
from core.matcher import score_label

st.set_page_config(
    page_title="Job Tracker",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #f6f6f9; }
    .block-container { padding-top: 2rem; }
    div[data-testid="stMetricValue"] { font-size: 2rem; }
</style>
""", unsafe_allow_html=True)

#  Header 
st.title("Job Application Tracker")
st.caption("Track applications · Match resumes · Spot keyword gaps")
st.divider()

jobs = get_all_jobs()

if not jobs:
    st.info(
        "No applications tracked yet. "
        "Click **Add Job** in the sidebar to get started.",
        icon="",
    )
    st.stop()

#  Summary metrics 
scores = [j["match_score"] for j in jobs if j["match_score"] > 0]
statuses = [j["status"] for j in jobs]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Applications", len(jobs))
c2.metric("Avg Match Score", f"{sum(scores)/len(scores):.1f}%" if scores else "—")
c3.metric("Interviewing", statuses.count("Interviewing") + statuses.count("Final Round"))
c4.metric("Offers", statuses.count("Offer"))
c5.metric("Response Rate", f"{(len([s for s in statuses if s not in ('Applied', 'Withdrawn')]) / len(jobs) * 100):.0f}%")

st.divider()

#  Recent applications 
st.subheader("Recent Applications")

STATUS_COLORS = {
    "Applied":      "#6c757d",
    "Phone Screen": "#0d6efd",
    "Interviewing": "#0dcaf0",
    "Take-Home":    "#6f42c1",
    "Final Round":  "#7F77DD",
    "Offer":        "#198754",
    "Rejected":     "#dc3545",
    "Withdrawn":    "#adb5bd",
}

for job in jobs[:8]:
    label, color = score_label(job["match_score"])
    status_color = STATUS_COLORS.get(job["status"], "#6c757d")

    col_main, col_score, col_status = st.columns([4, 1, 1])

    with col_main:
        company_role = f"**{job['company']}** — {job['role']}"
        if job["location"]:
            company_role += f"  ·  {job['location']}"
        st.markdown(company_role)
        if job["applied_date"]:
            st.caption(f"Applied {job['applied_date']}")

    with col_score:
        if job["match_score"] > 0:
            st.markdown(
                f"<span style='color:{color}; font-weight:600'>{job['match_score']:.0f}%</span>",
                unsafe_allow_html=True,
            )
        else:
            st.caption("No score")

    with col_status:
        st.markdown(
            f"<span style='background:{status_color}22; color:{status_color}; "
            f"padding:3px 10px; border-radius:12px; font-size:13px'>"
            f"{job['status']}</span>",
            unsafe_allow_html=True,
        )

    st.divider()

if len(jobs) > 8:
    st.caption(f"Showing 8 of {len(jobs)} — see all on the **Applications** page.")
