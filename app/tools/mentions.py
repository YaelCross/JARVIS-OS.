import json
import threading
from datetime import datetime

import requests

from app import config
from app.agents.tool import PELIGROSO, params, texto, tool


ARCHIVO = config.DATA_DIR / "menciones.json"
_lock = threading.Lock()


# ==================================================
# ALMACÉN DE MENCIONES
# ==================================================

def cargar():
    if not ARCHIVO.exists():
        return []

    try:
        return json.loads(ARCHIVO.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []


def guardar(menciones):
    ARCHIVO.write_text(
        json.dumps(menciones, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def agregar(mencion):
    with _lock:
        menciones = cargar()
        mencion["id"] = str(len(menciones) + 1)
        mencion["estado"] = "pendiente"
        mencion["recibida"] = datetime.now().isoformat(timespec="seconds")
        menciones.append(mencion)
        guardar(menciones)
        return mencion


def _buscar(mencion_id):
    for m in cargar():
        if m["id"] == str(mencion_id):
            return m

    raise RuntimeError(f"No existe la mención {mencion_id}.")


def _actualizar(mencion_id, **cambios):
    with _lock:
        menciones = cargar()

        for m in menciones:
            if m["id"] == str(mencion_id):
                m.update(cambios)

        guardar(menciones)


def telegram(metodo, **datos):
    if not config.TELEGRAM_BOT_TOKEN:
        raise RuntimeError("Falta TELEGRAM_BOT_TOKEN en el archivo .env.")

    respuesta = requests.post(
        f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/{metodo}",
        json=datos,
        timeout=40,
    )
    respuesta.raise_for_status()
    return respuesta.json()["result"]


# ==================================================
# HERRAMIENTAS
# ==================================================

@tool(
    "menciones_listar",
    f"Lista las menciones a {config.MENTION_HANDLE} recibidas en grupos.",
    params({"estado": texto("pendiente, atendida o todas (por defecto pendiente)")}),
)
def menciones_listar(estado="pendiente"):
    menciones = cargar()

    if estado != "todas":
        menciones = [m for m in menciones if m["estado"] == estado]

    return "\n".join(
        f"[{m['id']}] {m['recibida']} | {m['grupo']} | {m['autor']}: "
        f"{m['texto']} ({m['estado']})"
        for m in menciones[-40:]
    ) or "No hay menciones."


@tool(
    "menciones_responder",
    "Responde en el grupo al mensaje de una mención (por su id).",
    params(
        {"mencion_id": texto("Id de la mención"), "texto": texto("Respuesta")},
        ["mencion_id", "texto"],
    ),
    risk=PELIGROSO,
)
def menciones_responder(mencion_id, texto):
    m = _buscar(mencion_id)

    telegram(
        "sendMessage",
        chat_id=m["chat_id"],
        text=texto,
        reply_to_message_id=m["message_id"],
    )

    _actualizar(mencion_id, estado="atendida", respuesta=texto)
    return f"Respondí en {m['grupo']}."


@tool(
    "menciones_marcar_atendida",
    "Marca una mención como atendida sin responder.",
    params({"mencion_id": texto("Id de la mención")}, ["mencion_id"]),
)
def menciones_marcar_atendida(mencion_id):
    _buscar(mencion_id)
    _actualizar(mencion_id, estado="atendida")
    return "Mención marcada como atendida."


TOOLS = [menciones_listar, menciones_responder, menciones_marcar_atendida]
