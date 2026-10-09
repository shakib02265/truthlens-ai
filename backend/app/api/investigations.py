import asyncio
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api.deps import get_db, get_current_user
from app.models.models import (
    User, Investigation, Claim, Source, Evidence, Verdict, AgentRun, HumanReview
)
from app.schemas.schemas import (
    InvestigationCreate, InvestigationOut, InvestigationDetail,
    SourceOut, EvidenceOut, AgentRunOut, VerdictOut, HumanReviewCreate, HumanReviewOut,
    EvidenceGraphData
)
from app.services.investigation_service import InvestigationService
from app.services.report_service import ReportService
from app.services.sse_service import sse_broadcaster

router = APIRouter(prefix="/investigations", tags=["Investigations"])

@router.post("", response_model=InvestigationOut, status_code=status.HTTP_201_CREATED)
async def create_investigation(
    payload: InvestigationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inv = InvestigationService.create_investigation(
        db=db,
        user_id=current_user.id,
        claim_text=payload.claim,
        mode=payload.mode or "DEMO"
    )
    # Schedule background execution automatically using investigation ID on the main async event loop
    background_tasks.add_task(InvestigationService.run_investigation, inv.id)
    return inv

@router.get("", response_model=List[InvestigationOut])
def list_investigations(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    investigations = db.query(Investigation).filter(
        Investigation.user_id == current_user.id
    ).order_by(Investigation.created_at.desc()).offset(skip).limit(limit).all()
    return investigations

@router.get("/dashboard/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total = db.query(Investigation).filter(Investigation.user_id == current_user.id).count()
    completed = db.query(Investigation).filter(
        Investigation.user_id == current_user.id,
        Investigation.status == "COMPLETED"
    ).count()
    
    avg_conf = db.query(func.avg(Investigation.confidence_score)).filter(
        Investigation.user_id == current_user.id,
        Investigation.confidence_score.isnot(None)
    ).scalar() or 0.0

    recent = db.query(Investigation).filter(
        Investigation.user_id == current_user.id
    ).order_by(Investigation.created_at.desc()).limit(5).all()

    # Verdict distribution
    verdict_counts = db.query(
        Investigation.verdict_status, func.count(Investigation.id)
    ).filter(
        Investigation.user_id == current_user.id,
        Investigation.verdict_status.isnot(None)
    ).group_by(Investigation.verdict_status).all()

    distribution = {v_status: count for v_status, count in verdict_counts}

    return {
        "total_investigations": total,
        "verified_investigations": completed,
        "average_confidence": round(float(avg_conf), 4),
        "verdict_distribution": distribution,
        "recent_investigations": [InvestigationOut.model_validate(inv) for inv in recent]
    }

@router.get("/{id}", response_model=InvestigationDetail)
def get_investigation(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inv = db.query(Investigation).filter(
        Investigation.id == id,
        Investigation.user_id == current_user.id
    ).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return inv

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_investigation(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inv = db.query(Investigation).filter(
        Investigation.id == id,
        Investigation.user_id == current_user.id
    ).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    db.delete(inv)
    db.commit()
    return None

@router.post("/{id}/run", response_model=InvestigationOut)
async def run_investigation(
    id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inv = db.query(Investigation).filter(
        Investigation.id == id,
        Investigation.user_id == current_user.id
    ).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    background_tasks.add_task(InvestigationService.run_investigation, inv.id)
    inv.status = "IN_PROGRESS"
    db.commit()
    db.refresh(inv)
    return inv

@router.post("/{id}/stop", response_model=InvestigationOut)
def stop_investigation(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inv = db.query(Investigation).filter(
        Investigation.id == id,
        Investigation.user_id == current_user.id
    ).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    inv.status = "STOPPED"
    db.commit()
    db.refresh(inv)
    return inv

@router.get("/{id}/sources", response_model=List[SourceOut])
def get_sources(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sources = db.query(Source).filter(Source.investigation_id == id).all()
    return sources

@router.get("/{id}/evidence", response_model=List[EvidenceOut])
def get_evidence(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    evidence = db.query(Evidence).filter(Evidence.investigation_id == id).all()
    return evidence

@router.get("/{id}/graph", response_model=EvidenceGraphData)
def get_graph(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    graph_data = InvestigationService.get_evidence_graph(db, id)
    return graph_data

@router.get("/{id}/trace", response_model=List[AgentRunOut])
def get_trace(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    runs = db.query(AgentRun).filter(AgentRun.investigation_id == id).order_by(AgentRun.created_at.asc()).all()
    return runs

from app.api.deps import get_db, get_current_user, get_current_user_from_token
from fastapi import Query

@router.get("/{id}/stream")
async def stream_trace(
    id: str,
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Server-Sent Events (SSE) live streaming endpoint for real-time agent execution trace."""
    user = get_current_user_from_token(token, db) if token else None
    queue = sse_broadcaster.subscribe(id)

    async def event_generator():
        try:
            while True:
                data = await queue.get()
                yield data
        except asyncio.CancelledError:
            sse_broadcaster.unsubscribe(id, queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/{id}/review", response_model=HumanReviewOut)
def submit_human_review(
    id: str,
    review_in: HumanReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inv = db.query(Investigation).filter(Investigation.id == id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    review = HumanReview(
        investigation_id=id,
        reviewer_id=current_user.id,
        action=review_in.action,
        feedback=review_in.feedback,
        status="COMPLETED"
    )
    db.add(review)

    if review_in.action == "ACCEPT":
        inv.status = "COMPLETED"
    elif review_in.action == "REJECT":
        inv.status = "REJECTED"
    elif review_in.action == "REQUEST_MORE_INVESTIGATION":
        inv.status = "PENDING"

    db.commit()
    db.refresh(review)
    return review

@router.post("/{id}/report")
def export_report(
    id: str,
    format: str = "html",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inv = db.query(Investigation).filter(Investigation.id == id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")

    detail = InvestigationDetail.model_validate(inv).model_dump()

    if format.lower() == "pdf":
        pdf_bytes = ReportService.generate_pdf_report(detail)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=truthlens_report_{id}.pdf"}
        )
    else:
        html_str = ReportService.generate_html_report(detail)
        return Response(content=html_str, media_type="text/html")
