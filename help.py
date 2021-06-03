from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp


class Help(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Window.bind(on_keyboard=self.android_back_button)

    def android_back_button(self, window, key, *largs):
        if key == 27:
            self.go_back()

            return True

    @staticmethod
    def go_back():
        MDApp.get_running_app().root.get_screen('help').manager.transition.direction = 'right'
        MDApp.get_running_app().root.get_screen('help').manager.current = 'mainscreen'
