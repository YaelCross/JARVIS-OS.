import webbrowser
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

import requests
from bs4 import BeautifulSoup

from app.agents.tool import params, texto, tool


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}

MAX_PAGINA = 10000


@tool(
    "buscar_google",
    "Abre en el navegador una búsqueda de Google.",
    params({"consulta": texto("Qué buscar")}, ["consulta"]),
)
def buscar_google(consulta):
    webbrowser.open(f"https://www.google.com/search?q={quote_plus(consulta)}")
    return f"Abrí Google con la búsqueda: {consulta}"


@tool(
    "buscar_youtube",
    "Abre en el navegador una búsqueda de YouTube.",
    params({"consulta": texto("Qué buscar")}, ["consulta"]),
)
def buscar_youtube(consulta):
    webbrowser.open(
        "https://www.youtube.com/results?search_query=" + quote_plus(consulta)
    )
    return f"Abrí YouTube con la búsqueda: {consulta}"


@tool(
    "abrir_sitio",
    "Abre una página web en el navegador.",
    params({"url": texto("Dirección, ej. https://www.canva.com")}, ["url"]),
)
def abrir_sitio(url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    webbrowser.open(url)
    return f"Abrí {url}"


def _url_real(href):
    # DuckDuckGo envuelve los enlaces: /l/?uddg=<url>
    if "uddg=" in href:
        return unquote(parse_qs(urlparse(href).query).get("uddg", [href])[0])

    return href


@tool(
    "buscar_en_internet",
    "Busca en internet y devuelve títulos, enlaces y resúmenes de los "
    "resultados (sin abrir el navegador). Úsalo para investigar.",
    params({"consulta": texto("Qué buscar")}, ["consulta"]),
)
def buscar_en_internet(consulta):
    respuesta = requests.post(
        "https://html.duckduckgo.com/html/",
        data={"q": consulta, "kl": "mx-es"},
        headers=HEADERS,
        timeout=15,
    )
    respuesta.raise_for_status()

    soup = BeautifulSoup(respuesta.text, "html.parser")
    resultados = []

    for item in soup.select(".result")[:8]:
        enlace = item.select_one(".result__a")
        resumen = item.select_one(".result__snippet")

        if not enlace:
            continue

        resultados.append(
            f"- {enlace.get_text(strip=True)}\n"
            f"  {_url_real(enlace.get('href', ''))}\n"
            f"  {resumen.get_text(strip=True) if resumen else ''}"
        )

    return "\n".join(resultados) or "Sin resultados."


@tool(
    "leer_pagina",
    "Descarga una página web y devuelve su texto principal.",
    params({"url": texto("Dirección de la página")}, ["url"]),
)
def leer_pagina(url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    respuesta = requests.get(url, headers=HEADERS, timeout=20)
    respuesta.raise_for_status()

    soup = BeautifulSoup(respuesta.text, "html.parser")

    for basura in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        basura.decompose()

    titulo = soup.title.get_text(strip=True) if soup.title else url
    lineas = [l.strip() for l in soup.get_text("\n").splitlines()]
    contenido = "\n".join(l for l in lineas if l)

    if len(contenido) > MAX_PAGINA:
        contenido = contenido[:MAX_PAGINA] + "\n...(página recortada)"

    return f"# {titulo}\n\n{contenido}"


TOOLS_INVESTIGACION = [buscar_en_internet, leer_pagina]

TOOLS = [buscar_google, buscar_youtube, abrir_sitio] + TOOLS_INVESTIGACION
