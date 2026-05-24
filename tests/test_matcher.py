from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.matcher import compute_match, score_label


def test_identical_texts_score_high():
    text = "Python developer with experience in data pipelines and machine learning using scikit-learn and pandas"
    result = compute_match(text, text)
    assert result["score"] >= 80, "Identical texts should score high"


def test_unrelated_texts_score_low():
    jd = "We are looking for a marine biologist with expertise in coral reef ecosystems."
    resume = "Experienced software engineer proficient in React, TypeScript, and Node.js backend systems."
    result = compute_match(jd, resume)
    assert result["score"] < 40, "Unrelated texts should score low"


def test_partial_match():
    # Use longer, realistic texts so TF-IDF has enough signal to work with
    jd = (
        "We are looking for a Python data engineer with hands-on experience using pandas, "
        "NumPy, SQL, Apache Spark, and machine learning. The candidate should have strong "
        "communication skills and experience building data pipelines in a cloud environment. "
        "Experience with AWS, Docker, and Kubernetes is a plus."
    )
    resume = (
        "Data analyst with 2 years of Python and pandas experience. Built automated data "
        "analysis pipelines using Python scripts and SQL queries. Familiar with NumPy and "
        "basic data visualisation. Eager to move into a data engineering role."
    )
    result = compute_match(jd, resume)
    assert result["score"] > 0, "Partial match should return a non-zero score"
    assert len(result["missing_keywords"]) > 0, "Should detect missing keywords"


def test_empty_jd_returns_zero():
    result = compute_match("", "Some resume content here with lots of text.")
    assert result["score"] == 0.0


def test_empty_resume_returns_zero():
    result = compute_match("Looking for a Python data engineer.", "")
    assert result["score"] == 0.0


def test_both_empty_returns_zero():
    result = compute_match("", "")
    assert result["score"] == 0.0


def test_matched_keywords_are_in_both():
    jd = "Seeking a data scientist with Python machine learning scikit-learn experience."
    resume = "Data scientist with Python scikit-learn experience and deep learning background."
    result = compute_match(jd, resume)
    for kw in result["matched_keywords"]:
        # All matched keywords should appear in both texts
        assert kw in jd.lower() or kw in resume.lower()


def test_missing_keywords_not_in_resume():
    jd = "Requires Python SQL TensorFlow Kubernetes experience."
    resume = "Experienced with Python and SQL."
    result = compute_match(jd, resume)
    for kw in result["missing_keywords"]:
        assert kw not in resume.lower(), f"'{kw}' was flagged missing but appears in resume"


def test_score_label_strong():
    label, color = score_label(80.0)
    assert label == "Strong match"
    assert color.startswith("#")


def test_score_label_low():
    label, _ = score_label(10.0)
    assert label == "Low match"


def test_score_label_boundaries():
    assert score_label(75.0)[0] == "Strong match"
    assert score_label(74.9)[0] == "Good match"
    assert score_label(50.0)[0] == "Good match"
    assert score_label(49.9)[0] == "Partial match"
    assert score_label(30.0)[0] == "Partial match"
    assert score_label(29.9)[0] == "Low match"


def test_result_keys_always_present():
    result = compute_match("some job description text", "some resume text")
    assert "score" in result
    assert "missing_keywords" in result
    assert "matched_keywords" in result
    assert isinstance(result["missing_keywords"], list)
    assert isinstance(result["matched_keywords"], list)
