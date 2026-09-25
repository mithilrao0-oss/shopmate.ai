import re
import requests


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

    OLLAMA_URL = "http://localhost:11434/api/generate"
    MODEL = "qwen3:1.7b"
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

        return f"₹{self.price}"

    def _build_prompt(self, revision: bool = False) -> str:
        revision_instruction = ""

        if revision:
            revision_instruction = """
A previous draft triggered a Responsible AI wording check.

Create a revised version that:
- removes stereotypes or discriminatory wording
- avoids insults or degrading language
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

    def _generate_with_qwen(self, prompt: str) -> str:
        response = requests.post(
            self.OLLAMA_URL,
            json={
                "model": self.MODEL,
                "prompt": prompt,
                "stream": False,
                "think": False,
            },
            timeout=120,
        )

        response.raise_for_status()

        data = response.json()

        return data.get("response", "").strip()

    def _responsible_ai_check(self, content: str) -> dict:
        """
        Basic rule-based Responsible AI screening.

        This is a first-level screening mechanism, not a guarantee
        that content is completely unbiased or safe.
        """

        fairness_patterns = [
            r"\bwomen are\b",
            r"\bmen are\b",
            r"\bgirls are\b",
            r"\bboys are\b",
            r"\bpeople like you\b",
            r"\bstupid\b",
            r"\bdumb\b",
            r"\binferior\b",
            r"\bsuperior race\b",
            r"\blazy people\b",
            r"\bthose people\b",
        ]

        safety_patterns = [
            r"\b100% guaranteed\b",
            r"\bguaranteed results\b",
            r"\brisk[- ]free\b",
            r"\bno risk\b",
            r"\bcures\b",
            r"\bclinically proven\b",
        ]

        privacy_patterns = [
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            r"\b\d{10}\b",
        ]

        fairness_issues = [
            pattern
            for pattern in fairness_patterns
            if re.search(pattern, content, re.IGNORECASE)
        ]

        safety_issues = [
            pattern
            for pattern in safety_patterns
            if re.search(pattern, content, re.IGNORECASE)
        ]

        privacy_issues = [
            pattern
            for pattern in privacy_patterns
            if re.search(pattern, content, re.IGNORECASE)
        ]

        issues = []

        if fairness_issues:
            issues.append("potentially biased or inappropriate wording")

        if safety_issues:
            issues.append("potentially unsupported or exaggerated claims")

        if privacy_issues:
            issues.append("possible personal information")

        return {
            "passed": len(issues) == 0,
            "issues": issues,
        }

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
        }

        while attempts < self.MAX_ATTEMPTS:
            attempts += 1

            prompt = self._build_prompt(
                revision=revision_performed
            )

            final_content = self._generate_with_qwen(prompt)

            final_check = self._responsible_ai_check(final_content)

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