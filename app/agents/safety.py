import json
from datetime import datetime

from app import config
from app.agents.tool import INTERNO


class SafetyGate:
    """Decide si una acción necesita la confirmación de Yael.

    Modos (SAFETY_MODE en .env):
      - confirmar_peligroso: solo pide permiso para acciones peligrosas
      - confirmar_todo:      pide permiso para cualquier acción
      - autonomo:            nunca pide permiso
    """

    def __init__(self, mode=None, confirmer=None):
        self.mode = mode or config.SAFETY_MODE
        # confirmer(descripcion) -> bool. Lo asigna la interfaz
        # (voz o texto). Sin confirmer, lo peligroso se rechaza.
        self.confirmer = confirmer
        self.log_file = config.LOGS_DIR / "acciones.log"

    def needs_confirmation(self, tool):
        if self.mode == "autonomo" or tool.risk == INTERNO:
            return False

        if self.mode == "confirmar_todo":
            return True

        return tool.dangerous

    def authorize(self, agent_name, tool, arguments):
        if not self.needs_confirmation(tool):
            self.log(agent_name, tool, arguments, "autorizada")
            return True

        description = self.describe(tool, arguments)

        if self.confirmer is None:
            self.log(agent_name, tool, arguments, "rechazada (sin confirmador)")
            return False

        approved = bool(self.confirmer(description))

        self.log(
            agent_name,
            tool,
            arguments,
            "aprobada" if approved else "rechazada",
        )

        return approved

    def describe(self, tool, arguments):
        detalles = ", ".join(
            f"{clave}: {str(valor)[:80]}"
            for clave, valor in arguments.items()
        )

        return f"{tool.name} ({detalles})" if detalles else tool.name

    def log(self, agent_name, tool, arguments, resultado):
        linea = json.dumps(
            {
                "fecha": datetime.now().isoformat(timespec="seconds"),
                "agente": agent_name,
                "accion": tool.name,
                "argumentos": arguments,
                "resultado": resultado,
            },
            ensure_ascii=False,
            default=str,
        )

        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(linea + "\n")
        except OSError:
            pass
