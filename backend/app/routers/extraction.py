from fastapi import APIRouter
from pydantic import BaseModel

from ..services.llm_extraction import extract_invoice

router = APIRouter(prefix="/api/v1", tags=["extraction"])


class ExtractRequest(BaseModel):
    text: str


@router.post("/extract")
def extract(payload: ExtractRequest) -> dict:
    return extract_invoice(payload.text)