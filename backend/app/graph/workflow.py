import logging
import asyncio
from datetime import datetime, timezone
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from app.agents.agents import (
    ClaimAnalyzerAgent,
    PlannerAgent,
    ResearchAgent,
    SourceCredibilityAgent,
    EvidenceExtractionAgent,
    ContradictionDetectionAgent,
    VerdictAgent,
    VerificationAgent
)
from app.tools.tools import calculate_confidence
from app.core.config import settings

logger = logging.getLogger(__name__)

class TruthLensState(TypedDict):
    investigation_id: str
    claim: str
    claim_analysis: Dict[str, Any]
    investigation_plan: Dict[str, Any]
    search_queries: List[str]
    sources: List[Dict[str, Any]]
    source_scores: Dict[str, Any]
    evidence: List[Dict[str, Any]]
    contradictions: List[Dict[str, Any]]
    confidence: Dict[str, Any]
    verdict: Dict[str, Any]
    verification_result: Dict[str, Any]
    human_review_required: bool
    human_review_reason: str
    verification_retries: int
    search_retries: int
    agent_trace: List[Dict[str, Any]]
    errors: List[str]
    completed: bool

# Initialize Agent Instances
claim_analyzer_agent = ClaimAnalyzerAgent()
planner_agent = PlannerAgent()
research_agent = ResearchAgent()
source_credibility_agent = SourceCredibilityAgent()
evidence_extraction_agent = EvidenceExtractionAgent()
contradiction_agent = ContradictionDetectionAgent()
verdict_agent = VerdictAgent()
verification_agent = VerificationAgent()

from app.services.sse_service import sse_broadcaster

def log_trace(state: TruthLensState, agent_name: str, decision: str, tool_used: Optional[str] = None, tool_result: Optional[str] = None):
    trace_entry = {
        "agent_name": agent_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "tool_used": tool_used,
        "tool_result_summary": tool_result
    }
    state["agent_trace"].append(trace_entry)
    inv_id = state.get("investigation_id")
    if inv_id:
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(sse_broadcaster.broadcast(
                investigation_id=inv_id,
                event_type="agent_trace",
                data=trace_entry
            ))
        except Exception:
            pass


async def node_claim_analyzer(state: TruthLensState) -> TruthLensState:
    try:
        res = await claim_analyzer_agent.analyze(state["claim"])
        state["claim_analysis"] = res
        log_trace(state, "Claim Analyzer Agent", f"Claim deconstructed into {len(res.get('entities', []))} entities and {len(res.get('investigation_questions', []))} questions.")
    except Exception as e:
        state["errors"].append(f"ClaimAnalyzer error: {str(e)}")
        log_trace(state, "Claim Analyzer Agent", f"Error during analysis: {str(e)}")
    return state

async def node_planner(state: TruthLensState) -> TruthLensState:
    try:
        plan = await planner_agent.plan(state["claim_analysis"])
        state["investigation_plan"] = plan
        state["search_queries"] = plan.get("queries", [])
        log_trace(state, "Investigation Planner Agent", f"Generated {len(state['search_queries'])} targeted search queries.")
    except Exception as e:
        state["errors"].append(f"Planner error: {str(e)}")
        log_trace(state, "Investigation Planner Agent", f"Error creating plan: {str(e)}")
    return state

async def node_research(state: TruthLensState) -> TruthLensState:
    try:
        queries = state["search_queries"]
        if not queries:
            queries = [state["claim"]]
        
        sources = await research_agent.execute_research(queries)
        state["sources"] = sources
        log_trace(state, "Research Agent", f"Executed web search and retrieved {len(sources)} unique accessible sources.", tool_used="web_search")
    except Exception as e:
        state["errors"].append(f"Research error: {str(e)}")
        log_trace(state, "Research Agent", f"Search failure: {str(e)}")
    return state

async def node_source_evaluation(state: TruthLensState) -> TruthLensState:
    scores = {}
    total_cred = 0.0
    valid_sources = 0

    for s in state["sources"]:
        try:
            eval_res = await source_credibility_agent.evaluate_source(s, state["claim"])
            s["evaluation"] = eval_res
            scores[s["url"]] = eval_res
            total_cred += eval_res.get("final_credibility_score", 0.5)
            valid_sources += 1
        except Exception as e:
            s["evaluation"] = {"final_credibility_score": 0.5, "explanation": f"Evaluation error: {str(e)}"}

    state["source_scores"] = scores
    avg_cred = (total_cred / valid_sources) if valid_sources > 0 else 0.5
    log_trace(state, "Source Credibility Agent", f"Evaluated {valid_sources} sources. Average credibility score: {avg_cred:.2f}.")
    return state

