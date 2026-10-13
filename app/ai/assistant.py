import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class Assistant:

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "No se encontró OPENAI_API_KEY en el archivo .env"
            )

        self.client = OpenAI(api_key=api_key)

    def ask(self, question):

        response = self.client.responses.create(
            model="gpt-5",
            instructions=(
                "Eres JARVIS, el asistente personal de Yael. "
                "Hablas siempre en español. "
                "Eres profesional, elegante, claro y directo. "
                "Ayudas a Yael de forma práctica."
            ),
            input=question
        )

        return response.output_text