import threading
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from src.utils.file_scanner import listar_archivos_galeria
from src.utils.thumbnail_generator import ruta_thumbnail, thumbnail_existe, generar_thumbnail
from src.widgets.thumbnail_card import ThumbnailCard
from src.widgets.icon_button import IconButton

COLUMNAS       = 3
ESPACIADO      = 6
PADDING_H      = 16   # 8px cada lado
COLOR_PLAY     = get_color_from_hex('#e63946')
COLOR_VOLVER   = get_color_from_hex('#333355')


class GalleryScreen(Screen):

    def __init__(self, carpeta='videos', **kwargs):
        super().__init__(**kwargs)
        self.carpeta = carpeta
        self.archivos = []
        self._cards = {}       # {ruta_archivo: ThumbnailCard}
        self._hilo = None

        raiz = BoxLayout(orientation='vertical', spacing=4, padding=[8, 8, 8, 8])

        # --- Barra superior ---
        top_bar = BoxLayout(size_hint_y=None, height=64, spacing=6)

        btn_volver = IconButton(
            icon='arrow-left',
            text='VOLVER',
            callback=self._on_volver,
            orientation='horizontal',
            icon_size='28sp',
            text_size='18sp',
            bg_color=COLOR_VOLVER,
            radio=10,
            size_hint_x=0.22,
        )
        self.btn_play_all = IconButton(
            icon='play-circle-outline',
            text='REPRODUCIR TODO',
            callback=self._on_play_all,
            orientation='horizontal',
            icon_size='28sp',
            text_size='20sp',
            bg_color=COLOR_PLAY,
            radio=10,
            size_hint_x=0.78,
        )

        top_bar.add_widget(btn_volver)
        top_bar.add_widget(self.btn_play_all)

        # --- Grilla con scroll ---
        self.scroll = ScrollView(do_scroll_x=False)
        self.grid = GridLayout(
            cols=COLUMNAS,
            spacing=ESPACIADO,
            size_hint_y=None,
        )
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)

        raiz.add_widget(top_bar)
        raiz.add_widget(self.scroll)
        self.add_widget(raiz)

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------

    def on_enter(self):
        self.archivos = listar_archivos_galeria(self.carpeta)
        self._construir_grilla()
        if self.archivos:
            self._hilo = threading.Thread(target=self._generar_thumbs_bg, daemon=True)
            self._hilo.start()

    def on_leave(self):
        self._hilo = None   # señal de salida para el hilo

    # ------------------------------------------------------------------
    # Construcción de la grilla
    # ------------------------------------------------------------------

    def _construir_grilla(self):
        self.grid.clear_widgets()
        self._cards.clear()

        if not self.archivos:
            self.grid.add_widget(Label(
                text='Colocá archivos en la carpeta  videos/',
                font_size='20sp',
                color=(1, 1, 1, 0.4),
                size_hint_y=None,
                height=200,
            ))
            return

        ancho_celda = (Window.width - PADDING_H - (COLUMNAS - 1) * ESPACIADO) / COLUMNAS
        alto_celda  = ancho_celda * 0.72

        for archivo in self.archivos:
            thumb = ruta_thumbnail(archivo)
            card = ThumbnailCard(
                archivo=archivo,
                thumb_path=thumb if thumbnail_existe(archivo) else '',
                callback=self._on_tap_thumbnail,
                size_hint_y=None,
                height=alto_celda,
            )
            self.grid.add_widget(card)
            self._cards[archivo] = card

    # ------------------------------------------------------------------
    # Generación de thumbnails en segundo plano
    # ------------------------------------------------------------------

    def _generar_thumbs_bg(self):
        hilo_actual = self._hilo
        for archivo in list(self.archivos):
            if self._hilo is not hilo_actual:
                break
            if not thumbnail_existe(archivo):
                thumb = generar_thumbnail(archivo)
                if thumb:
                    Clock.schedule_once(
                        lambda dt, a=archivo, t=thumb: self._actualizar_card(a, t)
                    )

    def _actualizar_card(self, archivo, thumb_path):
        card = self._cards.get(archivo)
        if card:
            card.actualizar_thumbnail(thumb_path)

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _on_volver(self):
        self.manager.current = 'menu'

    def _on_play_all(self):
        if not self.archivos:
            return
        player = self.manager.get_screen('player')
        player.iniciar(self.archivos, 0)
        self.manager.current = 'player'

    def _on_tap_thumbnail(self, archivo):
        player = self.manager.get_screen('player')
        player.iniciar(self.archivos, self.archivos.index(archivo))
        self.manager.current = 'player'
