from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd

from core.database import get_all_jobs, update_job, delete_job, STATUSES
from core.matcher import score_label

st.set_page_config(page_title="Applications", page_icon="📋", layout="wide")

st.title("Applications")
st.divider()

# ── Load data ─────────────────────────────────────────────────────────────────
jobs = get_all_jobs()

if not jobs:
    st.info("No applications yet. Add one from the ** Add Job** page.", icon="")
    st.stop()


def badge(text: str, color: str, bg_alpha: str = "22") -> str:
    return (
        f"<span style='background:{color}{bg_alpha}; color:{color}; padding:3px 9px;"
        f" border-radius:12px; font-size:12px; font-weight:500; white-space:nowrap'>"
        f"{text}</span>"
    )


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

# ── Filters ────────────────────────────────────────────────────────────────────
f1, f2, f3 = st.columns([2, 2, 1])
search_query = f1.text_input("Search", placeholder="Company or role…", label_visibility="collapsed")
status_filter = f2.multiselect("Filter by status", options=STATUSES, placeholder="All statuses", label_visibility="collapsed")
sort_by = f3.selectbox(
    "Sort",
    options=["Newest first", "Highest score", "Lowest score", "A–Z (Company)"],
    label_visibility="collapsed",
)

# Apply filters
filtered = jobs

if search_query.strip():
    q = search_query.lower()
    filtered = [j for j in filtered if q in j["company"].lower() or q in j["role"].lower()]

if status_filter:
    filtered = [j for j in filtered if j["status"] in status_filter]

if sort_by == "Highest score":
    filtered = sorted(filtered, key=lambda j: j["match_score"], reverse=True)
elif sort_by == "Lowest score":
    filtered = sorted(filtered, key=lambda j: j["match_score"])
elif sort_by == "A–Z (Company)":
    filtered = sorted(filtered, key=lambda j: j["company"].lower())
# "Newest first" is already the default order from DB

st.caption(f"Showing {len(filtered)} of {len(jobs)} applications")
st.divider()

#  Application rows 
if not filtered:
    st.warning("No applications match your filters.")
    st.stop()

for job in filtered:
    with st.container():
        header_col, score_col, status_col, action_col = st.columns([4, 1, 2, 1])

        with header_col:
            title_parts = [f"**{job['company']}**", job["role"]]
            if job["location"]:
                title_parts.append(f"*{job['location']}*")
            st.markdown(" — ".join(title_parts))
            if job["applied_date"]:
                st.caption(f"Applied {job['applied_date']}")

        with score_col:
            if job["match_score"] > 0:
                label, color = score_label(job["match_score"])
                st.markdown(
                    f"<div style='font-size:20px; font-weight:600; color:{color}'>"
                    f"{job['match_score']:.0f}%</div>"
                    f"<div style='font-size:11px; color:{color}'>{label}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.caption("No score")

        with status_col:
            color = STATUS_COLORS.get(job["status"], "#6c757d")
            st.markdown(badge(job["status"], color), unsafe_allow_html=True)

        with action_col:
            expand_key = f"expand_{job['id']}"
            if expand_key not in st.session_state:
                st.session_state[expand_key] = False

            if st.button("Details", key=f"btn_detail_{job['id']}", use_container_width=True):
                st.session_state[expand_key] = not st.session_state[expand_key]

        #  Expanded detail panel 
        if st.session_state.get(f"expand_{job['id']}", False):
            with st.container():
                st.markdown(
                    "<div style='background:#f6f6f9; border-radius:8px; padding:1rem; margin:8px 0'>",
                    unsafe_allow_html=True,
                )

                d1, d2 = st.columns(2)

                with d1:
                    if job["matched_keywords"]:
                        st.markdown("**Keywords you have**")
                        tags = " ".join(badge(k, "#1D9E75") for k in job["matched_keywords"][:15])
                        st.markdown(tags, unsafe_allow_html=True)

                    if job["missing_keywords"]:
                        st.markdown("**Keywords to add**")
                        tags = " ".join(badge(k, "#A32D2D") for k in job["missing_keywords"][:15])
                        st.markdown(tags, unsafe_allow_html=True)

                    if not job["matched_keywords"] and not job["missing_keywords"]:
                        st.caption("No keyword analysis — re-run with a resume to generate insights.")

                with d2:
                    if job["notes"]:
                        st.markdown("**Notes**")
                        st.markdown(job["notes"])

                    if job["deadline"]:
                        st.markdown(f"**Deadline:** {job['deadline']}")

                    if job["job_url"]:
                        st.markdown(f"**Posting:** [{job['job_url'][:60]}…]({job['job_url']})")

                # Edit status + delete
                st.markdown("")
                edit_col, del_col = st.columns([3, 1])

                with edit_col:
                    current_idx = STATUSES.index(job["status"]) if job["status"] in STATUSES else 0
                    new_status = st.selectbox(
                        "Update status",
                        options=STATUSES,
                        index=current_idx,
                        key=f"status_sel_{job['id']}",
                    )
                    if new_status != job["status"]:
                        if st.button("Save status", key=f"save_status_{job['id']}"):
                            update_job(job["id"], {"status": new_status})
                            st.success("Status updated!")
                            st.rerun()

                with del_col:
                    if st.button("Delete", key=f"del_{job['id']}", type="secondary"):
                        st.session_state[f"confirm_del_{job['id']}"] = True

                    if st.session_state.get(f"confirm_del_{job['id']}", False):
                        st.warning(f"Delete **{job['company']} — {job['role']}**?")
                        yes, no = st.columns(2)
                        if yes.button("Yes, delete", key=f"yes_del_{job['id']}", type="primary"):
                            delete_job(job["id"])
                            st.session_state.pop(f"confirm_del_{job['id']}", None)
                            st.rerun()
                        if no.button("Cancel", key=f"no_del_{job['id']}"):
                            st.session_state.pop(f"confirm_del_{job['id']}", None)
                            st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

        st.divider()

#  Export 
st.subheader("Export")
export_df = pd.DataFrame([
    {
        "Company": j["company"],
        "Role": j["role"],
        "Location": j["location"],
        "Status": j["status"],
        "Match Score": j["match_score"],
        "Applied Date": j["applied_date"],
        "Deadline": j["deadline"],
        "Notes": j["notes"],
        "Job URL": j["job_url"],
    }
    for j in jobs
])

st.download_button(
    label="Download as CSV",
    data=export_df.to_csv(index=False).encode("utf-8"),
    file_name="job_applications.csv",
    mime="text/csv",
)
