import threading
import time
from datetime import date, datetime, timedelta, timezone

from app import config
from app.core.notifications import notifications
from app.tools import mentions, trello


# ==================================================
# MENCIONES EN GRUPOS DE TELEGRAM
# ==================================================

class MentionWatcher(threading.Thread):
    """Escucha los grupos donde está el bot y avisa cuando
    alguien escribe la mención configurada (ej. @YaelCS)."""

    def __init__(self):
        super().__init__(daemon=True, name="MentionWatcher")
        self.offset = None
        self.handle = config.MENTION_HANDLE.lower()

    def run(self):
        print(f"[Vigilante] Menciones a {config.MENTION_HANDLE} activas.")

        while True:
            try:
                self.poll()
            except Exception as e:
                print("[Vigilante] Error de Telegram:", repr(e))
                time.sleep(15)

    def poll(self):
        datos = {"timeout": 30, "allowed_updates": ["message"]}

        if self.offset is not None:
            datos["offset"] = self.offset

        for update in mentions.telegram("getUpdates", **datos):
            self.offset = update["update_id"] + 1
            mensaje = update.get("message") or {}
            texto = mensaje.get("text") or mensaje.get("caption") or ""

            if self.handle not in texto.lower():
                continue

            chat = mensaje.get("chat", {})
            autor = mensaje.get("from", {})

            mencion = mentions.agregar({
                "grupo": chat.get("title") or chat.get("username") or "chat privado",
                "chat_id": chat.get("id"),
                "message_id": mensaje.get("message_id"),
                "autor": (
                    autor.get("first_name", "")
                    + (f" (@{autor['username']})" if autor.get("username") else "")
                ).strip(),
                "texto": texto,
            })

            notifications.notify(
                "menciones",
                f"Señor {config.USER_NAME}, lo mencionaron en "
                f"{mencion['grupo']}. {mencion['autor']} dice: {texto[:200]}",
            )


# ==================================================
# PENDIENTES DE TRELLO
# ==================================================

class TrelloWatcher(threading.Thread):
    """Revisa Trello cada cierto tiempo y avisa de tarjetas
    vencidas o que vencen en las próximas 24 horas."""

    def __init__(self, minutes):
        super().__init__(daemon=True, name="TrelloWatcher")
        self.interval = minutes * 60
        # (id de tarjeta, día) ya avisados, para no repetir
        self.avisadas = set()

    def run(self):
        print(f"[Vigilante] Trello cada {self.interval // 60} minutos.")

        while True:
            try:
                self.check()
            except Exception as e:
                print("[Vigilante] Error de Trello:", repr(e))

            time.sleep(self.interval)

    def check(self):
        ahora = datetime.now(timezone.utc)
        limite = ahora + timedelta(hours=24)
        hoy = date.today()

        vencidas, proximas = [], []

        for c in trello.pendientes():
            vence = trello._fecha(c["vence"])

            if not vence or (c["id"], hoy) in self.avisadas:
                continue

            if vence < ahora:
                vencidas.append(c["tarjeta"])
            elif vence <= limite:
                proximas.append(c["tarjeta"])
            else:
                continue

            self.avisadas.add((c["id"], hoy))

        partes = []

        if vencidas:
            partes.append(
                f"{len(vencidas)} pendientes vencidos: " + ", ".join(vencidas[:5])
            )

        if proximas:
            partes.append(
                f"{len(proximas)} vencen en las próximas 24 horas: "
                + ", ".join(proximas[:5])
            )

        if partes:
            notifications.notify("trello", "En Trello tiene " + ". ".join(partes) + ".")


def start_watchers():
    activos = []

    if config.TELEGRAM_BOT_TOKEN:
        watcher = MentionWatcher()
        watcher.start()
        activos.append("menciones")

    if trello.configurado() and config.TRELLO_CHECK_MINUTES > 0:
        watcher = TrelloWatcher(config.TRELLO_CHECK_MINUTES)
        watcher.start()
        activos.append("trello")

    return activos
