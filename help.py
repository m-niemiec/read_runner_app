from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp


class Help(Screen):
    @staticmethod
    def go_back():
        MDApp.get_running_app().root.get_screen('help').manager.transition.direction = 'right'
        MDApp.get_running_app().root.get_screen('help').manager.current = 'mainscreen'
