import webbrowser
from urllib.parse import quote_plus

import requests

from app import config
from app.agents.tool import params, texto, tool


API = "https://api.canva.com/rest/v1"

# Formatos comunes -> tamaño en píxeles y término de búsqueda de plantillas
FORMATOS = {
    "post_instagram": (1080, 1080, "instagram post"),
    "historia_instagram": (1080, 1920, "instagram story"),
    "reel": (1080, 1920, "instagram reel"),
    "post_facebook": (1200, 630, "facebook post"),
    "anuncio_facebook": (1080, 1080, "facebook ad"),
    "miniatura_youtube": (1280, 720, "youtube thumbnail"),
    "banner_youtube": (2560, 1440, "youtube banner"),
    "tiktok": (1080, 1920, "tiktok video"),
    "flyer": (1240, 1754, "flyer"),
    "logo": (500, 500, "logo"),
    "presentacion": (1920, 1080, "presentation"),
    "linkedin": (1200, 627, "linkedin post"),
}


def _headers():
    return {
        "Authorization": f"Bearer {config.CANVA_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }


@tool(
    "canva_crear_diseno",
    "Crea un diseño nuevo en Canva y lo abre en el navegador para "
    "editarlo. Formatos: " + ", ".join(FORMATOS) + ".",
    params(
        {
            "formato": texto("Uno de los formatos disponibles"),
            "titulo": texto("Título del diseño"),
        },
        ["formato", "titulo"],
    ),
)
def canva_crear_diseno(formato, titulo):
    ancho, alto, busqueda = FORMATOS.get(
        formato, FORMATOS["post_instagram"]
    )

    if not config.CANVA_ACCESS_TOKEN:
        # Sin API: abrir plantillas de Canva del formato pedido
        url = "https://www.canva.com/templates/?query=" + quote_plus(busqueda)
        webbrowser.open(url)
        return (
            f"Abrí plantillas de Canva para '{busqueda}'. "
            "(Con CANVA_ACCESS_TOKEN en .env puedo crear el diseño directamente.)"
        )

    respuesta = requests.post(
        f"{API}/designs",
        headers=_headers(),
        json={
            "design_type": {"type": "custom", "width": ancho, "height": alto},
            "title": titulo[:255],
        },
        timeout=20,
    )
    respuesta.raise_for_status()

    diseno = respuesta.json()["design"]
    webbrowser.open(diseno["urls"]["edit_url"])

    return f"Diseño '{titulo}' ({ancho}x{alto}) creado y abierto en Canva."


@tool(
    "canva_mis_disenos",
    "Lista los diseños recientes de Canva (requiere CANVA_ACCESS_TOKEN).",
    params({"buscar": texto("Texto a buscar (opcional)")}),
)
def canva_mis_disenos(buscar=""):
    if not config.CANVA_ACCESS_TOKEN:
        raise RuntimeError("Falta CANVA_ACCESS_TOKEN en el archivo .env.")

    consulta = {"query": buscar} if buscar else {}
    respuesta = requests.get(
        f"{API}/designs", headers=_headers(), params=consulta, timeout=20
    )
    respuesta.raise_for_status()

    return "\n".join(
        f"- {d.get('title') or '(sin título)'}: {d['urls']['edit_url']}"
        for d in respuesta.json().get("items", [])[:20]
    ) or "No hay diseños."


TOOLS = [canva_crear_diseno, canva_mis_disenos]
