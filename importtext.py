import re

from kivy.core.clipboard import Clipboard
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.filemanager import MDFileManager


class ImportText(Screen):
    imported_text = StringProperty('')
    text = None
    manager_open = False
    file_manager = None

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
        text_file_path = path
        self.exit_manager()
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

        self.save_new_text_data(new_text)

    def import_pdf_file(self, text_file_path):
        pass

    def import_mobi_file(self, text_file_path):
        pass

    def save_new_text_data(self, new_text):
        print(new_text)
        pass
