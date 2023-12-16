import logging
import config as cfg
import murkups as nav
import requests

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import ContentTypes, Message
from background import keep_alive
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from urllib.parse import urljoin

API_TOKEN = cfg.TOKEN

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


def extract_links_from_section(section, base_url):
  soup = BeautifulSoup(str(section), 'html.parser')
  links = {urljoin(base_url, a['href']) for a in soup.find_all('a', href=True)}
  return list(links)

# Function for image
def extract_section(url, section_class):
  response = requests.get(url)

  if response.status_code == 200:
      soup = BeautifulSoup(response.text, 'html.parser')

      section_content = soup.find('section', class_=section_class)

      if section_content:
          links = extract_links_from_section(section_content, url)
          return '\n\n'.join(links[:17])
      else:
          return f"Секция с классом '{section_class}' не найдена на странице."
  else:
      return f"Ошибка при запросе страницы. Код состояния: {response.status_code}"

# Function for text
def extract_results(url, results_class):
  response = requests.get(url)

  if response.status_code == 200:
      soup = BeautifulSoup(response.text, 'html.parser')

      results_content = soup.find('div', class_=results_class)

      if results_content:
          links = extract_links_from_section(results_content, url)
          return '\n\n'.join(links[:17])
      else:
          return f"Элемент с классом '{results_class}' не найден на странице."
  else:
      return f"Ошибка при запросе страницы. Код состояния: {response.status_code}"


@dp.message_handler(commands=['start'])
async def send_welcome(message: Message):
  if message.chat.type == 'private':
    await message.answer(
        "Добро пожаловать! Этот бот умеет производить поиск по никнеймy или фотографии. 🕵️‍♂️",
        reply_markup=nav.BotMenu)


@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def process_username(message: types.Message):
    if message.chat.type == 'private':
        username = message.text

        url = f"https://search.brave.com/search?q=%22{username}%22"
        results_class = 'results'

        result = extract_results(url, results_class)
        if result == '':
            await message.reply("По вашему запросу ничего не найдено.")
        else:
            await message.reply(result)


@dp.message_handler(content_types=ContentTypes.PHOTO)
async def what_photo(message: Message):
  photo = message.photo[-1]

  file_info = await bot.get_file(photo.file_id)

  photo_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_info.file_path}"

  yandex_search_url = 'https://yandex.ru/images/search'
  yandex_payload = {
      'source': 'collections',
      'rpt': 'imageview',
      'url': photo_url
  }

  url = f"{yandex_search_url}?{urlencode(yandex_payload)}"
  section_class = 'CbirSites'
  result = extract_section(url, section_class)
  await message.answer(f"Результат поиска по картинке:\n\n{result}")


@dp.callback_query_handler(text="srch")
async def srch(callback: types.CallbackQuery):
  await bot.delete_message(callback.from_user.id, callback.message.message_id)
  await bot.send_message(callback.from_user.id,
                         "Введите никнейм или отправьте фотографию:")


keep_alive()

if __name__ == '__main__':
  executor.start_polling(dp, skip_updates=True)