#меню бота
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

def main_sections_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Проверки"), KeyboardButton(text="Задачи")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите раздел"
    )