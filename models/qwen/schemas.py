from typing import Any

from pydantic import BaseModel

class ChatUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatMessage(BaseModel):
    role: str
    content: Any


class ChatResponse(BaseModel):
    text: str
    usage: ChatUsage | None = None

    
class VehicleInformation(BaseModel):

    brand: str | None = None

    model: str | None = None

    year: int | None = None

    body_type: str | None = None

    color: str | None = None

    confidence: float | None = None
    model_config = {
    "extra": "ignore"
}