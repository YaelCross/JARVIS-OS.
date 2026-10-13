import anthropic

from app import config
from app.brain.llm import Conversation, LLMProvider, ToolCall, Turn


FALLBACK_BETA = "server-side-fallback-2026-07-01"


class AnthropicConversation(Conversation):

    def __init__(self, client, system, tools):
        self.client = client
        self.system = system
        self.messages = []
        self.tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.parameters,
            }
            for tool in tools
        ]

    def add_user(self, text):
        self.messages.append({"role": "user", "content": text})

    def next(self):
        kwargs = {
            "model": config.ANTHROPIC_MODEL,
            "max_tokens": 16000,
            "system": self.system,
            "messages": self.messages,
            "output_config": {"effort": config.ANTHROPIC_EFFORT},
        }

        if self.tools:
            kwargs["tools"] = self.tools

        if config.ANTHROPIC_FALLBACKS:
            # Si el modelo rechaza la solicitud, la API la
            # reintenta automáticamente con un modelo de respaldo.
            kwargs["betas"] = [FALLBACK_BETA]
            kwargs["extra_body"] = {"fallbacks": "default"}
            response = self.client.beta.messages.create(**kwargs)
        else:
            response = self.client.messages.create(**kwargs)

        # Guardar el contenido completo (incluye bloques de
        # razonamiento) para que el historial solo crezca.
        self.messages.append({
            "role": "assistant",
            "content": response.content,
        })

        if response.stop_reason == "refusal":
            return Turn(
                text="Lo siento, no puedo ayudar con esa solicitud."
            )

        text = "".join(
            block.text
            for block in response.content
            if block.type == "text"
        )

        calls = [
            ToolCall(
                id=block.id,
                name=block.name,
                arguments=dict(block.input or {}),
            )
            for block in response.content
            if block.type == "tool_use"
        ]

        if response.stop_reason == "max_tokens" and not calls:
            text += "\n(La respuesta se cortó por longitud.)"

        return Turn(text=text, tool_calls=calls)

    def add_tool_results(self, results):
        # Todas las respuestas de herramientas van en un solo mensaje
        self.messages.append({
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": result.call_id,
                    "content": result.content,
                    "is_error": result.is_error,
                }
                for result in results
            ],
        })


class AnthropicProvider(LLMProvider):

    def __init__(self):
        # Sin clave explícita el SDK busca ANTHROPIC_API_KEY
        # o un perfil de `ant auth login`.
        if config.ANTHROPIC_API_KEY:
            self.client = anthropic.Anthropic(
                api_key=config.ANTHROPIC_API_KEY
            )
        else:
            self.client = anthropic.Anthropic()

    def new_conversation(self, system, tools):
        return AnthropicConversation(self.client, system, tools)
