import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Command, Text, state
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

from .alt_parser import get_name_price, get_price_list
from .database import (add_item, add_items, check_item, delete_item, get_all,
                       update_item, create_database, delete_all)
from .settings import ITEM_LINK, DATABASE_NAME, BASE_DIR, INSTRUCTION
from .utils import get_id


DB_PATH = os.path.join(BASE_DIR, f'{DATABASE_NAME}.db')


class BotTelegram:
    storage = MemoryStorage()

    class SureStates(state.StatesGroup):
        sure = state.State()

    def __init__(
        self,
        chat_id,
        token,
        local: bool = False,
    ) -> None:
        self.local = local
        self.token = token
        self.chat_id = chat_id
        self.bot = Bot(token=token)
        self.dp = Dispatcher(bot=self.bot, storage=self.storage)

        @self.dp.message_handler(commands=['start'])
        async def cmd_start(message: types.Message):
            """Ответ бота на команду /start"""
            print('pants')
            await message.answer('Штаны подтянуты, можно добавлять товары!')

        @self.dp.message_handler(lambda m: not m.text.startswith('/del'),
                                 Text(contains='wildberries.ru/catalog/'))
        async def follow_item(message: types.Message,):
            if 'catalog' in message.text:
                item_id = await get_id(message.text)
                if not await check_item(item_id):
                    return await message.answer(
                        'Вы уже следите за этим товаром.'
                    )
                name, price = await get_name_price(item_id,)
                item = (item_id, price, name)
                await add_item(item)
                await message.answer('Товар добавлен!')
            else:
                await message.answer(
                    f'Убедитесь что ссылка есть в сообщении: '
                    f'{ITEM_LINK.format("id_товара")}.'
                )

        @self.dp.message_handler(commands=['get_all'])
        async def all_tems(
            message: types.Message, command: Command.CommandObj
        ):
            items = list(await get_all('item'))
            if not items:
                await message.answer('Вы ни за чем не следите!')

            text = [
                f'{num}. {item.title} ({item.price} руб.)\n'
                f'id: <u>{item.id}</u> '
                f'<a href="{ITEM_LINK.format(item.id)}">Ссылка</a>'
                for num, item in enumerate(items, start=1)
            ]
            await message.answer('\n'.join(text), parse_mode='html')

        @self.dp.message_handler(commands=['add_list'])
        async def cmd_add_list(
            message: types.Message, command: Command.CommandObj
        ):
            """Ответ бота на команду /add_list"""
            if command.args:
                items = [int(item) for item in command.args.split(' ')
                         if item.isdigit() and await check_item(int(item))]
                product_price = await get_price_list(items)
                await add_items(product_price)
                await message.answer('Товары добавлены!')
            else:
                await message.answer(
                    'Формат -- id через пробел: "/add_list 45242 2423 123..."'
                )

        @self.dp.message_handler(commands=['del'])
        async def cmd_delete(
            message: types.Message, command: Command.CommandObj
        ):
            """Ответ бота на команду /delete"""
            item_id = await get_id(command.args)
            if item_id is not None:
                if await check_item(item_id):
                    return await message.answer(
                        'Вы не следите за этим товаром.'
                    )
                await delete_item(item_id)
                await message.answer('Товар удален!')
            else:
                await message.answer(
                        f'Убедитесь что сообщение в формате:\n'
                        f'"/del {ITEM_LINK.format("id_товара")}"\n'
                        f'или просто:\n "/del {"id_товара"}"'
                    )

        @self.dp.message_handler(commands=['clear_db'])
        async def cmd_clear_db(message: types.Message, state: FSMContext):
            """Ответ бота на команду /clear_db"""
            kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
            yes_btn = types.KeyboardButton('/Да')
            not_btn = types.KeyboardButton('/Нет')
            kb.add(yes_btn, not_btn)
            await state.set_state(self.SureStates.sure)
            await message.answer(
                'Вы уверены, что хотите удалить все товары?',
                reply_markup=kb
                )

        @self.dp.message_handler(state=self.SureStates.sure,
                                 commands=('Да', 'Нет'))
        async def clear_db_confirm(message: types.Message, state: FSMContext):
            if message.get_command() == '/Да':
                await delete_all('item')
                await state.finish()
                await message.reply(
                    'Все товары удалены!',
                    reply_markup=types.ReplyKeyboardRemove()
                )
            if message.get_command() == '/Нет':
                await state.finish()
                await message.reply(
                    'Товары не тронуты!',
                    reply_markup=types.ReplyKeyboardRemove()
                )

        @self.dp.message_handler(commands=['help'])
        async def cmd_help(message: types.Message):
            """Ответ бота на команду /help"""
            await message.answer(INSTRUCTION)

    async def commands_menu(self):
        await self.dp.bot.set_my_commands([
            types.BotCommand('get_all', 'Список отслеживаемого'),
            types.BotCommand('help', 'Инструкции'),
            types.BotCommand('clear_db', 'Удалить все товары'),
        ])

    async def send_message(self, text):
        await self.bot.send_message(self.chat_id, text)

    async def scan_prices(self):
        while True:
            if not os.path.isfile(DB_PATH):
                print(DB_PATH)
                await asyncio.sleep(5)
                continue
            db_items = list(await get_all('item'))
            item_pks = [item.id for item in db_items]
            site_items = await get_price_list(item_pks)
            print(db_items, site_items)
            for item in db_items:
                site_price, title = site_items.get(item.id)
                if site_price is not None:
                    print(item.id, item.price, site_price)
                    difference = item.price - site_price
                    if difference >= 100:
                        await self.send_message(
                            f'Цена на <a href="{ITEM_LINK.format(item.id)}">'
                            f'{title}</a> снизилась на {difference} рублей.\n'
                            f'Было:{item.price}, стало: {site_price}.',
                            parse_mode='html'
                        )
                        await update_item(
                            (item.id, site_price)
                        )
                    if difference <= -100:
                        await self.send_message(
                            f'Цена на {ITEM_LINK.format(item.id)} '
                            'повысилась более чем на 100 рублей:'
                            f'{abs(difference)}', parse_mode='html'
                        )
                        await update_item((item.id, site_price))
            print('круг')
            await asyncio.sleep(60 * 30)

    async def run(self):
        print('bot is running')
        await create_database()
        await self.bot.send_message(self.chat_id, 'Начал слежку')
        if not self.local:
            loop = asyncio.get_running_loop()
            asyncio.run_coroutine_threadsafe(
                self.dp.start_polling(timeout=3), loop
            )
            asyncio.run_coroutine_threadsafe(self.scan_prices(), loop)
            return None
        menu = asyncio.create_task(self.commands_menu())
        poll = asyncio.create_task(self.dp.start_polling(timeout=3))
        scan = asyncio.create_task(self.scan_prices())
        await asyncio.gather(poll, scan, menu)


if __name__ == "__main__":
    load_dotenv(os.path.join(BASE_DIR, '.env'))

    asyncio.run(
        BotTelegram(os.getenv('CHAT_ID'), os.getenv('BOT_TOKEN'), True).run()
    )
