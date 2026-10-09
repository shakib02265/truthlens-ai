import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Boolean, Float, Integer, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), default="investigator")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    investigations = relationship("Investigation", back_populates="user", cascade="all, delete-orphan")
    human_reviews = relationship("HumanReview", back_populates="reviewer")

class Claim(Base):
    __tablename__ = "claims"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    text = Column(Text, nullable=False)
    topic = Column(String(255), nullable=True)
    claim_type = Column(String(100), nullable=True)
    time_sensitive = Column(Boolean, default=False)
    entities = Column(JSON, default=list)
    investigation_questions = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    investigations = relationship("Investigation", back_populates="claim")

class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    claim_id = Column(String(36), ForeignKey("claims.id"), nullable=False)
    title = Column(String(255), nullable=False)
    status = Column(String(50), default="PENDING")  # PENDING, IN_PROGRESS, COMPLETED, FAILED, AWAITING_HUMAN_REVIEW
    verdict_status = Column(String(50), nullable=True)
    confidence_score = Column(Float, nullable=True)
    mode = Column(String(50), default="DEMO")  # DEMO or LIVE
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="investigations")
    claim = relationship("Claim", back_populates="investigations")
    search_queries = relationship("SearchQuery", back_populates="investigation", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="investigation", cascade="all, delete-orphan")
    evidence = relationship("Evidence", back_populates="investigation", cascade="all, delete-orphan")
    contradictions = relationship("Contradiction", back_populates="investigation", cascade="all, delete-orphan")
    agent_runs = relationship("AgentRun", back_populates="investigation", cascade="all, delete-orphan")
    verdicts = relationship("Verdict", back_populates="investigation", cascade="all, delete-orphan")
    human_reviews = relationship("HumanReview", back_populates="investigation", cascade="all, delete-orphan")

class SearchQuery(Base):
    __tablename__ = "search_queries"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    investigation_id = Column(String(36), ForeignKey("investigations.id"), nullable=False)
    query_text = Column(Text, nullable=False)
    rationale = Column(Text, nullable=True)
    status = Column(String(50), default="EXECUTED")
    results_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    investigation = relationship("Investigation", back_populates="search_queries")

class Source(Base):
    __tablename__ = "sources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    investigation_id = Column(String(36), ForeignKey("investigations.id"), nullable=False)
    url = Column(Text, nullable=False)
    title = Column(Text, nullable=True)
    domain = Column(String(255), nullable=True)
    publication_date = Column(String(100), nullable=True)
    snippet = Column(Text, nullable=True)
    source_type = Column(String(100), nullable=True)  # academic, news, government, opinion, blog, unknown
    content = Column(Text, nullable=True)
    is_accessible = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    investigation = relationship("Investigation", back_populates="sources")
    evaluation = relationship("SourceEvaluation", back_populates="source", uselist=False, cascade="all, delete-orphan")
    evidence_items = relationship("Evidence", back_populates="source", cascade="all, delete-orphan")

class SourceEvaluation(Base):
    __tablename__ = "source_evaluations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    source_id = Column(String(36), ForeignKey("sources.id"), nullable=False, unique=True)
    authority_score = Column(Float, default=0.5)
    recency_score = Column(Float, default=0.5)
    primary_secondary_score = Column(Float, default=0.5)
    evidence_quality_score = Column(Float, default=0.5)
    domain_reputation_score = Column(Float, default=0.5)
    citation_quality_score = Column(Float, default=0.5)
    final_credibility_score = Column(Float, default=0.5)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    source = relationship("Source", back_populates="evaluation")

class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    investigation_id = Column(String(36), ForeignKey("investigations.id"), nullable=False)
    source_id = Column(String(36), ForeignKey("sources.id"), nullable=False)
    evidence_text = Column(Text, nullable=False)
    stance = Column(String(50), nullable=False)  # SUPPORTS, CONTRADICTS, NEUTRAL
    strength = Column(Float, default=0.7)  # 0.0 to 1.0
    context = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    investigation = relationship("Investigation", back_populates="evidence")
    source = relationship("Source", back_populates="evidence_items")

class Contradiction(Base):
    __tablename__ = "contradictions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    investigation_id = Column(String(36), ForeignKey("investigations.id"), nullable=False)
    supporting_evidence_ids = Column(JSON, default=list)
    contradicting_evidence_ids = Column(JSON, default=list)
    contradiction_type = Column(String(100), nullable=True)  # direct_factual, methodological, date_difference, definition_difference, population_difference
    description = Column(Text, nullable=False)
    severity = Column(Float, default=0.5)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    investigation = relationship("Investigation", back_populates="contradictions")

class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    investigation_id = Column(String(36), ForeignKey("investigations.id"), nullable=False)
    agent_name = Column(String(100), nullable=False)
    start_time = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    end_time = Column(DateTime(timezone=True), nullable=True)
    input_summary = Column(Text, nullable=True)
    tool_used = Column(String(255), nullable=True)
    tool_result_summary = Column(Text, nullable=True)
    decision = Column(Text, nullable=True)
    token_usage = Column(JSON, default=dict)
    error = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    investigation = relationship("Investigation", back_populates="agent_runs")

class Verdict(Base):
    __tablename__ = "verdicts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    investigation_id = Column(String(36), ForeignKey("investigations.id"), nullable=False)
    verdict = Column(String(50), nullable=False)  # TRUE, MOSTLY TRUE, PARTIALLY TRUE, MISLEADING, MOSTLY FALSE, FALSE, UNVERIFIED, INSUFFICIENT EVIDENCE
    reasoning_summary = Column(Text, nullable=False)
    key_evidence = Column(JSON, default=list)
    limitations = Column(JSON, default=list)
    verified = Column(Boolean, default=False)
    verification_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    investigation = relationship("Investigation", back_populates="verdicts")

class HumanReview(Base):
    __tablename__ = "human_reviews"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    investigation_id = Column(String(36), ForeignKey("investigations.id"), nullable=False)
    reviewer_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    action = Column(String(50), nullable=False)  # ACCEPT, REJECT, REQUEST_MORE_INVESTIGATION
    feedback = Column(Text, nullable=True)
    status = Column(String(50), default="SUBMITTED")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    investigation = relationship("Investigation", back_populates="human_reviews")
    reviewer = relationship("User", back_populates="human_reviews")
