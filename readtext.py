import json
import sqlite3

from kivy.properties import Clock, StringProperty, NumericProperty
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp


class ReadText(Screen):
    reading_running = False
    text_iterator = None
    text_position = 0
    text_position_progress = 0
    event = None
    progress = NumericProperty(0)
    progress_text = StringProperty('')
    text_db = None
    text_left = None
    event_2 = None
    text_id = None
    text_data = None
    preferences_data = None

    def __init__(self, text_id=None, **kwargs):
        super().__init__(**kwargs)

        if text_id:
            self.text_id = text_id

            self.get_text_data()
            self.update_status(progress=self.progress)
            self.get_user_preferences()

    def get_text_data(self):
        connection = sqlite3.connect('read_runner.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM texts WHERE text_id = (?)', (self.text_id, ))
        self.text_data = cursor.fetchone()
        self.text_db = str(self.text_data[6]).split()
        self.text_position = self.text_data[1]
        self.progress = self.text_data[2]

    def get_user_preferences(self):
        connection = sqlite3.connect('read_runner.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * from preferences')

        self.preferences_data = json.loads(cursor.fetchone()[0])
        self.use_user_preferences()

    def use_user_preferences(self):
        if self.preferences_data['word_size'] == 'small':
            MDApp.get_running_app().root.get_screen("readtext").ids.text_word.font_style = 'Body1'
        elif self.preferences_data['word_size'] == 'medium':
            MDApp.get_running_app().root.get_screen("readtext").ids.text_word.font_style = 'H5'
        elif self.preferences_data['word_size'] == 'large':
            MDApp.get_running_app().root.get_screen("readtext").ids.text_word.font_style = 'H4'

        if self.preferences_data['word_size'] == 'bright':
            MDApp.get_running_app().root.get_screen("readtext").ids.text_word.font_style = 'Primary'
        elif self.preferences_data['word_size'] == 'dark':
            MDApp.get_running_app().root.get_screen("readtext").ids.text_word.font_style = 'Hint'

    def start_reading(self):
        self.reading_running = True
        self.text_position_progress = 0
        self.text_left = self.text_db[self.text_position:]
        self.text_iterator = iter(self.text_left)
        self.event = Clock.schedule_interval(self.get_next_word, 1.0/(int(self.preferences_data['reading_speed'])/60))
        self.event_2 = Clock.schedule_interval(self.update_status, 1.0)

    def update_status(self, dt=None, progress=None):
        status_text_position = self.text_position + self.text_position_progress
        self.progress = 100 - int((len(self.text_db[status_text_position:]) * 100 / len(self.text_db)))

        MDApp.get_running_app().root.get_screen("readtext").ids.progress_bar.value = self.progress
        MDApp.get_running_app().root.get_screen("readtext").ids.progress_text.text = str(self.progress)

    def get_next_word(self, dt):
        if not self.reading_running:
            return

        try:
            MDApp.get_running_app().root.get_screen("readtext").ids.text_word.text = next(self.text_iterator)
        except StopIteration:
            self.event.cancel()
            self.stop_reading()

        self.text_position_progress += 1

    def stop_reading(self):
        if self.reading_running:
            self.event_2.cancel()
            self.event.cancel()
            self.reading_running = False
            self.text_position += self.text_position_progress
            self.text_position_progress = 0

    def update_data_db(self):
        connection = sqlite3.connect('read_runner.db')
        cursor = connection.cursor()

        cursor.execute('UPDATE texts SET text_position = (?) WHERE text_id = (?)', (self.text_position, self.text_id))

        cursor.execute('UPDATE texts SET text_progress = (?) WHERE text_id = (?)', (self.progress, self.text_id))

        connection.commit()

    def stop_start(self):
        if self.reading_running:
            self.stop_reading()
            self.update_data_db()
        else:
            self.start_reading()

    def go_backward(self):
        self.stop_reading()

        if self.text_position - 10 < 0:
            self.text_position = 0
        else:
            self.text_position -= 10

        self.update_status()

    def go_forward(self):
        self.stop_reading()

        if self.text_position + 10 > len(self.text_db):
            self.text_position = len(self.text_db)
        else:
            self.text_position += 10

        self.update_status()

    def go_back(self):
        self.stop_reading()
        self.update_data_db()

        MDApp.get_running_app().root.get_screen("readtext").manager.transition.direction = 'right'
        MDApp.get_running_app().root.get_screen("readtext").manager.current = 'mainscreen'
