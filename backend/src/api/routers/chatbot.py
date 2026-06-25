import time
from collections import defaultdict
from typing import List, Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.application.services.chatbot_service import ChatbotService

router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])

RATE_LIMIT_REQUESTS = 10
RATE_LIMIT_WINDOW_SECONDS = 60
_peticiones_por_ip: dict[str, list[float]] = defaultdict(list)


def _obtener_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "desconocida"


def _verificar_rate_limit(request: Request) -> None:
    ip = _obtener_ip(request)
    ahora = time.time()
    recientes = [t for t in _peticiones_por_ip[ip] if ahora - t < RATE_LIMIT_WINDOW_SECONDS]
    if len(recientes) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail="Demasiadas preguntas en poco tiempo. Esperá un minuto e intentá de nuevo.",
        )
    recientes.append(ahora)
    _peticiones_por_ip[ip] = recientes


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    dataset_id: int = 1


@router.post("/ask")
def preguntar(payload: ChatRequest, request: Request, db: Session = Depends(get_db)):
    _verificar_rate_limit(request)

    try:
        respuesta = ChatbotService().responder(
            db, [m.model_dump() for m in payload.messages], dataset_id=payload.dataset_id
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error al consultar el modelo de lenguaje: {e}")

    return {"respuesta": respuesta}
