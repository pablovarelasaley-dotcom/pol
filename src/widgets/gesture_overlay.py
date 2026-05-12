from kivy.uix.widget import Widget
from kivy.clock import Clock

SWIPE_UMBRAL = 80     # píxeles mínimos para considerar swipe
LONG_PRESS_T = 1.0    # segundos de hold para long press
DOBLE_TAP_T  = 0.32   # ventana de tiempo para detectar segundo tap


class GestureOverlay(Widget):
    """
    Capa transparente que detecta gestos táctiles sobre el reproductor.
    Todos los callbacks son opcionales; se pasan como kwargs al construir.
    """

    def __init__(self, on_swipe_left=None, on_swipe_right=None,
                 on_single_tap=None, on_double_tap=None, on_long_press=None,
                 **kwargs):
        super().__init__(**kwargs)
        self._cb = {
            'swipe_left':  on_swipe_left,
            'swipe_right': on_swipe_right,
            'single_tap':  on_single_tap,
            'double_tap':  on_double_tap,
            'long_press':  on_long_press,
        }
        self._start_pos    = None
        self._es_swipe     = False
        self._long_timer   = None
        self._tap_timer    = None
        self._espera_doble = False

    # ------------------------------------------------------------------
    # Eventos de touch
    # ------------------------------------------------------------------

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        self._start_pos  = touch.pos
        self._es_swipe   = False
        self._long_timer = Clock.schedule_once(self._disparar_long_press, LONG_PRESS_T)
        return True

    def on_touch_move(self, touch):
        if self._start_pos is None:
            return False
        dx = abs(touch.pos[0] - self._start_pos[0])
        dy = abs(touch.pos[1] - self._start_pos[1])
        if dx > SWIPE_UMBRAL or dy > SWIPE_UMBRAL:
            self._es_swipe = True
            self._cancelar_long_timer()
        return True

    def on_touch_up(self, touch):
        if self._start_pos is None:
            return False
        self._cancelar_long_timer()

        if self._es_swipe:
            dx = touch.pos[0] - self._start_pos[0]
            self._limpiar_estado()
            if dx < -SWIPE_UMBRAL:
                self._fire('swipe_left')
            elif dx > SWIPE_UMBRAL:
                self._fire('swipe_right')
            return True

        # --- Tap simple o doble ---
        if self._espera_doble:
            # Segundo tap dentro de la ventana → doble tap
            self._cancelar_tap_timer()
            self._limpiar_estado()
            self._fire('double_tap')
        else:
            # Primer tap: esperar si viene un segundo
            self._espera_doble = True
            self._start_pos    = None   # listo para recibir segundo touch_down
            self._tap_timer    = Clock.schedule_once(self._confirmar_single_tap, DOBLE_TAP_T)

        return True

    # ------------------------------------------------------------------
    # Timers
    # ------------------------------------------------------------------

    def _disparar_long_press(self, dt):
        self._long_timer = None
        self._cancelar_tap_timer()
        self._limpiar_estado()
        self._fire('long_press')

    def _confirmar_single_tap(self, dt):
        self._tap_timer    = None
        self._espera_doble = False
        self._fire('single_tap')

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _cancelar_long_timer(self):
        if self._long_timer:
            self._long_timer.cancel()
            self._long_timer = None

    def _cancelar_tap_timer(self):
        if self._tap_timer:
            self._tap_timer.cancel()
            self._tap_timer = None

    def _limpiar_estado(self):
        self._start_pos    = None
        self._es_swipe     = False
        self._espera_doble = False

    def _fire(self, nombre):
        cb = self._cb.get(nombre)
        if cb:
            cb()
