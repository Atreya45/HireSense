from __future__ import annotations

import io
import re


def extract_pdf_text(file_bytes: bytes) -> str:
    """
    Extract plain text from a PDF given its raw bytes.
    Returns cleaned text ready for the matcher.
    Raises ValueError with a user-friendly message on failure.
    """
    try:
        import pdfplumber
    except ImportError:
        raise ImportError(
            "pdfplumber is not installed. Run: pip install pdfplumber"
        )

    try:
        pages: list[str] = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)

        if not pages:
            raise ValueError(
                "No text could be extracted. The PDF may be scanned/image-only."
            )

        return clean_text("\n\n".join(pages))

    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"Failed to read PDF: {exc}") from exc


def clean_text(text: str) -> str:
    """Normalise whitespace and remove junk characters from extracted text."""
    # Collapse runs of blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse runs of spaces (but keep newlines)
    text = re.sub(r"[^\S\n]{2,}", " ", text)
    # Strip leading/trailing whitespace per line
    lines = [line.strip() for line in text.splitlines()]
    text = "\n".join(lines)
    return text.strip()
