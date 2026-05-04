#меню бота
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from bot.keyboards.callbacks import LogoutConfirmCb

def main_sections_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Проверки"), KeyboardButton(text="Задачи")], [KeyboardButton(text="Выйти из аккаунта")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите раздел"
    )

def logout_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Да",
                    callback_data=LogoutConfirmCb(action="yes").pack()
                ),
                InlineKeyboardButton(
                    text="Отмена",
                    callback_data=LogoutConfirmCb(action="cancel").pack()
                ),
            ]
        ]
    )