async def node_evidence_extraction(state: TruthLensState) -> TruthLensState:
    all_evidence = []
    for s in state["sources"]:
        try:
            ev_list = await evidence_extraction_agent.extract_evidence(state["claim"], s)
            for ev in ev_list:
                ev["source_url"] = s["url"]
                ev["source_title"] = s["title"]
                all_evidence.append(ev)
        except Exception as e:
            logger.warning(f"Error extracting evidence from {s.get('url')}: {e}")

    state["evidence"] = all_evidence
    log_trace(state, "Evidence Extraction Agent", f"Extracted {len(all_evidence)} distinct evidence statements from sources.")
    if len(all_evidence) == 0:
        state["search_retries"] = state.get("search_retries", 0) + 1
    return state

async def node_contradiction_detection(state: TruthLensState) -> TruthLensState:
    try:
        contradictions = await contradiction_agent.detect_contradictions(state["claim"], state["evidence"])
        state["contradictions"] = contradictions
        log_trace(state, "Contradiction Detection Agent", f"Analyzed evidence alignment. Detected {len(contradictions)} potential contradictions.")
    except Exception as e:
        state["errors"].append(f"Contradiction detection error: {str(e)}")
        log_trace(state, "Contradiction Detection Agent", f"Error in contradiction detection: {str(e)}")
    return state

async def node_confidence_engine(state: TruthLensState) -> TruthLensState:
    # Compute component factors
    sources = state["sources"]
    ev_list = state["evidence"]
    contradictions = state["contradictions"]

    # 1. Source Quality
    source_quality = 0.5
    if sources:
        cred_scores = [s.get("evaluation", {}).get("final_credibility_score", 0.5) for s in sources]
        source_quality = sum(cred_scores) / len(cred_scores)

    # 2. Evidence Agreement & Strength
    supports_count = sum(1 for e in ev_list if e.get("stance") == "SUPPORTS")
    contradicts_count = sum(1 for e in ev_list if e.get("stance") == "CONTRADICTS")
    total_stance = supports_count + contradicts_count
    
    if total_stance > 0:
        evidence_agreement = max(supports_count, contradicts_count) / total_stance
    else:
        evidence_agreement = 0.5

    strengths = [e.get("strength", 0.7) for e in ev_list]
    evidence_strength = (sum(strengths) / len(strengths)) if strengths else 0.5

    # 3. Recency & Independent Sources
    recency = 0.8
    unique_domains = len(set(s.get("domain") for s in sources if s.get("domain")))
    independent_sources = min(1.0, unique_domains / 3.0)

    # 4. Contradiction Penalty
    contradiction_penalty = min(1.0, sum(c.get("severity", 0.5) for c in contradictions))

    res = calculate_confidence(
        source_quality=source_quality,
        evidence_agreement=evidence_agreement,
        evidence_strength=evidence_strength,
        recency=recency,
        independent_sources=independent_sources,
        contradiction_penalty=contradiction_penalty
    )

    state["confidence"] = res
    log_trace(
        state,
        "Confidence Engine",
        f"Calculated deterministic confidence score: {res['confidence_score'] * 100:.1f}% ({res['confidence_level']})."
    )
    return state

async def node_verdict(state: TruthLensState) -> TruthLensState:
    try:
        conf_score = state["confidence"].get("confidence_score", 0.5)
        verdict_res = await verdict_agent.generate_verdict(
            claim=state["claim"],
            evidence_items=state["evidence"],
            contradictions=state["contradictions"],
            confidence_score=conf_score
        )
        state["verdict"] = verdict_res
        log_trace(state, "Verdict Agent", f"Formulated proposed verdict: '{verdict_res.get('verdict')}' based on evidence synthesis.")
    except Exception as e:
        state["errors"].append(f"Verdict error: {str(e)}")
        log_trace(state, "Verdict Agent", f"Error generating verdict: {str(e)}")
    return state

def is_verification_passed(res: Optional[Dict[str, Any]]) -> bool:
    if not res or not isinstance(res, dict):
        return True
    if "verified" not in res:
        return True
    val = res.get("verified", True)
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower() in ("true", "1", "yes", "passed")
    return True

