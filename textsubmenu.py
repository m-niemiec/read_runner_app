from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen


class TextSubMenu(BoxLayout):
    def __init__(self, text_id=None, **kwargs):
        super().__init__(**kwargs)

        self.text_id = text_id
        print('works')
