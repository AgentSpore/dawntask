import time
import httpx
from fastapi import APIRouter, HTTPException
from ..schemas.plan import GeneratePlanRequest, PlanResponse
from ..services.plan_service import generate_plan, PlanError
from ..core.config import settings

router = APIRouter(prefix="/api", tags=["plans"])

_models_cache: list[dict] = []
_models_cache_ts: float = 0
CACHE_TTL = 3600


async def _fetch_free_models() -> list[dict]:
    global _models_cache, _models_cache_ts
    if _models_cache and time.time() - _models_cache_ts < CACHE_TTL:
        return _models_cache
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get("https://openrouter.ai/api/v1/models")
            data = resp.json()
            models = []
            for m in data.get("data", []):
                pricing = m.get("pricing", {})
                if pricing.get("prompt") == "0" and pricing.get("completion") == "0":
                    modalities = m.get("architecture", {}).get("output_modalities", [])
                    if "text" not in modalities:
                        continue
                    models.append({
                        "id": m["id"],
                        "name": m.get("name", m["id"]),
                        "context_length": m.get("context_length", 0),
                    })
            models.sort(key=lambda x: x["name"])
            _models_cache = models
            _models_cache_ts = time.time()
            return models
    except Exception:
        return _models_cache or []


@router.get("/config")
async def get_config():
    models = await _fetch_free_models()
    default = settings.llm_model
    # Ensure default is a free model
    free_ids = {m["id"] for m in models}
    if default not in free_ids and models:
        default = models[0]["id"]
    return {
        "default_model": default,
        "models": models,
        "has_api_key": bool(settings.openrouter_api_key),
    }


@router.post("/generate-plan", response_model=PlanResponse)
async def create_plan(req: GeneratePlanRequest):
    thoughts = [{"content": t.content, "created_at": t.created_at} for t in req.thoughts]
    try:
        result = await generate_plan(thoughts, req.model, req.energy)
    except PlanError as e:
        raise HTTPException(502, str(e))
    return PlanResponse(
        letter=result["letter"],
        items=result.get("items", []),
        model_used=result["model_used"],
        insights=result.get("insights", []),
    )
