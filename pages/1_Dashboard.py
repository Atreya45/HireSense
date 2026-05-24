from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core.database import get_all_jobs, STATUSES

st.set_page_config(page_title="Dashboard", page_icon="", layout="wide")

st.title("Dashboard")
st.caption("A visual overview of your job search.")
st.divider()

jobs = get_all_jobs()

if not jobs:
    st.info("No data yet. Add your first application to see charts here.", icon="")
    st.stop()

df = pd.DataFrame(jobs)
df["match_score"] = pd.to_numeric(df["match_score"], errors="coerce").fillna(0)
df["applied_date"] = pd.to_datetime(df["applied_date"], errors="coerce")

#  Top metrics 
scored = df[df["match_score"] > 0]
c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Applications", len(df))
c2.metric(
    "Avg Match Score",
    f"{scored['match_score'].mean():.1f}%" if not scored.empty else "—",
)
c3.metric(
    "Highest Score",
    f"{scored['match_score'].max():.0f}%" if not scored.empty else "—",
)
responded = df[~df["status"].isin(["Applied", "Withdrawn"])]
c4.metric(
    "Response Rate",
    f"{len(responded) / len(df) * 100:.0f}%",
)

st.divider()

#  Row 1: Status breakdown + Match score distribution 
col1, col2 = st.columns(2)

with col1:
    st.subheader("Application Status")

    status_counts = (
        df["status"]
        .value_counts()
        .reindex(STATUSES, fill_value=0)
        .reset_index()
    )
    status_counts.columns = ["Status", "Count"]
    status_counts = status_counts[status_counts["Count"] > 0]

    COLOR_MAP = {
        "Applied":      "#ADB5BD",
        "Phone Screen": "#74C0FC",
        "Interviewing": "#38BDF8",
        "Take-Home":    "#A78BFA",
        "Final Round":  "#7F77DD",
        "Offer":        "#4ADE80",
        "Rejected":     "#F87171",
        "Withdrawn":    "#D1D5DB",
    }

    fig_status = px.bar(
        status_counts,
        x="Count",
        y="Status",
        orientation="h",
        color="Status",
        color_discrete_map=COLOR_MAP,
        text="Count",
    )
    fig_status.update_traces(textposition="outside", textfont_size=13)
    fig_status.update_layout(
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=30, t=10, b=10),
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, title=""),
        height=300,
    )
    st.plotly_chart(fig_status, use_container_width=True)

with col2:
    st.subheader("Match Score Distribution")

    if scored.empty:
        st.info("Run the AI scorer on some applications to see the distribution.")
    else:
        fig_hist = px.histogram(
            scored,
            x="match_score",
            nbins=10,
            range_x=[0, 100],
            labels={"match_score": "Match Score (%)"},
            color_discrete_sequence=["#7F77DD"],
        )
        fig_hist.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            bargap=0.08,
            yaxis=dict(showgrid=True, gridcolor="#f0f0f0", title="Count"),
            xaxis=dict(showgrid=False, title="Match Score (%)"),
            showlegend=False,
            height=300,
        )
        st.plotly_chart(fig_hist, use_container_width=True)

st.divider()

#  Row 2: Applications over time + Score vs Status scatter 
col3, col4 = st.columns(2)

with col3:
    st.subheader("Applications Over Time")

    dated = df.dropna(subset=["applied_date"]).copy()
    if dated.empty:
        st.info("Add applied dates to see this chart.")
    else:
        dated["week"] = dated["applied_date"].dt.to_period("W").dt.start_time
        weekly = dated.groupby("week").size().reset_index(name="count")
        weekly["cumulative"] = weekly["count"].cumsum()

        fig_time = go.Figure()
        fig_time.add_trace(go.Bar(
            x=weekly["week"],
            y=weekly["count"],
            name="This week",
            marker_color="#C3C0F7",
        ))
        fig_time.add_trace(go.Scatter(
            x=weekly["week"],
            y=weekly["cumulative"],
            name="Cumulative",
            line=dict(color="#7F77DD", width=2),
            yaxis="y2",
        ))
        fig_time.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            height=300,
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#f0f0f0", title="Applications"),
            yaxis2=dict(
                overlaying="y",
                side="right",
                showgrid=False,
                title="Cumulative",
            ),
        )
        st.plotly_chart(fig_time, use_container_width=True)

with col4:
    st.subheader("Match Score by Status")

    if scored.empty:
        st.info("Score some applications to see this chart.")
    else:
        fig_box = px.box(
            scored,
            x="status",
            y="match_score",
            color="status",
            color_discrete_map=COLOR_MAP,
            labels={"match_score": "Match Score (%)", "status": ""},
            category_orders={"status": STATUSES},
            points="all",
        )
        fig_box.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
            height=300,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
        )
        st.plotly_chart(fig_box, use_container_width=True)

st.divider()

#  Top companies table 
st.subheader("Top Companies Applied To")
company_df = (
    df.groupby("company")
    .agg(
        Applications=("id", "count"),
        Avg_Score=("match_score", lambda x: f"{x[x>0].mean():.0f}%" if any(x > 0) else "—"),
        Best_Status=("status", lambda x: x.iloc[0]),
    )
    .reset_index()
    .rename(columns={"company": "Company", "Avg_Score": "Avg Score", "Best_Status": "Latest Status"})
    .sort_values("Applications", ascending=False)
    .head(10)
)
st.dataframe(company_df, use_container_width=True, hide_index=True)
