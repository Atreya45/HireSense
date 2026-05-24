from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Make sure data/ folder exists before creating the DB there
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "jobs.db"
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company = Column(String(200), nullable=False)
    role = Column(String(200), nullable=False)
    location = Column(String(200), default="")
    job_url = Column(String(500), default="")
    jd_text = Column(Text, default="")
    resume_text = Column(Text, default="")
    match_score = Column(Float, default=0.0)
    missing_keywords = Column(Text, default="[]")
    matched_keywords = Column(Text, default="[]")
    status = Column(String(50), default="Applied")
    applied_date = Column(String(20), default="")
    deadline = Column(String(20), default="")
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(engine)

STATUSES = ["Applied", "Phone Screen", "Interviewing", "Take-Home", "Final Round", "Offer", "Rejected", "Withdrawn"]


def _job_to_dict(job: Job) -> dict[str, Any]:
    return {
        "id": job.id,
        "company": job.company,
        "role": job.role,
        "location": job.location or "",
        "job_url": job.job_url or "",
        "jd_text": job.jd_text or "",
        "resume_text": job.resume_text or "",
        "match_score": job.match_score or 0.0,
        "missing_keywords": json.loads(job.missing_keywords or "[]"),
        "matched_keywords": json.loads(job.matched_keywords or "[]"),
        "status": job.status or "Applied",
        "applied_date": job.applied_date or "",
        "deadline": job.deadline or "",
        "notes": job.notes or "",
        "created_at": job.created_at.strftime("%Y-%m-%d") if job.created_at else "",
    }


def add_job(data: dict[str, Any]) -> dict[str, Any]:
    db = SessionLocal()
    try:
        job = Job(
            company=data.get("company", ""),
            role=data.get("role", ""),
            location=data.get("location", ""),
            job_url=data.get("job_url", ""),
            jd_text=data.get("jd_text", ""),
            resume_text=data.get("resume_text", ""),
            match_score=data.get("match_score", 0.0),
            missing_keywords=json.dumps(data.get("missing_keywords", [])),
            matched_keywords=json.dumps(data.get("matched_keywords", [])),
            status=data.get("status", "Applied"),
            applied_date=data.get("applied_date", datetime.now().strftime("%Y-%m-%d")),
            deadline=data.get("deadline", ""),
            notes=data.get("notes", ""),
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return _job_to_dict(job)
    finally:
        db.close()


def get_all_jobs() -> list[dict[str, Any]]:
    db = SessionLocal()
    try:
        jobs = db.query(Job).order_by(Job.created_at.desc()).all()
        return [_job_to_dict(j) for j in jobs]
    finally:
        db.close()


def get_job_by_id(job_id: int) -> Optional[dict[str, Any]]:
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        return _job_to_dict(job) if job else None
    finally:
        db.close()


def update_job(job_id: int, updates: dict[str, Any]) -> bool:
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return False
        for key, value in updates.items():
            if hasattr(job, key):
                setattr(job, key, value)
        db.commit()
        return True
    finally:
        db.close()


def delete_job(job_id: int) -> bool:
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return False
        db.delete(job)
        db.commit()
        return True
    finally:
        db.close()
