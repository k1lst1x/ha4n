from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

btnSrch = InlineKeyboardButton(text="Начать поиск", callback_data="srch")
BotMenu = InlineKeyboardMarkup(row_width=1)
BotMenu.insert(btnSrch)