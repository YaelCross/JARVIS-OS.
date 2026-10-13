import re
from datetime import datetime, timezone

import requests

from app import config
from app.agents.tool import PELIGROSO, params, texto, tool


API = "https://api.trello.com/1"

# Listas que se consideran "terminadas"
LISTAS_HECHAS = re.compile(r"hecho|done|terminad|complet|finaliz", re.I)


def configurado():
    return bool(config.TRELLO_API_KEY and config.TRELLO_TOKEN)


def _api(metodo, ruta, **datos):
    if not configurado():
        raise RuntimeError(
            "Trello no está configurado. Agrega TRELLO_API_KEY y "
            "TRELLO_TOKEN al archivo .env (https://trello.com/power-ups/admin)."
        )

    auth = {"key": config.TRELLO_API_KEY, "token": config.TRELLO_TOKEN}

    if metodo == "GET":
        respuesta = requests.get(API + ruta, params={**auth, **datos}, timeout=20)
    else:
        respuesta = requests.request(
            metodo, API + ruta, params=auth, json=datos, timeout=20
        )

    respuesta.raise_for_status()
    return respuesta.json()


def tableros():
    return _api("GET", "/members/me/boards", filter="open", fields="name,url")


def _tablero(nombre):
    nombre_l = nombre.lower()

    for t in tableros():
        if nombre_l in t["name"].lower() or t["id"] == nombre:
            return t

    raise RuntimeError(f"No encontré el tablero '{nombre}'.")


def _listas(tablero_id):
    return _api("GET", f"/boards/{tablero_id}/lists", filter="open", fields="name")


def _fecha(due):
    if not due:
        return None

    return datetime.fromisoformat(due.replace("Z", "+00:00"))


def pendientes(tablero=None):
    """Tarjetas sin completar de uno o todos los tableros."""
    lista_tableros = [_tablero(tablero)] if tablero else tableros()
    resultado = []

    for t in lista_tableros:
        listas = {l["id"]: l["name"] for l in _listas(t["id"])}
        tarjetas = _api(
            "GET",
            f"/boards/{t['id']}/cards/open",
            fields="name,due,dueComplete,idList,shortUrl",
        )

        for c in tarjetas:
            lista = listas.get(c["idList"], "")

            if c.get("dueComplete") or LISTAS_HECHAS.search(lista):
                continue

            resultado.append({
                "id": c["id"],
                "tarjeta": c["name"],
                "tablero": t["name"],
                "lista": lista,
                "vence": c.get("due"),
                "url": c.get("shortUrl"),
            })

    # Primero las que tienen fecha, de la más próxima a la más lejana
    resultado.sort(key=lambda c: (c["vence"] is None, c["vence"] or ""))
    return resultado


def _formato(c):
    vence = _fecha(c["vence"])
    texto_vence = ""

    if vence:
        ahora = datetime.now(timezone.utc)
        local = vence.astimezone().strftime("%d/%m %H:%M")
        texto_vence = f" — VENCIDA ({local})" if vence < ahora else f" — vence {local}"

    return f"[{c['id']}] {c['tarjeta']} ({c['tablero']} / {c['lista']}){texto_vence}"


@tool(
    "trello_tableros",
    "Lista los tableros de Trello de Yael.",
)
def trello_tableros():
    return "\n".join(f"- {t['name']} ({t['url']})" for t in tableros())


@tool(
    "trello_pendientes",
    "Lista las tarjetas pendientes (no completadas), con vencimientos. "
    "Si no se indica tablero, revisa todos.",
    params({"tablero": texto("Nombre del tablero (opcional)")}),
)
def trello_pendientes(tablero=""):
    tarjetas = pendientes(tablero or None)
    return "\n".join(_formato(c) for c in tarjetas[:60]) or "No hay pendientes."


@tool(
    "trello_listas",
    "Muestra las listas (columnas) de un tablero.",
    params({"tablero": texto("Nombre del tablero")}, ["tablero"]),
)
def trello_listas(tablero):
    t = _tablero(tablero)
    return "\n".join(f"- {l['name']}" for l in _listas(t["id"]))


@tool(
    "trello_crear_tarjeta",
    "Crea una tarjeta en una lista de un tablero.",
    params(
        {
            "tablero": texto("Nombre del tablero"),
            "lista": texto("Nombre de la lista"),
            "nombre": texto("Título de la tarjeta"),
            "descripcion": texto("Descripción (opcional)"),
            "vence": texto("Fecha límite ISO, ej. 2026-10-20T17:00:00 (opcional)"),
        },
        ["tablero", "lista", "nombre"],
    ),
    risk=PELIGROSO,
)
def trello_crear_tarjeta(tablero, lista, nombre, descripcion="", vence=""):
    t = _tablero(tablero)
    destino = next(
        (l for l in _listas(t["id"]) if lista.lower() in l["name"].lower()),
        None,
    )

    if destino is None:
        raise RuntimeError(f"No encontré la lista '{lista}' en {t['name']}.")

    datos = {"idList": destino["id"], "name": nombre, "desc": descripcion}

    if vence:
        datos["due"] = datetime.fromisoformat(vence).astimezone().isoformat()

    tarjeta = _api("POST", "/cards", **datos)
    return f"Tarjeta creada: {tarjeta['name']} ({tarjeta['shortUrl']})"


@tool(
    "trello_mover_tarjeta",
    "Mueve una tarjeta (por su id) a otra lista del mismo tablero.",
    params(
        {
            "tarjeta_id": texto("Id de la tarjeta"),
            "lista": texto("Nombre de la lista destino"),
        },
        ["tarjeta_id", "lista"],
    ),
    risk=PELIGROSO,
)
def trello_mover_tarjeta(tarjeta_id, lista):
    tarjeta = _api("GET", f"/cards/{tarjeta_id}", fields="name,idBoard")
    destino = next(
        (
            l for l in _listas(tarjeta["idBoard"])
            if lista.lower() in l["name"].lower()
        ),
        None,
    )

    if destino is None:
        raise RuntimeError(f"No encontré la lista '{lista}'.")

    _api("PUT", f"/cards/{tarjeta_id}", idList=destino["id"])
    return f"'{tarjeta['name']}' movida a {destino['name']}."


@tool(
    "trello_completar_tarjeta",
    "Marca como completada la fecha de una tarjeta (por su id).",
    params({"tarjeta_id": texto("Id de la tarjeta")}, ["tarjeta_id"]),
    risk=PELIGROSO,
)
def trello_completar_tarjeta(tarjeta_id):
    tarjeta = _api("PUT", f"/cards/{tarjeta_id}", dueComplete=True)
    return f"Tarjeta completada: {tarjeta['name']}"


@tool(
    "trello_comentar",
    "Agrega un comentario a una tarjeta (por su id).",
    params(
        {"tarjeta_id": texto("Id de la tarjeta"), "texto": texto("Comentario")},
        ["tarjeta_id", "texto"],
    ),
    risk=PELIGROSO,
)
def trello_comentar(tarjeta_id, texto):
    _api("POST", f"/cards/{tarjeta_id}/actions/comments", text=texto)
    return "Comentario agregado."


TOOLS = [
    trello_tableros,
    trello_pendientes,
    trello_listas,
    trello_crear_tarjeta,
    trello_mover_tarjeta,
    trello_completar_tarjeta,
    trello_comentar,
]
