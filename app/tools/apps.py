import os
import shutil
import subprocess

from app.agents.tool import PELIGROSO, params, texto, tool


# Nombres comunes -> comando o protocolo de Windows
APP_ALIASES = {
    "chrome": "chrome",
    "google chrome": "chrome",
    "edge": "msedge",
    "firefox": "firefox",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "outlook": "outlook",
    "bloc de notas": "notepad",
    "notepad": "notepad",
    "calculadora": "calc",
    "explorador": "explorer",
    "paint": "mspaint",
    "spotify": "spotify:",
    "whatsapp": "whatsapp:",
    "configuracion": "ms-settings:",
    "configuración": "ms-settings:",
    "vscode": "code",
    "visual studio code": "code",
    "terminal": "wt",
    "powershell": "powershell",
}


def _gw():
    try:
        import pygetwindow
    except ImportError as e:
        raise RuntimeError(
            "Falta pygetwindow (pip install pygetwindow). "
            "Solo funciona en Windows."
        ) from e

    return pygetwindow


def _buscar_ventana(titulo):
    gw = _gw()
    titulo_l = titulo.lower()

    ventanas = [
        w for w in gw.getAllWindows()
        if w.title.strip() and titulo_l in w.title.lower()
    ]

    if not ventanas:
        raise RuntimeError(f"No encontré ninguna ventana con '{titulo}'.")

    return ventanas[0]


@tool(
    "listar_ventanas",
    "Lista los títulos de las ventanas abiertas (programas activos).",
)
def listar_ventanas():
    gw = _gw()
    titulos = sorted({t.strip() for t in gw.getAllTitles() if t.strip()})
    return "\n".join(titulos) or "No hay ventanas visibles."


@tool(
    "abrir_aplicacion",
    "Abre un programa por su nombre (chrome, word, excel, spotify, "
    "whatsapp, bloc de notas...) o una ruta a un .exe.",
    params({"nombre": texto("Nombre del programa o ruta")}, ["nombre"]),
)
def abrir_aplicacion(nombre):
    objetivo = APP_ALIASES.get(nombre.lower().strip(), nombre)

    if os.path.exists(objetivo):
        os.startfile(objetivo)
    elif objetivo.endswith(":"):
        os.startfile(objetivo)
    elif shutil.which(objetivo):
        subprocess.Popen([objetivo])
    else:
        # 'start' busca en las rutas registradas de Windows
        subprocess.Popen(f'start "" "{objetivo}"', shell=True)

    return f"Abriendo {nombre}."


@tool(
    "enfocar_ventana",
    "Trae al frente una ventana abierta buscando parte de su título.",
    params({"titulo": texto("Parte del título de la ventana")}, ["titulo"]),
)
def enfocar_ventana(titulo):
    ventana = _buscar_ventana(titulo)

    if ventana.isMinimized:
        ventana.restore()

    ventana.activate()
    return f"Ventana enfocada: {ventana.title}"


@tool(
    "minimizar_ventana",
    "Minimiza una ventana abierta buscando parte de su título.",
    params({"titulo": texto("Parte del título de la ventana")}, ["titulo"]),
)
def minimizar_ventana(titulo):
    ventana = _buscar_ventana(titulo)
    ventana.minimize()
    return f"Ventana minimizada: {ventana.title}"


@tool(
    "maximizar_ventana",
    "Maximiza una ventana abierta buscando parte de su título.",
    params({"titulo": texto("Parte del título de la ventana")}, ["titulo"]),
)
def maximizar_ventana(titulo):
    ventana = _buscar_ventana(titulo)
    ventana.maximize()
    return f"Ventana maximizada: {ventana.title}"


@tool(
    "cerrar_ventana",
    "Cierra una ventana abierta buscando parte de su título. "
    "Puede perder trabajo no guardado.",
    params({"titulo": texto("Parte del título de la ventana")}, ["titulo"]),
    risk=PELIGROSO,
)
def cerrar_ventana(titulo):
    ventana = _buscar_ventana(titulo)
    nombre = ventana.title
    ventana.close()
    return f"Ventana cerrada: {nombre}"


@tool(
    "listar_procesos",
    "Lista los procesos que más memoria usan.",
)
def listar_procesos():
    import psutil

    procesos = []

    for p in psutil.process_iter(["pid", "name", "memory_info"]):
        try:
            memoria = p.info["memory_info"].rss / (1024 * 1024)
            procesos.append((memoria, p.info["pid"], p.info["name"]))
        except (psutil.Error, AttributeError):
            continue

    procesos.sort(reverse=True)

    return "\n".join(
        f"{nombre} (pid {pid}) - {memoria:.0f} MB"
        for memoria, pid, nombre in procesos[:25]
    )


@tool(
    "cerrar_proceso",
    "Termina todos los procesos con ese nombre (ej. chrome.exe).",
    params({"nombre": texto("Nombre del proceso")}, ["nombre"]),
    risk=PELIGROSO,
)
def cerrar_proceso(nombre):
    import psutil

    nombre_l = nombre.lower()
    cerrados = 0

    for p in psutil.process_iter(["name"]):
        if (p.info["name"] or "").lower() == nombre_l:
            try:
                p.terminate()
                cerrados += 1
            except psutil.Error:
                pass

    return f"Procesos cerrados: {cerrados}"


TOOLS = [
    listar_ventanas,
    abrir_aplicacion,
    enfocar_ventana,
    minimizar_ventana,
    maximizar_ventana,
    cerrar_ventana,
    listar_procesos,
    cerrar_proceso,
]
