from app import config
from app.agents.base_agent import Agent
from app.agents.safety import SafetyGate
from app.agents.specialists import build_specialists
from app.agents.tool import INTERNO, Tool, params, texto


MEMORY_TURNS = 6


class YaelCore:
    """Orquestador de la red: recibe la orden de Yael, decide qué
    especialistas necesita, les delega subtareas (en orden, pasando
    resultados de uno a otro) y responde con un resumen breve."""

    def __init__(self, confirmer=None):
        self.safety = SafetyGate(confirmer=confirmer)
        self.specialists = build_specialists(self.safety)
        self.memory = []

        self.agent = Agent(
            key="yaelcore",
            name=config.ASSISTANT_NAME,
            role="coordinar la red de agentes especialistas.",
            instructions=self.instructions(),
            tools=[self.delegation_tool(a) for a in self.specialists.values()],
            safety=self.safety,
        )

    def set_confirmer(self, confirmer):
        self.safety.confirmer = confirmer

    def set_event_handler(self, handler):
        self.agent.on_event = handler

        for agent in self.specialists.values():
            agent.on_event = handler

    def instructions(self):
        return (
            f"Eres el asistente personal por voz de {config.USER_NAME}, a quien "
            "llamas 'señor Yael'. Eres profesional, elegante, claro y directo.\n\n"
            "Tienes una red de agentes especialistas. Para cualquier acción en "
            "la computadora, en internet o en las apps de Yael, DELEGA con la "
            "herramienta del especialista adecuado, dándole una tarea completa "
            "y autocontenida (él no ve esta conversación).\n"
            "- Tareas compuestas: divide en pasos y delega en orden, pasando "
            "al siguiente agente lo que obtuvo el anterior (ej. investigar con "
            "Web -> campaña con Marketing -> diseño con Diseño).\n"
            "- Preguntas generales o conversación: responde tú directamente.\n\n"
            "Tu respuesta final se dirá en voz alta: máximo 3 frases, sin "
            "markdown, sin listas largas ni enlaces. Si se generó un documento, "
            "menciona que quedó guardado."
        )

    def delegation_tool(self, specialist):
        def delegate(tarea):
            return specialist.run(tarea)

        return Tool(
            name=f"delegar_{specialist.key}",
            description=f"Delega al {specialist.name}: {specialist.role}",
            parameters=params(
                {"tarea": texto("Tarea completa y detallada para el especialista")},
                ["tarea"],
            ),
            func=delegate,
            risk=INTERNO,
        )

    def handle(self, command):
        contexto = ""

        if self.memory:
            contexto = "Conversación reciente:\n" + "\n".join(
                f"Yael: {u}\nTú: {r}" for u, r in self.memory
            ) + "\n\n"

        try:
            respuesta = self.agent.run(f"{contexto}Orden actual de Yael: {command}")
        except Exception as e:
            print("ERROR YAELCORE:", repr(e))
            respuesta = (
                "Lo siento señor Yael, ocurrió un error al procesar su "
                f"solicitud: {type(e).__name__}."
            )

        self.memory.append((command, respuesta))
        self.memory = self.memory[-MEMORY_TURNS:]

        return respuesta
