import json

from openai import OpenAI

from app import config
from app.brain.llm import Conversation, LLMProvider, ToolCall, Turn


class OpenAIConversation(Conversation):

    def __init__(self, client, system, tools):
        self.client = client
        self.messages = [{"role": "system", "content": system}]
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            }
            for tool in tools
        ]

    def add_user(self, text):
        self.messages.append({"role": "user", "content": text})

    def next(self):
        kwargs = {
            "model": config.OPENAI_MODEL,
            "messages": self.messages,
        }

        if self.tools:
            kwargs["tools"] = self.tools

        response = self.client.chat.completions.create(**kwargs)
        message = response.choices[0].message

        # Guardar el turno del asistente tal cual en el historial
        entry = {"role": "assistant", "content": message.content or ""}

        if message.tool_calls:
            entry["tool_calls"] = [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    },
                }
                for call in message.tool_calls
            ]

        self.messages.append(entry)

        calls = []

        for call in message.tool_calls or []:
            try:
                arguments = json.loads(call.function.arguments or "{}")
            except json.JSONDecodeError:
                arguments = {}

            calls.append(
                ToolCall(
                    id=call.id,
                    name=call.function.name,
                    arguments=arguments,
                )
            )

        return Turn(text=message.content or "", tool_calls=calls)

    def add_tool_results(self, results):
        for result in results:
            content = result.content

            if result.is_error:
                content = "ERROR: " + content

            self.messages.append({
                "role": "tool",
                "tool_call_id": result.call_id,
                "content": content,
            })


class OpenAIProvider(LLMProvider):

    def __init__(self):
        if not config.OPENAI_API_KEY:
            raise ValueError(
                "No se encontró OPENAI_API_KEY en el archivo .env"
            )

        self.client = OpenAI(api_key=config.OPENAI_API_KEY)

    def new_conversation(self, system, tools):
        return OpenAIConversation(self.client, system, tools)
