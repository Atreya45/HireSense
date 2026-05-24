from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from core.parser import clean_text


def test_clean_text_strips_whitespace():
    raw = "  hello world  "
    assert clean_text(raw) == "hello world"


def test_clean_text_collapses_blank_lines():
    raw = "line one\n\n\n\nline two"
    cleaned = clean_text(raw)
    assert "\n\n\n" not in cleaned


def test_clean_text_collapses_spaces():
    raw = "too   many    spaces    here"
    cleaned = clean_text(raw)
    assert "  " not in cleaned


def test_clean_text_preserves_newlines():
    raw = "first line\nsecond line"
    cleaned = clean_text(raw)
    assert "first line" in cleaned
    assert "second line" in cleaned


def test_clean_text_empty_string():
    assert clean_text("") == ""


def test_clean_text_only_whitespace():
    assert clean_text("   \n  \n  ") == ""


def test_extract_pdf_text_invalid_bytes():
    """Should raise ValueError on garbage bytes, not crash with an unhandled exception."""
    from core.parser import extract_pdf_text
    with pytest.raises(ValueError):
        extract_pdf_text(b"this is not a pdf file at all")


def test_extract_pdf_text_empty_bytes():
    from core.parser import extract_pdf_text
    with pytest.raises(ValueError):
        extract_pdf_text(b"")
