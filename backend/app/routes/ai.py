from fastapi import APIRouter
from pydantic import BaseModel
import requests

from app.agent.content_agent import ShopMateContentAgent


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


@router.post("/test")
def test_ai():
    prompt = "Write a short product description for an LED desk lamp."

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen3:1.7b",
            "prompt": prompt,
            "stream": False,
            "think": False
        },
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    return {
        "prompt": prompt,
        "response": data.get("response", "")
    }


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

    result = agent.run()

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