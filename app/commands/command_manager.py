from datetime import datetime
import re


class CommandManager:
    """Respuestas instantáneas que no necesitan IA.
    Si la orden no es una de estas, devuelve None y la
    orden pasa a la red de agentes de YAELCORE."""

    def execute(self, command):
        command = re.sub(r"[¿?¡!.,]", "", command.lower()).strip()

        # Saludo (solo si no viene acompañado de otra orden)
        if command in ("hola", "hola jarvis", "buenas", "hey jarvis"):
            return "Hola señor Yael. ¿Cómo puedo ayudarle?"

        # Hora
        if command in ("hora", "qué hora es", "que hora es", "dime la hora"):
            hora = datetime.now().strftime("%H:%M")
            return f"Son las {hora}"

        # Fecha
        if command in (
            "fecha",
            "qué fecha es",
            "que fecha es",
            "qué día es hoy",
            "que dia es hoy",
            "dime la fecha",
        ):
            fecha = datetime.now().strftime("%d/%m/%Y")
            return f"Hoy es {fecha}"

        return None
