import re
import requests

from app.config import (
    OLLAMA_MAX_TOKENS,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
    OLLAMA_URL,
)
from app.responsible_ai import check_content


class ShopMateContentAgent:
    """
    Agentic workflow for ShopMate.ai content generation.

    Workflow:
    1. Understand the product/content task.
    2. Build a task-specific prompt.
    3. Generate content with Qwen3 through Ollama.
    4. Run a Responsible AI screening check.
    5. If an issue is detected, revise the prompt and regenerate once.
    6. Return the final content and workflow information.
    """

    OLLAMA_URL = OLLAMA_URL
    MODEL = OLLAMA_MODEL
    MAX_ATTEMPTS = 2

    def __init__(
        self,
        product_name: str,
        category: str | None,
        price: float | int | None,
        content_type: str,
        tone: str,
    ):
        self.product_name = product_name
        self.category = category or "Not specified"
        self.price = price
        self.content_type = content_type
        self.tone = tone

    def _price_text(self) -> str:
        if self.price is None:
            return "Not specified"

        return f"\u20b9{self.price}"

    def _build_prompt(
        self,
        previous_draft: str = "",
        previous_check: dict | None = None,
    ) -> str:
        revision_instruction = ""

        if previous_draft and previous_check and not previous_check["passed"]:
            flagged_text = [
                text
                for texts in previous_check.get("matches", {}).values()
                for text in texts
            ]

            revision_instruction = f"""
A previous draft was flagged by a Responsible AI wording check.
Reasons: {", ".join(previous_check["issues"])}
Flagged wording: {", ".join(flagged_text) if flagged_text else "not available"}

Previous draft:
{previous_draft}

Write a new version that:
- removes the flagged wording
- avoids stereotypes, insults, and degrading language
- avoids unsupported or exaggerated claims
- remains useful and natural
- keeps the requested tone
"""

        return f"""
You are the ShopMate.ai Content Agent.

Your task is to create a {self.content_type.lower()} for a product.

Product name: {self.product_name}
Category: {self.category}
Price: {self._price_text()}
Requested tone: {self.tone}

Requirements:
- Write clear and useful marketing content.
- Match the requested tone.
- Use only information provided about the product.
- Do not invent technical specifications.
- Do not make unsupported medical, financial, safety, or performance claims.
- Do not use discriminatory stereotypes.
- Do not insult or demean any person or group.
- Do not mention AI, prompts, language models, or this instruction.
- Return only the final content.

{revision_instruction}
"""

    @staticmethod
    def _strip_thinking(text: str) -> str:
        """Remove <think> blocks that some Ollama/Qwen3 versions still emit."""

        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

        # A block that was cut off before it closed.
        text = re.sub(r"<think>.*$", "", text, flags=re.DOTALL)

        return text.strip()

    def _generate_with_qwen(self, prompt: str) -> str:
        response = requests.post(
            self.OLLAMA_URL,
            json={
                "model": self.MODEL,
                "prompt": prompt,
                "stream": False,
                "think": False,
                "keep_alive": "10m",
                "options": {"num_predict": OLLAMA_MAX_TOKENS},
            },
            timeout=OLLAMA_TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

        return self._strip_thinking(data.get("response", ""))

    def run(self) -> dict:
        """
        Execute the ShopMate AI agent workflow.
        """

        attempts = 0
        revision_performed = False
        final_content = ""
        final_check = {
            "passed": False,
            "issues": ["No content generated"],
            "matches": {},
        }

        while attempts < self.MAX_ATTEMPTS:
            attempts += 1

            prompt = self._build_prompt(
                previous_draft=final_content if revision_performed else "",
                previous_check=final_check if revision_performed else None,
            )

            final_content = self._generate_with_qwen(prompt)

            if final_content:
                final_check = check_content(final_content)
            else:
                final_check = {
                    "passed": False,
                    "issues": ["No content generated"],
                    "matches": {},
                }

            if final_check["passed"]:
                break

            if attempts < self.MAX_ATTEMPTS:
                revision_performed = True

        return {
            "response": final_content,
            "model": self.MODEL,
            "agent": "ShopMate Content Agent",
            "workflow": [
                "Task analysis",
                "Prompt construction",
                "Qwen3 generation",
                "Responsible AI screening",
                "Human review",
            ],
            "attempts": attempts,
            "revision_performed": revision_performed,
            "responsible_ai": final_check,
        }
