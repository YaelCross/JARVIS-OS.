import json
import mimetypes
import os
import uuid
from urllib import error, request

from dotenv import load_dotenv


load_dotenv()


class WhatsAppError(Exception):
    pass


class WhatsApp:
    """
    Cliente de WhatsApp Business Cloud API (Meta Graph API).

    Operaciones (las mismas del nodo de n8n):
        Mensajes: send_text, send_template
        Media:    upload_media, download_media, delete_media
    """

    def __init__(self):
        self.token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.default_to = os.getenv("WHATSAPP_DEFAULT_TO")
        self.api_version = os.getenv("WHATSAPP_API_VERSION", "v23.0")

        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    def is_configured(self):
        return bool(self.token and self.phone_number_id)

    # ==========================================
    # HTTP
    # ==========================================

    def _request(self, method, url, body=None, headers=None, raw=False):

        if not self.is_configured():
            raise WhatsAppError(
                "Faltan WHATSAPP_ACCESS_TOKEN o "
                "WHATSAPP_PHONE_NUMBER_ID en el archivo .env"
            )

        all_headers = {"Authorization": f"Bearer {self.token}"}
        all_headers.update(headers or {})

        req = request.Request(
            url,
            data=body,
            headers=all_headers,
            method=method
        )

        try:
            with request.urlopen(req, timeout=30) as response:
                data = response.read()

        except error.HTTPError as e:
            detalle = e.read().decode("utf-8", errors="replace")
            raise WhatsAppError(
                f"WhatsApp API error {e.code}: {detalle}"
            ) from e

        except error.URLError as e:
            raise WhatsAppError(
                f"No se pudo conectar con WhatsApp: {e.reason}"
            ) from e

        if raw:
            return data

        return json.loads(data or b"{}")

    def _post_json(self, path, payload):
        return self._request(
            "POST",
            f"{self.base_url}/{path}",
            body=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

    def _recipient(self, to):
        destino = to or self.default_to

        if not destino:
            raise WhatsAppError(
                "No hay destinatario. Indique un número o "
                "configure WHATSAPP_DEFAULT_TO en el archivo .env"
            )

        # Formato internacional sin "+", espacios ni guiones.
        return "".join(c for c in destino if c.isdigit())

    # ==========================================
    # MENSAJES
    # ==========================================

    def send_text(self, text, to=None, preview_url=False):
        """
        Envía un mensaje de texto libre.

        Meta solo permite texto libre dentro de la ventana de
        24 horas desde el último mensaje del usuario; fuera de
        ella hay que usar send_template.
        """

        return self._post_json(
            f"{self.phone_number_id}/messages",
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": self._recipient(to),
                "type": "text",
                "text": {
                    "body": text,
                    "preview_url": preview_url
                }
            }
        )

    def send_template(
        self,
        template_name,
        to=None,
        language="es_MX",
        parameters=None
    ):
        """
        Envía una plantilla aprobada en WhatsApp Manager.
        `parameters` es una lista de textos para {{1}}, {{2}}...
        del cuerpo de la plantilla.
        """

        template = {
            "name": template_name,
            "language": {"code": language}
        }

        if parameters:
            template["components"] = [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": str(p)}
                        for p in parameters
                    ]
                }
            ]

        return self._post_json(
            f"{self.phone_number_id}/messages",
            {
                "messaging_product": "whatsapp",
                "to": self._recipient(to),
                "type": "template",
                "template": template
            }
        )

    # ==========================================
    # MEDIA
    # ==========================================

    def upload_media(self, file_path, mime_type=None):
        """Sube un archivo y devuelve su media_id."""

        mime_type = (
            mime_type
            or mimetypes.guess_type(file_path)[0]
            or "application/octet-stream"
        )

        with open(file_path, "rb") as f:
            contenido = f.read()

        boundary = uuid.uuid4().hex
        nombre = os.path.basename(file_path)

        partes = [
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="messaging_product"'
            "\r\n\r\nwhatsapp\r\n",
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="type"'
            f"\r\n\r\n{mime_type}\r\n",
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="file"; '
            f'filename="{nombre}"\r\n'
            f"Content-Type: {mime_type}\r\n\r\n",
        ]

        body = (
            "".join(partes).encode("utf-8")
            + contenido
            + f"\r\n--{boundary}--\r\n".encode("utf-8")
        )

        respuesta = self._request(
            "POST",
            f"{self.base_url}/{self.phone_number_id}/media",
            body=body,
            headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}"
            }
        )

        return respuesta["id"]

    def download_media(self, media_id, output_path):
        """Descarga un archivo por su media_id y lo guarda en disco."""

        info = self._request("GET", f"{self.base_url}/{media_id}")

        contenido = self._request("GET", info["url"], raw=True)

        with open(output_path, "wb") as f:
            f.write(contenido)

        return output_path

    def delete_media(self, media_id):
        return self._request("DELETE", f"{self.base_url}/{media_id}")
