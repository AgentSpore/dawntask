"""Habits and weekly reflection endpoints."""

from fastapi import APIRouter, HTTPException

from ..schemas.habit import WeeklyReflectionRequest, ReflectionResponse
from ..services.reflection_service import generate_reflection, ReflectionError

router = APIRouter(prefix="/api", tags=["habits"])


@router.post("/weekly-reflection", response_model=ReflectionResponse)
async def create_reflection(req: WeeklyReflectionRequest):
    habits = [h.model_dump() for h in req.habits]
    checkins = [c.model_dump() for c in req.checkins]
    energy = [e.model_dump() for e in req.energy]
    try:
        result = await generate_reflection(habits, checkins, energy, req.lang)
    except ReflectionError as e:
        raise HTTPException(502, str(e))
    return ReflectionResponse(
        reflection=result.get("reflection", ""),
        patterns=result.get("patterns", []),
        suggestions=result.get("suggestions", []),
        model_used=result.get("model_used", ""),
    )
