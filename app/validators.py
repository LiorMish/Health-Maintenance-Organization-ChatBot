from models import UserInfo
from typing import Tuple, List

HMOs = ["מכבי", "מאוחדת", "כללית", "maccabi", "meuhedet", "clalit", "Maccabi", "Meuhedet", "Clalit"]
Tiers = ["זהב", "כסף", "ארד", "gold", "silver", "bronze", "Gold", "Silver", "Bronze"]

def validate_profile(p: UserInfo, lang: str = "en") -> Tuple[bool, List[str]]:
    """Simple extra checks (duplicate of pydantic for demo)."""
    errs = []
    # Check existence of required fields
    required_fields = ["id_number", "hmo", "tier", "age", "hmo_card", "first_name", "last_name"]
    for field in required_fields:
        if not hasattr(p, field) or getattr(p, field) is None:
            if lang == "he":
                errs.append(f"שדה {field} חסר")
            else:
                errs.append(f"Missing field: {field}")

    # Only proceed with value checks if all fields exist
    if not errs:
        if lang == "he":
            if len(p.id_number) != 9:
                errs.append("מספר תעודת זהות חייב להיות בן 9 ספרות")
            if p.hmo not in HMOs:
                errs.append("קופת חולים לא תקינה")
            if p.tier not in Tiers:
                errs.append("רמת ביטוח לא תקינה")
            if p.age < 0 or p.age > 120:
                errs.append("גיל חייב להיות בין 0 ל-120")
            if len(p.hmo_card) != 9:
                errs.append("מספר כרטיס קופה חייב להיות בן 9 ספרות")
            if not p.first_name or not p.last_name:
                errs.append("שם פרטי ושם משפחה לא יכולים להיות ריקים")
        else:
            if len(p.id_number) != 9:
                errs.append("ID number must have 9 digits")
            if p.hmo.lower() not in HMOs:
                errs.append("Invalid HMO name")
            if p.tier.lower() not in Tiers:
                errs.append("Invalid membership tier")
            if p.age < 0 or p.age > 120:
                errs.append("Age must be between 0 and 120")
            if len(p.hmo_card) != 9:
                errs.append("HMO card number must have 9 digits")
            if not p.first_name or not p.last_name:
                errs.append("First and last name cannot be empty")
    return (len(errs) == 0, errs)
