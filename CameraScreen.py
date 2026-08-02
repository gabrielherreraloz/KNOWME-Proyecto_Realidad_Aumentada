from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from AmigosMenu import AmigosMenu
from AniadiramigoMenu import AniadirAmigoMenu
from NuevogrupoMenu import NuevogrupoMenu
from PerfilMenu import PerfilMenu
from kivy.animation import Animation
from threading import Thread
from microfono import Microfono
from kivy.clock import Clock

class CameraScreen(FloatLayout):
    def __init__(self, app, username, connection, **kwargs):
        super().__init__(**kwargs)
        self.estado_amigos = 0
        self.estado_perfil = 0
        self.app = app
        self.connection = connection

        # Inicialización de las clases asociadas a los submenus
        self.amigos_interface = AmigosMenu(self, username, connection)

        self.aniadiramigos_interface = AniadirAmigoMenu(self.amigos_interface, username, connection)
        self.aniadiramigos_interface.pos_hint = {'center_x': -0.5, 'center_y': 0.5}
        self.aniadiramigos_interface.opacity = 0

        self.nuevogrupo_interface = NuevogrupoMenu(self.amigos_interface, username, connection)
        self.nuevogrupo_interface.pos_hint = {'center_x': -0.5, 'center_y': 0.5}
        self.nuevogrupo_interface.opacity = 0

        self.perfil_interface = PerfilMenu(self, username, connection)
        self.perfil_interface.pos_hint = {'center_x': -0.5, 'center_y': 0.5}
        self.perfil_interface.opacity = 0

        #Animaciones de aparición de los submenus
        self.anim = Animation(pos_hint={'center_x': 0.5, 'center_y': 0.5},
                              opacity=1,
                              duration=0.4,
                              t='out_cubic')
        self.anim_boton_cerrar = Animation(pos_hint={'center_x': 0.24, 'center_y': 0.44},
                                           opacity=1,
                                           duration=0.4,
                                           t='out_cubic')
        self.anim_boton_volver = Animation(pos_hint={'center_x': 0.035, 'center_y': 0.44},
                                           opacity=1,
                                           duration=0.4,
                                           t='out_cubic')

        button_layout = BoxLayout(orientation='horizontal',
                                  spacing=10, size_hint=(None, None),
                                  size=(75 * 3 + 10 * 2, 75),
                                  pos_hint={'center_x': 0.5, 'center_y': 0.1})

        self.boton_amigos = Button(background_normal='iconos/amigos.png',
                                   size_hint=(None, None),
                                   border=(0, 0, 0, 0),
                                   size=(75, 75),
                                   on_press=self.abrir_amigos)
        button_layout.add_widget(self.boton_amigos)

        self.boton_perfil = Button(background_normal='iconos/perfil.png',
                                   size_hint=(None, None),
                                   border=(0, 0, 0, 0),
                                   size=(75, 75),
                                   on_press=self.abrir_perfil)
        button_layout.add_widget(self.boton_perfil)

        self.boton_salir = Button(background_normal='iconos/salir.png',
                                  size_hint=(None, None),
                                  border=(0, 0, 0, 0),
                                  size=(75, 75),
                                  on_press=self.salir)
        button_layout.add_widget(self.boton_salir)

        self.add_widget(button_layout)

        self.boton_cerrar = Button(background_normal='iconos/cerrar.png',
                                   size_hint=(None, None),
                                   size=(80, 80),
                                   pos_hint={'center_x': -0.5, 'center_y': 0.44},
                                   on_press=self.cerrar)

        self.boton_volver = Button(background_normal='iconos/volver.png',
                                   size_hint=(None, None),
                                   size=(80, 80),
                                   pos_hint={'center_x': -0.5, 'center_y': 0.44},
                                   opacity = 0,
                                   on_press=self.volver)

        self.boton_microfono = Button(background_normal='iconos/microfono.png',
                                     size_hint=(None, None),
                                     size=(50, 50),
                                     pos_hint={'center_x': 0.5, 'center_y': 0.95},
                                     on_press=self.reconocimiento_voz)
        self.add_widget(self.boton_microfono)

    ###########################################################################################################################

    # Abre el submenu amigos
    def abrir_amigos(self, instance=None):
        if self.estado_amigos == 0:
            self.amigos_interface.actualizar_contenido()
            self.aniadiramigos_interface.actualizar_opciones()
            self.cerrar()

            # Configura estado inicial del widget (fuera de pantalla y transparente)
            self.amigos_interface.pos_hint = {'center_x': -0.5, 'center_y': 0.5}
            self.amigos_interface.opacity = 0
            self.add_widget(self.amigos_interface)

            # Animación de entrada suave al centro
            self.anim.start(self.amigos_interface)

            self.estado_amigos = 1
        else:
            self.cerrar()

    ###########################################################################################################################

    # Vuelve al estado inicial
    def cerrar(self, instance=None):
        # Lista completa de interfaces a animar
        widgets_a_cerrar = [self.amigos_interface, self.boton_cerrar, self.boton_volver, self.aniadiramigos_interface, self.nuevogrupo_interface, self.perfil_interface]

        for widget in widgets_a_cerrar:
            if widget in self.children:
                anim = Animation(pos_hint={'center_x': -0.5},
                                 opacity=0, duration=0.3,
                                 t='in_cubic')
                anim.bind(on_complete=lambda *a, w=widget: self.remove_widget(w))
                anim.start(widget)

        self.estado_amigos = 0
        self.estado_perfil = 0

    ###########################################################################################################################

    # Usada desde el menu añadiramigos y creargrupo para volver al menu amigos
    def volver(self, instance=None):
        self.cerrar()
        self.abrir_amigos()

    ###########################################################################################################################

    # Abre el submenu añadiramigos
    def abrir_añadiramigos(self, instance=None):
        self.cerrar()
        self.add_widget(self.aniadiramigos_interface)
        self.add_widget(self.boton_cerrar)
        self.add_widget(self.boton_volver)

        self.anim.start(self.aniadiramigos_interface)
        self.anim_boton_cerrar.start(self.boton_cerrar)
        self.anim_boton_volver.start(self.boton_volver)

    ###########################################################################################################################

    # Abre el submenu para crear nuevogrupo
    def abrir_nuevogrupo(self, instance=None):
        self.cerrar()
        self.add_widget(self.nuevogrupo_interface)
        self.add_widget(self.boton_cerrar)
        self.add_widget(self.boton_volver)

        self.anim.start(self.nuevogrupo_interface)
        self.anim_boton_cerrar.start(self.boton_cerrar)
        self.anim_boton_volver.start(self.boton_volver)

    ###########################################################################################################################

    # Abre el submenu del perffil, donde editar los datos personales
    def abrir_perfil(self, instance=None):
        if self.estado_perfil == 0:
            self.cerrar()
            self.add_widget(self.perfil_interface)

            # Animación de entrada suave al centro
            self.anim.start(self.perfil_interface)
            self.estado_perfil = 1
        else:
            self.cerrar()

    ###########################################################################################################################

    # Vuelve a la pantalla inicial de inicio de sesión
    def salir(self, instance=None):
        self.app.mostrar_pantalla_inicio()

    ###########################################################################################################################

    # Crea una hebra para el reconocimiento de voz con el fin de no interrumpir el funcionamiento de la cámara
    def reconocimiento_voz(self, instance):
        self.boton_microfono.background_normal = 'iconos/microfono_grabar.png'

        # Lanzar el reconocimiento paralelo
        voz = Thread(target = self.reconocimiento_hebra)
        voz.start()

    ###########################################################################################################################

    # Pregunta al reconocimiento de voz sobre el texto reconocido para activar uno u otro menú
    def reconocimiento_hebra(self):
        mic = Microfono()
        mic.capturar_audio()
        texto = mic.devolver_audio()

        # En base al texto recibido ejecuta una acción
        if texto == "abrir amigos" or texto == "amigos":
            Clock.schedule_once(lambda dt: self.abrir_amigos(), 0)
        elif texto == "abrir perfil" or texto == "perfil" or texto == "editar perfil":
            Clock.schedule_once(lambda dt: self.abrir_perfil(), 0)
        elif texto == "añadir amigo" or texto == "nuevo amigo" or texto == "añadir amigos":
            Clock.schedule_once(lambda dt: self.abrir_añadiramigos(), 0)
        elif texto == "añadir grupo" or texto == "nuevo grupo" or texto == "añadir grupos":
            Clock.schedule_once(lambda dt: self.abrir_nuevogrupo(), 0)
        elif texto == "salir" or texto == "volver" or texto == "menu principal" or texto == "menu inicio" or texto == "inicio":
            Clock.schedule_once(lambda dt: self.salir(), 0)

        Clock.schedule_once(lambda dt: self.restaurar_icono(), 0)

    ###########################################################################################################################

    # Cuando finaliza el reconocimiento de voz restablece el icono de nuevo
    def restaurar_icono(self):
        self.boton_microfono.background_normal = 'iconos/microfono.png'

    ###########################################################################################################################
