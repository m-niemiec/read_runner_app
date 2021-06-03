import os
import sqlite3
from functools import partial
from shutil import copy

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import Clock
from kivy.uix.screenmanager import Screen, WipeTransition
from kivy.utils import platform, get_color_from_hex
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import IconLeftWidget, IconRightWidget, ThreeLineAvatarIconListItem

import helper_texts
from help import Help
from importtext import ImportText
from preferences import Preferences
from readtext import ReadText
from textsubmenu import TextSubMenu

# Ask for necessary permissions while running on android platform.
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

'''
Read Runner app works best on Kivy 2.0.0 and kivymd 0.104.1 (currently from pip, NOT from master branch on GitHub).
List of changes made to source file of KivyMD:
    - dialog.py - lines 504 and 507. Changed width values to fix problem with custom type MDDialog.
'''

# Temp windows size hard coded for developing process.
# Window.size = (360, 780)


class MainScreen(Screen):
    help_dialog = None
    text_id = None
    readtext = None
    importtext = None
    textsubmenu = None
    menu = None
    text_sub_menu_dialog = None
    preferences = None
    help = None

    # Custom method 'on_enter' to make sure that all ids will be already generated.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._on_enter_trig = trig = Clock.create_trigger(self.custom_on_enter)
        self.bind(on_enter=trig)

        Window.bind(on_keyboard=self.android_back_button)

    def custom_on_enter(self, *args):
        self.manager.transition = WipeTransition(clearcolor=get_color_from_hex('#303030'), duration=0.2)

        self.ids.container.clear_widgets()

        connection = sqlite3.connect(os.path.join(getattr(MDApp.get_running_app(), 'user_data_dir'), 'read_runner.db'))
        cursor = connection.cursor()

        try:
            cursor.execute('SELECT * FROM texts')
        except sqlite3.OperationalError:
            copy('read_runner.db', os.path.join(getattr(MDApp.get_running_app(), 'user_data_dir')))

        texts = cursor.fetchall()

        for text in texts:
            icon_left = IconLeftWidget(icon='book-open-variant' if text[3] == 'Book' else 'note-text-outline',
                                       on_release=partial(self.select_text, text[0]))
            icon_right = IconRightWidget(icon='dots-vertical', on_release=partial(self.show_text_sub_menu, text[0]))
            item = ThreeLineAvatarIconListItem(text=str(text[4]),
                                               secondary_text=str(text[5]),
                                               tertiary_text=f'Progress - {text[2]}%',
                                               on_release=partial(self.select_text, text[0]))

            item.add_widget(icon_left)
            item.add_widget(icon_right)

            self.ids.container.add_widget(item)

    def import_text(self):
        self.manager.current = 'importtext'

        self.importtext = ImportText()

    def show_text_sub_menu(self, text_id, obj):
        self.textsubmenu = TextSubMenu(text_id)

        self.text_sub_menu_dialog = MDDialog(
            type='custom',
            content_cls=self.textsubmenu,
            auto_dismiss=False,
            buttons=[MDFlatButton(text='CANCEL', on_release=self.textsubmenu.close_text_sub_menu_dialog)])

        self.text_sub_menu_dialog.open()

    def show_instructions(self):
        self.help_dialog = MDDialog(
            text=helper_texts.help_dialog_text,
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(0.9, 0.8),
            buttons=[MDFlatButton(text='CANCEL', on_release=self.close_help_dialog)])

        self.help_dialog.open()

    def close_help_dialog(self, obj):
        self.help_dialog.dismiss()

    def select_text(self, text_id, obj):
        self.manager.current = 'readtext'

        self.readtext = ReadText(text_id=text_id)

    def view_preferences(self):
        self.manager.current = 'preferences'

        self.preferences = Preferences()

    def view_help(self):
        self.manager.current = 'help'

        self.help = Help()

    @staticmethod
    def android_back_button(window, key, *largs):
        if key == 27:
            return True

    @staticmethod
    def close_app():
        exit()


class ReadRunnerApp(MDApp):
    help_dialog = None

    def build(self):
        screen = Builder.load_file('main.kv')

        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'BlueGray'
        self.theme_cls.accent_palette = 'Red'
        self.theme_cls.primary_hue = '700'

        return screen


if __name__ == '__main__':
    ReadRunnerApp().run()
