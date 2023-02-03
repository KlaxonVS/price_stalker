import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Command
from dotenv import load_dotenv

from parsers import get_prices
from settings import ITEM_LINK
from utils import get_id
from database import add_item, get_all, update_item


load_dotenv()


CHAT_ID = os.getenv('CHAT_ID')
BOT = Bot(token=os.getenv('BOT_TOKEN'))
DP = Dispatcher(BOT)


@DP.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    """Ответ бота на команду /start"""
    print('pants')
    await message.answer('Штаны подтянуты!')


@DP.message_handler(commands=['add'])
async def cmd_add(message: types.Message, command: Command.CommandObj):
    """Ответ бота на команду /add"""
    if command.args and 'catalog' in command.args:
        item_id = await get_id(command.args)
        price = await get_prices(item_id)
        item = (item_id, price)
        await add_item(item)
        await message.answer('Товар добавлен!')
    else:
        await message.answer(
            f'Убедитесь что ссылка в формате: {ITEM_LINK.format("id_товара")}.'
        )


async def send_message(text):
    await BOT.send_message(CHAT_ID, text)


async def scan_prices():
    while True:
        for item in await get_all('item'):
            site_price = await get_prices(item.id, True)
            difference = item.price - site_price
            if difference >= 100:
                await send_message(
                    f'Цена на {ITEM_LINK.format(item.id)} '
                    f'снизилась более чем на 100 рублей: {difference}'
                )
                await update_item((item.id, site_price))
            if difference <= -100:
                await send_message(
                    f'Цена на {ITEM_LINK.format(item.id)} '
                    f'повысилась более чем на 100 рублей: {abs(difference)}'
                )
                await update_item((item.id, site_price))
        print('круг')
        await asyncio.sleep(60 * 60)


async def main():
    """Функция main бота"""
    poll = asyncio.create_task(DP.start_polling(timeout=3))
    scan = asyncio.create_task(scan_prices())
    await asyncio.gather(poll, scan)


if __name__ == "__main__":
    asyncio.run(main())
