from pydantic import BaseModel, Field


class ThoughtItem(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    created_at: str = ""  # ISO timestamp from client


class GeneratePlanRequest(BaseModel):
    thoughts: list[ThoughtItem] = Field(..., min_length=1, max_length=50)
    model: str = ""  # optional model override
    language: str = ""  # auto-detect if empty
    energy: str = ""  # zombie | okay | energized


class PlanItem(BaseModel):
    text: str
    priority: str  # high, medium, low
    estimated_minutes: int
    category: str = ""  # fitness, work, personal, etc.


class PlanResponse(BaseModel):
    letter: str  # "letter from yesterday you"
    items: list[PlanItem]
    model_used: str
    insights: list[str] = []  # patterns noticed
