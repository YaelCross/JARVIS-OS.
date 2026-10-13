import threading

from app.core.jarvis import Jarvis
from app.ui.splash import JarvisSplash
from app.ui.core_ui import JarvisCoreUI


def start_jarvis():

    jarvis = Jarvis()

    ui = JarvisCoreUI(
        jarvis
    )

    # Conectar el sistema de voz de JARVIS
    # con la interfaz principal.
    

    def run_jarvis():

        jarvis.start()

    threading.Thread(
        target=run_jarvis,
        daemon=True
    ).start()

    ui.show()


def start_system():

    splash = JarvisSplash(
        on_complete=start_jarvis
    )

    splash.show()


if __name__ == "__main__":

    start_system()