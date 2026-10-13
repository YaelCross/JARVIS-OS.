import re
import threading
from datetime import datetime

from app import config
from app.agents.orchestrator import YaelCore
from app.commands.command_manager import CommandManager
from app.core.notifications import notifications
from app.core.state import JarvisState
from app.watchers.watchers import start_watchers


SALIR = ("salir", "apágate", "apagate", "adiós jarvis", "adios jarvis")
AFIRMATIVO = re.compile(
    r"\b(s[ií]|confirmo|confirmado|adelante|hazlo|procede|claro|ok|okay|dale)\b"
)


class Jarvis:

    def __init__(self, mode="voz"):
        self.name = config.ASSISTANT_NAME
        self.version = "0.2.0"
        self.mode = mode

        self.state = JarvisState.BOOTING

        # Callbacks opcionales para la interfaz gráfica
        self.on_command = None
        self.on_response = None

        if mode == "voz":
            # Solo se cargan en modo voz (dependen de Windows y micrófono)
            from app.voice.listener import Listener
            from app.voice.speaker import Speaker

            self.speaker = Speaker()
            self.listener = Listener()

        self.command_manager = CommandManager()
        self.core = YaelCore(confirmer=self.confirm)

        self.lock = threading.Lock()

    # ==========================================
    # ENTRADA / SALIDA
    # ==========================================

    def say(self, text):
        print(f"{self.name}:", text)

        if self.on_response:
            self.on_response(text)

        if self.mode == "voz":
            previous = self.state
            self.state = JarvisState.SPEAKING
            self.speaker.say(text)
            self.state = previous

    def hear(self):
        if self.mode == "voz":
            return self.listener.listen()

        try:
            return input("\nTú: ").strip()
        except EOFError:
            return "salir"

    def confirm(self, description):
        """Pide permiso a Yael antes de una acción peligrosa."""
        self.say(
            f"Necesito su confirmación para: {description}. ¿Procedo?"
        )

        self.state = JarvisState.LISTENING
        answer = (self.hear() or "").lower()
        self.state = JarvisState.PROCESSING

        approved = bool(AFIRMATIVO.search(answer)) and "no" not in answer.split()

        print("CONFIRMACIÓN:", "aprobada" if approved else "rechazada")
        return approved

    # ==========================================
    # SALUDO
    # ==========================================

    def get_greeting(self):
        hour = datetime.now().hour

        if 5 <= hour < 12:
            return "Buenos días"
        elif 12 <= hour < 19:
            return "Buenas tardes"
        else:
            return "Buenas noches"

    # ==========================================
    # AVISOS DE LOS VIGILANTES
    # ==========================================

    def announce_notifications(self):
        for notification in notifications.drain():
            self.say(notification.text)

    def notification_printer(self):
        # En modo texto los avisos se imprimen en cuanto llegan
        while True:
            notification = notifications.queue.get()
            print(f"\n🔔 {notification.text}\nTú: ", end="", flush=True)

    # ==========================================
    # PROCESAR UNA ORDEN
    # ==========================================

    def handle(self, comando):
        with self.lock:
            self.state = JarvisState.PROCESSING
            print("ESTADO:", self.state.value)

            if self.on_command:
                self.on_command(comando)

            respuesta = self.command_manager.execute(comando)

            if respuesta is None:
                respuesta = self.core.handle(comando)

            return respuesta

    # ==========================================
    # BUCLE PRINCIPAL
    # ==========================================

    def start(self):

        activos = start_watchers()

        mensaje = (
            f"{self.get_greeting()}, señor {config.USER_NAME}. "
            f"{config.SYSTEM_NAME} en línea con "
            f"{len(self.core.specialists)} agentes especialistas. "
            "Estoy listo para asistirle."
        )

        print("=" * 50)
        print(f"{config.SYSTEM_NAME} // {self.name} v{self.version}")
        print(f"Cerebro: {config.LLM_PROVIDER} | Seguridad: {config.SAFETY_MODE}")
        print(f"Vigilantes activos: {', '.join(activos) or 'ninguno'}")
        print("=" * 50)

        if self.mode == "texto":
            threading.Thread(target=self.notification_printer, daemon=True).start()

        self.say(mensaje)

        while True:

            if self.mode == "voz":
                self.announce_notifications()

            # ==========================================
            # ESCUCHANDO
            # ==========================================

            self.state = JarvisState.LISTENING
            print("ESTADO:", self.state.value)

            comando = self.hear()

            if not comando:
                continue

            # ==========================================
            # SALIR
            # ==========================================

            if comando.lower().strip(" .!") in SALIR:
                self.say(f"Hasta luego señor {config.USER_NAME}.")
                break

            # ==========================================
            # PROCESANDO (red de agentes)
            # ==========================================

            respuesta = self.handle(comando)

            # ==========================================
            # RESPUESTA
            # ==========================================

            self.say(respuesta)

            self.state = JarvisState.IDLE
            print("ESTADO:", self.state.value)
