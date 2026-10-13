import fnmatch
import os
import platform
import re
import subprocess
from pathlib import Path

from app.agents.tool import PELIGROSO, entero, params, texto, tool


MAX_LECTURA = 15000

# Comandos que nunca se ejecutan, aunque Yael confirme.
BLOQUEADOS = [
    r"format-volume",
    r"\bformat\s+[a-z]:",
    r"clear-disk",
    r"remove-partition",
    r"initialize-disk",
    r"remove-item\s+.*[a-z]:\\\s*(-|$)",
    r"\brd\s+/s\s+.*[a-z]:\\\s*$",
    r"bcdedit",
    r"vssadmin\s+delete",
    r"cipher\s+/w",
]


def _ruta(ruta):
    return Path(os.path.expandvars(os.path.expanduser(ruta)))


@tool(
    "leer_archivo",
    "Lee el contenido de un archivo de texto, código, CSV, JSON, "
    "Word (.docx) o PDF.",
    params({"ruta": texto("Ruta del archivo")}, ["ruta"]),
)
def leer_archivo(ruta):
    archivo = _ruta(ruta)

    if not archivo.is_file():
        raise FileNotFoundError(f"No existe el archivo: {archivo}")

    sufijo = archivo.suffix.lower()

    if sufijo == ".docx":
        import docx
        documento = docx.Document(str(archivo))
        contenido = "\n".join(p.text for p in documento.paragraphs)

    elif sufijo == ".pdf":
        from pypdf import PdfReader
        lector = PdfReader(str(archivo))
        contenido = "\n".join(
            pagina.extract_text() or "" for pagina in lector.pages
        )

    else:
        contenido = archivo.read_text(encoding="utf-8", errors="replace")

    if len(contenido) > MAX_LECTURA:
        contenido = contenido[:MAX_LECTURA] + "\n...(archivo recortado)"

    return contenido


@tool(
    "listar_carpeta",
    "Lista archivos y subcarpetas de una carpeta. Acepta ~ para la "
    "carpeta del usuario (ej. ~/Desktop, ~/Documents, ~/Downloads).",
    params({"ruta": texto("Ruta de la carpeta")}, ["ruta"]),
)
def listar_carpeta(ruta):
    carpeta = _ruta(ruta)

    if not carpeta.is_dir():
        raise FileNotFoundError(f"No existe la carpeta: {carpeta}")

    lineas = []

    for item in sorted(carpeta.iterdir())[:200]:
        tipo = "[carpeta]" if item.is_dir() else f"{item.stat().st_size} bytes"
        lineas.append(f"{item.name}  {tipo}")

    return "\n".join(lineas) or "La carpeta está vacía."


@tool(
    "buscar_archivos",
    "Busca archivos por nombre con comodines (ej. *.pdf, *factura*).",
    params(
        {
            "patron": texto("Patrón del nombre, ej. *contrato*.docx"),
            "carpeta": texto("Carpeta donde buscar (por defecto ~)"),
        },
        ["patron"],
    ),
)
def buscar_archivos(patron, carpeta="~"):
    raiz = _ruta(carpeta)
    encontrados = []

    for actual, dirs, archivos in os.walk(raiz):
        # Saltar carpetas ocultas y pesadas
        dirs[:] = [
            d for d in dirs
            if not d.startswith(".")
            and d not in ("node_modules", "AppData", "__pycache__")
        ]

        for nombre in archivos:
            if fnmatch.fnmatch(nombre.lower(), patron.lower()):
                encontrados.append(os.path.join(actual, nombre))

                if len(encontrados) >= 50:
                    return "\n".join(encontrados) + "\n(primeros 50)"

    return "\n".join(encontrados) or "No encontré archivos."


@tool(
    "escribir_archivo",
    "Crea o sobrescribe un archivo de texto con el contenido indicado.",
    params(
        {
            "ruta": texto("Ruta del archivo"),
            "contenido": texto("Contenido a escribir"),
        },
        ["ruta", "contenido"],
    ),
    risk=PELIGROSO,
)
def escribir_archivo(ruta, contenido):
    archivo = _ruta(ruta)
    archivo.parent.mkdir(parents=True, exist_ok=True)
    archivo.write_text(contenido, encoding="utf-8")
    return f"Archivo guardado: {archivo}"


@tool(
    "info_sistema",
    "Muestra el estado de la PC: CPU, memoria, disco y batería.",
)
def info_sistema():
    import psutil

    memoria = psutil.virtual_memory()
    disco = psutil.disk_usage(str(Path.home().anchor or "/"))
    bateria = psutil.sensors_battery() if hasattr(psutil, "sensors_battery") else None

    lineas = [
        f"Sistema: {platform.system()} {platform.release()}",
        f"CPU: {psutil.cpu_percent(interval=0.5)}%",
        f"Memoria: {memoria.percent}% usada de "
        f"{memoria.total / 1024 ** 3:.1f} GB",
        f"Disco: {disco.percent}% usado, "
        f"{disco.free / 1024 ** 3:.1f} GB libres",
    ]

    if bateria:
        estado = "cargando" if bateria.power_plugged else "con batería"
        lineas.append(f"Batería: {bateria.percent:.0f}% ({estado})")

    return "\n".join(lineas)


@tool(
    "ejecutar_powershell",
    "Ejecuta un comando de PowerShell y devuelve la salida. Úsalo para "
    "tareas del sistema que no cubren otras herramientas.",
    params(
        {
            "comando": texto("Comando de PowerShell"),
            "timeout": entero("Segundos máximos (por defecto 60)"),
        },
        ["comando"],
    ),
    risk=PELIGROSO,
)
def ejecutar_powershell(comando, timeout=60):
    for patron in BLOQUEADOS:
        if re.search(patron, comando, re.IGNORECASE):
            raise PermissionError(
                "Comando bloqueado por seguridad: puede dañar el sistema."
            )

    ejecutable = "powershell" if os.name == "nt" else "pwsh"

    resultado = subprocess.run(
        [ejecutable, "-NoProfile", "-NonInteractive", "-Command", comando],
        capture_output=True,
        text=True,
        timeout=timeout,
        encoding="utf-8",
        errors="replace",
    )

    salida = (resultado.stdout or "") + (resultado.stderr or "")
    salida = salida.strip() or "(sin salida)"

    return f"Código de salida: {resultado.returncode}\n{salida}"


TOOLS_ARCHIVOS = [leer_archivo, listar_carpeta, buscar_archivos]

TOOLS = TOOLS_ARCHIVOS + [escribir_archivo, info_sistema, ejecutar_powershell]
