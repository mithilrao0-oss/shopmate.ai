import json
import re
import requests

from app.agent.reel_script import (
    MAX_ON_SCREEN_WORDS,
    MAX_VOICEOVER_WORDS,
    REEL_JSON_SCHEMA,
    SCENE_COUNT,
    estimate_seconds,
    normalize_reel,
    parse_reel_json,
    render_reel_text,
    validate_reel,
)
from app.config import (
    OLLAMA_MAX_TOKENS,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
    OLLAMA_URL,
)
from app.responsible_ai import check_content


REEL_CONTENT_TYPE = "reel script"


class ShopMateContentAgent:
    """
    Agentic workflow for ShopMate.ai content generation.

    Text workflow (captions, descriptions):
    1. Understand the product/content task.
    2. Build a task-specific prompt.
    3. Generate content with Qwen3 through Ollama.
    4. Run a Responsible AI screening check.
    5. If an issue is detected, revise the prompt and regenerate once.
    6. Return the final content and workflow information.

    Reel workflow: the model returns structured JSON (scenes, caption,
    hashtags) that is validated by code before a human sees it.
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
        highlights: list[str] | None = None,
    ):
        self.product_name = product_name
        self.category = category or "Not specified"
        self.price = price
        self.content_type = content_type
        self.tone = tone
        self.highlights = [
            item.strip() for item in (highlights or []) if item and item.strip()
        ]

    def _price_text(self) -> str:
        if self.price is None:
            return "Not specified"

        return f"\u20b9{self.price}"

    @staticmethod
    def _strip_thinking(text: str) -> str:
        """Remove <think> blocks that some Ollama/Qwen3 versions still emit."""

        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

        # A block that was cut off before it closed.
        text = re.sub(r"<think>.*$", "", text, flags=re.DOTALL)

        return text.strip()

    # ------------------------------------------------------------------
    # Text content (captions, descriptions)
    # ------------------------------------------------------------------

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

    def _run_text(self) -> dict:
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
            "structured": None,
            "estimated_seconds": None,
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

    # ------------------------------------------------------------------
    # Reel scripts (structured JSON)
    # ------------------------------------------------------------------

    def _build_reel_prompt(
        self,
        previous_payload: dict | None = None,
        previous_check: dict | None = None,
        invalid_json: bool = False,
    ) -> str:
        if self.highlights:
            facts = "; ".join(self.highlights)
        else:
            facts = (
                "none provided. Do not describe any features. "
                "Speak about the product in general terms only."
            )

        price_rule = (
            f"The only number you may use is the price {self._price_text()}."
            if self.price is not None
            else "Do not use any numbers."
        )

        revision = ""

        if invalid_json:
            revision = """
Your previous reply was not valid JSON that matched the format.
Return only the JSON object.
"""
        elif previous_payload and previous_check and not previous_check["passed"]:
            problems = "\n".join(f"- {issue}" for issue in previous_check["issues"])

            revision = f"""
Your previous script was rejected for these reasons:
{problems}

Previous script:
{json.dumps(previous_payload, ensure_ascii=False)}

Write a corrected script that fixes every reason above.
"""

        return f"""
You write short Instagram Reel scripts for an online seller.

Product name: {self.product_name}
Category: {self.category}
Price: {self._price_text()}
Known facts about the product: {facts}
Tone: {self.tone}

Write a script of exactly {SCENE_COUNT} scenes, about 30 seconds in total.
The scenes, in order:
1. Hook: an attention-grabbing opening line.
2. Product: introduce the product by its exact name "{self.product_name}".
3. Benefit: one benefit that comes from the known facts.
4. Call to action: invite viewers to check the product out.

Each scene has two fields:
- voiceover: one or two short spoken sentences, at most {MAX_VOICEOVER_WORDS} words.
  Plain text only. No emoji, no brackets, no quotation marks, no stage directions.
- on_screen_text: {MAX_ON_SCREEN_WORDS} words or fewer, shown on the video.

Also write:
- caption: one or two sentences for the Instagram post.
- hashtags: 3 to 5 relevant hashtags.

Rules:
- Use only the facts listed above.
- Do not invent customer reviews, testimonials, ratings, discounts, offers,
  specifications, guarantees, or comparisons.
- {price_rule}
- Do not mention AI, prompts, or these instructions.

Return only the JSON object.
{revision}
"""

    def _generate_reel_with_qwen(self, prompt: str) -> str:
        def call(output_format):
            return requests.post(
                self.OLLAMA_URL,
                json={
                    "model": self.MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "think": False,
                    "format": output_format,
                    "keep_alive": "10m",
                    "options": {
                        "num_predict": max(OLLAMA_MAX_TOKENS, 500),
                        "temperature": 0.5,
                    },
                },
                timeout=OLLAMA_TIMEOUT,
            )

        response = call(REEL_JSON_SCHEMA)

        # Older Ollama versions only understand format="json".
        if response.status_code == 400:
            response = call("json")

        response.raise_for_status()

        return self._strip_thinking(response.json().get("response", ""))

    def _run_reel(self) -> dict:
        attempts = 0
        revision_performed = False
        payload = None
        invalid_json = False
        check = {
            "passed": False,
            "issues": ["No script generated"],
            "matches": {},
        }

        while attempts < self.MAX_ATTEMPTS:
            attempts += 1

            prompt = self._build_reel_prompt(
                previous_payload=payload if revision_performed else None,
                previous_check=check if revision_performed else None,
                invalid_json=invalid_json,
            )

            raw_reply = self._generate_reel_with_qwen(prompt)

            try:
                payload = normalize_reel(parse_reel_json(raw_reply))
                invalid_json = False
                check = validate_reel(payload, self.product_name, self.price)
            except ValueError:
                invalid_json = True

                if payload:
                    # Keep the last parseable script and its real problems.
                    check = validate_reel(payload, self.product_name, self.price)
                else:
                    check = {
                        "passed": False,
                        "issues": ["The model did not return a valid JSON script"],
                        "matches": {},
                    }

            if check["passed"]:
                break

            if attempts < self.MAX_ATTEMPTS:
                revision_performed = True

        return {
            "response": (
                render_reel_text(self.product_name, payload) if payload else ""
            ),
            "structured": payload,
            "estimated_seconds": estimate_seconds(payload) if payload else None,
            "model": self.MODEL,
            "agent": "ShopMate Content Agent",
            "workflow": [
                "Task analysis",
                "Prompt construction",
                "Qwen3 structured generation (JSON)",
                "Script validation",
                "Responsible AI screening",
                "Human review",
            ],
            "attempts": attempts,
            "revision_performed": revision_performed,
            "responsible_ai": check,
        }

    # ------------------------------------------------------------------

    def run(self) -> dict:
        """
        Execute the ShopMate AI agent workflow.
        """

        if self.content_type.strip().lower() == REEL_CONTENT_TYPE:
            return self._run_reel()

        return self._run_text()
