from __future__ import annotations
from typing import Dict, List
import json, re
from logger import init_logger

logger = init_logger(name="chatbot.profile_extractor", level="DEBUG", filename="profile_extractor.log")

# The template must match your pydantic UserInfo exactly
JSON_TEMPLATE = {
    "first_name": None,
    "last_name":  None,
    "id_number":  None,
    "gender":     None,
    "age":        None,
    "hmo":        None,
    "hmo_card":   None,
    "tier":       None,
}

SYS_PROMPT = (
    "You are a strict JSON extractor. "
    "Given the conversation so far, return ONLY the following JSON "
    "with the fields you can infer filled in (all others must be null).\n\n"
    + json.dumps(JSON_TEMPLATE, ensure_ascii=False, indent=2)
)

def _format_history(history: List[Dict[str, str]]) -> str:
    """Flatten history to a readable block for the LM."""
    return "\n".join(f"{m['role']}: {m['content']}" for m in history)

def extract_profile(history: List[Dict[str, str]], *, client) -> Dict:
    """
    Ask the language model to produce a partial profile JSON
    based on the *entire* info-collection history.
    """
    messages = [
        {"role": "system", "content": SYS_PROMPT},
        {"role": "user",   "content": _format_history(history)},
    ]

    logger.info("Sending %d tokens to extractor model", len(messages))
    raw_reply = client.chat(messages)          # <-- your wrapper returns str
    logger.info("Extractor raw reply: %s", raw_reply[:200])

    # The model must reply with JSON only; strip markdown fences if any.
    cleaned = re.sub(r"^```json|```$", "", raw_reply.strip(), flags=re.I).strip()
    try:
        data = json.loads(cleaned)
        # Keep only the exact keys we expect
        return {k: data.get(k) for k in JSON_TEMPLATE}
    except json.JSONDecodeError:
        logger.info("Extractor returned invalid JSON")
        return {}
