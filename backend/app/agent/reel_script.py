"""
Structured reel scripts.

A reel script is a small JSON document instead of free text:

    {
      "scenes": [ {"voiceover": "...", "on_screen_text": "..."}, ... 4 scenes ],
      "caption": "...",
      "hashtags": ["#one", "#two", "#three"]
    }

Later steps read the voiceover lines for text-to-speech and the on-screen
text for video captions, so the fields must be plain text only. This module
builds the JSON schema, parses the model reply, and validates the result.

The validation is rule based. It reduces invented facts but does not remove
the need for human review.
"""

import json
import re

from app.responsible_ai import check_content


SCENE_COUNT = 4
SCENE_LABELS = ["Hook", "Product", "Benefit", "Call to action"]

MAX_VOICEOVER_WORDS = 20
MAX_ON_SCREEN_WORDS = 7
MIN_HASHTAGS = 3
MAX_HASHTAGS = 5

# Average speaking pace used for the length estimate (about 150 words/min).
WORDS_PER_SECOND = 2.5


# JSON schema handed to Ollama so the model can only produce this shape.
REEL_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "scenes": {
            "type": "array",
            "minItems": SCENE_COUNT,
            "maxItems": SCENE_COUNT,
            "items": {
                "type": "object",
                "properties": {
                    "voiceover": {"type": "string"},
                    "on_screen_text": {"type": "string"},
                },
                "required": ["voiceover", "on_screen_text"],
            },
        },
        "caption": {"type": "string"},
        "hashtags": {
            "type": "array",
            "minItems": MIN_HASHTAGS,
            "maxItems": MAX_HASHTAGS,
            "items": {"type": "string"},
        },
    },
    "required": ["scenes", "caption", "hashtags"],
}


# ---------- Parsing and normalising ----------

def parse_reel_json(text: str) -> dict:
    """Extract the JSON object from a model reply. Raises ValueError."""

    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE)

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end <= start:
        raise ValueError("No JSON object found in the reply")

    data = json.loads(text[start:end + 1])

    if not isinstance(data, dict):
        raise ValueError("The reply is not a JSON object")

    return data


def _clean(value) -> str:
    return " ".join(str(value or "").split())


def normalize_reel(payload) -> dict:
    """Return a tidy copy with only the expected fields."""

    if not isinstance(payload, dict):
        payload = {}

    raw_scenes = payload.get("scenes")

    if not isinstance(raw_scenes, list):
        raw_scenes = []

    scenes = []

    for scene in raw_scenes:
        if not isinstance(scene, dict):
            scene = {}

        scenes.append(
            {
                "voiceover": _clean(scene.get("voiceover")),
                "on_screen_text": _clean(scene.get("on_screen_text")),
            }
        )

    raw_tags = payload.get("hashtags")

    if isinstance(raw_tags, str):
        raw_tags = raw_tags.split()

    if not isinstance(raw_tags, list):
        raw_tags = []

    hashtags = []

    for tag in raw_tags:
        tag = re.sub(r"\s+", "", str(tag)).lstrip("#")

        if not tag:
            continue

        tag = "#" + tag

        if tag.lower() not in [existing.lower() for existing in hashtags]:
            hashtags.append(tag)

    return {
        "scenes": scenes,
        "caption": _clean(payload.get("caption")),
        "hashtags": hashtags,
    }


def _word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def estimate_seconds(reel: dict) -> int:
    words = sum(_word_count(scene["voiceover"]) for scene in reel["scenes"])

    return round(words / WORDS_PER_SECOND)


# ---------- Validation rules ----------

STAGE_DIRECTION_PATTERNS = [
    r"[\[\]{}*_<>#]",
    r"\b(?:visual|scene\s*\d*|music|sfx|b-?roll|voice[- ]?over|on-screen text|narrator)\s*:",
    r"\b(?:upbeat music|background music|cut to|fade in|fade out|montage)\b",
]

TESTIMONIAL_PATTERNS = [
    r"\b(?:customers?|users?|buyers?|reviewers?|shoppers?|everyone|people|folks)\s+"
    r"(?:say|says|said|love|loves|loved|rave|raves|report|reports|swear|swears|agree)\b",
    r"\b(?:i|we|my)\s+(?:love|loved|use|used|bought|tried|recommend|swear)\b",
    r"\b(?:best|greatest)\b[^.!?]{0,40}\bever\b",
    r"\b\d(?:\.\d)?\s*(?:/\s*5|out of 5|stars?)\b",
    r"\b(?:testimonials?|five[- ]star|top[- ]rated|best[- ]sell(?:er|ing)|award[- ]winning)\b",
]

CLAIM_PATTERNS = [
    r"\bguarantee[ds]?\b",
    r"\bwarranty\b",
    r"\b(?:discounts?|sale|cashback|limited[- ]time|today only)\b",
    r"\bfree (?:shipping|delivery)\b",
    r"\bwhile (?:stocks?|supplies) last\b",
    r"\b(?:waterproof|water[- ]resistant|stainless|bpa[- ]free|unbreakable|long[- ]lasting)\b",
    r"\b(?:powerful|battery life|hours of)\b",
    r"\bcrush(?:es|ing)? ice\b",
    r"\b(?:number one|world'?s (?:best|first)|best[- ]in[- ]class)\b",
]

QUOTE_PATTERN = r"[\"\u201c\u201d]"

EMOJI_PATTERN = r"[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F]"

NUMBER_PATTERN = r"\d[\d,]*(?:\.\d+)?"


