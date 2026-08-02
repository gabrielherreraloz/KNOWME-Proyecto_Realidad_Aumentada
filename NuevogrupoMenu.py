from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.clock import Clock

class NuevogrupoMenu(FloatLayout):
    def __init__(self, app, username, connection, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.username = username
        self.connection = connection

        # Rectángulo transparente sobre el que situamos el menu actual
        with self.canvas.before:
            Color(0.859, 1.0, 0.988, 0.8)  # Azul con 80% de opacidad
            self.rect = Rectangle(pos=self.pos,
                                  size=(300, 400),
                                  size_hint=(None, None),
                                  pos_hint={'center_x': 0.5, 'center_y': 0.9})

        # Titulo
        self.titulo = Label(text="CREAR GRUPO",
                            font_name="Roboto-Bold",
                            font_size=30,
                            pos_hint={'center_x': 0.13, 'center_y': 0.35},
                            color=(0, 0, 0, 1))
        self.add_widget(self.titulo)
        self.add_grupo_spinner()

    ###########################################################################################################################

    def add_grupo_spinner(self):
        campos_layout = BoxLayout(orientation='vertical',
                                  spacing=10,
                                  size_hint=(None, None),
                                  size=(250, 200),
                                  pos_hint={'center_x': 0.13, 'center_y': 0.18})

        # Imput del nombre
        self.input_nombre = TextInput(hint_text="Nombre del grupo",
                                      font_size=20,
                                      multiline=False)
        campos_layout.add_widget(self.input_nombre)

        # Campo selector de color
        colores = {"Rojo", "Azul", "Amarillo", "Verde"}
        self.spinner = Spinner(text='Seleccionar color',
                               values=colores,
                               background_normal='',
                               background_color=(1, 1, 1, 1),
                               font_size=20,
                               color=(0, 0, 0, 1))
        campos_layout.add_widget(self.spinner)

        # Aviso de error
        self.warn = Label(text="",
                          font_size=15,
                          pos_hint={'center_x': 0.5, 'center_y': 0.32},
                          color=(1, 0, 0, 1))

        # Botón Guardar
        self.boton_guardar = Button(text="Guardar",
                                    size_hint=(None, None),
                                    size=(200, 40),
                                    pos_hint={'center_x': 0.5},
                                    on_press=self.aniadir_grupo)
        campos_layout.add_widget(self.boton_guardar)

        campos_layout.add_widget(self.warn)
        self.add_widget(campos_layout)

    ###########################################################################################################################

    def aniadir_grupo(self, instance):
        cursor = self.connection.cursor()

        # Busca en la BD si hay algún grupo asociado al usuario actual con el mismo nombre
        cursor.execute("SELECT NOMBRE_GRUPO FROM GRUPOS_PERSONALIZADOS WHERE NOMBRE_GRUPO = :nombre AND USUARIO_PROPIETARIO = :usuario",
                       {'nombre': self.input_nombre.text, 'usuario': self.username})
        grupo = cursor.fetchone()

        # Si ya hay un grupo con el mismo nombre da error
        if grupo:
            self.warn.text = "Ya hay un grupo con el mismo nombre"
        else:
            # Si todos los campos están rellenos hace la inserción
            if self.input_nombre.text != "" or self.spinner.text == "Seleccionar color":
                # Realiza la inserción en la BD
                cursor.execute("INSERT INTO GRUPOS_PERSONALIZADOS (USUARIO_PROPIETARIO, NOMBRE_GRUPO, COLOR) VALUES (:usuario, :nombre, :color)",
                               {'usuario': self.username, 'nombre': self.input_nombre.text, 'color': self.spinner.text})
                self.connection.commit()
                self.app.actualizar_contenido()
                self.warn.text = "Guardado correctamente"

                # Borra el mensaje de aviso de error tras 3 segundos de visualización
                Clock.schedule_once(lambda dt: self.borrar_mensaje(), 3)

                self.input_nombre.text = ""
            else:
                self.warn.text = "Nombre o color no seleccionado"

    ###########################################################################################################################

    # Borra el mensaje de aviso de error
    def borrar_mensaje(self):
        self.warn.text = ""

    ###########################################################################################################################