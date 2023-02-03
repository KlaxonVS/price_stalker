import asyncio

from asyncselenium.webdriver.chrome.async_webdriver import AsyncChromeDriver
from asyncselenium.webdriver.support.async_wait import AsyncWebDriverWait
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from settings import BASE_DIR, ITEM_LINK

options = webdriver.ChromeOptions()
options.headless = True
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

path = f'{BASE_DIR}/chromewin/chromedriver.exe'


async def get_prices(product_id: int, only_final=True):
    "Возвращает финальную и старую цену с сайта"
    driver = await AsyncChromeDriver(executable_path=path, options=options)
    await driver.get(
            ITEM_LINK.format(product_id),
        )
    await asyncio.sleep(5)
    if await check_product(driver):
        await asyncio.sleep(5)
        search_final = await driver.find_element_by_class_name(
                'price-block__final-price'
            )
        if only_final:
            final = await search_final.text
            await driver.quit()
            print(final)
            return int(''.join(
                [integer for integer in final if integer.isdigit()]
                ))


async def check_product(driver):
    """проверяет что страница товара существует."""
    try:
        await driver.find_element_by_class_name('content404__title')
        print('404')
        return False
    except NoSuchElementException:
        print('product exist')
        return True


async def check_18_plus(driver):
    """Если страница 18+ то закрывает вспл. окно."""
    button = await driver.find_element_by_class_name(
        'popup__btn-main.j-confirm'
        )
    if await button.is_displayed():
        await button.click()
        print('18+')


'''
async def get_prices(product_id: int, only_final=True):
    "Возвращает финальную и старую цену с сайта"
    driver = await AsyncChromeDriver(executable_path=path, options=options)
    await driver.get(
            ITEM_LINK.format(product_id),
        )
    await asyncio.sleep(5)
    if await check_product(driver):
        await asyncio.sleep(5)
        search_final = await driver.find_element_by_class_name(
                'price-block__final-price'
            )
        if only_final:
            final = await search_final.text
            await driver.quit()
            print(final)
            return int(''.join(
                [integer for integer in final if integer.isdigit()]
                ))
        search_old = await driver.find_element_by_class_name(
                'price-block__old-price'
            )
        final, old = await search_final.text, await search_old.text
        await driver.quit()
        print(final, old)
        # rewrite needed
        return [int(price.split(' ')[0]) for price in [final, old]]
'''