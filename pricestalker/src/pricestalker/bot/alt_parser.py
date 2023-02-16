from aiohttp import ClientSession

from .settings import ALT_ITEM_LINK


def session(function):
    async def wrapper(*args, **kwargs):
        session = ClientSession()
        result = await function(session, *args, **kwargs)
        await session.close()
        return result
    return wrapper


@session
async def get_name_price(
    session: ClientSession, product_id, only_check=False, only_price=False
):
    async with session:
        response = await session.get(ALT_ITEM_LINK.format(product_id),)
        content = await response.json(content_type=None)
        products = content.get('data').get('products')
        if products and only_check:
            return True
        elif products:
            product = products[0]
            final_price = int(product.get('salePriceU') / 100)
            if only_price:
                return final_price
            name = (f'{product.get("brand")} {product.get("name")}'
                    if product.get("brand") else f'{product.get("name")}')
            return name, final_price
        else:
            return False


@session
async def get_price_list(session: ClientSession, product_pks):
    to_compare = {}
    async with session:
        response = await session.get(
            ALT_ITEM_LINK.format(';'.join(str(pk) for pk in product_pks)),
            )
        content = await response.json(content_type=None)
        if products := content.get('data').get('products'):
            for product in products:
                pk = product.get('id')
                final_price = int(product.get('salePriceU') / 100)
                title = (f'{product.get("brand")} {product.get("name")}'
                         if product.get("brand") else f'{product.get("name")}')
                to_compare[pk] = (final_price, title)
            return to_compare
