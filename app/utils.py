from langdetect import detect, LangDetectException
from typing import List, Dict
# from googletrans import Translator

HMO_NAMES_HE = ["מכבי", "מאוחדת", "כללית"]
HMO_NAMES_EN = ["maccabi", "meuhedet", "clalit"]

HE_2_EN = {
    "מכבי": "maccabi",
    "מאוחדת": "meuhedet",
    "כללית": "clalit",
}
EN_2_HE = {v: k for k, v in HE_2_EN.items()}

# Simple language detection: tries langdetect, otherwise heuristic fallback.
def detect_lang(message: str, history: List[Dict]) -> str:
    """Return 'he' (Hebrew) or 'en' (English)."""
    try:
        code = detect(message)
        return "he" if code == "he" else "en"
    except LangDetectException:
        # Fallback: check previous user messages for Hebrew chars
        for m in reversed(history):
            if m.get("role") == "user":
                if any("֐" <= ch <= "ת" for ch in m["content"]):
                    return "he"
                break
        return "en"
    
# ── HMO mention detection ────────────────────────────────────────────
def detect_hmos(text: str) -> List[str]:
    """Return list of HMO names mentioned in text (Hebrew or English)."""
    lower = text.lower()
    found = []
    for he, en in zip(HMO_NAMES_HE, HMO_NAMES_EN):
        if he in text or en in lower:
            found.append(he)
            found.append(en)
    return found

# # ── ENG2HEB Language translation ───────────────────────────────────────────
# def translate_to_he(text: str) -> str:
#     """Translate English text to Hebrew using Google Translate."""
#     translator = Translator()
#     try:
#         result = translator.translate(text, src='en', dest='he')
#         return result.text
#     except Exception as e:
#         print(f"Translation error: {e}")
#         return text  # Fallback to original text on error