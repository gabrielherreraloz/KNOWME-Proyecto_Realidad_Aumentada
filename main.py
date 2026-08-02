from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from database import conectar
from LoginScreen import LoginScreen
from kivy.core.window import Window

class KNOWME(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        #Abre la conexion de la BD al inciar el programa
        self.connection = conectar()

        self.root_layout = FloatLayout()
        Window.size = (1100, 850)
        Window.clearcolor = (0.859, 1.0, 0.988, 1)

    ###########################################################################################################################

    def build(self):
        self.mostrar_pantalla_inicio()
        return self.root_layout

    ###########################################################################################################################

    # Muestra en pantalla el menu inicial de inicio de sesión
    def mostrar_pantalla_inicio(self, *args):
        self.root_layout.clear_widgets()
        self.root_layout.add_widget(LoginScreen(self, self.connection))

# Ejecutar la aplicación
KNOWME().run()
