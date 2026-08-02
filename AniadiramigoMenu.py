from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.clock import Clock

class AniadirAmigoMenu(FloatLayout):
    def __init__(self, app, username, connection, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.username = username
        self.connection = connection

        # Rectangulo transparente sobre el que situamos el menu actual
        with self.canvas.before:
            Color(0.859, 1.0, 0.988, 0.8)  # Azul con 80% de opacidad
            self.rect = Rectangle(pos=self.pos,
                                  size=(300, 400),
                                  size_hint=(None, None),
                                  pos_hint={'center_x': 0.5, 'center_y': 0.9})

        # Titulo
        self.titulo = Label(text="AÑADIR AMIGO",
                            font_name="Roboto-Bold",
                            font_size=30,
                            pos_hint={'center_x': 0.13, 'center_y': 0.35},
                            color=(0, 0, 0, 1))
        self.add_widget(self.titulo)
        self.add_grupo_spinner()

    ###########################################################################################################################

    #Crea una caja de seleccion de opciones para el selector del grupo donde se añadirá el nuevo amigo
    def add_grupo_spinner(self):
        self.campos_layout = BoxLayout(orientation='vertical',
                                  spacing=10,
                                  size_hint=(None, None),
                                  size=(250, 200),
                                  pos_hint={'center_x': 0.13, 'center_y': 0.18})

        self.input_nombre = TextInput(hint_text="Nombre de usuario",
                                      font_size=20,
                                      multiline=False)
        self.campos_layout.add_widget(self.input_nombre)

        #Caja de elección
        self.spinner = Spinner(text='Seleccionar grupo',
                               background_normal='',
                               background_color=(1, 1, 1, 1),
                               font_size=20,
                               color=(0, 0, 0, 1))

        #Mensaje de aviso sobre algún error en la introducción de la información, se inicializa en blanco
        self.warn = Label(text="",
                          font_size=15,
                          pos_hint={'center_x': 0.5, 'center_y': 0.32},
                          color=(1, 0, 0, 1))

        self.boton_guardar = Button(text="Guardar",
                                    size_hint=(None, None),
                                    size=(200, 40),
                                    pos_hint={'center_x': 0.5})
        self.boton_guardar.bind(on_press=self.aniadir_amigo)

        #Se añaden los grupos posibles a la caja de elección
        self.actualizar_opciones()

        self.add_widget(self.campos_layout)

    ###########################################################################################################################

    #Añade el nuevo amigo con la información introducida a la base de datos
    def aniadir_amigo(self, instance):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT USERNAME FROM USUARIOS WHERE USERNAME = :username",
                           {'username': self.input_nombre.text})
            user_1 = cursor.fetchone()

            if not user_1 or self.input_nombre.text == self.username:
                self.warn.text = "Usuario no válido"
            else:
                cursor.execute("SELECT USUARIO_MIEMBRO FROM GRUPO_USUARIOS WHERE USUARIO_MIEMBRO = :miembro AND USUARIO_PROPIETARIO = :propietario",
                               {'miembro': self.input_nombre.text, 'propietario': self.username})
                user = cursor.fetchone()

                if not user:
                    if (self.spinner.text != "Seleccionar grupo") and (self.input_nombre.text != ""):
                        cursor.execute("INSERT INTO GRUPO_USUARIOS (USUARIO_PROPIETARIO, USUARIO_MIEMBRO, NOMBRE_GRUPO) VALUES (:propietario, :miembro, :grupo)",
                                       {'propietario': self.username, 'miembro': self.input_nombre.text, 'grupo': self.spinner.text})
                        self.connection.commit()
                        self.app.actualizar_contenido()
                        self.warn.text = "Guardado correctamente"

                        # Borra el mensaje de aviso de error tras 3 segundos de visualización
                        Clock.schedule_once(lambda dt: self.borrar_mensaje(), 3)

                        self.input_nombre.text = ""

                    else:
                        self.warn.text = "Usuario o grupo no seleccionado"
                else:
                    self.warn.text = "Usuario ya guardado en un grupo"

    ###########################################################################################################################

    #Borra el mensaje de aviso de error
    def borrar_mensaje(self):
        self.warn.text = ""

    ###########################################################################################################################

    #Actualiza los valores de la caja de elección de grupo
    def actualizar_opciones(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT NOMBRE_GRUPO FROM GRUPOS_PERSONALIZADOS WHERE USUARIO_PROPIETARIO = :username",
                           {'username': self.username})
            grupos = [row[0] for row in cursor.fetchall()]

        #Eliminamos todos los elementos para que al volver a añadir la caja de elección, se muestren en el mismo orden
        self.campos_layout.remove_widget(self.spinner)
        self.campos_layout.remove_widget(self.boton_guardar)
        self.campos_layout.remove_widget(self.warn)
        self.spinner.values = grupos
        self.campos_layout.add_widget(self.spinner)
        self.campos_layout.add_widget(self.boton_guardar)
        self.campos_layout.add_widget(self.warn)

    ###########################################################################################################################

