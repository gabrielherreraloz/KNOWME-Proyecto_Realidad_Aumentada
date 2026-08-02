from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

class PerfilMenu(FloatLayout):
    def __init__(self, app, username, connection, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.connection = connection
        self.username = username

        # Rectángulo transparente sobre el que situamos el menu actual
        with self.canvas.before:
            Color(0.859, 1.0, 0.988, 0.8)  # Azul con 80% de opacidad
            self.rect = Rectangle(pos=self.pos,
                                  size=(300, 900),
                                  size_hint=(None, None),
                                  pos_hint={'center_x': 0.5, 'center_y': 0.7})

        # Botón para cerrar el menú actual
        self.boton_cerrar = Button(background_normal='iconos/cerrar.png',
                                   size_hint=(None, None),
                                   size=(80, 80),
                                   pos_hint={'center_x': 0.24, 'center_y': 0.96},
                                   on_press = self.app.cerrar)
        self.add_widget(self.boton_cerrar)

        # Título
        self.titulo = Label(text="MI PERFIL",
                            font_name="Roboto-Bold",
                            font_size=40,
                            pos_hint={'center_x': 0.13, 'center_y': 0.85},
                            color=(0, 0, 0, 1))
        self.add_widget(self.titulo)

        campos_layout = BoxLayout(orientation='vertical',
                                  spacing=10,
                                  size_hint=(None, None),
                                  size=(250, 350),
                                  pos_hint={'center_x': 0.13, 'center_y': 0.5})

        # Campo de texto para el nombre
        self.input_nombre = TextInput(hint_text="Nombre",
                                      font_size=25,
                                      multiline=False)
        campos_layout.add_widget(self.input_nombre)

        # Campo de texto para los apellidos
        self.input_apellido = TextInput(hint_text="Apellido(s)",
                                        font_size=25,
                                        multiline=False)
        campos_layout.add_widget(self.input_apellido)

        # Campo de texto para la edad
        self.input_edad = TextInput(hint_text="Edad",
                                    font_size=25,
                                    multiline=False)
        campos_layout.add_widget(self.input_edad)

        # Campo de texto para la ciudad
        self.input_ciudad = TextInput(hint_text="Ciudad",
                                      font_size=25,
                                      multiline=False)
        campos_layout.add_widget(self.input_ciudad)

        # Campo de texto para el teléfono
        self.input_telefono = TextInput(hint_text="Número de teléfono",
                                        font_size=25,
                                        multiline=False)
        campos_layout.add_widget(self.input_telefono)

        # Campo de texto para el usuario de Instagram
        self.input_instagram = TextInput(hint_text="@ de Instagram",
                                         font_size=25,
                                         multiline=False)
        campos_layout.add_widget(self.input_instagram)

        self.add_widget(campos_layout)

        # Aviso de error
        self.warn = Label(text="",
                          font_size=15,
                          pos_hint={'center_x': 0.13, 'center_y': 0.05},
                          color=(1, 0, 0, 1))

        self.boton_guardar = Button(text = "Guardar",
                                    size_hint=(None, None),
                                    size=(200, 50),
                                    font_size = 20,
                                    pos_hint = {'center_x': 0.13, 'center_y': 0.10},
                                    background_color = (0.859, 1.0, 0.988, 1),
                                    color = (1, 1, 1, 1),
                                    on_press=self.guardar)
        self.add_widget(self.boton_guardar)
        self.add_widget(self.warn)

        self.rellenar_campos()

    ###########################################################################################################################

    # Guarda la información introducida en los campos de texto en la BD
    def guardar(self, instance):
        cursor = self.connection.cursor()

        cursor.execute("UPDATE USUARIOS SET NOMBRE = :nombre,APELLIDO = :apellido,EDAD = :edad, INSTAGRAM = :insta, CIUDAD = :ciudad, TELEFONO = :telf WHERE USERNAME = :usuario",
            {'usuario': self.username,'nombre': self.input_nombre.text,'apellido': self.input_apellido.text,'edad': self.input_edad.text,
            'insta': self.input_instagram.text,'ciudad': self.input_ciudad.text,'telf': self.input_telefono.text})

        self.connection.commit()
        self.warn.text = "Guardado correctamente"

        # Borra el mensaje de aviso de error tras 3 segundos de visualización
        Clock.schedule_once(lambda dt: self.borrar_mensaje(), 3)

    ###########################################################################################################################

    # Si hay información ya guardada sobre alguno de los campos de texto, la rellena en ellos
    def rellenar_campos(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT NOMBRE, APELLIDO, EDAD, INSTAGRAM, CIUDAD, TELEFONO FROM USUARIOS WHERE USERNAME = :usuario",
                       {'usuario': self.username})
        grupo = cursor.fetchone()

        if grupo:
            if grupo[0]:
                self.input_nombre.text = grupo[0]
            if grupo[1]:
                self.input_apellido.text = grupo[1]
            if grupo[2]:
                self.input_edad.text = str(grupo[2])
            if grupo[3]:
                self.input_instagram.text = grupo[3]
            if grupo[4]:
                self.input_ciudad.text = grupo[4]
            if grupo[5]:
                self.input_telefono.text = str(grupo[5])

    ###########################################################################################################################

    # Borra el mensaje de aviso de error
    def borrar_mensaje(self):
        self.warn.text = ""