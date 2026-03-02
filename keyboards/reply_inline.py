# keyboards/reply_inline.py

from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)


def get_admin_menu():
    kb = [
        [KeyboardButton(text="📝 Создать новый список")],
        [KeyboardButton(text="🎙 Настроить анонс")],
        [KeyboardButton(text="🔄 Сбросить анонс")],
        [KeyboardButton(text="📢 Рассылка")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_list_ikb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Упорядочить список", callback_data="reorder")]
    ])
