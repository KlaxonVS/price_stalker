"""
Bot container.
"""
from aiogram.utils.exceptions import ValidationError
import os

import toga
from dotenv import load_dotenv, set_key, get_key
from toga.style import Pack
from toga.style.pack import COLUMN, LEFT, CENTER

from .bot.settings import BASE_DIR
from .bot.bot_code import BotTelegram


BOT_DIR = BASE_DIR
ENV_PATH = os.path.join(BOT_DIR, '.env')
IS_ENV = load_dotenv(ENV_PATH)


class PriceStalker(toga.App):

    def startup(self):
        """
        Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        self.main_box = toga.Box(style=Pack(direction=COLUMN,))
        self.commands_box = toga.Box(style=Pack(direction=COLUMN,))
        self.input_data_box = toga.Box(style=Pack(direction=COLUMN,))
        self.error_box = toga.Box(style=Pack(direction=COLUMN,))

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.main_box
        self.main_window.show()

        def input_statuses():
            chat_id = get_key(ENV_PATH, 'CHAT_ID')
            token = get_key(ENV_PATH, 'BOT_TOKEN')
            if chat_id != 'None' and token != 'None':
                return 'Изменить id чата', 'Изменить токен бота', True
            if token != 'None':
                return 'Изменить id чата', 'Введите токен бота', False
            if chat_id != 'None':
                return 'Введите id чата', 'Изменить токен бота', False
            return 'Введите id чата', 'Введите токен бота', False

        id_label = toga.Label('Ваш id:', style=Pack(padding=5, alignment=LEFT))
        self.chat_id = toga.TextInput(
            placeholder=input_statuses()[0],
            style=Pack(padding=5, alignment=LEFT)
        )
        token_label = toga.Label(
            'Ваш токен:', style=Pack(padding=5, alignment=LEFT)
        )
        self.token = toga.TextInput(
            placeholder=input_statuses()[1],
            style=Pack(padding=5, alignment=LEFT)
        )
        error_label = toga.Label(
            'Сообщения от программы:', style=Pack(padding=5, alignment=LEFT)
        )
        self.error_text = toga.TextInput(
            value='Ошибок нет',
            readonly=True,
            style=Pack(padding=5, alignment=CENTER)
        )

        confirm_button = toga.Button(
            'Подтвердить данные',
            on_press=self.create_data,
            style=Pack(padding=5, alignment=LEFT)
        )

        self.run_button = toga.Button(
            "Запустить бот",
            on_press=self.run_bot,
            style=Pack(padding=5, alignment=LEFT),
            enabled=input_statuses()[2]
        )

        stop_button = toga.Button(
            "Выключить бот",
            on_press=self.stop_bot,
            style=Pack(padding=5, alignment=LEFT)
        )

        self.input_data_box.add(token_label)
        self.input_data_box.add(self.token)
        self.input_data_box.add(id_label)
        self.input_data_box.add(self.chat_id)
        self.input_data_box.add(confirm_button)

        self.error_box.add(error_label)
        self.error_box.add(self.error_text)

        self.commands_box.add(self.run_button)
        self.commands_box.add(stop_button)

        self.main_box.add(self.commands_box)
        self.main_box.add(self.error_box)
        self.main_box.add(self.input_data_box)

    async def run_bot(self, widget):
        chat_id = get_key(ENV_PATH, 'CHAT_ID')
        token = get_key(ENV_PATH, 'BOT_TOKEN')
        try:
            await BotTelegram(chat_id, token).run()
        except ValidationError:
            self.error_text.value = 'Токен неверен!'

    def stop_bot(self, widget):
        self.exit()

    def create_data(self, widget):
        old_id = get_key(ENV_PATH, 'CHAT_ID') if IS_ENV else None
        old_token = get_key(ENV_PATH, 'BOT_TOKEN') if IS_ENV else None
        bot_token = self.token.value if self.chat_id.value != '' else old_token
        pk = self.chat_id.value if self.chat_id.value != '' else old_id
        if bot_token is None and pk is None:
            return None
        set_key(ENV_PATH, 'CHAT_ID', pk)
        set_key(ENV_PATH, 'BOT_TOKEN', bot_token)
        print(get_key(ENV_PATH, 'CHAT_ID'), get_key(ENV_PATH, 'BOT_TOKEN'))
        self.run_button.enabled = True


def main():
    return PriceStalker()
