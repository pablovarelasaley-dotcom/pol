from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import get_color_from_hex
from src.widgets.icon_button import IconButton

COLOR_BTN_LOGO   = get_color_from_hex('#16213e')
COLOR_BTN_VIDEOS = get_color_from_hex('#0f3460')


class MenuScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', spacing=8, padding=[12, 12, 12, 12])

        btn_logo = IconButton(
            icon='image-outline',
            text='LOGO',
            callback=self._on_logo,
            icon_size='88sp',
            text_size='42sp',
            bg_color=COLOR_BTN_LOGO,
            radio=20,
        )
        btn_videos = IconButton(
            icon='play-box-multiple-outline',
            text='VIDEOS',
            callback=self._on_videos,
            icon_size='88sp',
            text_size='42sp',
            bg_color=COLOR_BTN_VIDEOS,
            radio=20,
        )

        layout.add_widget(btn_logo)
        layout.add_widget(btn_videos)
        self.add_widget(layout)

    def _on_logo(self):
        self.manager.current = 'logo'

    def _on_videos(self):
        self.manager.current = 'gallery'
