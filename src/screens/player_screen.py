from pathlib import Path
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.video import Video
from kivy.graphics import Color, Rectangle
from src.widgets.gesture_overlay import GestureOverlay
from src.utils.file_scanner import EXTENSIONES_VIDEO


class PlayerScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.archivos = []
        self.indice   = 0
        self._video   = None

        with self.canvas.before:
            Color(0, 0, 0, 1)
            self._fondo = Rectangle(pos=self.pos, size=self.size)
        self.bind(
            pos  = lambda *_: setattr(self._fondo, 'pos',  self.pos),
            size = lambda *_: setattr(self._fondo, 'size', self.size),
        )

        self.layout = FloatLayout()

        self.img = Image(
            allow_stretch=True, keep_ratio=True, opacity=0,
            size_hint=(1, 1), pos_hint={'x': 0, 'y': 0},
        )
        self.layout.add_widget(self.img)

        # El overlay va siempre encima (último en agregarse = index 0 en children)
        overlay = GestureOverlay(
            on_swipe_left  = self._siguiente,
            on_swipe_right = self._anterior,
            on_single_tap  = self._toggle_play,
            on_double_tap  = self._volver_grilla,
            on_long_press  = self._volver_menu,
            size_hint=(1, 1), pos_hint={'x': 0, 'y': 0},
        )
        self.layout.add_widget(overlay)
        self.add_widget(self.layout)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def iniciar(self, archivos, indice=0):
        self.archivos = archivos
        self.indice   = indice
        self._reproducir_actual()

    # ------------------------------------------------------------------
    # Reproducción
    # ------------------------------------------------------------------

    def _reproducir_actual(self):
        if not self.archivos:
            return
        self._detener_todo()
        archivo = self.archivos[self.indice]
        if Path(archivo).suffix.lower() in EXTENSIONES_VIDEO:
            self._play_video(archivo)
        else:
            self._show_foto(archivo)

    def _play_video(self, path):
        self.img.opacity = 0
        self._video = Video(
            source=path,
            state='play',
            volume=0,            # sin audio: la terminal no tiene parlantes
            allow_stretch=True,
            keep_ratio=True,
            options={'eos': 'stop'},
            size_hint=(1, 1),
            pos_hint={'x': 0, 'y': 0},
        )
        # Detectar fin de video por cambio de state → 'stop'
        self._video.bind(state=self._on_video_state)
        # index=1: debajo del overlay (index=0), encima del img
        self.layout.add_widget(self._video, index=1)

    def _on_video_state(self, instance, value):
        if value == 'stop':
            self._siguiente()

    def _show_foto(self, path):
        self.img.source  = path
        self.img.opacity = 1

    def _detener_todo(self):
        if self._video:
            # Desligar callback antes de parar para que no dispare _siguiente
            self._video.unbind(state=self._on_video_state)
            self._video.state = 'stop'
            try:
                self.layout.remove_widget(self._video)
            except Exception:
                pass
            self._video = None
        self.img.opacity = 0

    # ------------------------------------------------------------------
    # Gestos
    # ------------------------------------------------------------------

    def _siguiente(self):
        if self.archivos:
            self.indice = (self.indice + 1) % len(self.archivos)
            self._reproducir_actual()

    def _anterior(self):
        if self.archivos:
            self.indice = (self.indice - 1) % len(self.archivos)
            self._reproducir_actual()

    def _toggle_play(self):
        """Pausa/reanuda video. En fotos no hace nada."""
        if self._video:
            self._video.state = 'pause' if self._video.state == 'play' else 'play'

    def _volver_grilla(self):
        self._detener_todo()
        if self.manager:
            self.manager.current = 'gallery'

    def _volver_menu(self):
        self._detener_todo()
        if self.manager:
            self.manager.current = 'menu'

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------

    def on_leave(self):
        self._detener_todo()
