import time
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class SessionRecord(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, index=True)
    source_language = Column(String, default="en-IN")
    target_languages = Column(String, default="ta-IN,hi-IN,ml-IN")
    mode = Column(String, default="fast")
    created_at = Column(Float, default=time.time)
    ended_at = Column(Float, nullable=True)
    status = Column(String, default="active")

class SegmentRecord(Base):
    __tablename__ = "segments"

    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.id"), index=True)
    original_text = Column(Text)
    status = Column(String, default="final")  # partial, committed, final
    created_at = Column(Float, default=time.time)

class TranslationRecord(Base):
    __tablename__ = "translations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    segment_id = Column(String, ForeignKey("segments.id"), index=True)
    target_language = Column(String, index=True)
    translated_text = Column(Text)
    latency_ms = Column(Integer, default=0)
    status = Column(String, default="final")
    created_at = Column(Float, default=time.time)

class MetricRecord(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.id"), index=True)
    segment_id = Column(String, index=True)
    stt_latency_ms = Column(Integer, default=0)
    first_word_latency_ms = Column(Integer, default=0)
    final_latency_ms = Column(Integer, default=0)
    stability_score = Column(Float, default=1.0)
    rewrites = Column(Integer, default=0)
    timestamp = Column(Float, default=time.time)

class GlossaryRecord(Base):
    __tablename__ = "glossary_terms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    term = Column(String, unique=True, index=True)
    action = Column(String, default="preserve")  # preserve, preferred
    replacement = Column(String, nullable=True)
    target_language = Column(String, nullable=True)
    created_at = Column(Float, default=time.time)

class BenchmarkRecord(Base):
    __tablename__ = "benchmark_runs"

    id = Column(String, primary_key=True, index=True)
    timestamp = Column(Float, default=time.time)
    results_json = Column(Text)
