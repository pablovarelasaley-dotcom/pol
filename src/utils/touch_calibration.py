"""
Aplica la calibración táctil leída de touch_calibration.json.
Si el archivo no existe, no hace nada (coordenadas nativas).

Transformaciones en orden:
  1. Corregir rangos efectivos del dispositivo (min/max)
  2. Swap de ejes X ↔ Y
  3. Inversión de X y/o Y
"""
import json
import os
from kivy.core.window import Window

CALIB_FILE  = 'touch_calibration.json'
DEVICE_MAX  = 2048

# Defaults sin calibración (no modifican nada)
_DEFAULTS = {
    'swap_axes': False,
    'invert_x':  False,
    'invert_y':  False,
    'min_x': 0,    'max_x': DEVICE_MAX,
    'min_y': 0,    'max_y': DEVICE_MAX,
}

_calib = None


def _cargar():
    global _calib
    if not os.path.exists(CALIB_FILE):
        print('[touch_calibration] Archivo no encontrado — sin corrección.')
        return None
    try:
        with open(CALIB_FILE) as f:
            data = json.load(f)
        # Fusionar con defaults para tolerar JSONs parciales
        _calib = {**_DEFAULTS, **data}
        print(f'[touch_calibration] Cargado: '
              f'swap={_calib["swap_axes"]}  '
              f'inv_x={_calib["invert_x"]}  '
              f'inv_y={_calib["invert_y"]}  '
              f'x=[{_calib["min_x"]},{_calib["max_x"]}]  '
              f'y=[{_calib["min_y"]},{_calib["max_y"]}]')
        return _calib
    except Exception as e:
        print(f'[touch_calibration] Error al leer JSON: {e}')
        return None


def _remap(window, touch):
    if _calib is None:
        return False

    w = Window.width
    h = Window.height

    # sx/sy ya normalizados por Kivy usando el rango del dispositivo
    sx = touch.sx
    sy = touch.sy

    # 1 — Corregir rango efectivo del dispositivo
    min_xn = _calib['min_x'] / DEVICE_MAX
    max_xn = _calib['max_x'] / DEVICE_MAX
    min_yn = _calib['min_y'] / DEVICE_MAX
    max_yn = _calib['max_y'] / DEVICE_MAX

    rng_x = max_xn - min_xn or 1.0
    rng_y = max_yn - min_yn or 1.0
    sx = (sx - min_xn) / rng_x
    sy = (sy - min_yn) / rng_y

    # 2 — Swap de ejes
    if _calib['swap_axes']:
        sx, sy = sy, sx

    # 3 — Inversión
    if _calib['invert_x']:
        sx = 1.0 - sx
    if _calib['invert_y']:
        sy = 1.0 - sy

    # Clampar a [0, 1]
    sx = max(0.0, min(1.0, sx))
    sy = max(0.0, min(1.0, sy))

    # Actualizar el objeto touch (mismo objeto que recibirán los widgets)
    touch.sx  = sx
    touch.sy  = sy
    touch.x   = sx * w
    touch.y   = sy * h
    touch.pos = (touch.x, touch.y)

    return False   # no consumir el evento; solo transformar


def aplicar_calibracion():
    """
    Llamar una vez desde App.on_start().
    Registra los handlers en Window para interceptar todos los toques.
    """
    calib = _cargar()
    if calib is None:
        return

    Window.bind(on_touch_down=_remap)
    Window.bind(on_touch_move=_remap)
    Window.bind(on_touch_up=_remap)
    print('[touch_calibration] Handlers registrados en Window.')
