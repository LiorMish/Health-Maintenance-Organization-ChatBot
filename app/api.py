from typing import Dict, List, Tuple
from fastapi import APIRouter, HTTPException
from models import ChatRequest, ChatResponse, UserInfo
from openai_client import AzureOpenAIClient
from kb_search import Retriever
from data_loader import ChunkedKnowledgeBase
from pathlib import Path
from logger import init_logger
from utils import detect_lang, detect_hmos
from prompts import get_system_prompt
from validators import validate_profile
from utils import HE_2_EN, EN_2_HE
from profile_extractor import extract_profile


# ────────────────────────── API Router ────────────────────────────────
router = APIRouter()
logger = init_logger(name="chatbot.api", level="DEBUG", filename="api.log")
kb = ChunkedKnowledgeBase(Path("phase2_data"))
openai = AzureOpenAIClient()
retriever = Retriever(kb, openai)


def gather_profile(
    phase: str,
    history: List[Dict[str, str]],
    user_text: str,
    lang: str,
    existing: Dict | None,
) -> Tuple[Dict, bool]:
    """
    Returns (profile_dict, is_complete_and_valid)
    * Extracts new info with a secondary model during 'info_collection'.
    * Re-validates during 'qa'.
    """
    profile = dict(existing or {})

    if phase == "info_collection":
        logger.info("Phase is info_collection, extracting profile.")
        extracted = extract_profile(history + [{"role": "user",
                                                "content": user_text}],
                                    client=openai)
        profile.update({k: v for k, v in extracted.items() if v})

    try:
        user_obj = UserInfo(**profile) 
        ok, _ = validate_profile(user_obj, lang)
        if not ok:
            logger.info("Profile is incomplete or invalid, returning empty.")
            return {}, False
    except Exception:
        ok = False

    return profile, ok


def add_kb_and_profile(
    messages: List[Dict[str, str]],
    profile: UserInfo,
    user_text: str,
    lang: str,
    history: List[Dict[str, str]],
):
    """Insert profile + KB context into the system messages list (in place)."""
    profile_txt = (
        f"User profile:\n"
        f"Full name: {profile.first_name} {profile.last_name}\n"
        f"HMO: {profile.hmo}\n"
        f"Tier: {profile.tier}\n"
        f"Age: {profile.age}\n"
        f"Gender: {profile.gender}\n"
    )
    messages.insert(1, {"role": "system", "content": profile_txt})

    # build KB context
    hmo_names = [h.lower() for h in detect_hmos(user_text)]
    profile_hmo_lower = profile.hmo.lower() if profile.hmo else ""

    # Add both Hebrew and English variants if missing
    he_name = EN_2_HE.get(profile_hmo_lower, profile_hmo_lower)
    en_name = HE_2_EN.get(profile_hmo_lower, profile_hmo_lower)

    if profile_hmo_lower not in hmo_names:
        hmo_names.append(profile_hmo_lower)
    if he_name not in hmo_names:
        hmo_names.append(he_name)
    if en_name not in hmo_names:
        hmo_names.append(en_name)

    # Build context from the last 2 messages + user input
    extra_context = ""
    if len(history) >= 2:
        extra_context = history[-2]["content"] + "\n" + history[-1]["content"] + "\n"
    query_text = extra_context + user_text
    ctx = retriever.build_context(hmo_names, query_text)
    # ctx = retriever.build_context(hmo_names, user_text)
    messages.insert(2, {"role": "system", "content": f"Knowledge Base:\n{ctx}"})



# ─────────────────────────── Endpoint ────────────────────────────
@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        if req.phase not in {"info_collection", "qa"}:
            raise HTTPException(400, "Phase must be 'info_collection' or 'qa'.")

        # language + base system prompt
        lang = detect_lang(req.message, req.history)
        system_msg = {"role": "system", "content": get_system_prompt(req.phase, lang)}
        messages = [system_msg, *req.history, {"role": "user", "content": req.message}]

        # collect / validate the profile
        profile_dict, ok = gather_profile(
            req.phase, req.history, req.message, lang, req.user_info
        )

        # if finished collecting → switch to QA
        if req.phase == "info_collection" and ok:
            logger.info("Profile is complete and valid, switching to QA phase.")
            req.phase = "qa"

        # If we’re in QA, we must have a complete profile
        if req.phase == "qa":
            if not ok:
                raise HTTPException(400, "Incomplete or invalid profile for QA phase.")

            profile_obj = UserInfo(**profile_dict)
            add_kb_and_profile(messages, profile_obj, req.message, lang, req.history)

        # ask the assistant
        reply = openai.chat(messages)

        # build response
        history = req.history + [
            {"role": "user", "content": req.message},
            {"role": "assistant", "content": reply},
        ]
        resp_data = {
            "reply":    reply,
            "history":  history,
            "full_info": ok,
        }
        if ok:
            resp_data["user_info"] = profile_dict

        return ChatResponse(**resp_data)

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Chat failed")
        raise HTTPException(500, str(exc))