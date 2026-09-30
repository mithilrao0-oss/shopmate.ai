"""
Central configuration for the ShopMate.ai backend.

Values are read from environment variables. If a file named `.env` exists in
the backend folder, it is loaded first (see `.env.example` for the options).
"""

import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent


def _load_env_file() -> None:
    env_path = BACKEND_DIR / ".env"

    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")

        # Real environment variables win over the .env file.
        os.environ.setdefault(key.strip(), value)


_load_env_file()


# ---------- Database ----------
DATABASE_PATH = Path(os.getenv("SHOPMATE_DB", str(BACKEND_DIR / "shopmate.db")))

# ---------- Ollama / LLM ----------
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:1.7b")

# The demo PC is CPU-only, so generation can be slow. Keep timeouts generous.
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "300"))
OLLAMA_MAX_TOKENS = int(os.getenv("OLLAMA_MAX_TOKENS", "350"))

# ---------- CORS ----------
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]
