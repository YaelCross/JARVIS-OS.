from datetime import datetime
import webbrowser


class CommandManager:

    def execute(self, command):
        command = command.lower()

        # Saludo
        if "hola" in command:
            return "Hola señor Yael. ¿Cómo puedo ayudarle?"

        # Hora
        elif "hora" in command:
            hora = datetime.now().strftime("%H:%M")
            return f"Son las {hora}"

        # Fecha
        elif "fecha" in command:
            fecha = datetime.now().strftime("%d/%m/%Y")
            return f"Hoy es {fecha}"

        # Google
        elif "google" in command:
            webbrowser.open("https://www.google.com")
            return "Abriendo Google."

        # YouTube
        elif "youtube" in command:
            webbrowser.open("https://www.youtube.com")
            return "Abriendo YouTube."

        else:
            return "Lo siento, todavía no conozco ese comando."