from datetime import datetime

from app.voice.speaker import Speaker
from app.voice.listener import Listener
from app.commands.command_manager import CommandManager
from app.ai.assistant import Assistant
from app.core.state import JarvisState


class Jarvis:

    def __init__(self):
        self.name = "JARVIS"
        self.version = "0.1.0"

        self.state = JarvisState.BOOTING

        self.speaker = Speaker()
        self.listener = Listener()
        self.command_manager = CommandManager()
        self.assistant = Assistant()

    def get_greeting(self):
        hour = datetime.now().hour

        if 5 <= hour < 12:
            return "Buenos días"
        elif 12 <= hour < 19:
            return "Buenas tardes"
        else:
            return "Buenas noches"

    def start(self):

        mensaje = (
            f"{self.get_greeting()}, señor Yael. "
            "Todos los sistemas están operativos. "
            "Estoy listo para asistirle."
        )

        print("=" * 50)
        print(f"{self.name} OS v{self.version}")
        print("=" * 50)
        print(mensaje)
        print("=" * 50)

        self.speaker.say(mensaje)

        while True:

            # ==========================================
            # ESCUCHANDO
            # ==========================================

            self.state = JarvisState.LISTENING
            print("ESTADO:", self.state.value)

            comando = self.listener.listen()

            if not comando:
                continue

            # ==========================================
            # SALIR
            # ==========================================

            if "salir" in comando.lower():

                self.speaker.say(
                    "Hasta luego señor Yael."
                )

                break

            # ==========================================
            # PROCESANDO
            # ==========================================

            self.state = JarvisState.PROCESSING
            print("ESTADO:", self.state.value)

            respuesta = self.command_manager.execute(
                comando
            )

            # ==========================================
            # IA
            # ==========================================

            if "todavía no conozco ese comando" in respuesta:

                print(
                    "DEBUG 2 - Enviando comando a la IA..."
                )

                respuesta = self.assistant.ask(
                    comando
                )

                print(
                    "DEBUG 3 - Respuesta recibida de la IA:",
                    respuesta
                )

            # ==========================================
            # RESPUESTA
            # ==========================================

            print(
                "JARVIS:",
                respuesta
            )

            # ==========================================
            # HABLANDO
            # ==========================================

            self.state = JarvisState.SPEAKING
            print("ESTADO:", self.state.value)

            self.speaker.say(
                respuesta
            )

            # ==========================================
            # LISTO
            # ==========================================

            self.state = JarvisState.IDLE
            print("ESTADO:", self.state.value)