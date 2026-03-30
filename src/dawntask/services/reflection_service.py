"""Weekly reflection generation via LLM."""

import json
import re

import httpx

from ..core.config import settings

SYSTEM_PROMPT = """\
You are DawnTask — a compassionate habit coach that NEVER uses streaks, guilt, or punishment.

Given a user's habits, check-ins, and energy levels for the past week, generate a warm weekly reflection.

Rules:
- NEVER mention streaks or consecutive days
- NEVER guilt-trip about missed days
- Celebrate what WAS done, not what wasn't
- Notice patterns: "You're most active on days you feel 'okay' energy"
- Suggest micro-adjustments, not big changes
- Tone: warm friend, not drill sergeant
- If they did very little, say "Even showing up to check is progress"

{lang_instruction}

Return ONLY valid JSON (no markdown fences):
{{
  "reflection": "2-3 paragraph warm reflection letter",
  "patterns": ["pattern 1 noticed", "pattern 2 noticed"],
  "suggestions": ["gentle suggestion 1", "gentle suggestion 2"]
}}"""


class ReflectionError(Exception):
    pass


async def generate_reflection(
    habits: list[dict],
    checkins: list[dict],
    energy: list[dict],
    lang: str = "en",
    model: str = "",
) -> dict:
    used_model = model or settings.llm_model

    if not settings.openrouter_api_key:
        raise ReflectionError("No API key configured.")

    lang_instruction = ""
    if lang == "ru":
        lang_instruction = "IMPORTANT: Write everything in Russian."

    # Build summary for LLM
    habit_map = {h["id"]: h["name"] for h in habits}
    lines = ["## Habits:"]
    for h in habits:
        lines.append(f"- {h['emoji']} {h['name']} (full: {h.get('full','')}, micro: {h.get('micro','')})")

    lines.append("\n## This week's check-ins:")
    by_date = {}
    for c in checkins:
        by_date.setdefault(c["date"], []).append(c)
    for date in sorted(by_date.keys()):
        items = by_date[date]
        done = [f"{habit_map.get(c['habit_id'], '?')}{'(micro)' if c.get('micro') else ''}" for c in items if c.get("done")]
        lines.append(f"- {date}: {', '.join(done) if done else 'no check-ins'}")

    lines.append("\n## Energy levels:")
    for e in energy:
        lines.append(f"- {e['date']}: {e['level']}")

    user_text = "\n".join(lines)

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
                        {"role": "system", "content": SYSTEM_PROMPT.format(lang_instruction=lang_instruction)},
                        {"role": "user", "content": f"Here's my week:\n\n{user_text}\n\nGenerate my weekly reflection."},
                    ],
                    "temperature": 0.7,
                },
            )
        except Exception as e:
            raise ReflectionError(f"Failed to connect to AI: {e}")

    if resp.status_code != 200:
        err = resp.json().get("error", {}).get("message", resp.text[:200])
        raise ReflectionError(f"LLM error ({resp.status_code}): {err}")

    try:
        content = resp.json()["choices"][0]["message"]["content"]
        content = re.sub(r"```json?\s*", "", content)
        content = re.sub(r"```", "", content)
        result = json.loads(content.strip())
    except (KeyError, json.JSONDecodeError) as e:
        raise ReflectionError(f"Failed to parse AI response: {e}")

    result["model_used"] = used_model
    return result
