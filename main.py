import os

# KIOSK=1 activa pantalla completa y deshabilita resize (para el Pi)
# En Windows de desarrollo simplemente no se setea
KIOSK = os.environ.get('KIOSK', '0') == '1'

# Configurar ventana antes de cualquier otro import de Kivy
from kivy.config import Config
Config.set('graphics', 'width',     '1024')
Config.set('graphics', 'height',    '600')
Config.set('graphics', 'resizable', '0' if KIOSK else '1')
if KIOSK:
    Config.set('graphics', 'fullscreen', '1')

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

from src.utils.touch_calibration import aplicar_calibracion
from src.screens.menu_screen import MenuScreen
from src.screens.logo_screen import LogoScreen
from src.screens.gallery_screen import GalleryScreen
from src.screens.player_screen import PlayerScreen

COLOR_FONDO = get_color_from_hex('#1a1a2e')


class MultimediaApp(MDApp):

    def build(self):
        self.title = 'Massaro Propiedades'
        self.theme_cls.theme_style = 'Dark'

        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(LogoScreen(name='logo'))
        sm.add_widget(GalleryScreen(name='gallery'))
        sm.add_widget(PlayerScreen(name='player'))
        return sm

    def on_start(self):
        Window.clearcolor = COLOR_FONDO
        aplicar_calibracion()   # no-op si touch_calibration.json no existe


if __name__ == '__main__':
    MultimediaApp().run()
