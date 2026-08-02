from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.uix.scrollview import ScrollView

class AmigosMenu(FloatLayout):
    def __init__(self, app, username, connection, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.connection = connection
        self.username = username

        # Rectangulo transparente sobre el que situamos el menu actual
        with self.canvas.before:
            Color(0.859, 1.0, 0.988, 0.8)  # Azul con 80% de opacidad
            self.rect = Rectangle(pos=self.pos,
                                  size=(300, 900),
                                  size_hint=(None, None),
                                  pos_hint={'center_x': 0.5, 'center_y': 0.7})

        # Boton para cerrar menu actual
        self.boton_cerrar = Button(background_normal='iconos/cerrar.png',
                                   size_hint=(None, None),
                                   size=(80, 80),
                                   pos_hint={'center_x': 0.24, 'center_y': 0.96},
                                   on_press = self.app.cerrar
        )
        self.add_widget(self.boton_cerrar)

        # Titulo
        self.titulo = Label(text="GRUPOS",
                            font_name="Roboto-Bold",
                            font_size=40,
                            pos_hint={'center_x': 0.13, 'center_y': 0.85},
                            color=(0, 0, 0, 1))
        self.add_widget(self.titulo)

        # Boton para entrar al menu AniadirAmigo
        self.boton_aniadiramigo = Button(text ="Añadir amigo",
                                         size_hint=(None, None),
                                         size=(200, 50),  # Tamaño del botón
                                         font_size = 20,
                                         on_press=self.crear_amigos,
                                         pos_hint = {'center_x': 0.13, 'center_y': 0.10},
                                         background_color = (0.859, 1.0, 0.988, 1),
                                         color = (1, 1, 1, 1)
                                         )
        self.add_widget(self.boton_aniadiramigo)

        # Boton para entrar al menu NuevoGrupo
        self.boton_creargrupo = Button(
            text="Nuevo grupo",
            size_hint=(None, None),
            size=(200, 50),  # Tamaño del botón
            font_size=20,
            pos_hint={'center_x': 0.13, 'center_y': 0.17},
            background_color=(0.859, 1.0, 0.988, 1),
            color=(1, 1, 1, 1),
            on_press = self.crear_grupo
        )
        self.add_widget(self.boton_creargrupo)

        # Scroll donde se muestra la lista de grupos y amigos
        self.scrollview = ScrollView(size_hint=(0.4, 0.5),
                                     pos_hint={'center_x': 0.08, 'center_y': 0.5})

        # Relllena el Scrollview con la información sobre grupos y amigos de la BD
        self.actualizar_contenido()
        self.add_widget(self.scrollview)

    ###########################################################################################################################

    #Abre el menu para añadir un nuevo amigo
    def crear_amigos(self, instance):
        self.app.abrir_añadiramigos()

    ###########################################################################################################################

    # Abre el menu para crear un nuevo grupo personalizado
    def crear_grupo(self, instance):
        self.app.abrir_nuevogrupo()

    ###########################################################################################################################

    #Actualiza el contenido mostrado en la lista de grupos y amigos tras haber añadido algo nuevo
    def actualizar_contenido(self):
        with self.connection.cursor() as cursor:
            #Eliminamos el widget para poder actualizar su contenido
            self.scrollview.clear_widgets()

            # Busca los nombres de grupos asociados al perfil actual en la BD
            cursor.execute("SELECT NOMBRE_GRUPO FROM GRUPOS_PERSONALIZADOS WHERE USUARIO_PROPIETARIO = :usuario",
                           {'usuario': self.username})
            grupo = cursor.fetchall()

            self.amigos = Label(text="", font_size=25, color=(0, 0, 0, 1), size_hint_y=None)
            self.amigos.bind(texture_size=self.amigos.setter('size'))

            for (nombre_grupo,) in grupo:
                #Busca los colores asociados a cada grupo del perfil actual de la BD
                cursor.execute("SELECT COLOR FROM GRUPOS_PERSONALIZADOS WHERE USUARIO_PROPIETARIO = :usuario AND NOMBRE_GRUPO =: nombre",
                               {'usuario': self.username, 'nombre': nombre_grupo})
                color = cursor.fetchone()
                color = color[0]

                self.amigos.text += "                   " + nombre_grupo + " (" + color + ")" + "\n"

                # Busca los nombres de usuarios asociados a cada grupo del perfil actual en la BD
                cursor.execute("SELECT USUARIO_MIEMBRO FROM GRUPO_USUARIOS WHERE NOMBRE_GRUPO = :grupo AND USUARIO_PROPIETARIO = :usuario",
                               {'grupo': nombre_grupo, 'usuario': self.username})
                grupo_2 = cursor.fetchall()

                for (user,) in grupo_2:
                    self.amigos.text += "                       • " + user + "\n"
                self.amigos.text += "\n"

            #Volvemos a añadir el widget con su contenido actualizado
            self.scrollview.add_widget(self.amigos)

    ###########################################################################################################################
