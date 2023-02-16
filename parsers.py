import asyncio

from asyncselenium.webdriver.chrome.async_webdriver import AsyncChromeDriver
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from asyncselenium.webdriver.support.async_wait import AsyncWebDriverWait
from asyncselenium.webdriver.support import async_expected_conditions as ec

from settings import BASE_DIR, ITEM_LINK

options = webdriver.ChromeOptions()
options.headless = True
options.page_load_strategy = 'normal'
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

path = f'{BASE_DIR}/chromewin/chromedriver.exe'


async def get_prices(product_id: int, only_final=True):
    "Возвращает финальную и старую цену с сайта"
    driver = await AsyncChromeDriver(executable_path=path, options=options)
    waiter = AsyncWebDriverWait(driver, 5)
    await driver.get(
            ITEM_LINK.format(product_id),
        )
    if await check_product(driver):
        search_final = await waiter.until(ec.presence_of_element_located(
            (By.CLASS_NAME, 'price-block__final-price')
            ))
        if only_final:
            final = await search_final.text
            await driver.quit()
            return int(''.join(
                [integer for integer in final if integer.isdigit()]
                ))
        # there is might be branch to gey multiply dom elements


async def check_product(driver):
    """проверяет что страница товара существует."""
    try:
        await asyncio.sleep(1)
        await driver.find_element_by_class_name('content404__title')
        return False
    except NoSuchElementException:
        print('product exist')
        return True


async def check_18_plus(driver):
    """Если страница 18+ то закрывает вспл. окно."""
    asyncio.sleep(1)
    button = await driver.find_element_by_class_name(
        'popup__btn-main.j-confirm'
        )
    if await button.is_displayed():
        await button.click()
