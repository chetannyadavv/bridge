from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.dispute import Dispute
from app.schemas.dispute import DisputeCreate, DisputeOut
from app.schemas.evidence import EvidenceCreate, EvidenceOut
from app.schemas.timeline_event import TimelineEventOut
from app.schemas.recommendation import RecommendationOut, AcceptRecommendationRequest
from app.services import dispute_service, evidence_service, timeline_service, recommendation_service
from app.services.recommendation_service import get_latest_recommendation
from app.decision_engine import DecisionEngine
from app.websocket.manager import manager
from app.websocket.snapshot import build_dispute_snapshot_messages

router = APIRouter(prefix="/disputes", tags=["disputes"])


def _get_dispute_or_404(db: Session, dispute_id: str) -> Dispute:
    dispute = dispute_service.get_dispute(db, dispute_id)
    if dispute is None:
        raise HTTPException(status_code=404, detail="Dispute not found")
    return dispute


async def _broadcast_dispute_state(db: Session, dispute_id: str) -> None:
    """Called after any mutation. Locked per-dispute so two nearly
    simultaneous writes (Requirement 7 — concurrent uploads) each get a
    clean, uninterleaved turn to read the current DB state and broadcast
    it — every connected client always receives a complete, internally
    consistent snapshot, never a partial one."""
    async with manager.lock_for(dispute_id):
        messages = await run_in_threadpool(build_dispute_snapshot_messages, db, dispute_id)
        for message in messages:
            await manager.broadcast(dispute_id, message)


@router.get("", response_model=list[DisputeOut])
def get_disputes(db: Session = Depends(get_db)):
    return dispute_service.list_disputes(db)


@router.post("", response_model=DisputeOut, status_code=201)
def create_dispute(payload: DisputeCreate, db: Session = Depends(get_db)):
    # Not broadcast: nobody can be connected to a dispute's room before
    # the dispute exists, so there's no room to broadcast into yet.
    return dispute_service.create_dispute(db, payload)


@router.get("/{dispute_id}", response_model=DisputeOut)
def get_dispute(dispute_id: str, db: Session = Depends(get_db)):
    return _get_dispute_or_404(db, dispute_id)


@router.get("/{dispute_id}/timeline", response_model=list[TimelineEventOut])
def get_timeline(dispute_id: str, db: Session = Depends(get_db)):
    _get_dispute_or_404(db, dispute_id)
    return timeline_service.list_timeline(db, dispute_id)


@router.get("/{dispute_id}/evidence", response_model=list[EvidenceOut])
def get_evidence(dispute_id: str, db: Session = Depends(get_db)):
    _get_dispute_or_404(db, dispute_id)
    return evidence_service.list_evidence(db, dispute_id)


@router.post("/{dispute_id}/evidence", response_model=EvidenceOut, status_code=201)
async def post_evidence(dispute_id: str, payload: EvidenceCreate, db: Session = Depends(get_db)):
    dispute = _get_dispute_or_404(db, dispute_id)
    evidence = await run_in_threadpool(evidence_service.add_evidence, db, dispute, payload)
    await _broadcast_dispute_state(db, dispute_id)
    return evidence


@router.get("/{dispute_id}/recommendation", response_model=list[RecommendationOut])
def get_recommendation(dispute_id: str, db: Session = Depends(get_db)):
    _get_dispute_or_404(db, dispute_id)
    return recommendation_service.list_recommendations(db, dispute_id)


@router.get("/{dispute_id}/decision", response_model=RecommendationOut)
def get_decision(dispute_id: str, db: Session = Depends(get_db)):
    """
    Returns the latest Decision Engine output in full — reason code,
    category, the 5-way engine recommendation, confidence, summary,
    reasons, missing evidence, and next steps. Reuses the same
    RecommendationOut schema and the same get_latest_recommendation
    service function as /recommendation, rather than returning the raw
    internal DecisionResult dataclass (which was never meant to leave
    the engine layer, and doesn't match this endpoint's documented
    contract).
    """
    _get_dispute_or_404(db, dispute_id)
    latest = recommendation_service.get_latest_recommendation(db, dispute_id)
    if latest is None:
        raise HTTPException(status_code=404, detail="No decision has been generated yet for this dispute")
    return latest


@router.post("/{dispute_id}/recommendation/accept", response_model=RecommendationOut)
async def accept_recommendation(dispute_id: str, payload: AcceptRecommendationRequest, db: Session = Depends(get_db)):
    dispute = _get_dispute_or_404(db, dispute_id)
    result = await run_in_threadpool(recommendation_service.accept_recommendation, db, dispute, payload.role)
    if result is None:
        raise HTTPException(status_code=400, detail="No recommendation exists yet for this dispute")
    await _broadcast_dispute_state(db, dispute_id)
    return result
