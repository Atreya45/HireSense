from __future__ import annotations

import re
import warnings
from typing import Any

warnings.filterwarnings("ignore")

from sklearn.feature_extraction.text import (
    ENGLISH_STOP_WORDS,
    CountVectorizer,
)
from sklearn.metrics.pairwise import cosine_similarity


# Stop words

_EXTRA_STOP: set[str] = {
    "strong", "good", "great", "excellent",
    "outstanding", "exceptional", "proven",
    "help", "ensure", "support", "define",
    "include", "including", "responsibilities",
    "requirements", "role", "position",
    "company", "preferred", "plus",
    "field", "degree", "bachelor",
    "master", "ability", "familiarity",
    "proficiency", "knowledge", "expertise",
    "skills", "skill", "communicate",
    "communication", "following", "able",
    "multiple", "various", "key",
    "primary", "collaborate", "maintain",
    "manage", "implement", "identify",
    "report", "reporting", "drive",
    "deliver", "provide", "conduct",
    "perform", "present", "prepare",
    "responsible", "requirement",
    "required", "nice", "minimum",
    "bonus", "build", "building",
    "built", "create", "created",
    "develop", "developed", "development",
    "work", "working", "worked",
    "design", "designed", "analyze",
    "track", "tracking", "looking",
    "join", "experience", "understanding",
    "tools", "platform", "platforms",
    "concept", "concepts", "analyst",
    "analysis", "team", "teams",
    "product", "products", "project",
    "projects", "system", "systems",
    "process", "processes", "service",
    "services", "solution", "solutions",

    # Generic corporate words
    "intern", "internship", "engineer",
    "developer", "development",
    "software", "application",
    "applications", "problem",
    "solving", "fundamentals",
    "candidate", "ideal",
    "opportunity", "technology",
    "technologies", "organization",
    "client", "business",
    "enterprise", "environment",
    "professional", "industry",
    "scalable", "scalability",
    "architecture", "architectures",
    "search", "semantic",
    "recommendation", "recommendations",

    # Company names
    "amazon", "microsoft",
    "google", "meta",
    "netflix", "uber",
    "linkedin",
    "use",
    "using",
    "used",
    "write",
    "written",
    "large",
    "small",
    "hoc",
    "chain",
    "based",
    "across",
    "within",
    "ability",
    "kpis",
    "metrics",
    "bi",
}

_STOP: frozenset[str] = (
    ENGLISH_STOP_WORDS |
    frozenset(_EXTRA_STOP)
)


# Important ATS skills

IMPORTANT_TERMS = {

    # Programming
    "python", "java", "javascript",
    "typescript", "c++", "cpp",
    "golang", "go", "rust",

    # Frontend
    "react", "angular", "vue",
    "nextjs", "redux",

    # Backend
    "nodejs", "express",
    "django", "flask",
    "fastapi", "spring",
    "springboot",

    # Databases
    "sql", "mysql",
    "postgresql", "mongodb",
    "redis",

    # Cloud
    "aws", "azure", "gcp",

    # DevOps
    "docker", "kubernetes",
    "terraform", "jenkins",

    # AI / ML
    "machine_learning",
    "deep_learning",
    "natural_language_processing",
    "computer_vision",
    "tensorflow",
    "pytorch",
    "llm",
    "genai",

    # Concepts
    "microservices",
    "rest_api",
    "graphql",
    "data_structures",
    "algorithms",

    # Analytics
    "tableau",
    "powerbi",

    # Tools
    "git",
    "github",
    "linux",

    "artificial_intelligence",
    "generative_ai",
    "large_language_model",
    "large_language_models",
    "continuous_integration",
    "object_oriented_programming",
}


# Synonyms

SYNONYMS = {

    "ai": [
        "artificial_intelligence"
    ],

    "ml": [
        "machine_learning"
    ],

    "nlp": [
        "natural_language_processing"
    ],

    "llm": [
        "large_language_model",
        "large_language_models",
    ],

    "genai": [
        "generative_ai",
        "generative_artificial_intelligence",
    ],

    "cpp": ["c++"],
    "js": ["javascript"],
    "ts": ["typescript"],

    "reactjs": ["react"],
    "react.js": ["react"],

    "next": ["nextjs"],
    "next.js": ["nextjs"],

    "node": ["nodejs"],
    "node.js": ["nodejs"],

    "springboot": ["spring"],

    "restful": ["rest_api"],

    "mongo": ["mongodb"],

    "postgres": ["postgresql"],

    "amazon_web_services": ["aws"],

    "google_cloud": ["gcp"],

    "k8s": ["kubernetes"],

    "ci/cd": ["continuous_integration"],

    "oop": [
        "object_oriented_programming"
    ],

    "dsa": [
        "data_structures",
        "algorithms",
    ],

    "power_bi": ["powerbi"],
}


