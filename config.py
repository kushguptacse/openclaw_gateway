"""
config.py — OpenClaw Gateway configuration

Loads all settings from .env (in the same directory as this file).
Falls back to real environment variables if .env is absent.

Usage:
    from config import cfg
    print(cfg.VLLM_API_KEY)
"""

import os
from dataclasses import dataclass
from pathlib import Path

# ── .env loader (no third-party deps) ────────────────────────────────────────
def _load_dotenv(env_path: Path) -> None:
    """Parse key=value pairs from a .env file into os.environ."""
    if not env_path.exists():
        return
    with env_path.open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)   # env vars already set take priority


_ENV_FILE = Path(__file__).parent / ".env"
_load_dotenv(_ENV_FILE)


# ── Config dataclass ──────────────────────────────────────────────────────────
@dataclass(frozen=True)
class Config:
    # LLM provider
    VLLM_BASE_URL: str
    VLLM_API_KEY: str
    VLLM_MODEL_ID: str

    # Derived full model key used by openclaw (provider/model-id)
    MODEL: str

    # WhatsApp
    WHATSAPP_TARGET: str       # no leading +  e.g. "919716575789"
    WHATSAPP_TARGET_E164: str  # E.164          e.g. "+919716575789"

    # Agent behaviour
    AGENT_TIMEOUT: int         # seconds


def _require(key: str) -> str:
    """Read a required env variable; raise clearly if missing."""
    val = os.environ.get(key, "").strip()
    if not val:
        raise EnvironmentError(
            f"Required environment variable '{key}' is not set.\n"
            f"Add it to {_ENV_FILE} (copy .env.example as a starting point)."
        )
    return val


def _build_config() -> Config:
    model_id = _require("VLLM_MODEL_ID")
    return Config(
        VLLM_BASE_URL=_require("VLLM_BASE_URL"),
        VLLM_API_KEY=_require("VLLM_API_KEY"),
        VLLM_MODEL_ID=model_id,
        MODEL=f"vllm/{model_id}",
        WHATSAPP_TARGET=_require("WHATSAPP_TARGET"),
        WHATSAPP_TARGET_E164=_require("WHATSAPP_TARGET_E164"),
        AGENT_TIMEOUT=int(os.environ.get("AGENT_TIMEOUT", "120")),
    )


cfg = _build_config()
