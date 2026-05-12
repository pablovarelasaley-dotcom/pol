from pathlib import Path
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle


class ThumbnailCard(ButtonBehavior, BoxLayout):
    """Celda de la grilla: thumbnail + nombre de archivo."""

    def __init__(self, archivo, thumb_path, callback, **kwargs):
        super().__init__(orientation='vertical', spacing=2, padding=[3, 3, 3, 3], **kwargs)
        self._archivo = archivo
        self._callback = callback

        with self.canvas.before:
            Color(0.13, 0.13, 0.18, 1)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._actualizar_bg, size=self._actualizar_bg)

        self.img = Image(
            source=thumb_path,
            allow_stretch=True,
            keep_ratio=True,
            size_hint_y=0.82,
        )

        self.lbl = Label(
            text=Path(archivo).name,
            font_size='11sp',
            color=(0.75, 0.75, 0.75, 1),
            size_hint_y=0.18,
            shorten=True,
            shorten_from='right',
            halign='center',
            valign='middle',
        )
        self.lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], val[1])))

        self.add_widget(self.img)
        self.add_widget(self.lbl)

    def _actualizar_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def actualizar_thumbnail(self, thumb_path):
        self.img.source = thumb_path
        self.img.reload()

    def on_press(self):
        self._callback(self._archivo)