def _number_key(value) -> str | None:
    try:
        number = float(str(value).replace(",", "").strip())
    except ValueError:
        return None

    return f"{number:g}"


def _find(patterns, text) -> list[str]:
    found = []

    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            found.append(match.group(0))

    return found


def validate_reel(payload, product_name: str, price=None) -> dict:
    """
    Check a reel script and return:
      passed            - True when nothing was flagged
      issues            - readable descriptions of the problems
      matches           - the flagged text, grouped by category
      estimated_seconds - rough spoken length
    """

    reel = normalize_reel(payload)

    issues = []
    matches = {}

    def flag(category, message, found=None):
        if message not in issues:
            issues.append(message)

        if found:
            matches.setdefault(category, []).extend(found)

    # --- Structure ---
    scenes = reel["scenes"]

    if len(scenes) != SCENE_COUNT:
        flag(
            "structure",
            f"the script must have exactly {SCENE_COUNT} scenes "
            f"(found {len(scenes)})",
        )

    for number, scene in enumerate(scenes, start=1):
        if not scene["voiceover"]:
            flag("structure", f"scene {number} has no voiceover")
        elif _word_count(scene["voiceover"]) > MAX_VOICEOVER_WORDS:
            flag(
                "structure",
                f"scene {number} voiceover is longer than "
                f"{MAX_VOICEOVER_WORDS} words",
            )

        if not scene["on_screen_text"]:
            flag("structure", f"scene {number} has no on-screen text")
        elif _word_count(scene["on_screen_text"]) > MAX_ON_SCREEN_WORDS:
            flag(
                "structure",
                f"scene {number} on-screen text is longer than "
                f"{MAX_ON_SCREEN_WORDS} words",
            )

    if not reel["caption"]:
        flag("structure", "the caption is empty")

    if not MIN_HASHTAGS <= len(reel["hashtags"]) <= MAX_HASHTAGS:
        flag(
            "structure",
            f"the script needs {MIN_HASHTAGS} to {MAX_HASHTAGS} hashtags",
        )

    # --- Content rules ---
    voiceovers = [scene["voiceover"] for scene in scenes]

    # Hashtags legitimately contain "#", so formatting checks skip them.
    body_text = "\n".join(
        voiceovers
        + [scene["on_screen_text"] for scene in scenes]
        + [reel["caption"]]
    )

    all_text = body_text + "\n" + "\n".join(reel["hashtags"])

    found = _find(STAGE_DIRECTION_PATTERNS, body_text)
    if found:
        flag(
            "stage_directions",
            "contains stage directions, brackets or formatting "
            "(only plain spoken text is allowed)",
            found,
        )

    found = _find(TESTIMONIAL_PATTERNS, all_text)
    if found:
        flag(
            "testimonial",
            "contains an invented customer opinion, testimonial or rating",
            found,
        )

    found = re.findall(QUOTE_PATTERN, "\n".join(voiceovers))
    if found:
        flag(
            "quotes",
            "a voiceover contains quotation marks (possible invented quote)",
            found,
        )

    found = re.findall(EMOJI_PATTERN, "\n".join(voiceovers))
    if found:
        flag(
            "emoji",
            "a voiceover contains emoji, which a voice cannot read",
            found,
        )

    found = _find(CLAIM_PATTERNS, all_text)
    if found:
        flag(
            "claims",
            "contains unsupported claims (discounts, guarantees, "
            "specifications or superlatives)",
            found,
        )

    allowed_numbers = set()

    if price is not None:
        allowed_numbers.add(_number_key(price))

    # Numbers that are part of the product name (for example "Fan 2000").
    for number in re.findall(NUMBER_PATTERN, product_name or ""):
        allowed_numbers.add(_number_key(number.rstrip(",")))

    unexpected = [
        number
        for number in (
            match.rstrip(",")
            for match in re.findall(NUMBER_PATTERN, all_text)
        )
        if _number_key(number) not in allowed_numbers
    ]
    if unexpected:
        flag(
            "numbers",
            "contains numbers that were not provided (only the price may "
            "be used)",
            unexpected,
        )

    if product_name and not any(
        product_name.lower() in voiceover.lower() for voiceover in voiceovers
    ):
        flag(
            "structure",
            f"the product name \"{product_name}\" is never said in a voiceover",
        )

    # --- Shared Responsible AI screening (fairness, safety, privacy) ---
    shared = check_content(all_text)

    for description in shared["issues"]:
        if description not in issues:
            issues.append(description)

    for category, texts in shared["matches"].items():
        matches.setdefault(category, []).extend(texts)

    return {
        "passed": len(issues) == 0,
        "issues": issues,
        "matches": matches,
        "estimated_seconds": estimate_seconds(reel),
    }


# ---------- Plain-text rendering (Review Queue, copy button) ----------

def render_reel_text(product_name: str, payload) -> str:
    reel = normalize_reel(payload)

    lines = [
        f"Reel Script: {product_name} "
        f"(about {estimate_seconds(reel)} seconds)",
        "",
    ]

    for number, scene in enumerate(reel["scenes"], start=1):
        label = (
            SCENE_LABELS[number - 1]
            if number <= len(SCENE_LABELS)
            else f"Scene {number}"
        )

        lines.append(f"Scene {number} - {label}")
        lines.append(f"Voiceover: {scene['voiceover']}")
        lines.append(f"On-screen text: {scene['on_screen_text']}")
        lines.append("")

    lines.append(f"Caption: {reel['caption']}")
    lines.append(f"Hashtags: {' '.join(reel['hashtags'])}")

    return "\n".join(lines)
