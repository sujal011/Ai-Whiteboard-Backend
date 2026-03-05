from typing import Optional, Dict, Any
from pydantic import BaseModel

class GenerateRequest(BaseModel):
    prompt: str

class AskRequest(BaseModel):
    question: str
    workspace_id: int

class GeneralRequest(BaseModel):
    prompt: Optional[str] = None
    image_base64: Optional[str] = None
    dict_of_vars: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    result: Any
