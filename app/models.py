from pydantic import BaseModel, Field, constr, conint
from typing import List, Literal, Optional

class UserInfo(BaseModel):
    first_name: str
    last_name: str
    id_number: constr(pattern=r"^\d{9}$")
    gender: str  # Male / Female / other – validated client‑side
    age: conint(ge=0, le=120)
    hmo: str  # מכבי | מאוחדת | כללית
    hmo_card: constr(pattern=r"^\d{9}$")
    tier: str  # זהב | כסף | ארד

class ChatRequest(BaseModel):
    phase: str = Field(..., description="info_collection | qa")
    user_info: Optional[UserInfo] = None  # required for qa
    history: List[dict]  # [{"role": "user"|"assistant", "content": str}, ...]
    message: str  # user question or answer

class ChatResponse(BaseModel):
    reply: str
    history: List[dict]
    user_info: Optional[UserInfo] = None 
    full_info: bool
    