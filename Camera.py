import cv2
import pickle
import face_recognition as fr
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.uix.scrollview import ScrollView
import threading
import time

class Camera(FloatLayout):
    def __init__(self, connection, username, **kwargs):
        super().__init__(**kwargs)
        self.lock = threading.Lock()
        self.connection = connection
        self.username = username
        self.red = cv2.dnn.readNetFromCaffe("dnn/deploy.prototxt", "dnn/res10_300x300_ssd_iter_140000.caffemodel")

        # Vectores de almacenamiento de info de los usuarios
        self.vector_caras = []
        self.nombres = []
        self.detalles = []
        self.colores = []
        self.indice_actual = -1
        self.ultimo_indice = -1
        self.cargar_caras()

        self.nombre_actual = ""
        self.ultimo_nombre = ""
        self.contador_sindetectar = 0
        self.frames_restantes = 0
        self.last_db_query_time = 0
        self.query_interval = 1  # segundos entre consultas
        self.consulta_en_curso = False
        self.num_frames = 0

        # Crear el widget Image para mostrar la cámara
        self.image = Image(size=self.size)
        self.add_widget(self.image)

        # Iniciar la captura de video preferentemente con id 2
        self.webcam = cv2.VideoCapture(2, cv2.CAP_ANY)

        # En caso de no estar conectada la camara por usb usa la webcam del portátil
        if not self.webcam.isOpened():
            self.webcam = cv2.VideoCapture(0, cv2.CAP_ANY)

        if self.webcam.isOpened():
            # Programar la actualización del frame cada 1/30 segundos (30 fps)
            Clock.schedule_interval(self.update, 1.0 / 30.0)
        else:
            print("Error al iniciar la cámara")

        # Rectángulo transparente sobre el que situamos el menu actual
        with self.canvas.before:
            Color(0.859, 1.0, 0.988, 0.8)  # Azul con 80% de opacidad
            self.rect = Rectangle(size=(300, 250),
                                  size_hint=(None, None),
                                  pos=(800, 500))

        # Cuadro de texto scrolleable donde se muestra la lista de grupos y amigos
        self.scrollview = ScrollView(size_hint=(0.4, 0.5),
                                     pos_hint={'center_x': 0.85, 'center_y': 0.6})

        self.info = Label(text="",
                          font_size=20,
                          color=(0, 0, 0, 1),
                          size_hint_y=None)
        self.info.bind(texture_size=self.info.setter('size'))

        self.scrollview.add_widget(self.info)
        self.add_widget(self.scrollview)

    ###########################################################################################################################

    def update(self, dt):
        ret, frame = self.webcam.read()

        if not ret:
            return

        # Convertir el frame a formato RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Voltear la imagen horizontalmente
        frame = cv2.flip(frame, 1)

        # Llamada a la función de reconocimiento de caras
        frame = self.reconocimiento(frame)

        # Voltear la imagen verticalmente
        frame = cv2.flip(frame, 0)  # 0 indica que se voltea verticalmente

        # Redimensionar el frame al tamaño de la ventana
        frame = cv2.resize(frame, (self.image.width, self.image.height))

        # Crear la textura
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
        texture.blit_buffer(frame.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
        self.image.texture = texture

    ############################################################################################################################

    # Reconocimiento de una sola cara
    def reconocimiento(self, imagen):
        imagen_entrada = cv2.dnn.blobFromImage(imagen, size=(300, 300))
        self.red.setInput(imagen_entrada)
        salida = self.red.forward()

        h, w, _ = imagen.shape
        cara_detectada = False
        nombre = self.nombre_actual  # por defecto usamos el último

        for cara in salida[0][0]:
            if cara[2] > 0.5:
                c1 = (int(w * cara[3]), int(h * cara[6]))
                c2 = (int(w * cara[5]), int(h * cara[4]))

                if nombre == "" or self.num_frames == 15:
                    now = time.time()
                    if (now - self.last_db_query_time > self.query_interval) and (not self.consulta_en_curso):
                        self.last_db_query_time = now
                        self.consulta_en_curso = True
                        threading.Thread(target=self.actualizar_info, args=(imagen,), daemon=True).start()
                    self.num_frames = 0
                else:
                    self.num_frames += 1

                if self.indice_actual != -1 or self.contador_sindetectar < 200:
                    self.indice_actual = self.ultimo_indice
                    self.contador_sindetectar += 1
                    # Calcular centro horizontal de la cara
                    centro_x = c1[0] + (c2[0] - c1[0]) // 2
                    altura_rostro = abs(c2[1] - c1[1])
                    escala_texto = max(0.5, min(2.0, altura_rostro / 150))  # límites entre 0.5 y 2.0

                    # Calcular tamaño del texto
                    (texto_ancho, texto_alto), _ = cv2.getTextSize(self.nombres[self.indice_actual], cv2.FONT_HERSHEY_SIMPLEX,escala_texto, 2)

                    # Nueva posición centrada arriba del rectángulo
                    texto_pos = (centro_x - texto_ancho // 2, c1[1] - 220)

                    # Buscar color
                    color = self.colores[self.indice_actual]

                    # Elegir color según el nombre
                    colores_bgr = {"Rojo": (0, 0, 255),
                                   "Azul": (255, 0, 0),
                                   "Amarillo": (0, 255, 255),
                                   "Verde": (0, 255, 0),
                                   "Gris": (169, 169, 169)}

                    color_bgr = colores_bgr.get(color, (169, 169, 169))

                    # Dibujar rectángulo y texto
                    cv2.rectangle(imagen, c1, c2, color_bgr, 3)
                    cv2.putText(imagen, self.nombres[self.indice_actual], texto_pos, cv2.FONT_HERSHEY_SIMPLEX, escala_texto, color_bgr, 2,cv2.LINE_AA)

                    # Si la cara está cerca, mostrar los detalles del usuario
                    if escala_texto >= 1.5:
                        escala_texto_detalles = escala_texto * 0.5
                        for i, linea in enumerate(self.detalles[self.indice_actual]):
                            offset_y = texto_alto + 5  # separación entre líneas
                            posicion = (c2[0] + 10, c1[1] - 275 + (i + 1) * offset_y)
                            cv2.putText(imagen, linea, posicion, cv2.FONT_HERSHEY_SIMPLEX, escala_texto_detalles, color_bgr, 2, cv2.LINE_AA)


        return imagen

    ###########################################################################################################################

    def buscar_cara(self, cara):
        indice = -1
        try:
            resultado = fr.compare_faces(self.vector_caras, cara, tolerance=0.6)
            for i, match in enumerate(resultado):
                if match:
                    return i
        except Exception as e:
            print("Error en buscar_cara:", e)

        return indice

    ###########################################################################################################################

    # Carga en los vectores toda la información de los usuarios de la base de datos
    def cargar_caras(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT USERNAME, FACE FROM USUARIOS")
                resultados = cursor.fetchall()
                for nombre, face_blob in resultados:
                    encoding = pickle.loads(face_blob.read())
                    self.vector_caras.append(encoding)
                    self.nombres.append(nombre)
                    self.detalles.append(self.obtener_detalles(nombre))
                    self.colores.append(self.buscar_color(nombre))
        except Exception as e:
            print("Error al cargar las caras:", e)

    ###########################################################################################################################

    # Devuelve toda la información detallada de los usuarios de la base de datos
    def obtener_detalles(self, nombre):
        texto_detalles = []

        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT USERNAME, NOMBRE, APELLIDO, EDAD, INSTAGRAM, CIUDAD, TELEFONO FROM USUARIOS WHERE USERNAME = :nombre",
                {'nombre': nombre})
            resultados = cursor.fetchone()

            if resultados:
                texto_detalles.append(f"Usuario: {resultados[0]}")
                texto_detalles.append(f"Nombre: {resultados[1]}")
                texto_detalles.append(f"Apellido: {resultados[2]}")
                texto_detalles.append(f"Edad: {resultados[3]}")
                texto_detalles.append(f"Instagram: {resultados[4]}")
                texto_detalles.append(f"Ciudad: {resultados[5]}")
                texto_detalles.append(f"Telefono: {resultados[6]}")
            else:
                texto_detalles.append("No encontrado")

        return texto_detalles

    ###########################################################################################################################

    # Devuelve los colores asociados a cada grupo según el usuario activo
    def buscar_color(self, nombre):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT NOMBRE_GRUPO FROM GRUPO_USUARIOS WHERE USUARIO_PROPIETARIO = :name AND USUARIO_MIEMBRO = :amigo",
                            {'name': str(self.username), 'amigo': str(nombre)})
            resultados = cursor.fetchone()

            if resultados:
                cursor.execute("SELECT COLOR FROM GRUPOS_PERSONALIZADOS WHERE USUARIO_PROPIETARIO = :nombre AND NOMBRE_GRUPO = :grupo",
                                {'nombre': str(self.username), 'grupo': str(resultados[0])})
                resultados = cursor.fetchone()
            else:
                return "Gris"

            return str(resultados[0])

    ###########################################################################################################################

    def stop_camera(self):
        print("Liberando cámara...")
        self.webcam.release()

    ###########################################################################################################################

    # Actualiza la información mostrada sobre la cara del usuario seleccionado
    def actualizar_info(self, image):
        nombre = ""
        try:
            small_frame = cv2.resize(image, (0, 0), fx=1, fy=1)
            small_frame = cv2.cvtColor(small_frame, cv2.COLOR_RGB2BGR)
            ubicaciones = fr.face_locations(small_frame)
            encodings = fr.face_encodings(small_frame, known_face_locations=ubicaciones)

            if len(encodings) > 0:
                self.indice_actual = self.buscar_cara(encodings[0])
                if self.indice_actual != -1:
                    nombre = self.nombres[self.indice_actual]
                    self.ultimo_indice = self.indice_actual
                    self.contador_sindetectar = 0
                else:
                    nombre = ""

                if nombre != "":
                    if nombre != self.nombre_actual:
                        self.nombre_actual = nombre

                self.frames_restantes = 60
        except Exception as e:
            print("Error procesando la cara:", e)

        self.consulta_en_curso = False

    ###########################################################################################################################



