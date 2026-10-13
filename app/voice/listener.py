import speech_recognition as sr


class Listener:

    def __init__(self):
        self.recognizer = sr.Recognizer()

    def listen(self):
        with sr.Microphone() as source:

            print("🎤 Escuchando...")

            self.recognizer.adjust_for_ambient_noise(source, duration=1)

            audio = self.recognizer.listen(source)

        try:

            texto = self.recognizer.recognize_google(
                audio,
                language="es-MX"
            )

            print("Tú dijiste:", texto)

            return texto

        except sr.UnknownValueError:
            print("No entendí lo que dijiste.")
            return ""

        except sr.RequestError:
            print("Error de conexión con el servicio de reconocimiento.")
            return ""