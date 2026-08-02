import cv2
import face_recognition as fr
import numpy as np
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import pickle

class RegisterScreen(FloatLayout):
    def __init__(self, app, connection, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.connection = connection
        self.capturado = False
        self.codigo_cara = None

        # Título
        logo_layout = BoxLayout(orientation='vertical',
                                size_hint=(None, None),
                                size=(400, 300),
                                pos_hint={'center_x': 0.5, 'center_y': 0.8})
        logo_layout.add_widget(Image(source="iconos/Logo.png"))
        self.add_widget(logo_layout)
        self.add_widget(Label(text="Crear cuenta",
                              font_size=30,
                              font_name="Roboto-Bold",
                              color=(0, 0, 0, 1),
                              pos_hint={'center_x': 0.5, 'center_y': 0.57}))

        # Inputs
        input_layout = BoxLayout(orientation='vertical',
                                 spacing=10,
                                 size_hint=(None, None),
                                 size=(400, 175),
                                 pos_hint={'center_x': 0.3, 'center_y': 0.4})
        self.input_nuevo_nombre = TextInput(hint_text="Nombre de usuario",
                                            font_size=30,
                                            size=(400, 50),
                                            multiline=False)
        self.input_nueva_contraseña = TextInput(hint_text="Contraseña",
                                                font_size=30,
                                                size=(400, 50),
                                                password=True,
                                                multiline=False)
        self.input_confirmar_contraseña = TextInput(hint_text="Confirmar contraseña",
                                                    font_size=30,
                                                    size=(400, 50),
                                                    password=True,
                                                    multiline=False)
        input_layout.add_widget(self.input_nuevo_nombre)
        input_layout.add_widget(self.input_nueva_contraseña)
        input_layout.add_widget(self.input_confirmar_contraseña)
        self.add_widget(input_layout)

        #Camara
        self.boton_capturar = Button(background_normal='iconos/foto.png',
                                     size=(75, 75),
                                     size_hint=(None, None),
                                     font_size=20,
                                     pos_hint={'center_x': 0.8, 'center_y': 0.4},
                                     on_press=self.capturar_cara)
        self.add_widget(self.boton_capturar)
        self.camara()

        button_layout = BoxLayout(orientation='vertical',
                                  spacing=5,
                                  size_hint=(None, None),
                                  size=(600, 110),
                                  pos_hint={'center_x': 0.5, 'center_y': 0.2})

        # Botón para Crear Cuenta
        self.boton_crear = Button(text="Crear cuenta",
                                  font_size=30,
                                  size_hint_x=0.8,
                                  size_hint_y=None,
                                  height=50,
                                  pos_hint={'center_x': 0.5})
        self.boton_crear.bind(on_press=self.crear_cuenta)
        button_layout.add_widget(self.boton_crear)

        # Botón para volver atrás
        self.boton_volver = Button(text="Volver",
                                   font_size=20,
                                   size_hint_x=0.5,
                                   size_hint_y=None,
                                   height=40,
                                   pos_hint={'center_x': 0.5},
                                   on_press=lambda x: self.volver())
        button_layout.add_widget(self.boton_volver)

        self.add_widget(button_layout)

        # Aviso de error
        self.warn = Label(text="",
                          font_size=20,
                          pos_hint={'center_x': 0.5, 'center_y': 0.275},
                          color=(1, 0, 0, 1))
        self.add_widget(self.warn)

    ###########################################################################################################################

    def crear_cuenta(self, instance):
        nombre = self.input_nuevo_nombre.text
        contraseña = self.input_nueva_contraseña.text
        confirmar_contraseña = self.input_confirmar_contraseña.text
        resultado = False

        # Busca en la BD usuarios con el mismo nombre
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT * FROM usuarios WHERE username = :1", (nombre,))
                resultado = cursor.fetchone()
        except Exception as e:
            print("Error al buscar la cuenta:", e)

        # Si hay un usuario con el mismo nombre da error
        if resultado:
            self.warn.text = "* Nombre de usuario no disponible"
            Clock.schedule_once(lambda dt: self.borrar_mensaje(), 3)
            return

        # Si no se han rellenado todos los campos da error
        if not nombre or not contraseña or not confirmar_contraseña:
            self.warn.text = "* Debes rellenar todos los campos"
            Clock.schedule_once(lambda dt: self.borrar_mensaje(), 3)
            return

        # Si las contraseñas no coinciden da error
        if contraseña != confirmar_contraseña:
            self.warn.text = "* Las contraseñas no coinciden"
            Clock.schedule_once(lambda dt: self.borrar_mensaje(), 3)
            return

        # Si todo es correcto realiza la inserción en la BD
        try:
            with self.connection.cursor() as cursor:
                cara_serializada = pickle.dumps(self.codigo_cara)

                cursor.execute("INSERT INTO usuarios (USERNAME, PASSWORD, FACE) VALUES (:username, :password, :face)",
                               {'username': nombre, 'password': contraseña,'face': cara_serializada})
                self.connection.commit()
                print("Cuenta creada con éxito")
                self.webcam.release()
                self.app.mostrar_pantalla_inicio()
        except Exception as e:
            print("Error al crear la cuenta:", e)

    ###########################################################################################################################

    # Captura el frma en el que se detectó la cara y guarda los datos de esta
    def capturar_cara(self, instance):
        ret, frame = self.webcam.read()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        ubicaciones = fr.face_locations(frame_rgb)

        if ubicaciones:
            self.capturado = True
            self.codigo_cara = fr.face_encodings(frame_rgb, known_face_locations = ubicaciones)[0]
            self.buscar_cara()
        else:
            self.warn.text = "* Cara no capturada"
            # Borra el mensaje de aviso de error tras 3 segundos de visualización
            Clock.schedule_once(lambda dt: self.borrar_mensaje(), 3)

    ###########################################################################################################################

    def camara(self):
        self.image = Image(size = (200, 200),
                           size_hint=(None, None),
                           pos_hint={'center_x': 0.65, 'center_y': 0.4})
        self.add_widget(self.image)

        # Iniciar la captura de video preferentemente con id 2
        self.webcam = cv2.VideoCapture(2, cv2.CAP_ANY)

        # En caso de no estar conectada la camara por usb usa la webcam del portátil
        if not self.webcam.isOpened():
            self.webcam = cv2.VideoCapture(0, cv2.CAP_ANY)

        # Programar la actualización del frame cada 1/30 segundos (30 fps)
        Clock.schedule_interval(self.update, 1.0 / 30.0)

    ###########################################################################################################################

    def update(self, dt):
        if self.capturado == False:
            ret, frame = self.webcam.read()
            if not ret:
                return

            # Convertir el frame de BGR (OpenCV) a RGB (Kivy)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Voltear la imagen horizontalmente (modo espejo)
            frame = cv2.flip(frame, 1)

            # Voltear la imagen verticalmente
            frame = cv2.flip(frame, 0)  # 0 indica que se voltea verticalmente

            # Crear una textura a partir del frame
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
            texture.blit_buffer(frame.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
            self.image.texture = texture

    ###########################################################################################################################

    # Borra el mensaje de aviso de error
    def borrar_mensaje(self):
        self.warn.text = ""

    ###########################################################################################################################

    # Libera la cámara y vuelve al menu inicial de inicio de sesión
    def volver(self):
        print("Liberando cámara...")
        self.webcam.release()
        self.app.mostrar_pantalla_inicio()

    ###########################################################################################################################

    # Busca coincidencias en la BD con la cara capturada
    def buscar_cara(self):
        vector_caras = []

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT FACE FROM USUARIOS")
                caras = cursor.fetchall()

                for cara in caras:
                    encoding = pickle.loads(cara[0].read())
                    vector_caras.append(encoding)

                resultado = fr.compare_faces(vector_caras, self.codigo_cara)

                # Verificamos si hay alguna coincidencia
                if np.any(resultado):
                    self.warn.text = "* Cara ya registrada"
                    self.capturado = False

                    # Borra el mensaje de aviso de error tras 3 segundos de visualización
                    Clock.schedule_once(lambda dt: self.borrar_mensaje(), 3)
                    return True

        except Exception as e:
            print("Error", e)

        return False  # Si no se encontró ninguna coincidencia

    ###########################################################################################################################