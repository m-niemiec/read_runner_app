from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp


class Help(Screen):
    def go_back(self):
        MDApp.get_running_app().root.get_screen("help").manager.transition.direction = 'right'
        MDApp.get_running_app().root.get_screen("help").manager.current = 'mainscreen'
