import re
import pythoncom
import win32com.client


class Speaker:

    def __init__(self):

        self.voice_name = (
            "Microsoft Sabina Desktop - Spanish (Mexico)"
        )

        self.rate = 0
        self.volume = 100

    def say(self, text):

        print(
            "DEBUG SPEAKER 1 - Iniciando voz SAPI..."
        )

        pythoncom.CoInitialize()

        try:

            # Crear el motor de voz de Windows
            engine = win32com.client.Dispatch(
                "SAPI.SpVoice"
            )

            # Obtener voces instaladas
            voices = engine.GetVoices()

            voz_encontrada = False

            for i in range(voices.Count):

                voice = voices.Item(i)

                nombre = voice.GetDescription()

                print(
                    "DEBUG SPEAKER - Voz disponible:",
                    nombre
                )

                if (
                    "Sabina" in nombre
                    and "Spanish (Mexico)" in nombre
                ):

                    engine.Voice = voice

                    print(
                        "DEBUG SPEAKER - Voz seleccionada:",
                        nombre
                    )

                    voz_encontrada = True

                    break

            if not voz_encontrada:

                print(
                    "ERROR SPEAKER - No se encontró Sabina."
                )

                return

            # Configuración de voz
            engine.Rate = self.rate
            engine.Volume = self.volume

            # Limpiar espacios innecesarios
            text = re.sub(
                r"\s+",
                " ",
                text
            ).strip()

            # Pausas naturales
            text = text.replace(
                ". ",
                "... "
            )

            text = text.replace(
                "? ",
                "?... "
            )

            text = text.replace(
                "! ",
                "!... "
            )

            print(
                "DEBUG SPEAKER 2 - Hablando:",
                text
            )

            # Hablar
            engine.Speak(text)

            print(
                "DEBUG SPEAKER 3 - Voz terminada"
            )

        except Exception as e:

            print(
                "ERROR SPEAKER:",
                repr(e)
            )

        finally:

            pythoncom.CoUninitialize() 