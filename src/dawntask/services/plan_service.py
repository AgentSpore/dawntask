import json
import re
import httpx
from ..core.config import settings

SYSTEM_PROMPT = """You are DawnTask — an AI that transforms late-night thoughts into a structured morning action plan.

The user captured thoughts/ideas/plans last night before sleeping. Your job:

1. Read all their night thoughts carefully
2. Write a short, warm "letter from yesterday you" — motivational, personal, referencing their specific thoughts. 2-4 sentences max. Address them as "you" (second person).
3. Extract concrete ACTION ITEMS from their thoughts. Each item must be:
   - Specific and actionable (not vague)
   - Prioritized: high (must do today), medium (should do), low (nice to have)
   - Time-estimated in minutes
   - Categorized: work, health, personal, learning, creative, finance, social
4. If you notice patterns or insights (e.g. "you often plan fitness but skip it"), add them.

LANGUAGE: Detect the language of the thoughts and write EVERYTHING in that same language.

Return ONLY valid JSON (no markdown fences):
{
  "letter": "Your motivational morning letter...",
  "items": [
    {
      "text": "Specific action item",
      "priority": "high",
      "estimated_minutes": 30,
      "category": "work"
    }
  ],
  "insights": ["Pattern or insight noticed"]
}

Rules:
- Maximum 10 action items (focus > quantity)
- Be specific: "Run 3km in the park" not "Exercise"
- If a thought is vague, interpret it into the most likely actionable form
- Letter tone: warm, encouraging, like a supportive friend
- Never add items the user didn't mention or imply"""


class PlanError(Exception):
    pass


async def generate_plan(thoughts: list[dict], model: str = "", energy: str = "") -> dict:
    used_model = model or settings.llm_model

    if not settings.openrouter_api_key:
        raise PlanError("No API key configured. Set DT_OPENROUTER_API_KEY or OPENROUTER_API_KEY.")

    thoughts_text = "\n\n".join(
        f"[{t.get('created_at', 'night')}] {t['content']}" for t in thoughts
    )

    energy_note = ""
    if energy == "zombie":
        energy_note = "\n\nIMPORTANT: The user feels very low energy today (zombie mode). Only include the most essential 1-3 items. Suggest micro-versions of tasks. Be extra gentle."
    elif energy == "okay":
        energy_note = "\n\nThe user feels okay today. Normal energy. Include moderate number of items."
    elif energy == "energized":
        energy_note = "\n\nThe user feels energized today! Include all relevant items, maybe even suggest bonus challenges."

    user_prompt = f"Here are my thoughts from last night:\n\n{thoughts_text}{energy_note}\n\nCreate my morning action plan."

    async with httpx.AsyncClient(timeout=60) as client:
        try:
            resp = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.openrouter_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": used_model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.7,
                },
            )
        except Exception as e:
            raise PlanError(f"Failed to connect to AI: {e}")

    if resp.status_code != 200:
        err = resp.json().get("error", {}).get("message", resp.text[:200])
        raise PlanError(f"LLM error ({resp.status_code}): {err}")

    try:
        content = resp.json()["choices"][0]["message"]["content"]
        content = re.sub(r"```json?\s*", "", content)
        content = re.sub(r"```", "", content)
        result = json.loads(content.strip())
    except (KeyError, json.JSONDecodeError) as e:
        raise PlanError(f"Failed to parse AI response: {e}")

    if not result.get("letter") or not result.get("items"):
        raise PlanError("AI returned incomplete plan (missing letter or items)")

    result["model_used"] = used_model
    return result