# Tokenizer

def _tokenize(text: str) -> set[str]:

    text = text.lower()

    replacements = {

        "machine learning":
            "machine_learning",

        "deep learning":
            "deep_learning",

        "natural language processing":
            "natural_language_processing",

        "computer vision":
            "computer_vision",

        "data structures":
            "data_structures",

        "rest api":
            "rest_api",

        "object oriented programming":
            "oop",

        "artificial intelligence":
            "artificial_intelligence",

        "generative artificial intelligence":
            "generative_artificial_intelligence",

        "generative ai":
            "generative_ai",

        "large language model":
            "large_language_model",

        "large language models":
            "large_language_models",

        "continuous integration":
            "continuous_integration",

        "amazon web services":
            "amazon_web_services",

        "google cloud":
            "google_cloud",

        "power bi":
            "power_bi",
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    raw_tokens = re.findall(
        r"[a-zA-Z][a-zA-Z0-9_+#.\-]*",
        text
    )

    result = set()

    for tok in raw_tokens:

        tok = tok.strip().rstrip(".-,;:!?")

        if len(tok) < 2:
            continue

        if tok.isdigit():
            continue

        tok = tok.lower()

        if tok in _STOP:
            continue

        result.add(tok)

    return result


# def _term_in_text(
#     term: str,
#     text_lower: str
# ) -> bool:

#     pattern = (
#         r"\b" +
#         re.escape(term) +
#         r"\b"
#     )

#     return bool(
#         re.search(pattern, text_lower)
#     )

def _term_in_text(
    term: str,
    text_lower: str
) -> bool:

    return term in text_lower

def _normalize_text(text: str) -> str:

    text = text.lower()

    replacements = {

        "machine learning":
            "machine_learning",

        "deep learning":
            "deep_learning",

        "natural language processing":
            "natural_language_processing",

        "computer vision":
            "computer_vision",

        "data structures":
            "data_structures",

        "rest api":
            "rest_api",

        "object oriented programming":
            "object_oriented_programming",

        "large language model":
            "large_language_model",

        "large language models":
            "large_language_models",

        "generative ai":
            "generative_ai",

        "artificial intelligence":
            "artificial_intelligence",

        "continuous integration":
            "continuous_integration",

        "amazon web services":
            "amazon_web_services",

        "google cloud":
            "google_cloud",

        "power bi":
            "power_bi",

        "fast api":
            "fastapi",

        "postgre sql":
            "postgresql",

        "micro services":
            "microservices",

        "node js":
            "nodejs",

        "deep neural networks":
            "deep_learning",

        "nlp":
            "natural_language_processing",

        "ml":
            "machine_learning",

        "ai":
            "artificial_intelligence",
    }

    for k, v in replacements.items():

        pattern = r"\b" + re.escape(k) + r"\b"

        text = re.sub(
            pattern,
            v,
            text
        )

    return text

def compute_match(
    jd_text: str,
    resume_text: str
) -> dict[str, Any]:

    if not jd_text.strip() or not resume_text.strip():

        return {
            "score": 0.0,
            "missing_keywords": [],
            "matched_keywords": [],
        }

    jd_lower = _normalize_text(jd_text)
    resume_lower = _normalize_text(resume_text)

    jd_terms = _tokenize(jd_lower)

    # Keep only meaningful ATS terms

    VALID_SHORT_TERMS = {
        "aws",
        "gcp",
        "sql",
        "api",
        "oop",
        "cpp",
        "css",
        "html",
        "git",
        "ml",
        "ai",
        "nlp",
        "llm",
    }

    jd_terms = {
        t for t in jd_terms
        if (
            t in IMPORTANT_TERMS or
            t in VALID_SHORT_TERMS or
            "_" in t
        )
    }
    matched: list[str] = []
    missing: list[str] = []

    weighted_match_score = 0
    total_weight = 0

    for term in sorted(jd_terms):

        if term in IMPORTANT_TERMS:
            weight = 3

        elif "_" in term:
            weight = 2

        else:
            weight = 0.25

        total_weight += weight

        found = False


        if _term_in_text(
            term,
            resume_lower
        ):
            found = True


        if not found:

            for key, values in SYNONYMS.items():

                all_terms = [key] + values

                if (
                    term == key or
                    term in values
                ):

                    for alt in all_terms:

                        alt = alt.lower()

                        if alt in resume_lower:
                            found = True
                            break

                if found:
                    break

        if found:

            matched.append(term)

            weighted_match_score += weight

        else:

            missing.append(term)

    keyword_score = (
        weighted_match_score /
        total_weight
        if total_weight else 0.0
    )

    # Cosine similarity

    cos_sim = 0.0

    try:

        cv = CountVectorizer(
            ngram_range=(1, 3),
            stop_words="english",
            min_df=1,
            max_features=15000,
        )

        vecs = cv.fit_transform([
            jd_text,
            resume_text,
        ])

        cos_sim = float(
            cosine_similarity(
                vecs[0],
                vecs[1]
            )[0][0]
        )

    except Exception:
        pass

    # Resume quality checks

    resume_tokens = _tokenize(
        resume_lower
    )

    resume_word_count = len(
        resume_tokens
    )

    stuffing_penalty = 0

    # Short resume

    if resume_word_count < 20:
        stuffing_penalty += 20

    elif resume_word_count < 40:
        stuffing_penalty += 10

    # Keyword stuffing detection

    if len(matched) > 0:

        match_ratio = (
            len(matched) /
            max(resume_word_count, 1)
        )

        if match_ratio > 0.60:
            stuffing_penalty += 25

        elif match_ratio > 0.45:
            stuffing_penalty += 15

    # Missing important skills

    missing_important = 0

    for term in missing:

        if term in IMPORTANT_TERMS:
            missing_important += 1

    missing_penalty = (
        missing_important * 1.2
    )

    # Base score

    raw_score = (
        keyword_score * 68 +
        cos_sim * 32
    )

    # Strong stack bonus

    strong_stack_bonus = 0

    core_stack = {
        "python",
        "fastapi",
        "aws",
        "docker",
        "postgresql",
        "machine_learning",
        "natural_language_processing",
    }

    matched_core = 0

    for term in matched:

        if term in core_stack:
            matched_core += 1

    if matched_core >= 6:
        strong_stack_bonus += 10

    elif matched_core >= 4:
        strong_stack_bonus += 6

    raw_score += strong_stack_bonus

    # Penalties

    raw_score -= stuffing_penalty
    raw_score -= missing_penalty

    # Calibration

    if keyword_score < 0.20:
        raw_score *= 0.55

    elif keyword_score < 0.35:
        raw_score *= 0.70

    elif keyword_score < 0.50:
        raw_score *= 0.85

    # Prevent fake high scores

    if (
        cos_sim > 0.85 and
        keyword_score < 0.50
    ):
        raw_score -= 15

    # ATS caps

    if keyword_score < 0.60:
        raw_score = min(raw_score, 82)

    elif keyword_score < 0.75:
        raw_score = min(raw_score, 90)

    # Bonus for excellent matches

    if (
        keyword_score > 0.85 and
        cos_sim > 0.75
    ):
        raw_score += 5

    elif (
        keyword_score > 0.70 and
        cos_sim > 0.60
    ):
        raw_score += 2

    # Final score

    score = round(
        max(0, min(raw_score, 98)),
        1
    )

    return {
        "score": score,
        "missing_keywords": missing[:40],
        "matched_keywords": matched[:40],
    }


# Score label

def score_label(
    score: float
) -> tuple[str, str]:

    if score >= 80:
        return (
            "Excellent match",
            "#15803D"
        )

    elif score >= 65:
        return (
            "Strong match",
            "#1D9E75"
        )

    elif score >= 45:
        return (
            "Good match",
            "#BA7517"
        )

    elif score >= 30:
        return (
            "Partial match",
            "#D85A30"
        )

    return (
        "Low match",
        "#A32D2D"
    )