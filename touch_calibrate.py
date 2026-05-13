"""
Herramienta de calibración táctil — Massaro Propiedades
Uso: python touch_calibrate.py
Genera touch_calibration.json con los parámetros de corrección.
"""
import json
import math

from kivy.config import Config
Config.set('graphics', 'width',     '1024')
Config.set('graphics', 'height',    '600')
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'fullscreen','0')

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.core.window import Window
from kivy.clock import Clock

W, H   = 1024, 600
RADIO  = 24    # radio del círculo objetivo
MARGEN = 32    # distancia al borde

# Coordenadas en sistema Kivy (0,0 = abajo-izquierda)
OBJETIVOS = [
    (MARGEN,       H - MARGEN),   # 1  arriba-izquierda  (visual)
    (W - MARGEN,   H - MARGEN),   # 2  arriba-derecha    (visual)
    (W - MARGEN,   MARGEN),       # 3  abajo-derecha     (visual)
    (MARGEN,       MARGEN),       # 4  abajo-izquierda   (visual)
    (W // 2,       H // 2),       # 5  centro
]
ETIQUETAS = ['1 ↖', '2 ↗', '3 ↘', '4 ↙', '5 ●']
DEVICE_MAX = 2048   # rango máximo del dispositivo


class PantallaCalib(FloatLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._registrado  = {}    # {idx_objetivo: (x_real, y_real)}
        self._hover       = None  # idx del círculo resaltado
        self._exit_timer  = None

        self._dibujar()

        # Etiquetas de número sobre cada círculo
        for i, (px, py) in enumerate(OBJETIVOS):
            self.add_widget(Label(
                text=ETIQUETAS[i], bold=True, font_size='15sp',
                color=(1, 1, 1, 1), size=(56, 32),
                pos=(px - 28, py - 16),
            ))

        # Instrucción principal
        self.lbl_inst = Label(
            text='Tocá cada círculo numerado  (1 → 2 → 3 → 4 → 5)',
            font_size='20sp', bold=True,
            size_hint=(1, None), height=36,
            pos=(0, H - 50), color=(1, 1, 0.5, 1),
        )
        self.add_widget(self.lbl_inst)

        # Coordenadas en tiempo real
        self.lbl_coords = Label(
            text='TOQUE:  X = ---   Y = ---       (esperado  X = ---   Y = ---)',
            font_size='16sp',
            size_hint=(1, None), height=28,
            pos=(0, H - 85), color=(0.75, 0.9, 1, 1),
        )
        self.add_widget(self.lbl_coords)

        # Progreso
        self.lbl_prog = Label(
            text='Registrados: 0 / 5',
            font_size='15sp',
            size_hint=(1, None), height=24,
            pos=(0, H - 115), color=(0.55, 1, 0.55, 1),
        )
        self.add_widget(self.lbl_prog)

        # Botón guardar
        self.btn = Button(
            text='GUARDAR CALIBRACIÓN', font_size='20sp',
            size_hint=(None, None), size=(320, 52),
            pos=((W - 320) // 2, 14),
            background_normal='', background_down='',
            background_color=(0.12, 0.55, 0.18, 1),
            disabled=True, opacity=0.3,
        )
        self.btn.bind(on_press=self._guardar)
        self.add_widget(self.btn)

        # Nota de salida
        self.add_widget(Label(
            text='ESC  o  mantené presionada una esquina 3 seg para salir',
            font_size='12sp', color=(0.4, 0.4, 0.4, 1),
            size_hint=(1, None), height=20, pos=(0, 70),
        ))

        Window.bind(on_keyboard=self._tecla)

    # ------------------------------------------------------------------
    # Canvas
    # ------------------------------------------------------------------

    def _dibujar(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.05, 0.05, 0.1, 1)
            Rectangle(pos=(0, 0), size=(W, H))
            for i, (px, py) in enumerate(OBJETIVOS):
                if i in self._registrado:
                    Color(0.1, 0.85, 0.25, 1)   # verde: registrado
                elif i == self._hover:
                    Color(1.0, 0.82, 0.1, 1)    # amarillo: activo
                else:
                    Color(0.22, 0.32, 0.82, 1)  # azul: pendiente
                Ellipse(pos=(px - RADIO, py - RADIO),
                        size=(RADIO * 2, RADIO * 2))
                Color(1, 1, 1, 0.45)
                Line(circle=(px, py, RADIO + 3), width=1.4)

    # ------------------------------------------------------------------
    # Touch
    # ------------------------------------------------------------------

    def _mas_cercano(self, x, y):
        return min(range(len(OBJETIVOS)),
                   key=lambda i: math.hypot(x - OBJETIVOS[i][0],
                                            y - OBJETIVOS[i][1]))

    def on_touch_down(self, touch):
        idx = self._mas_cercano(touch.x, touch.y)
        self._hover = idx
        ex, ey = OBJETIVOS[idx]
        self.lbl_coords.text = (
            f'TOQUE:  X = {touch.x:.0f}   Y = {touch.y:.0f}'
            f'       (esperado  X = {ex}   Y = {ey})'
        )

        # Long press en esquinas para salir
        if idx in (0, 1, 2, 3):
            self._exit_timer = Clock.schedule_once(
                lambda _: App.get_running_app().stop(), 3.0)

        # Registrar inmediatamente en touch_down
        self._registrado[idx] = (touch.x, touch.y)
        n = len(self._registrado)
        self.lbl_prog.text = f'Registrados: {n} / 5'
        if n >= 5:
            self.btn.disabled = False
            self.btn.opacity = 1
            self.lbl_inst.text = '¡Completo! Tocá GUARDAR CALIBRACIÓN.'

        self._dibujar()
        return True

    def on_touch_up(self, touch):
        if self._exit_timer:
            self._exit_timer.cancel()
            self._exit_timer = None
        self._hover = None
        self._dibujar()
        return True

    def _tecla(self, window, key, *args):
        if key == 27:   # ESC
            App.get_running_app().stop()
        return False

    # ------------------------------------------------------------------
    # Guardado y cálculo
    # ------------------------------------------------------------------

    def _guardar(self, *_):
        calib = self._calcular()
        with open('touch_calibration.json', 'w') as f:
            json.dump(calib, f, indent=2)
        self.lbl_inst.text = '✓ Guardado en touch_calibration.json — cerrá y reiniciá la app'
        self.btn.text = '✓ GUARDADO'
        self.btn.background_color = (0.25, 0.25, 0.25, 1)
        print('\n=== Calibración guardada ===')
        for k, v in calib.items():
            if not k.startswith('_'):
                print(f'  {k}: {v}')
        print('\nDebug:')
        for k, v in calib.get('_debug', {}).items():
            print(f'  {k}: {v}')

    def _calcular(self):
        """
        Deriva swap_axes, invert_x, invert_y y rangos efectivos
        comparando las 5 posiciones esperadas con las reales.
        Usa covarianza para detectar correlación de ejes.
        """
        E = [OBJETIVOS[i]          for i in range(5)]
        A = [self._registrado[i]   for i in range(5)]

        # Normalizar a [0, 1]
        En = [(e[0] / W, e[1] / H) for e in E]
        An = [(a[0] / W, a[1] / H) for a in A]

        ex = [e[0] for e in En]; ey = [e[1] for e in En]
        ax = [a[0] for a in An]; ay = [a[1] for a in An]

        def cov(xs, ys):
            mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
            return sum((x - mx) * (y - my) for x, y in zip(xs, ys))

        r_xx = cov(ax, ex)   # actual_x  vs  esperado_x
        r_xy = cov(ax, ey)   # actual_x  vs  esperado_y  ← swap indicator

        # Si actual_x correlaciona más con expected_y → ejes intercambiados
        swap_axes = abs(r_xy) > abs(r_xx)

        if swap_axes:
            eff_x, eff_y = ay, ax   # después del swap teórico
        else:
            eff_x, eff_y = ax, ay

        invert_x = cov(eff_x, ex) < 0
        invert_y = cov(eff_y, ey) < 0

        # Rangos efectivos en unidades del dispositivo (0-DEVICE_MAX)
        min_x = round(min(eff_x) * DEVICE_MAX)
        max_x = round(max(eff_x) * DEVICE_MAX)
        min_y = round(min(eff_y) * DEVICE_MAX)
        max_y = round(max(eff_y) * DEVICE_MAX)

        return {
            'swap_axes': swap_axes,
            'invert_x':  invert_x,
            'invert_y':  invert_y,
            'min_x': min_x, 'max_x': max_x,
            'min_y': min_y, 'max_y': max_y,
            '_debug': {
                'r_xx': round(r_xx, 4),
                'r_xy': round(r_xy, 4),
                'actuales_norm':  [(round(a[0],3), round(a[1],3)) for a in An],
                'esperados_norm': [(round(e[0],3), round(e[1],3)) for e in En],
            }
        }


class CalibrateApp(App):
    def build(self):
        self.title = 'Calibración Touch'
        Window.clearcolor = (0, 0, 0, 1)
        return PantallaCalib()


if __name__ == '__main__':
    CalibrateApp().run()
