import sqlite3

from functools import partial

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import Clock
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import TwoLineAvatarListItem

import helper_texts
from readtext import ReadText

Window.size = (360, 780)


class MainScreen(Screen):
    help_dialog = None
    connection = None
    cursor = None

    # Custom method 'on_enter' to make sure that all ids will be already generated.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._on_enter_trig = trig = Clock.create_trigger(self.custom_on_enter)
        self.bind(on_enter=trig)

    def custom_on_enter(self, *args):
        self.ids.container.clear_widgets()
        self.connection = sqlite3.connect('read_runner.db')
        self.cursor = self.connection.cursor()
        sql_statement = 'SELECT * FROM texts'
        self.cursor.execute(sql_statement)
        texts = self.cursor.fetchall()

        for text in texts:
            item = TwoLineAvatarListItem(text=str(text[3]),
                                         secondary_text=str(text[2]),
                                         on_release=partial(self.select_text, text[0]))

            self.ids.container.add_widget(item)

    def navigation_draw(self):
        print('navigation_draw')
        pass

    def import_text(self):
        print('import_text')
        pass

    def show_instructions(self):
        if not self.help_dialog:
            self.help_dialog = MDDialog(
                text=helper_texts.help_dialog_text,
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                size_hint=(0.9, 0.8),
                buttons=[MDFlatButton(text="CANCEL", on_release=self.close_help_dialog)])

        self.help_dialog.open()

    def close_help_dialog(self, obj):
        self.help_dialog.dismiss()

    def select_text(self, text_id, obj):
        self.manager.transition.direction = 'left'
        self.manager.current = 'readtext'
        print(text_id)
        print(obj)

        ReadText(text_id=text_id)

    def close_app(self):
        # MDApp.get_running_app().stop()
        ReadRunnerApp().get_running_app().stop()


class PreferencesScreen(Screen):
    pass


class ReadRunnerApp(MDApp):
    help_dialog = None

    def build(self):
        screen = Builder.load_file('main.kv')

        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'BlueGray'
        self.theme_cls.accent_palette = 'Red'
        self.theme_cls.primary_hue = '700'

        return screen

    # def close_app(self):
    #     ReadRunnerApp().stop()


if __name__ == '__main__':
    ReadRunnerApp().run()


screen_manager = ScreenManager()
screen_manager.add_widget(MainScreen(name='mainscreen'))
screen_manager.add_widget(PreferencesScreen(name='preferencesscreen'))
screen_manager.add_widget(ReadText(name='readtext'))
