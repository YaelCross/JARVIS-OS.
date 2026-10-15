from datetime import datetime
import webbrowser

from app.integrations.whatsapp import WhatsApp, WhatsAppError


class CommandManager:

    def __init__(self):
        self.whatsapp = WhatsApp()

    def execute(self, command):
        original = command
        command = command.lower()

        # WhatsApp: "envía un whatsapp diciendo ..."
        if "whatsapp" in command:
            return self.send_whatsapp(original)

        # Saludo
        elif "hola" in command:
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

    def send_whatsapp(self, command):

        if not self.whatsapp.is_configured():
            return "WhatsApp no está configurado en el archivo .env."

        lower = command.lower()

        if "diciendo" not in lower:
            return (
                "Dígame el mensaje, por ejemplo: "
                "envía un WhatsApp diciendo llego en diez minutos."
            )

        mensaje = command[lower.index("diciendo") + len("diciendo"):].strip()

        if not mensaje:
            return "No escuché el mensaje que desea enviar."

        try:
            self.whatsapp.send_text(mensaje)
        except WhatsAppError as e:
            print("WhatsApp:", e)
            return "No pude enviar el mensaje de WhatsApp."

        return "Mensaje de WhatsApp enviado."
