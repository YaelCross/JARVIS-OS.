import argparse
import threading

from app.core.jarvis import Jarvis


def start_voice():
    # La interfaz gráfica solo se carga en modo voz
    from app.ui.core_ui import JarvisCoreUI
    from app.ui.splash import JarvisSplash

    def start_jarvis():

        jarvis = Jarvis(mode="voz")

        ui = JarvisCoreUI(
            jarvis
        )

        # Conectar JARVIS con la interfaz principal.
        # Tkinter solo puede actualizarse desde su propio hilo.
        jarvis.on_command = lambda text: ui.root.after(0, ui.show_command, text)
        jarvis.on_response = lambda text: ui.root.after(0, ui.show_response, text)

        threading.Thread(
            target=jarvis.start,
            daemon=True
        ).start()

        ui.show()

    splash = JarvisSplash(
        on_complete=start_jarvis
    )

    splash.show()


def start_text():
    Jarvis(mode="texto").start()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="YAELCORE-OS")
    parser.add_argument(
        "--texto",
        action="store_true",
        help="Chat por teclado en la consola (sin voz ni interfaz)",
    )
    args = parser.parse_args()

    if args.texto:
        start_text()
    else:
        start_voice()
