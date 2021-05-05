from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen


class Help(Screen):
    def go_back(self):
        MDApp.get_running_app().root.get_screen("help").manager.transition.direction = 'right'
        MDApp.get_running_app().root.get_screen("help").manager.current = 'mainscreen'
