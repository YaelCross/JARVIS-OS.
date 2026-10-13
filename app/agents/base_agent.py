import json
from datetime import datetime

from app import config
from app.brain.llm import ToolResult, get_provider


MAX_RESULT_CHARS = 12000

DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


class Agent:
    """Un agente: un rol (system prompt) + herramientas + bucle de
    razonamiento. Pide al modelo un paso, ejecuta las herramientas
    que solicite y repite hasta que el modelo responde sin pedir más."""

    def __init__(self, key, name, role, instructions, tools, safety):
        self.key = key
        self.name = name
        self.role = role
        self.instructions = instructions
        self.tools = {tool.name: tool for tool in tools}
        self.safety = safety
        # on_event(agente, mensaje) para mostrar progreso en la interfaz
        self.on_event = None

    def system_prompt(self):
        return (
            f"Eres {self.name}, agente de {config.SYSTEM_NAME}, "
            f"el sistema de agentes personal de {config.USER_NAME}. "
            f"Tu rol: {self.role}\n\n"
            f"{self.instructions}\n\n"
            "Reglas generales:\n"
            "- Responde siempre en español, claro y directo.\n"
            "- Usa tus herramientas para actuar; no inventes resultados.\n"
            "- Si una acción fue rechazada por el usuario, no la repitas: "
            "informa y sugiere alternativas.\n"
            "- Si te falta un dato imprescindible, dilo en tu respuesta final "
            "en lugar de adivinar.\n"
            "- Tu respuesta final debe resumir lo que hiciste y el resultado."
        )

    def emit(self, message):
        print(f"[{self.name}] {message}")

        if self.on_event:
            try:
                self.on_event(self.name, message)
            except Exception:
                pass

    def run(self, task):
        conversation = get_provider().new_conversation(
            self.system_prompt(),
            list(self.tools.values()),
        )

        now = datetime.now()
        ahora = f"{DIAS[now.weekday()]} {now.strftime('%d/%m/%Y %H:%M')}"
        conversation.add_user(f"(Fecha y hora: {ahora})\n\n{task}")

        for _ in range(config.MAX_AGENT_STEPS):
            turn = conversation.next()

            if not turn.tool_calls:
                return turn.text.strip() or "Listo."

            results = [self.execute(call) for call in turn.tool_calls]
            conversation.add_tool_results(results)

        return (
            "Detuve la tarea porque alcanzó el límite de pasos "
            f"({config.MAX_AGENT_STEPS}). Puede pedírmela de nuevo "
            "dividida en partes más pequeñas."
        )

    def execute(self, call):
        tool = self.tools.get(call.name)

        if tool is None:
            return ToolResult(
                call.id,
                f"La herramienta '{call.name}' no existe.",
                is_error=True,
            )

        if not self.safety.authorize(self.name, tool, call.arguments):
            self.emit(f"acción rechazada: {tool.name}")
            return ToolResult(
                call.id,
                "El usuario NO autorizó esta acción. No la ejecutes.",
                is_error=True,
            )

        self.emit(f"ejecutando {tool.name}")

        try:
            result = tool.func(**call.arguments)
        except TypeError as e:
            return ToolResult(call.id, f"Argumentos inválidos: {e}", True)
        except Exception as e:
            return ToolResult(call.id, f"{type(e).__name__}: {e}", True)

        if not isinstance(result, str):
            result = json.dumps(result, ensure_ascii=False, default=str)

        if len(result) > MAX_RESULT_CHARS:
            result = result[:MAX_RESULT_CHARS] + "\n...(resultado recortado)"

        return ToolResult(call.id, result)
