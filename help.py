from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp


class Help(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Window.bind(on_keyboard=self.android_back_button)

    @staticmethod
    def android_back_button(window, key, *largs):
        if key == 27:
            MDApp.get_running_app().root.get_screen('help').manager.current = 'mainscreen'

            return True

    @staticmethod
    def go_back():
        MDApp.get_running_app().root.get_screen('help').manager.transition.direction = 'right'
        MDApp.get_running_app().root.get_screen('help').manager.current = 'mainscreen'
