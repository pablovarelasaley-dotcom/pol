from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
from kivymd.icon_definitions import md_icons


class IconButton(ButtonBehavior, BoxLayout):
    """
    Botón con ícono Material Design + texto.
    orientation='vertical'   → ícono arriba, texto abajo  (menú principal)
    orientation='horizontal' → ícono izquierda, texto derecha  (barras de navegación)
    """

    def __init__(self, icon, text, callback=None,
                 orientation='vertical',
                 icon_size='72sp', text_size='36sp',
                 bg_color=(0.1, 0.1, 0.2, 1),
                 radio=16,
                 **kwargs):
        super().__init__(orientation=orientation, spacing=6,
                         padding=[12, 12, 12, 12], **kwargs)
        self._callback  = callback
        self._orig_color = tuple(bg_color)

        with self.canvas.before:
            self._color_instr = Color(*bg_color)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[radio])
        self.bind(pos=self._update_bg, size=self._update_bg)

        lbl_icono = Label(
            text=md_icons.get(icon, ''),
            font_name='Icons',
            font_size=icon_size,
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle',
        )
        lbl_icono.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        lbl_texto = Label(
            text=text,
            font_size=text_size,
            bold=True,
            color=(1, 1, 1, 0.92),
            halign='center',
            valign='middle',
        )
        lbl_texto.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        if orientation == 'vertical':
            lbl_icono.size_hint_y = 0.58
            lbl_texto.size_hint_y = 0.42
        else:
            lbl_icono.size_hint_x = 0.26
            lbl_texto.size_hint_x = 0.74
            lbl_texto.halign = 'left'

        self.add_widget(lbl_icono)
        self.add_widget(lbl_texto)

    def _update_bg(self, *args):
        self._bg.pos  = self.pos
        self._bg.size = self.size

    def on_press(self):
        c = self._orig_color
        self._color_instr.rgba = (c[0] * 0.6, c[1] * 0.6, c[2] * 0.6, c[3])

    def on_release(self):
        self._color_instr.rgba = self._orig_color
        if self._callback:
            self._callback()
