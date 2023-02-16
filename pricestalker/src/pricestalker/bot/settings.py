import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ITEM_LINK = 'https://www.wildberries.ru/catalog/{}/detail.aspx'
ALT_ITEM_LINK = 'https://card.wb.ru/cards/detail?lang=ru&curr=rub&nm={}'
DATABASE_NAME = 'wildberries_db'

INSTRUCTION = ('🔎Чтобы установить слежку за товаром просто пришлите боту '
               'сообщение содержащие ссылку на товар.\n Для добавления '
               'нескольких товаров сообщение должно начинаться с\n/add_list '
               'id_товара id_товара и так далее через пробел.\nid_товара '
               'находится в ссылке: wildberries.ru/catalog/id_товара/'
               'detail.aspx📄\nДля получения списка'
               'отслеживаемого отправте команду /get_all из меню или просто '
               'сообщением.\n🗑 Для удаления товара из отслеживаемого '
               'отправьте сообшение начинающиеся с /del и через пробел: либо '
               'скопируйте ссылку на товар из /get_all, либо id товара')
