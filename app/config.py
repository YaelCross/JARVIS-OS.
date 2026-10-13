import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


# ==================================================
# RUTAS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = DATA_DIR / "documentos"
CAPTURAS_DIR = DATA_DIR / "capturas"
LOGS_DIR = BASE_DIR / "logs"

for carpeta in (DATA_DIR, DOCS_DIR, CAPTURAS_DIR, LOGS_DIR):
    carpeta.mkdir(parents=True, exist_ok=True)


def env(nombre, defecto=""):
    return os.getenv(nombre, defecto).strip()


# ==================================================
# IDENTIDAD
# ==================================================

SYSTEM_NAME = "YAELCORE-OS"
ASSISTANT_NAME = env("ASSISTANT_NAME", "JARVIS")
USER_NAME = env("USER_NAME", "Yael")


# ==================================================
# CEREBRO (LLM)
# ==================================================

# openai | anthropic
LLM_PROVIDER = env("LLM_PROVIDER", "openai").lower()

OPENAI_API_KEY = env("OPENAI_API_KEY")
OPENAI_MODEL = env("OPENAI_MODEL", "gpt-5")

ANTHROPIC_API_KEY = env("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = env("ANTHROPIC_MODEL", "claude-opus-5-5")
# low | medium | high | xhigh | max
ANTHROPIC_EFFORT = env("ANTHROPIC_EFFORT", "medium")
# Si Claude rechaza una solicitud, la API la reintenta con otro modelo.
ANTHROPIC_FALLBACKS = env("ANTHROPIC_FALLBACKS", "1") == "1"

MAX_AGENT_STEPS = int(env("MAX_AGENT_STEPS", "12"))


# ==================================================
# SEGURIDAD
# ==================================================

# confirmar_peligroso | confirmar_todo | autonomo
SAFETY_MODE = env("SAFETY_MODE", "confirmar_peligroso").lower()


# ==================================================
# INTEGRACIONES
# ==================================================

TRELLO_API_KEY = env("TRELLO_API_KEY")
TRELLO_TOKEN = env("TRELLO_TOKEN")
# Minutos entre revisiones de pendientes de Trello (0 = desactivado)
TRELLO_CHECK_MINUTES = int(env("TRELLO_CHECK_MINUTES", "30"))

CANVA_ACCESS_TOKEN = env("CANVA_ACCESS_TOKEN")

TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN")
MENTION_HANDLE = env("MENTION_HANDLE", "@YaelCS")
