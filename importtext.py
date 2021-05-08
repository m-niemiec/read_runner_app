import re
import sqlite3
import uuid
import pdfplumber

from kivy.core.clipboard import Clipboard
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivy.properties import Clock
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton


class ImportText(Screen):
    imported_text = StringProperty('')
    text = None
    manager_open = False
    file_manager = None
    warning_dialog = None
    text_loading_dialog = None
    new_text = None

    def import_from_clipboard(self):
        self.imported_text = Clipboard.paste()
        MDApp.get_running_app().root.get_screen("importtext").ids.imported_text_field.text = self.imported_text

    def import_from_file(self):
        path = '/'
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path
        )
        self.file_manager.ext = [".txt", ".pdf"]
        self.file_manager.show(path)
        self.manager_open = True

    def file_manager_open(self):
        self.file_manager.show('/')
        self.manager_open = True

    def select_path(self, path):
        self.exit_manager()
        import time
        time.sleep(1)
        text_file_path = path
        toast(text_file_path)
        self.determine_file_type(text_file_path)

    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()

    def determine_file_type(self, text_file_path):
        if re.search(r'\S+.txt|\S+.TXT', text_file_path):
            self.import_txt_file(text_file_path)
        elif re.search(r'\S+.pdf|\S+.PDF', text_file_path):
            self.import_pdf_file(text_file_path)
        elif re.search(r'\S+.mobi|\S+.MOBI', text_file_path):
            self.import_mobi_file(text_file_path)
        else:
            pass
            # show dialog about wrong file type

    def import_txt_file(self, text_file_path):
        with open(text_file_path, encoding='utf-8-sig') as file:
            new_text = file.readlines()

        MDApp.get_running_app().root.get_screen("importtext").ids.imported_text_field.text = new_text

    def import_pdf_file(self, text_file_path):

        self.text_loading()

        i = 0
        new_text = ''

        with pdfplumber.open(text_file_path) as pdf:
            for page in pdf.pages[:10]:
                print(i)
                i += 1

                new_text += str(page.extract_text()).replace('\n', ' ')

                # connection = sqlite3.connect('read_runner.db')
                # cursor = connection.cursor()
                # cursor.execute("INSERT INTO temp_text VALUES (?, ?)",
                #                (text_file_path, str(page.extract_text()).replace('\n', ' ')))

                # cursor.execute("UPDATE temp_text SET text_body = text_body + ? WHERE text_id = ",
                #                (text_file_path, str(page.extract_text()).replace('\n', ' ')))

                # test = str(page.extract_text()).replace('\n', ' ')

                # cursor.execute(f"UPDATE temp_text SET text_body = text_body + (?)", (test, ))
                #
                # connection.commit()

                del page._objects
                del page._layout

        self.new_text = new_text

        MDApp.get_running_app().root.get_screen("importtext").ids.imported_text_field.text = new_text[:100]

        # self.text_loading_dialog.dismiss()

    def import_mobi_file(self, text_file_path):
        pass

    # def select_text_type(self, text_type):
    #     print(text_type)

    def save_new_text(self):
        text_title = MDApp.get_running_app().root.get_screen("importtext").ids.imported_text_title_field.text
        text_author = MDApp.get_running_app().root.get_screen("importtext").ids.imported_text_author_field.text
        text_body = MDApp.get_running_app().root.get_screen("importtext").ids.imported_text_field.text

        if text_title == '':
            return self.show_instructions('Please add title.')

        if text_body == '':
            return self.show_instructions('Please add text.')

        try:
            text_type = MDApp.get_running_app().root.get_screen("importtext").imported_text_type
        except AttributeError:
            return self.show_instructions('Please select text type.')

        new_id = str(uuid.uuid4()).replace('-', '')

        print(text_title)
        print(text_author)
        print(text_body)
        print(text_type)

        connection = sqlite3.connect('read_runner.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * from texts WHERE text_id = ?', (new_id,))

        if not cursor.fetchone():
            cursor.execute('INSERT INTO texts VALUES (?, 0, 0, ?, ?, ?, ?)',
                           (new_id, text_type, text_title, text_author, text_body[0]))
        else:
            self.save_new_text_data(self.save_new_text)

        connection.commit()
        connection.close()

    def show_instructions(self, warning_text):
        self.warning_dialog = MDDialog(
            text=warning_text,
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(0.9, 0.8),
            buttons=[MDFlatButton(text="CANCEL", on_release=self.close_help_dialog)])

        self.warning_dialog.open()

    def close_help_dialog(self, obj):
        self.warning_dialog.dismiss()

    def text_loading(self):
        print("im here")
        MDApp.get_running_app().root.get_screen("readtext").manager.transition.direction = 'right'
        MDApp.get_running_app().root.get_screen("readtext").manager.current = 'mainscreen'

    def text_loading_close(self):
        self.text_loading_dialog.dismiss()
