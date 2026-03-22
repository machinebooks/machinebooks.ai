# Extraído de: LibroCyberrange/cap-18-coaching-ia.md
# Ejemplo didáctico: cyber-range-builder/backend/routers/coaching.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.auth import get_current_user
from backend.services.ai.coaching_service import CoachingService

router = APIRouter(prefix="/gaming/coaching", tags=["AI Coaching"])
coaching_service = CoachingService()

class HintRequest(BaseModel):
    challenge_id: int
    message: Optional[str] = None  # Mensaje opcional del jugador

class HintFeedback(BaseModel):
    hint_id: int
    rating: int  # 1 (inútil) a 5 (muy útil)
    comment: Optional[str] = None

@router.post("/hint")
async def request_coaching_hint(
    req: HintRequest,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """
    Endpoint para solicitar una pista de coaching (modo reactivo).
    Integrado con el sistema de penalización de puntos.
    """
    try:
        result = await coaching_service.generate_reactive_hint(
            db=db,
            user_id=user.id,
            challenge_id=req.challenge_id,
            player_message=req.message
        )
        return {
            "success": True,
            "hint": result["hint"],
            "level": result["level"],
            "penalty_pct": result["penalty_pct"],
            "mode": result["mode"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando pista: {str(e)}")

@router.post("/evaluate/{challenge_id}")
async def request_evaluation(
    challenge_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """
    Endpoint para solicitar evaluación post-ejercicio (modo evaluativo).
    Solo disponible cuando el jugador ha completado o abandonado el reto.
    """
    result = await coaching_service.generate_evaluation_report(
        db=db, user_id=user.id, challenge_id=challenge_id
    )
    return {"success": True, "evaluation": result["report"]}

@router.post("/feedback")
async def submit_hint_feedback(
    feedback: HintFeedback,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """
    Feedback del jugador sobre la utilidad de una pista.
    Alimenta la mejora iterativa del prompt engineering.
    """
    coaching_service.feedback_collector.record(
        user_id=user.id,
        hint_id=feedback.hint_id,
        rating=feedback.rating,
        comment=feedback.comment
    )
    return {"success": True, "message": "Feedback registrado"}
