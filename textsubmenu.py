import sqlite3
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import Clock
from kivy.properties import StringProperty
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog


class TextSubMenu(Screen):
    text_progress = None
    text_data = None
    delete_dialog = None

    def __init__(self, text_id=None, **kwargs):
        super().__init__(**kwargs)

        if text_id:
            self.text_id = text_id
            self.custom_on_enter()

    def custom_on_enter(self):
        connection = sqlite3.connect('read_runner.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * from texts WHERE text_id = ?', (self.text_id,))

        self.text_data = cursor.fetchone()
        self.text_progress = self.text_data[2]

    def delete_selected_text(self):
        if not self.delete_dialog:
            self.delete_dialog = MDDialog(
                title='WARNING!',
                text='Are you sure that you want to delete this text?',
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                size_hint=(0.9, 0.8),
                buttons=[MDFlatButton(text="YES, delete it!", on_release=self.confirm_deletion),
                         MDFlatButton(text="NO, take me back!", on_release=self.close_delete_dialog)])

        self.delete_dialog.open()

    def close_delete_dialog(self, obj=None):
        self.delete_dialog.dismiss()

    def close_text_sub_menu_dialog(self, obj):
        connection = sqlite3.connect('read_runner.db')
        cursor = connection.cursor()
        cursor.execute('UPDATE texts SET text_progress = ? WHERE text_id = ?', (self.text_progress, self.text_id))
        connection.commit()

        MDApp.get_running_app().root.get_screen("mainscreen").custom_on_enter()
        MDApp.get_running_app().root.get_screen("mainscreen").text_sub_menu_dialog.dismiss()

    def confirm_deletion(self, obj):
        connection = sqlite3.connect('read_runner.db')
        cursor = connection.cursor()
        cursor.execute('DELETE FROM texts WHERE text_id = ?', (self.text_id,))
        connection.commit()

        MDApp.get_running_app().root.get_screen("mainscreen").custom_on_enter()
        MDApp.get_running_app().root.get_screen("mainscreen").text_sub_menu_dialog.dismiss()
        self.close_delete_dialog()

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
            f'You changed your progress to {self.text_progress}% !')
