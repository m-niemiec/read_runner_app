import json
import sqlite3

from kivy.properties import Clock
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp


class Preferences(Screen):
    preferences_data = None

    def __init__(self, **kw):
        super().__init__(**kw)

        self._on_enter_trig = trig = Clock.create_trigger(self.custom_on_enter)
        self.bind(on_enter=trig)

    def custom_on_enter(self, *args):
        connection = sqlite3.connect('read_runner.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * from preferences')

        self.preferences_data = json.loads(cursor.fetchone()[0])

        MDApp.get_running_app().root.get_screen("preferences").ids.reading_speed.text = self.preferences_data['reading_speed']

        if self.preferences_data['word_size'] == 'small':
            MDApp.get_running_app().root.get_screen("preferences").ids.checkbox_word_size_small.active = True
        elif self.preferences_data['word_size'] == 'medium':
            MDApp.get_running_app().root.get_screen("preferences").ids.checkbox_word_size_medium.active = True
        else:
            MDApp.get_running_app().root.get_screen("preferences").ids.checkbox_word_size_large.active = True

        if self.preferences_data['word_brightness'] == 'bright':
            MDApp.get_running_app().root.get_screen("preferences").ids.checkbox_brightness_bright.active = True
        else:
            MDApp.get_running_app().root.get_screen("preferences").ids.checkbox_brightness_dark.active = True

    def change_word_brightness(self, brightness):
        if brightness and self.preferences_data and brightness != self.preferences_data['word_brightness']:
            self.preferences_data['word_brightness'] = brightness

    def change_word_size(self, size):
        if size and self.preferences_data and size != self.preferences_data['word_size']:
            self.preferences_data['word_size'] = size

    def save_new_preferences(self):
        self.preferences_data['reading_speed'] = MDApp.get_running_app().root.get_screen("preferences").ids.reading_speed.text

        connection = sqlite3.connect('read_runner.db')
        cursor = connection.cursor()
        cursor.execute("DROP TABLE preferences")
        cursor.execute("CREATE TABLE preferences (data json)")
        cursor.execute("INSERT INTO preferences VALUES (?)", [json.dumps(self.preferences_data)])

        connection.commit()
        connection.close()

    @staticmethod
    def go_back():
        MDApp.get_running_app().root.get_screen("preferences").manager.transition.direction = 'right'
        MDApp.get_running_app().root.get_screen("preferences").manager.current = 'mainscreen'
