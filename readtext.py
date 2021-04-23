import sqlite3
from kivy.uix.screenmanager import Screen
from itertools import islice
from kivy.properties import Clock
from kivy.base import runTouchApp
from kivy.properties import StringProperty, NumericProperty
from kivymd.uix.label import MDLabel
from kivymd.uix.list import TwoLineAvatarListItem
from kivy.uix.label import Label


class ReadText(Screen):
    reading_running = False
    text_iterator = None
    text_position = 0
    text_position_progress = 0
    event = None
    my_string = StringProperty('a')
    progress = NumericProperty(0)
    progress_text = StringProperty('')
    text_db = None
    text_left = None
    event_2 = None

    def __init__(self, text_id=2, **kwargs):
        super().__init__(**kwargs)
        self.text_id = text_id
        connection = sqlite3.connect('read_runner.db')
        cursor = connection.cursor()
        sql_statement = f'SELECT text_body FROM texts WHERE text_id = {int(text_id)}'
        cursor.execute(sql_statement)
        self.text_db = str(cursor.fetchone()[0]).split()

        sql_statement = f'SELECT text_position FROM texts WHERE text_id = {int(text_id)}'
        cursor.execute(sql_statement)
        self.text_position = cursor.fetchone()[0]
        print(self.text_position)
        self.update_status()

    def start_reading(self):
        self.reading_running = True
        self.text_position_progress = 0
        self.text_left = self.text_db[self.text_position:]
        self.text_iterator = iter(self.text_left)

        self.event = Clock.schedule_interval(self.get_next_word, 1.0/2)
        self.event_2 = Clock.schedule_interval(self.update_status, 1.0)

    def update_status(self, dt=None):
        status_text_position = self.text_position + self.text_position_progress
        self.progress = 100 - int((len(self.text_db[status_text_position:]) * 100 / len(self.text_db)))
        self.progress_text = str(self.progress)

    def get_next_word(self, dt):
        if not self.reading_running:
            return

        try:
            # print(next(islice(self.text_iterator, self.text_position, None)))
            # self.my_string = next(islice(self.text_iterator, 10, None, None))
            # text_mdlabel.text = next(islice(self.text_iterator, self.text_position, None))
            self.my_string = next(self.text_iterator)

            # self.my_string = next(islice(self.text_iterator, self.text_position, None))
            # self.text_word = next(islice(self.text_iterator, self.text_position, None))
            # print(self.ids.text_word.text)
        except StopIteration:
            print('stop iteration')
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
            self.my_string = 'stoppedreading'

    def update_data_db(self):
        connection = sqlite3.connect('read_runner.db')
        cursor = connection.cursor()

        sql_statement = f'UPDATE texts SET text_position = {self.text_position} WHERE text_id = {int(self.text_id)}'
        cursor.execute(sql_statement)

        sql_statement = f'UPDATE texts SET text_progress = {self.progress} WHERE text_id = {int(self.text_id)}'
        cursor.execute(sql_statement)

        connection.commit()

    def stop_start(self):
        if self.reading_running:
            self.stop_reading()
            self.update_data_db()
        else:
            self.start_reading()

    def go_backward(self):
        self.stop_reading()
        # TO DO make sure that it doesn't go lower than 0
        self.text_position -= 10
        self.update_status()

    def go_forward(self):
        self.stop_reading()
        # TO DO make sure that it doesn't go higher than max length
        self.text_position += 10
        self.update_status()

    def go_back(self):
        self.stop_reading()
        self.update_data_db()
        self.manager.transition.direction = 'right'
        self.manager.current = 'mainscreen'
