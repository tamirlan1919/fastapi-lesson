from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='📜 Мои задачи', callback_data='menu:tasks'))
    builder.add(InlineKeyboardButton(text='➕ Добавить задачу', callback_data='menu:add'))
    builder.add(InlineKeyboardButton(text='📪Экспорт в Я.Диск', callback_data='menu:export'))
    builder.adjust(1)
    return builder.as_markup()

