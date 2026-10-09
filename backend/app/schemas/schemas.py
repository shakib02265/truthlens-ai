from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# User Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class TokenData(BaseModel):
    user_id: Optional[str] = None

# Claim Schemas
class ClaimCreate(BaseModel):
    text: str

class ClaimOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    text: str
    topic: Optional[str] = None
    claim_type: Optional[str] = None
    time_sensitive: bool = False
    entities: List[str] = []
    investigation_questions: List[str] = []
    created_at: datetime

# Source & Evaluation Schemas
class SourceEvaluationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    authority_score: float
    recency_score: float
    primary_secondary_score: float
    evidence_quality_score: float
    domain_reputation_score: float
    citation_quality_score: float
    final_credibility_score: float
    explanation: Optional[str] = None

class SourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    url: str
    title: Optional[str] = None
    domain: Optional[str] = None
    publication_date: Optional[str] = None
    snippet: Optional[str] = None
    source_type: Optional[str] = None
    is_accessible: bool = True
    evaluation: Optional[SourceEvaluationOut] = None

# Evidence Schemas
class EvidenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source_id: str
    evidence_text: str
    stance: str
    strength: float
    context: Optional[str] = None
    source: Optional[SourceOut] = None

# Contradiction Schemas
class ContradictionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    supporting_evidence_ids: List[str] = []
    contradicting_evidence_ids: List[str] = []
    contradiction_type: Optional[str] = None
    description: str
    severity: float

# Agent Run / Trace Schemas
class AgentRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    agent_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    input_summary: Optional[str] = None
    tool_used: Optional[str] = None
    tool_result_summary: Optional[str] = None
    decision: Optional[str] = None
    token_usage: Dict[str, Any] = {}
    error: Optional[str] = None
    retry_count: int = 0

# Verdict Schemas
class VerdictOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    verdict: str
    reasoning_summary: str
    key_evidence: List[Any] = []
    limitations: List[str] = []
    verified: bool = False
    verification_notes: Optional[str] = None
    created_at: datetime

# Human Review Schemas
class HumanReviewCreate(BaseModel):
    action: str  # ACCEPT, REJECT, REQUEST_MORE_INVESTIGATION
    feedback: Optional[str] = None

class HumanReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    reviewer_id: Optional[str] = None
    action: str
    feedback: Optional[str] = None
    status: str
    created_at: datetime

# Investigation Schemas
class InvestigationCreate(BaseModel):
    claim: str
    mode: Optional[str] = "DEMO"

class InvestigationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    claim_id: str
    title: str
    status: str
    verdict_status: Optional[str] = None
    confidence_score: Optional[float] = None
    mode: str
    created_at: datetime
    updated_at: datetime
    claim: ClaimOut

class SearchQueryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    query_text: str
    rationale: Optional[str] = None
    status: str
    results_count: int
    created_at: datetime

class InvestigationDetail(InvestigationOut):
    search_queries: List[SearchQueryOut] = []
    sources: List[SourceOut] = []
    evidence: List[EvidenceOut] = []
    contradictions: List[ContradictionOut] = []
    verdicts: List[VerdictOut] = []
    human_reviews: List[HumanReviewOut] = []
    agent_runs: List[AgentRunOut] = []

# Evidence Graph Schemas
class EvidenceGraphNode(BaseModel):
    id: str
    label: str
    type: str  # claim, source, evidence, verdict
    credibility_score: Optional[float] = None
    stance: Optional[str] = None
    data: Dict[str, Any] = {}

class EvidenceGraphEdge(BaseModel):
    id: str
    source: str
    target: str
    relationship: str  # SUPPORTS, CONTRADICTS, NEUTRAL, DERIVED_FROM
    weight: float = 1.0

class EvidenceGraphData(BaseModel):
    nodes: List[EvidenceGraphNode]
    edges: List[EvidenceGraphEdge]
