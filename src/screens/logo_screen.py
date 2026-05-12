from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.clock import Clock
from src.utils.file_scanner import listar_imagenes

DURACION_SLIDE = 10    # segundos entre imágenes
DURACION_FADE  = 0.8   # segundos de crossfade


class LogoScreen(Screen):

    def __init__(self, carpeta_logo='LOGO', **kwargs):
        super().__init__(**kwargs)
        self.carpeta_logo = carpeta_logo
        self.imagenes = []
        self.indice_actual = 0
        self._timer = None

        layout = FloatLayout()

        # Dos capas para crossfade: atras se carga con la imagen nueva,
        # luego se intercambian los roles al completar la animación
        self.img_atras = Image(
            allow_stretch=True, keep_ratio=True,
            size_hint=(1, 1), pos_hint={'x': 0, 'y': 0},
            opacity=0,
        )
        self.img_frente = Image(
            allow_stretch=True, keep_ratio=True,
            size_hint=(1, 1), pos_hint={'x': 0, 'y': 0},
            opacity=0,
        )
        self.lbl_vacio = Label(
            text='Colocá imágenes (.png / .jpg) en la carpeta  LOGO/',
            font_size='22sp',
            color=(1, 1, 1, 0.4),
            opacity=0,
        )

        layout.add_widget(self.img_atras)
        layout.add_widget(self.img_frente)
        layout.add_widget(self.lbl_vacio)
        self.add_widget(layout)

    # ------------------------------------------------------------------
    # Ciclo de vida de la pantalla
    # ------------------------------------------------------------------

    def on_enter(self):
        self.imagenes = listar_imagenes(self.carpeta_logo)
        self.indice_actual = 0

        if not self.imagenes:
            self.img_frente.opacity = 0
            self.lbl_vacio.opacity = 1
            return

        self.lbl_vacio.opacity = 0
        self._mostrar_imagen(self.imagenes[0])

        if len(self.imagenes) > 1:
            self._timer = Clock.schedule_interval(self._avanzar_slide, DURACION_SLIDE)

    def on_leave(self):
        if self._timer:
            self._timer.cancel()
            self._timer = None
        Animation.cancel_all(self.img_frente)
        Animation.cancel_all(self.img_atras)

    # ------------------------------------------------------------------
    # Slideshow
    # ------------------------------------------------------------------

    def _mostrar_imagen(self, ruta):
        self.img_frente.source = ruta
        self.img_frente.opacity = 1
        self.img_atras.source = ''
        self.img_atras.opacity = 0

    def _avanzar_slide(self, dt):
        Animation.cancel_all(self.img_frente)
        Animation.cancel_all(self.img_atras)

        self.indice_actual = (self.indice_actual + 1) % len(self.imagenes)

        self.img_atras.source = self.imagenes[self.indice_actual]
        self.img_atras.opacity = 0
        self.img_frente.opacity = 1

        anim_salida  = Animation(opacity=0, duration=DURACION_FADE)
        anim_entrada = Animation(opacity=1, duration=DURACION_FADE)
        anim_entrada.bind(on_complete=lambda *_: self._swap_capas())

        anim_salida.start(self.img_frente)
        anim_entrada.start(self.img_atras)

    def _swap_capas(self):
        # Intercambiar roles: la capa que acaba de aparecer pasa a ser "frente"
        self.img_frente, self.img_atras = self.img_atras, self.img_frente

    # ------------------------------------------------------------------
    # Gestos
    # ------------------------------------------------------------------

    def on_touch_down(self, touch):
        if self.manager:
            self.manager.current = 'menu'
        return True
