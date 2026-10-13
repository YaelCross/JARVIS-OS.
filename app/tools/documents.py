import os
import re
from datetime import datetime

from app import config
from app.agents.tool import params, texto, tool


def _slug(titulo):
    slug = re.sub(r"[^\w\s-]", "", titulo.lower()).strip()
    return re.sub(r"[\s_-]+", "_", slug)[:60] or "documento"


@tool(
    "guardar_documento",
    "Guarda un texto (guion, prompt, campaña, brief) como archivo "
    "Markdown nuevo en data/documentos. Nunca sobrescribe.",
    params(
        {
            "titulo": texto("Título del documento"),
            "contenido": texto("Contenido completo en Markdown"),
            "categoria": texto("guiones, prompts, campanas, disenos u otros"),
        },
        ["titulo", "contenido"],
    ),
)
def guardar_documento(titulo, contenido, categoria="otros"):
    carpeta = config.DOCS_DIR / _slug(categoria)
    carpeta.mkdir(parents=True, exist_ok=True)

    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta = carpeta / f"{marca}_{_slug(titulo)}.md"
    ruta.write_text(f"# {titulo}\n\n{contenido}\n", encoding="utf-8")

    return f"Documento guardado en {ruta}"


@tool(
    "listar_documentos",
    "Lista los documentos guardados por YAELCORE (guiones, prompts, "
    "campañas...).",
    params({"categoria": texto("Categoría opcional")}),
)
def listar_documentos(categoria=""):
    raiz = config.DOCS_DIR / _slug(categoria) if categoria else config.DOCS_DIR

    if not raiz.exists():
        return "No hay documentos en esa categoría."

    rutas = sorted(raiz.rglob("*.md"), key=os.path.getmtime, reverse=True)

    return "\n".join(
        str(r.relative_to(config.DOCS_DIR)) for r in rutas[:40]
    ) or "No hay documentos guardados."


@tool(
    "abrir_documento",
    "Abre un archivo con su programa predeterminado (Word, bloc de notas...).",
    params({"ruta": texto("Ruta del archivo")}, ["ruta"]),
)
def abrir_documento(ruta):
    destino = config.DOCS_DIR / ruta

    if not destino.exists():
        destino = os.path.expanduser(ruta)

    os.startfile(str(destino))
    return f"Abriendo {destino}"


TOOLS = [guardar_documento, listar_documentos, abrir_documento]
