from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests

from app.agent.content_agent import ShopMateContentAgent
from app.config import OLLAMA_MODEL, OLLAMA_TIMEOUT, OLLAMA_URL
from app.responsible_ai import check_content


router = APIRouter(
    prefix="/api/ai",
    tags=["AI"]
)


class GenerateContentRequest(BaseModel):
    product_name: str
    category: str | None = None
    price: float | int | None = None
    content_type: str
    tone: str


class CheckContentRequest(BaseModel):
    content: str


def _ollama_error(error: requests.RequestException) -> HTTPException:
    """Turn a failed Ollama call into a clear API error."""

    if isinstance(error, requests.ConnectionError):
        return HTTPException(
            status_code=503,
            detail=f"Cannot reach Ollama at {OLLAMA_URL}. Is Ollama running?",
        )

    if isinstance(error, requests.Timeout):
        return HTTPException(
            status_code=504,
            detail=(
                f"Ollama did not answer within {OLLAMA_TIMEOUT} seconds. "
                "Try again, or raise OLLAMA_TIMEOUT."
            ),
        )

    return HTTPException(
        status_code=502,
        detail=f"Ollama returned an error: {error}",
    )


@router.post("/test")
def test_ai():
    prompt = "Write a short product description for an LED desk lamp."

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "think": False
            },
            timeout=OLLAMA_TIMEOUT
        )

        response.raise_for_status()
    except requests.RequestException as error:
        raise _ollama_error(error)

    data = response.json()

    return {
        "prompt": prompt,
        "response": data.get("response", "")
    }


@router.post("/check")
def check_text(request: CheckContentRequest):
    """
    Run the Responsible AI screening on any text (for example, text the
    user edited after generation).
    """

    return check_content(request.content)


@router.post("/generate")
def generate_content(request: GenerateContentRequest):
    """
    Run the ShopMate Content Agent.

    The agent:
    1. Understands the content task.
    2. Builds the prompt.
    3. Calls Qwen3 through Ollama.
    4. Runs a Responsible AI check.
    5. Can regenerate once if the first result needs revision.
    6. Returns the final draft for human review.
    """

    agent = ShopMateContentAgent(
        product_name=request.product_name,
        category=request.category,
        price=request.price,
        content_type=request.content_type,
        tone=request.tone,
    )

    try:
        result = agent.run()
    except requests.RequestException as error:
        raise _ollama_error(error)

    return {
        "product_name": request.product_name,
        "content_type": request.content_type,
        "tone": request.tone,

        "response": result["response"],

        "model": result["model"],
        "agent": result["agent"],
        "workflow": result["workflow"],

        "attempts": result["attempts"],
        "revision_performed": result["revision_performed"],

        "responsible_ai": result["responsible_ai"],
    }
