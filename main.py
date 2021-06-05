import asyncio
from pprint import pprint
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Command, Text
from aiogram.types import InputFile
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from datetime import datetime, date, timedelta
import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import locale
import aioschedule as scheduleS

import project_settings

class SQLighter:
    def __init__(self, database_file):
        """Подключаемся к бд и сохраняем курсор соиденения"""
        self.connection = sqlite3.connect(database_file)
        self.cursor= self.connection.cursor()

    def url_add(self, url, price, nalichie):
        with self.connection:
            self.cursor.execute("INSERT INTO `tovar` (url, price, nalichie) VALUES(?, ?, ?)", (url, price, nalichie))

    def url_exists(self, url):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `tovar` WHERE `url` = ? ", (url,)).fetchall()
            return bool(len(result))

    def url_execute(self, url):
        with self.connection:
            result = self.cursor.execute("SELECT url, price, nalichie FROM tovar WHERE url = ?", (url,)).fetchall()
            car_price = {}
            for row in result:
                car_price.update({'url': row[0]})
                car_price.update({'price': row[1]})
                car_price.update({'nalichie': row[2]})
            return car_price

    def url_update(self, price, nalichie, url):
        with self.connection:
            self.cursor.execute("UPDATE tovar SET price = ?, nalichie = ? WHERE url = ?", (price, nalichie, url))


db = SQLighter(project_settings.BASE_DIR / 'rozetka.db')


TOKEN = project_settings.TOKEN
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
ADMINS = project_settings.ADMINS


async def shutdown(uka):
    for admin in ADMINS:
        await bot.send_message(admin, 'Я упал:(')


async def parse():
   # print('--------------------------------------------------------')
   # print(datetime.now())
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'}
    page_link = project_settings.PAGE_LINK
    response = requests.get(page_link, headers=headers)
    html = response.content.decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    allGoodsOnPage = soup.find_all('li', attrs={'class': 'catalog-grid__cell catalog-grid__cell_type_slim ng-star-inserted'})
    for singleGood in allGoodsOnPage:
        title = singleGood.find('span', attrs={'class': 'goods-tile__title'}).text
        img = singleGood.find('img', attrs={'class': 'lazy_img_hover display-none'})['src']
        nalichie = singleGood.find('div', attrs={'class': 'goods-tile__availability'}).text[1:-1]
        url = singleGood.find('a', attrs={'class': 'goods-tile__picture'})['href']
        try:
            price = singleGood.find('span', {'class': 'goods-tile__price-value'}).text
        #    print('price', price)
        except:
            price = 'NONE'
       # print(f'{allGoodsOnPage.index(singleGood)} / {len(allGoodsOnPage)} - {url}')
        if nalichie == 'Є в наявності':
            nalichie = '✅Є в наявності'
            price = singleGood.find('span', attrs={'class': 'goods-tile__price-value'}).text
        elif nalichie == 'Закінчився':
            nalichie = '❌Закінчився'
        if not db.url_exists(url):
          #  print(f'{url} - exists')
            db.url_add(url, price, nalichie)
            for admin in ADMINS:
                await bot.send_photo(admin, caption=f'*🆕НОВЫЙ ТОВАР*\n*{title}*\n{nalichie}\n💰{price}грн\n🔗{url}', photo=img,parse_mode='Markdown')
        elif db.url_execute(url):
            tovar = db.url_execute(url)
            if price != tovar.get('price') or nalichie != tovar.get('nalichie'):
                for admin in ADMINS:
                    await bot.send_photo(admin,caption=f'❗*ИЗМЕНЕНИЯ В ТОВАРЕ*❗\n*'f'{title}*\n''*СТАРАЯ ИНФОРМАЦИЯ*: \n'f'{tovar.get("nalichie")}\n'f'❌{tovar.get("price")}грн\n''*🆕НОВАЯ ИНФОРМАЦИЯ*: \n'f'{nalichie}\n'f'💰{price}грн\n'f'🔗{url}',photo=img, parse_mode='Markdown')
                    db.url_update(price=price, nalichie=nalichie, url=url)


async def scheduler(x):
    scheduleS.every(15).seconds.do(parse)
    while True:
        await scheduleS.run_pending()
        await asyncio.sleep(1)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=scheduler, on_shutdown=shutdown('ads'))
