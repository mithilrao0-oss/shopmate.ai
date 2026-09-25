from fastapi import APIRouter
import requests

router = APIRouter(
    prefix="/api/ai",
    tags=["AI"]
)


@router.post("/test")
def test_ai():
    prompt = "Write a short product description for an LED desk lamp."

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen3:1.7b",
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    return {
        "prompt": prompt,
        "response": data.get("response", "")
    }