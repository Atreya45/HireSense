# HireSense — Intelligent ATS Resume Matcher & Job Tracker

HireSense is an intelligent ATS-style Resume Matcher and Job Application Tracker
built using Python and Streamlit. The platform helps users analyze how well their
resume aligns with a job description using NLP-driven keyword analysis, weighted
skill matching, cosine similarity, and calibrated ATS scoring.

The application also provides a complete job application tracking system with
analytics dashboards, resume parsing, and application management features.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red)
![License](https://img.shields.io/badge/License-MIT-green)

---

# Features

## Intelligent ATS Resume Matching

- Weighted technical skill matching
- NLP-based keyword extraction
- Synonym-aware matching
- Keyword gap analysis
- ATS-style calibrated scoring
- Cosine similarity-based domain matching
- Keyword stuffing detection
- Resume-to-JD alignment analysis

## Job Application Tracking

- Add and manage applications
- Track application status
- Store company details, links, notes and scores
- Filter and browse applications

## Analytics Dashboard

- Application funnel visualization
- Match score distribution
- Status analytics
- Timeline tracking using Plotly charts

## Resume Parsing

- Upload PDF resumes
- Automatic text extraction using pdfplumber

## Export Support

- Export application data as CSV

---

# Tech Stack

| Layer       | Technology                        |
| ----------- | --------------------------------- |
| Frontend/UI | Streamlit, Plotly                 |
| NLP Engine  | scikit-learn, Custom NLP Pipeline |
| Backend     | Python                            |
| Database    | SQLite, SQLAlchemy                |
| Parsing     | pdfplumber                        |
| Testing     | pytest                            |
| Deployment  | Streamlit Cloud                   |

---

# Project Structure

```txt
HireSense/
│
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── .streamlit/
│   └── config.toml
│
├── core/
│   ├── __init__.py
│   ├── matcher.py
│   ├── parser.py
│   └── database.py
│
├── pages/
│   ├── 1_Dashboard.py
│   ├── 2_Add_Job.py
│   └── 3_Applications.py
│
├── tests/
    ├── test_matcher.py
    └── test_parser.py
```
