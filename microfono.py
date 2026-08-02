import speech_recognition as sr

class Microfono:
    def __init__(self):
        self.r = sr.Recognizer()
        self.audio = None

    def capturar_audio(self):
        with sr.Microphone() as source:
            self.r.adjust_for_ambient_noise(source)
            print("¡Di algo!")
            self.audio = self.r.listen(source, phrase_time_limit=5)
            print("Audio capturado.")

    def devolver_audio(self):
        texto = ""

        try:
            # Se llama a recognize_google con el audio capturado y se especifica 'es-ES' para el idioma español
            texto = self.r.recognize_google(self.audio, language='es-ES')
            # Si se reconoce el audio, se imprime el texto transcrito
            print("Google Speech Recognition cree que dijiste:", texto)
        except sr.UnknownValueError:
            # Esta excepción se captura cuando el servicio no logra interpretar el audio
            print("Google Speech Recognition no pudo entender el audio")
        except sr.RequestError as e:
            # Esta excepción se maneja en caso de errores en la solicitud (ej. problemas de conectividad)
            print("No se pudieron solicitar resultados del servicio de Google Speech Recognition; {0}".format(e))

        return texto
