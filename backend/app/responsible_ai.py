"""
Rule-based Responsible AI screening.

This is a first-level check, not a guarantee that content is safe or unbiased.
It is the single source of truth: the content agent, the /api/ai/check
endpoint, and the review queue all use this same function.
"""

import re


FAIRNESS_PATTERNS = [
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
    r"\billegal immigrants?\b",
]

SAFETY_PATTERNS = [
    r"\b100% guaranteed\b",
    r"\bguaranteed results\b",
    r"\brisk[- ]free\b",
    r"\bno risk\b",
    r"\bcures\b",
    r"\bclinically proven\b",
]

PRIVACY_PATTERNS = [
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    r"\b\d{10}\b",
]

CATEGORIES = [
    ("fairness", "potentially biased or inappropriate wording", FAIRNESS_PATTERNS),
    ("safety", "potentially unsupported or exaggerated claims", SAFETY_PATTERNS),
    ("privacy", "possible personal information", PRIVACY_PATTERNS),
]


def check_content(content: str) -> dict:
    """
    Screen text and return:
      passed  - True when nothing was flagged
      issues  - readable descriptions of what was flagged
      matches - the exact flagged text, grouped by category
    """

    issues = []
    matches = {}

    for name, description, patterns in CATEGORIES:
        found = []

        for pattern in patterns:
            for match in re.finditer(pattern, content or "", re.IGNORECASE):
                found.append(match.group(0))

        if found:
            issues.append(description)
            matches[name] = found

    return {
        "passed": len(issues) == 0,
        "issues": issues,
        "matches": matches,
    }
