from dataclasses import dataclass, field

from app import config


# ==================================================
# ESTRUCTURAS COMUNES
# ==================================================
# Cada proveedor (OpenAI, Claude) traduce su formato
# nativo a estas clases, así los agentes no dependen
# de ningún proveedor en particular.


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict


@dataclass
class Turn:
    text: str = ""
    tool_calls: list = field(default_factory=list)


@dataclass
class ToolResult:
    call_id: str
    content: str
    is_error: bool = False


class Conversation:
    """Una conversación con herramientas. La implementa cada proveedor."""

    def add_user(self, text):
        raise NotImplementedError

    def next(self):
        """Pide al modelo el siguiente turno y devuelve un Turn."""
        raise NotImplementedError

    def add_tool_results(self, results):
        raise NotImplementedError


class LLMProvider:

    def new_conversation(self, system, tools):
        raise NotImplementedError


# ==================================================
# FÁBRICA
# ==================================================

_provider = None


def get_provider():
    global _provider

    if _provider is not None:
        return _provider

    if config.LLM_PROVIDER == "anthropic":
        from app.brain.anthropic_provider import AnthropicProvider
        _provider = AnthropicProvider()

    elif config.LLM_PROVIDER == "openai":
        from app.brain.openai_provider import OpenAIProvider
        _provider = OpenAIProvider()

    else:
        raise ValueError(
            f"LLM_PROVIDER desconocido: {config.LLM_PROVIDER}. "
            "Usa 'openai' o 'anthropic'."
        )

    return _provider


def set_provider(provider):
    """Permite inyectar un proveedor (útil para pruebas)."""
    global _provider
    _provider = provider
