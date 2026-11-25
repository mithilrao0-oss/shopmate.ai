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

# ---------- Media and publishing ----------
MEDIA_DIR = BACKEND_DIR / "media"

# "dry-run" (the default) records a post as published without contacting
# Instagram or YouTube. Only the exact value "live" turns real posting on, so a
# typo can never post by accident.
PUBLISH_MODE = "live" if os.getenv("PUBLISH_MODE", "dry-run").strip().lower() == "live" else "dry-run"

# ---------- Instagram ----------
# Keep real values in backend/.env (gitignored), never in this file.
INSTAGRAM_ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN", "")
INSTAGRAM_ACCOUNT_ID = os.getenv("IG_USER_ID", "")

# Unified login and Facebook login use graph.facebook.com; Instagram login uses graph.instagram.com.
INSTAGRAM_API_HOST = os.getenv("INSTAGRAM_API_HOST", "https://graph.facebook.com").rstrip("/")
INSTAGRAM_API_VERSION = os.getenv("INSTAGRAM_API_VERSION", "v26.0")

# "resumable": upload the video file straight to Meta (no public link needed).
# "url": Instagram downloads the video from INSTAGRAM_PUBLIC_VIDEO_BASE_URL + file name.
INSTAGRAM_UPLOAD_MODE = os.getenv("INSTAGRAM_UPLOAD_MODE", "resumable").strip().lower()
INSTAGRAM_PUBLIC_VIDEO_BASE_URL = os.getenv("INSTAGRAM_PUBLIC_VIDEO_BASE_URL", "").strip()

# Tell Instagram the reel was made with AI (script and voice). On by default.
INSTAGRAM_AI_LABEL = os.getenv("INSTAGRAM_AI_LABEL", "true").strip().lower() != "false"
