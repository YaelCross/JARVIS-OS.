import time
from datetime import datetime

from app import config
from app.agents.tool import PELIGROSO, entero, params, texto, tool


def _pg():
    try:
        import pyautogui
    except ImportError as e:
        raise RuntimeError("Falta pyautogui (pip install pyautogui).") from e

    # Mover el ratón a una esquina detiene cualquier acción
    pyautogui.FAILSAFE = True
    return pyautogui


@tool(
    "escribir_texto",
    "Escribe texto en la aplicación que está activa, como si se "
    "tecleara (admite acentos y ñ).",
    params({"texto": texto("Texto a escribir")}, ["texto"]),
    risk=PELIGROSO,
)
def escribir_texto(texto):
    pg = _pg()
    import pyperclip

    # Pegar desde el portapapeles respeta acentos, ñ y emojis
    anterior = pyperclip.paste()
    pyperclip.copy(texto)
    time.sleep(0.1)
    pg.hotkey("ctrl", "v")
    time.sleep(0.2)
    pyperclip.copy(anterior)

    return f"Escribí {len(texto)} caracteres en la ventana activa."


@tool(
    "atajo_teclado",
    "Presiona un atajo de teclado en la app activa. Teclas separadas "
    "por '+', ej. 'ctrl+s', 'alt+tab', 'win+d', 'enter'.",
    params({"teclas": texto("Combinación, ej. ctrl+shift+esc")}, ["teclas"]),
    risk=PELIGROSO,
)
def atajo_teclado(teclas):
    pg = _pg()
    partes = [t.strip().lower() for t in teclas.split("+") if t.strip()]
    partes = ["win" if t in ("windows", "super") else t for t in partes]
    pg.hotkey(*partes)
    return f"Presioné {teclas}."


@tool(
    "hacer_clic",
    "Hace clic en una posición de la pantalla (x, y en píxeles).",
    params(
        {
            "x": entero("Coordenada horizontal"),
            "y": entero("Coordenada vertical"),
            "boton": texto("left, right o middle (por defecto left)"),
            "clics": entero("1 = clic, 2 = doble clic"),
        },
        ["x", "y"],
    ),
    risk=PELIGROSO,
)
def hacer_clic(x, y, boton="left", clics=1):
    pg = _pg()
    pg.click(x=x, y=y, button=boton, clicks=clics, interval=0.1)
    return f"Clic {boton} x{clics} en ({x}, {y})."


@tool(
    "mover_raton",
    "Mueve el puntero del ratón a una posición (x, y).",
    params({"x": entero("Horizontal"), "y": entero("Vertical")}, ["x", "y"]),
)
def mover_raton(x, y):
    _pg().moveTo(x, y, duration=0.2)
    return f"Ratón en ({x}, {y})."


@tool(
    "info_pantalla",
    "Devuelve el tamaño de la pantalla y la posición actual del ratón.",
)
def info_pantalla():
    pg = _pg()
    ancho, alto = pg.size()
    x, y = pg.position()
    return f"Pantalla: {ancho}x{alto}. Ratón en ({x}, {y})."


@tool(
    "captura_pantalla",
    "Toma una captura de pantalla y la guarda en data/capturas.",
    params({"nombre": texto("Nombre opcional del archivo")}),
)
def captura_pantalla(nombre=""):
    pg = _pg()
    nombre = nombre or datetime.now().strftime("captura_%Y%m%d_%H%M%S")
    ruta = config.CAPTURAS_DIR / f"{nombre}.png"
    pg.screenshot(str(ruta))
    return f"Captura guardada en {ruta}"


TOOLS = [
    escribir_texto,
    atajo_teclado,
    hacer_clic,
    mover_raton,
    info_pantalla,
    captura_pantalla,
]
