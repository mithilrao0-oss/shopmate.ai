from fastapi import APIRouter
from pydantic import BaseModel
import requests

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
    category_text = request.category or "Not specified"
    price_text = (
        f"₹{request.price}"
        if request.price is not None
        else "Not specified"
    )

    prompt = f"""
You are the AI content assistant for ShopMate.ai.

Create a {request.content_type.lower()} for the following product.

Product name: {request.product_name}
Category: {category_text}
Price: {price_text}
Tone: {request.tone}

Requirements:
- Keep the content clear and useful.
- Match the requested tone.
- Do not invent technical specifications or unsupported claims.
- Do not mention AI, prompts, or language models.
- Return only the final content.
"""

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
        "product_name": request.product_name,
        "content_type": request.content_type,
        "tone": request.tone,
        "response": data.get("response", "")
    }