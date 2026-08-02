from RegisterScreen import RegisterScreen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from Camera import Camera
from CameraScreen import CameraScreen
from kivy.uix.image import Image

class LoginScreen(FloatLayout):
    def __init__(self, app, connection, **kwargs):
        super().__init__(**kwargs)
        self.connection = connection
        self.app = app
        self.camera_widget = None

        # Título
        logo_layout = BoxLayout(orientation='vertical',
                                size_hint=(None, None),
                                size=(1000, 300),
                                pos_hint={'center_x': 0.5, 'center_y': 0.7})
        logo_layout.add_widget(Image(source="iconos/Logo.png"))
        self.add_widget(logo_layout)

        # Inputs
        input_layout = BoxLayout(orientation='vertical',
                                 spacing=10,
                                 size_hint=(None, None),
                                 size=(400, 105),
                                 pos_hint={'center_x': 0.5, 'center_y': 0.4})
        self.input_nombre = TextInput(hint_text="Nombre de usuario",
                                      font_size=30,
                                      size=(400, 50),
                                      multiline=False)
        self.input_contrasenia = TextInput(hint_text="Contraseña",
                                           font_size=30,
                                           size=(400, 50),
                                           password=True,
                                           multiline=False)
        input_layout.add_widget(self.input_nombre)
        input_layout.add_widget(self.input_contrasenia)
        self.add_widget(input_layout)

        # Botones
        button_layout = BoxLayout(orientation='vertical',
                                  spacing=5,
                                  size_hint=(None, None),
                                  size=(600, 110),
                                  pos_hint={'center_x': 0.5, 'center_y': 0.2},)
        self.boton_iniciar = Button(text="Iniciar sesión",
                                    font_size=30,
                                    size_hint_x=0.8,
                                    size_hint_y=None,
                                    height=50,
                                    pos_hint={'center_x': 0.5},
                                    on_press=self.comprobar_cuenta)
        self.boton_crear = Button(text="Crear cuenta",
                                  font_size=20,
                                  size_hint_x=0.5,
                                  size_hint_y=None,
                                  height=40,
                                  pos_hint={'center_x': 0.5},
                                  on_press=self.mostrar_pantalla_crear_cuenta)
        button_layout.add_widget(self.boton_iniciar)
        button_layout.add_widget(self.boton_crear)
        self.add_widget(button_layout)

        # Aviso de error
        self.warn = Label(text="",
                          font_size=20,
                          pos_hint={'center_x': 0.5, 'center_y': 0.32},
                          color=(1, 0, 0, 1))
        self.add_widget(self.warn)

    ###########################################################################################################################

    # Comprueba si los datos introducidos corresponden a una cuenta existente
    def comprobar_cuenta(self, instance):
        nombre = self.input_nombre.text
        contrasenia = self.input_contrasenia.text
        resultado = False

        if not nombre or not contrasenia:
            self.warn.text = "* Debes rellenar todos los campos"
            return

        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM usuarios WHERE username = :1 AND password = :2",
                           (nombre, contrasenia))
            resultado = cursor.fetchone()

        # Si encuentra una coincidencia en la BD accede a la aplicación
        if resultado:
            self.clear_widgets()
            layout = FloatLayout()
            self.camera_widget = Camera(self.connection, nombre)
            layout.add_widget(self.camera_widget)
            self.add_widget(layout)
            self.add_widget(CameraScreen(self, nombre, self.connection))
        else:
            self.warn.text = "* Usuario o contraseña incorrectos"

    ###########################################################################################################################

    # Elimina el contenido actual y muestra la pantalla de creación de una nueva cuenta
    def mostrar_pantalla_crear_cuenta(self, *args):
        self.clear_widgets()
        self.add_widget(RegisterScreen(self, self.connection))

    ###########################################################################################################################

    # Elimina el contenido actual y entra en la aplicación, mostrando la camara
    def mostrar_pantalla_inicio(self, *args):
        self.clear_widgets()
        if self.camera_widget:
            self.camera_widget.stop_camera()
        self.app.mostrar_pantalla_inicio()

    ###########################################################################################################################