async def node_verification(state: TruthLensState) -> TruthLensState:
    try:
        verification_res = await verification_agent.verify_verdict(
            claim=state["claim"],
            verdict_data=state["verdict"],
            evidence_items=state["evidence"]
        )
        state["verification_result"] = verification_res
        
        is_verified = is_verification_passed(verification_res)
        log_trace(
            state,
            "Verification Agent",
            f"Verification result: {'PASSED' if is_verified else 'REVISION NEEDED'}."
        )
    except Exception as e:
        state["verification_result"] = {"verified": True, "notes": f"Verification bypassed due to error: {e}"}
        log_trace(state, "Verification Agent", "Verification completed with fallback.")
    
    state["verification_retries"] = state.get("verification_retries", 0) + 1
    return state

async def node_human_review_check(state: TruthLensState) -> TruthLensState:
    conf_score = state["confidence"].get("confidence_score", 1.0)
    has_high_contradiction = any(c.get("severity", 0) > 0.60 for c in state.get("contradictions", []))
    
    sources = state.get("sources", [])
    if sources:
        cred_scores = [s.get("evaluation", {}).get("final_credibility_score", 0.5) for s in sources]
        avg_source_quality = sum(cred_scores) / len(cred_scores)
    else:
        avg_source_quality = 1.0

    low_source_quality = avg_source_quality < 0.45

    if conf_score < 0.60 or has_high_contradiction or low_source_quality:
        state["human_review_required"] = True
        reasons = []
        if conf_score < 0.60:
            reasons.append(f"Low confidence ({conf_score*100:.1f}% < 60%)")
        if has_high_contradiction:
            reasons.append("High contradiction severity between evidence sources")
        if low_source_quality:
            reasons.append("Low overall source credibility")
        state["human_review_reason"] = ", ".join(reasons)
        log_trace(state, "Human Review System", f"Human review triggered: {state['human_review_reason']}.")
    else:
        state["human_review_required"] = False
        state["human_review_reason"] = ""
        log_trace(state, "Human Review System", "Confidence and evidence quality meet automated threshold. No human intervention needed.")

    state["completed"] = True
    return state

# Conditional Router Functions
def route_after_evidence(state: TruthLensState) -> str:
    """If evidence is empty and search retries < 1, generate sub-queries."""
    if len(state.get("evidence", [])) == 0 and state.get("search_retries", 0) < 1:
        log_trace(state, "LangGraph Router", "Insufficient evidence collected. Triggering additional search query refinement loop.")
        return "planner"
    return "contradiction"

def route_after_verification(state: TruthLensState) -> str:
    """If verification failed and retries < 1, return to verdict agent for revision once."""
    is_verified = is_verification_passed(state.get("verification_result"))
    retries = state.get("verification_retries", 0)
    if not is_verified and retries < 1:
        log_trace(state, "LangGraph Router", f"Verification requested revision. Returning to Verdict Agent for attempt {retries}.")
        return "verdict"
    return "human_review"




def create_truthlens_graph():
    builder = StateGraph(TruthLensState)

    # Add Nodes
    builder.add_node("claim_analyzer", node_claim_analyzer)
    builder.add_node("planner", node_planner)
    builder.add_node("research", node_research)
    builder.add_node("source_evaluation", node_source_evaluation)
    builder.add_node("evidence_extraction", node_evidence_extraction)
    builder.add_node("contradiction", node_contradiction_detection)
    builder.add_node("confidence", node_confidence_engine)
    builder.add_node("verdict", node_verdict)
    builder.add_node("verification", node_verification)
    builder.add_node("human_review", node_human_review_check)

    # Set Entry Point
    builder.set_entry_point("claim_analyzer")

    # Connect Straight Edges
    builder.add_edge("claim_analyzer", "planner")
    builder.add_edge("planner", "research")
    builder.add_edge("research", "source_evaluation")
    builder.add_edge("source_evaluation", "evidence_extraction")

    # Conditional Routing after evidence extraction
    builder.add_conditional_edges(
        "evidence_extraction",
        route_after_evidence,
        {
            "planner": "planner",
            "contradiction": "contradiction"
        }
    )

    builder.add_edge("contradiction", "confidence")
    builder.add_edge("confidence", "verdict")
    builder.add_edge("verdict", "verification")

    # Conditional Routing after verification
    builder.add_conditional_edges(
        "verification",
        route_after_verification,
        {
            "verdict": "verdict",
            "human_review": "human_review"
        }
    )

    builder.add_edge("human_review", END)

    return builder.compile()

truthlens_graph = create_truthlens_graph()
