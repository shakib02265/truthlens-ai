import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.models import (
    User, Claim, Investigation, SearchQuery, Source, SourceEvaluation,
    Evidence, Contradiction, AgentRun, Verdict, HumanReview
)
from app.graph.workflow import truthlens_graph, TruthLensState
from app.services.sse_service import sse_broadcaster

logger = logging.getLogger(__name__)

class InvestigationService:

    @staticmethod
    def create_investigation(db: Session, user_id: str, claim_text: str, mode: str = "DEMO") -> Investigation:
        # Create Claim record
        claim = Claim(text=claim_text)
        db.add(claim)
        db.flush()

        title = claim_text[:50] + "..." if len(claim_text) > 50 else claim_text

        # Create Investigation record
        inv = Investigation(
            user_id=user_id,
            claim_id=claim.id,
            title=title,
            status="PENDING",
            mode=mode
        )
        db.add(inv)
        db.commit()
        db.refresh(inv)
        return inv

    @staticmethod
    async def run_investigation(investigation_id: str, db: Optional[Session] = None):
        """Runs the LangGraph multi-agent pipeline using a fresh DB session for BackgroundTask safety."""
        own_db = False
        if db is None:
            db = SessionLocal()
            own_db = True
        try:
            inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
            if not inv:
                logger.error(f"Investigation {investigation_id} not found in DB")
                return

            inv.status = "IN_PROGRESS"
            db.commit()

            claim = db.query(Claim).filter(Claim.id == inv.claim_id).first()
            if not claim:
                logger.error(f"Claim for investigation {investigation_id} not found in DB")
                return

            initial_state: TruthLensState = {
                "investigation_id": inv.id,
                "claim": claim.text,
                "claim_analysis": {},
                "investigation_plan": {},
                "search_queries": [],
                "sources": [],
                "source_scores": {},
                "evidence": [],
                "contradictions": [],
                "confidence": {},
                "verdict": {},
                "verification_result": {},
                "human_review_required": False,
                "human_review_reason": "",
                "verification_retries": 0,
                "search_retries": 0,
                "agent_trace": [],
                "errors": [],
                "completed": False
            }

            # Invoke multi-agent LangGraph workflow
            logger.info(f"Invoking multi-agent LangGraph workflow for investigation {investigation_id}...")
            final_state = await truthlens_graph.ainvoke(initial_state)

            # Broadcast execution traces over SSE
            for trace in final_state.get("agent_trace", []):
                await sse_broadcaster.broadcast(
                    investigation_id=inv.id,
                    event_type="agent_trace",
                    data=trace
                )

            # Update Claim metadata
            c_analysis = final_state.get("claim_analysis", {})
            claim.topic = c_analysis.get("topic")
            claim.claim_type = c_analysis.get("claim_type")
            claim.time_sensitive = c_analysis.get("time_sensitive", False)
            claim.entities = c_analysis.get("entities", [])
            claim.investigation_questions = c_analysis.get("investigation_questions", [])

            # Delete previous child records if re-running investigation to prevent UNIQUE constraint failures
            db.query(Verdict).filter(Verdict.investigation_id == inv.id).delete()
            db.query(SearchQuery).filter(SearchQuery.investigation_id == inv.id).delete()
            db.query(Evidence).filter(Evidence.investigation_id == inv.id).delete()
            db.query(Contradiction).filter(Contradiction.investigation_id == inv.id).delete()
            db.query(AgentRun).filter(AgentRun.investigation_id == inv.id).delete()
            # Delete source evaluations first, then sources
            existing_sources = db.query(Source).filter(Source.investigation_id == inv.id).all()
            for ex_s in existing_sources:
                db.query(SourceEvaluation).filter(SourceEvaluation.source_id == ex_s.id).delete()
            db.query(Source).filter(Source.investigation_id == inv.id).delete()
            db.flush()

            # Store Search Queries
            for q in final_state.get("search_queries", []):
                sq = SearchQuery(investigation_id=inv.id, query_text=q, rationale="Dynamic Planner query")
                db.add(sq)

            # Store Sources & Evaluations (Deduplicated by URL)
            url_to_source_model = {}
            seen_source_urls = set()
            for s in final_state.get("sources", []):
                s_url = s.get("url")
                if not s_url or s_url in seen_source_urls:
                    continue
                seen_source_urls.add(s_url)

                src_model = Source(
                    investigation_id=inv.id,
                    url=s_url,
                    title=s.get("title"),
                    domain=s.get("domain"),
                    publication_date=s.get("publication_date"),
                    snippet=s.get("snippet"),
                    source_type=s.get("source_type"),
                    content=s.get("content"),
                    is_accessible=s.get("is_accessible", True)
                )
                db.add(src_model)
                db.flush()
                url_to_source_model[s_url] = src_model

                eval_data = s.get("evaluation", {})
                if eval_data:
                    se = SourceEvaluation(
                        source_id=src_model.id,
                        authority_score=eval_data.get("authority_score", 0.5),
                        recency_score=eval_data.get("recency_score", 0.5),
                        primary_secondary_score=eval_data.get("primary_secondary_score", 0.5),
                        evidence_quality_score=eval_data.get("evidence_quality_score", 0.5),
                        domain_reputation_score=eval_data.get("domain_reputation_score", 0.5),
                        citation_quality_score=eval_data.get("citation_quality_score", 0.5),
                        final_credibility_score=eval_data.get("final_credibility_score", 0.5),
                        explanation=eval_data.get("explanation")
                    )
                    db.add(se)

            # Store Evidence
            for ev in final_state.get("evidence", []):
                src_url = ev.get("source_url")
                src_obj = url_to_source_model.get(src_url)
                if src_obj:
                    ev_model = Evidence(
                        investigation_id=inv.id,
                        source_id=src_obj.id,
                        evidence_text=ev.get("evidence_text", ""),
                        stance=ev.get("stance", "NEUTRAL"),
                        strength=ev.get("strength", 0.7),
                        context=ev.get("context")
                    )
                    db.add(ev_model)

            # Store Contradictions
            for cnt in final_state.get("contradictions", []):
                cnt_model = Contradiction(
                    investigation_id=inv.id,
                    contradiction_type=cnt.get("contradiction_type"),
                    description=cnt.get("description", ""),
                    severity=cnt.get("severity", 0.5)
                )
                db.add(cnt_model)

            # Store Agent Runs
            for trace in final_state.get("agent_trace", []):
                ar = AgentRun(
                    investigation_id=inv.id,
                    agent_name=trace.get("agent_name", "Agent"),
                    decision=trace.get("decision"),
                    tool_used=trace.get("tool_used"),
                    tool_result_summary=trace.get("tool_result_summary")
                )
                db.add(ar)

            # Store Verdict & Confidence
            conf_data = final_state.get("confidence", {})
            verdict_data = final_state.get("verdict", {})
            verdict_str = verdict_data.get("verdict", "UNVERIFIED")
            reasoning_str = verdict_data.get("reasoning_summary", "No reasoning produced.")

            from app.graph.workflow import is_verification_passed
            v_model = Verdict(
                investigation_id=inv.id,
                verdict=verdict_str,
                reasoning_summary=reasoning_str,
                key_evidence=verdict_data.get("key_evidence", []),
                limitations=verdict_data.get("limitations", []),
                verified=is_verification_passed(final_state.get("verification_result")),
                verification_notes=final_state.get("verification_result", {}).get("notes")
            )
            db.add(v_model)

            # Update Investigation Status
            print(f"SAVING INVESTIGATION {investigation_id} STATUS. human_review={final_state.get('human_review_required')}")
            inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
            inv.confidence_score = conf_data.get("confidence_score", 0.5)
            inv.verdict_status = verdict_str

            if final_state.get("human_review_required"):
                inv.status = "AWAITING_HUMAN_REVIEW"
            else:
                inv.status = "COMPLETED"

            db.commit()
            print(f"SUCCESSFULLY COMMITTED STATUS {inv.status} FOR {investigation_id}")
            logger.info(f"Investigation {investigation_id} successfully COMPLETED with status {inv.status} and verdict {verdict_str}")

            # Send completion SSE broadcast
            await sse_broadcaster.broadcast(
                investigation_id=inv.id,
                event_type="completed",
                data={"status": inv.status, "verdict": inv.verdict_status, "confidence": inv.confidence_score}
            )
        except Exception as ex:
            import traceback
            print(f"FAILED REASON FOR {investigation_id}: {ex}")
            traceback.print_exc()
            logger.error(f"Error in run_investigation task: {ex}", exc_info=True)
            db.rollback()
            try:
                inv_failed = db.query(Investigation).filter(Investigation.id == investigation_id).first()
                if inv_failed:
                    inv_failed.status = "FAILED"
                    db.commit()
            except Exception:
                pass
        finally:
            if own_db:
                db.close()

    @staticmethod
    def get_evidence_graph(db: Session, investigation_id: str) -> Dict[str, Any]:
        inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
        if not inv:
            return {"nodes": [], "edges": []}

        nodes = []
        edges = []

        # Claim Node
        claim = inv.claim
        nodes.append({
            "id": f"claim_{claim.id}",
            "label": f"Claim: {claim.text[:40]}...",
            "type": "claim",
            "data": {"text": claim.text, "topic": claim.topic}
        })

        # Verdict Node
        verdict = db.query(Verdict).filter(Verdict.investigation_id == investigation_id).first()
        if verdict:
            verdict_node_id = f"verdict_{verdict.id}"
            nodes.append({
                "id": verdict_node_id,
                "label": f"Verdict: {verdict.verdict}",
                "type": "verdict",
                "stance": verdict.verdict,
                "data": {"reasoning": verdict.reasoning_summary}
            })
            edges.append({
                "id": f"e_claim_verdict",
                "source": f"claim_{claim.id}",
                "target": verdict_node_id,
                "relationship": "DERIVED_FROM",
                "weight": inv.confidence_score or 0.8
            })

        # Sources & Evidence Nodes
        sources = db.query(Source).filter(Source.investigation_id == investigation_id).all()
        for src in sources:
            src_node_id = f"src_{src.id}"
            credibility = src.evaluation.final_credibility_score if src.evaluation else 0.5
            nodes.append({
                "id": src_node_id,
                "label": src.domain or src.title[:30],
                "type": "source",
                "credibility_score": credibility,
                "data": {"url": src.url, "domain": src.domain}
            })
            edges.append({
                "id": f"e_claim_src_{src.id}",
                "source": f"claim_{claim.id}",
                "target": src_node_id,
                "relationship": "CITES",
                "weight": credibility
            })

            # Evidence Items
            evidence_items = db.query(Evidence).filter(Evidence.source_id == src.id).all()
            for ev in evidence_items:
                ev_node_id = f"ev_{ev.id}"
                nodes.append({
                    "id": ev_node_id,
                    "label": f"Evidence ({ev.stance})",
                    "type": "evidence",
                    "stance": ev.stance,
                    "data": {"text": ev.evidence_text, "strength": ev.strength}
                })
                # Edge from source to evidence
                edges.append({
                    "id": f"e_src_ev_{ev.id}",
                    "source": src_node_id,
                    "target": ev_node_id,
                    "relationship": "PROVIDES",
                    "weight": ev.strength
                })
                # Edge from evidence to claim
                edges.append({
                    "id": f"e_ev_claim_{ev.id}",
                    "source": ev_node_id,
                    "target": f"claim_{claim.id}",
                    "relationship": ev.stance,  # SUPPORTS, CONTRADICTS, NEUTRAL
                    "weight": ev.strength
                })

        return {"nodes": nodes, "edges": edges}
