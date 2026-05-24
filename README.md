# Job Application Tracker + AI Match Score

A full-stack web application that helps you track job applications and score how well
your resume matches any job description using NLP. Built with Python, Streamlit, spaCy,
and SQLite.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Features

- **AI Match Score** — TF-IDF cosine similarity between job description and resume (0–100%)
- **Keyword Gap Analysis** — highlights skills in the JD that are missing from your resume
- **Application Tracker** — add, update, and delete applications with full status history
- **Analytics Dashboard** — Plotly charts for status funnel, score distribution, applications over time
- **PDF Resume Upload** — extract text automatically from your resume PDF
- **CSV Export** — download all your application data at any time

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/job-tracker.git
cd job-tracker
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Download the spaCy language model

```bash
python -m spacy download en_core_web_sm
```

### 5. Run the app

```bash
streamlit run main.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Project Structure

```
job-tracker/
├── main.py                  # Home page (Streamlit entry point)
├── pages/
│   ├── 1_Dashboard.py       # Analytics and charts
│   ├── 2_Add_Job.py         # Add application + AI scorer
│   └── 3_Applications.py   # Browse, filter, edit, delete
├── core/
│   ├── database.py          # SQLAlchemy models + CRUD
│   ├── matcher.py           # NLP match score engine
│   └── parser.py            # PDF text extraction
├── data/
│   └── jobs.db              # SQLite database (auto-created)
├── tests/
│   ├── test_matcher.py
│   └── test_parser.py
├── .streamlit/
│   └── config.toml          # Theme config
└── requirements.txt
```

---

## Running Tests

```bash
pytest tests/ -v
```

---

## How the Match Score Works

1. Both the job description and resume text are passed to a `TfidfVectorizer` with bigrams enabled.
2. Cosine similarity is computed between the two TF-IDF vectors and scaled to 0–100%.
3. spaCy extracts noun phrases, named entities, and content words from both texts.
4. Set difference between JD keywords and resume keywords reveals gaps.

| Score Range | Label          |
|-------------|----------------|
| 75–100%     | Strong match   |
| 50–74%      | Good match     |
| 30–49%      | Partial match  |
| 0–29%       | Low match      |

---

## Deploying to Streamlit Cloud

1. Push this repo to GitHub (make sure `data/jobs.db` is in `.gitignore`)
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app
3. Set **Main file path** to `main.py`
4. Add a `packages.txt` file with `en_core_web_sm` for the spaCy model:

```
# packages.txt
python3-dev
```

And a `setup.sh`:

```bash
#!/bin/bash
python -m spacy download en_core_web_sm
```

---

## Tech Stack

| Layer        | Technology                          |
|--------------|-------------------------------------|
| UI           | Streamlit, Plotly                   |
| NLP / AI     | spaCy, scikit-learn (TF-IDF)        |
| Data         | pandas, pdfplumber                  |
| Database     | SQLite, SQLAlchemy                  |
| Testing      | pytest                              |
| Deploy       | Streamlit Cloud                     |

---

## License

MIT
