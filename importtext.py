import os
import re
import shutil
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from functools import partial

import html2text
import mobi
import pdfplumber
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.filemanager import MDFileManager

import ebooklib
from ebooklib import epub

if platform == 'android':
    from android.storage import primary_external_storage_path


class TextLoading(Screen):
    import_progress = StringProperty('Estimating file size ...')


class ImportText(Screen):
    primary_ext_storage = primary_external_storage_path()
    imported_text = StringProperty('')
    text = None
    manager_open = False
    file_manager = None
    instructions_dialog = None
    text_loading_dialog = None
    new_text = None
    text_loading = None
    error_dialog = None
    pdf_page_count = 0
    import_progress = StringProperty('0%')

    def __init__(self, **kw):
        super().__init__(**kw)
        self.clear_temp_database()

        Window.bind(on_keyboard=self.android_back_button)

    def import_from_file(self):
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path
        )
        self.file_manager.ext = ['.txt', '.pdf', '.mobi', '.epub', '.TXT', '.PDF', '.MOBI', '.EPUB']

        # For PC:
        # self.file_manager.show('/')
        # For Android:
        self.file_manager.show(self.primary_ext_storage)

        self.manager_open = True

    def select_path(self, path):
        text_file_path = path
        toast(text_file_path)

        self.show_text_loading()
        self.exit_manager()

        executor = ThreadPoolExecutor(5)
        executor.submit(partial(self.determine_file_type, text_file_path))

    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()

    def determine_file_type(self, text_file_path):
        if re.search(r'\S+.txt', text_file_path, re.IGNORECASE):
            self.import_txt_file(text_file_path)
        elif re.search(r'\S+.pdf', text_file_path, re.IGNORECASE):
            self.import_pdf_file(text_file_path)
        elif re.search(r'\S+.mobi', text_file_path, re.IGNORECASE):
            self.import_mobi_file(text_file_path)
        elif re.search(r'\S+.epub', text_file_path, re.IGNORECASE):
            self.import_epub_file(text_file_path)
        else:
            self.show_error('Wrong file type selected. Please choose another one.')

    def import_txt_file(self, text_file_path):
        with open(text_file_path, encoding='utf-8-sig') as file:
            new_text = file.readlines()

        MDApp.get_running_app().root.get_screen("importtext").ids.imported_text_field.text = f'{new_text[:1000]} ... '

        self.save_temp_data(new_text)

        self.text_loading_dialog.dismiss()

    def import_pdf_file(self, text_file_path, obj=None):
        pdf_page_count = len(pdfplumber.open(text_file_path).pages)

        with pdfplumber.open(text_file_path) as pdf:
            for counter, page in enumerate(pdf.pages[:50], start=1):
                import_progress = '{:.2f}'.format(counter / pdf_page_count * 100)
                counter += 1

                self.text_loading.import_progress = f'Imported - {import_progress}%'

                new_text = str(page.extract_text()).replace('\n', ' ').encode('ascii', 'ignore').decode()

                self.save_temp_data(new_text)

                # We want to flush cache every loop to save as much RAM as possible.
                page.flush_cache()

        self.text_loading_dialog.dismiss()
        self.update_text_preview()

    def import_mobi_file(self, text_file_path):
        tempdir, filepath = mobi.extract(text_file_path)

        # If extracted MOBI file has extension TXT that means that everything worked properly.
        if re.search(r'\S+.txt|\S+.html', filepath, re.IGNORECASE):
            file = open(filepath, 'r', errors='ignore')
            content = file.read()
            new_text = html2text.html2text(content.replace('\\n', '')).encode('ascii', 'ignore').decode()

            self.save_temp_data(new_text)

            shutil.rmtree(tempdir, ignore_errors=True)
        # In other case (for example extracted file has EPUB format) that means that MOBI file was encrypted and
        # content will be corrupted.
        else:
            self.text_loading_dialog.dismiss()
            self.show_error('Something went wrong :( The file provided cannot be processed. Please try another one.')

        self.update_text_preview()
        self.text_loading_dialog.dismiss()

    def import_epub_file(self, text_file_path):
        book = epub.read_epub(text_file_path)
        epub_page_count = len(book.items)

        for counter, item in enumerate(book.get_items(), start=1):
            import_progress = '{:.2f}'.format(counter / epub_page_count * 100)
            counter += 1

            self.text_loading.import_progress = f'Imported - {import_progress}%'

            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                new_text = html2text.html2text(str(item.get_content()).replace('\\n', '')).encode('ascii', 'ignore').decode()

                self.save_temp_data(new_text)

        self.update_text_preview()
        self.text_loading_dialog.dismiss()

    def save_new_text(self):
        text_title = MDApp.get_running_app().root.get_screen('importtext').ids.imported_text_title_field.text
        text_author = MDApp.get_running_app().root.get_screen('importtext').ids.imported_text_author_field.text
        text_body_preview = MDApp.get_running_app().root.get_screen('importtext').ids.imported_text_field.text

        if text_title == '':
            return self.show_instructions('Please add title.')

        if text_body_preview == ' (import text to see preview ...)' or text_body_preview == '':
            return self.show_instructions('Please add text.')

        try:
            text_type = MDApp.get_running_app().root.get_screen('importtext').imported_text_type
        except AttributeError:
            return self.show_instructions('Please select text type.')

        connection = sqlite3.connect(os.path.join(getattr(MDApp.get_running_app(), 'user_data_dir'), 'read_runner.db'))
        cursor = connection.cursor()

        cursor.execute('INSERT INTO texts (text_body) SELECT text_body FROM temp_data')

        last_row_id = cursor.lastrowid

        cursor.execute('UPDATE texts SET text_position=0, text_progress=0, text_type=(?), text_title=(?), '
                       'text_author=(?) WHERE text_id = (?)', (text_type, text_title, text_author, last_row_id))

        connection.commit()
        connection.close()

        self.go_back()

        self.clear_temp_database()

    def show_instructions(self, warning_text):
        self.instructions_dialog = MDDialog(
            text=warning_text,
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(0.9, 0.8),
            buttons=[MDFlatButton(text='CANCEL', on_release=self.close_instructions_dialog)])

        self.instructions_dialog.open()

    def close_instructions_dialog(self, obj):
        self.instructions_dialog.dismiss()

    def show_text_loading(self):
        self.text_loading = TextLoading()

        self.text_loading_dialog = MDDialog(
            type='custom',
            content_cls=self.text_loading,
            auto_dismiss=False)

        self.text_loading_dialog.open()

    def show_error(self, error_text):
        self.error_dialog = MDDialog(
            text=error_text,
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(0.9, 0.8),
            buttons=[MDFlatButton(text='CANCEL', on_release=self.close_error_dialog)])

        self.error_dialog.open()

    def close_error_dialog(self, obj):
        self.error_dialog.dismiss()

    @staticmethod
    def import_from_clipboard():
        imported_text = Clipboard.paste()
        MDApp.get_running_app().root.get_screen("importtext").ids.imported_text_field.text = f'{imported_text[:1000]} ... '

    @staticmethod
    def update_text_preview():
        connection = sqlite3.connect(os.path.join(getattr(MDApp.get_running_app(), 'user_data_dir'), 'read_runner.db'))
        cursor = connection.cursor()

        cursor.execute('SELECT * from temp_data')
        new_text_preview = cursor.fetchone()[0][:1000]

        MDApp.get_running_app().root.get_screen('importtext').ids.imported_text_field.text = f'{new_text_preview} ... '

    @staticmethod
    def save_temp_data(text_body):
        connection = sqlite3.connect(os.path.join(getattr(MDApp.get_running_app(), 'user_data_dir'), 'read_runner.db'))
        cursor = connection.cursor()

        cursor.execute('CREATE TABLE IF NOT EXISTS temp_data (text_body text, id integer primary key )')

        cursor.execute('INSERT INTO temp_data(text_body, id) VALUES (?, 1) ON CONFLICT (id) DO UPDATE SET text_body = text_body || (?)', (text_body, text_body))

        connection.commit()

    @staticmethod
    def clear_temp_database():
        connection = sqlite3.connect(os.path.join(getattr(MDApp.get_running_app(), 'user_data_dir'), 'read_runner.db'))

        cursor = connection.cursor()
        cursor.execute('DROP TABLE IF EXISTS temp_data')

        connection.commit()

    @staticmethod
    def android_back_button(window, key, *largs):
        if key == 27:
            MDApp.get_running_app().root.get_screen('importtext').manager.current = 'mainscreen'

            return True

    @staticmethod
    def go_back():
        MDApp.get_running_app().root.get_screen('importtext').manager.transition.direction = 'right'
        MDApp.get_running_app().root.get_screen('importtext').manager.current = 'mainscreen'

        MDApp.get_running_app().root.get_screen('importtext').ids.imported_text_title_field.text = ''
        MDApp.get_running_app().root.get_screen('importtext').ids.imported_text_author_field.text = ''
        MDApp.get_running_app().root.get_screen('importtext').ids.imported_text_field.text = ' (import text to see preview ...)'
