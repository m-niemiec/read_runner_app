import sqlite3
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import Clock
from kivy.properties import StringProperty
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen


class TextSubMenu(Screen):
    text_progress = None
    progress_text = StringProperty('')

    def __init__(self, text_id=None, **kwargs):
        super().__init__(**kwargs)

        if text_id:
            self.text_id = text_id
            self.custom_on_enter()

    def custom_on_enter(self):
        connection = sqlite3.connect('read_runner.db')
        cursor = connection.cursor()
        cursor.execute('SELECT text_progress from texts WHERE text_id = ?', (self.text_id,))

        self.text_progress = cursor.fetchone()[0]

    def delete_selected_text(self):
        connection = sqlite3.connect('read_runner.db')
        cursor = connection.cursor()
        cursor.execute('DELETE from texts WHERE text_id = ?', (self.text_id,))
        connection.commit()

    def close_text_sub_menu_dialog(self):
        # REWRITE to ANOTHER SCREEN WITH CONFIRMATION
        connection = sqlite3.connect('read_runner.db')
        cursor = connection.cursor()
        cursor.execute('UPDATE texts SET text_progress = ? WHERE text_id = ?', (self.text_progress, self.text_id))
        connection.commit()

    def move_progress_backward(self):
        if self.text_progress >= 10:
            self.text_progress -= 10
            self.update_text_progress_label()

    def move_progress_forward(self):
        if self.text_progress <= 90:
            self.text_progress += 10
            self.update_text_progress_label()

    def set_progress_as_completed(self):
        self.text_progress = 100
        self.update_text_progress_label()

    def set_progress_as_zero(self):
        self.text_progress = 0
        self.update_text_progress_label()

    def update_text_progress_label(self):
        MDApp.get_running_app().root.get_screen("mainscreen").textsubmenu.ids.progress_text.text = str(
            f'Progress - {self.text_progress}%')
