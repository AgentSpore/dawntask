"""Habit tracking schemas for DawnTask v2."""

from pydantic import BaseModel, Field


class HabitData(BaseModel):
    id: str
    name: str
    category: str = ""
    emoji: str = ""
    full: str = ""
    micro: str = ""
    min_energy: str = "zombie"  # zombie | okay | energized


class CheckinData(BaseModel):
    date: str
    habit_id: str
    done: bool = True
    micro: bool = False


class EnergyData(BaseModel):
    date: str
    level: str  # zombie | okay | energized


class WeeklyReflectionRequest(BaseModel):
    habits: list[HabitData] = Field(default_factory=list, max_length=20)
    checkins: list[CheckinData] = Field(default_factory=list, max_length=200)
    energy: list[EnergyData] = Field(default_factory=list, max_length=14)
    lang: str = "en"


class ReflectionResponse(BaseModel):
    reflection: str
    patterns: list[str] = []
    suggestions: list[str] = []
    model_used: str = ""
