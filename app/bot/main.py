import asyncio
import os

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

load_dotenv()
router = Router()

#клавиатура после старта
def start_menu():
    kb = InlineKeyboardBuilder()

    kb.button(
        text="Получить статистику",
        callback_data="stats:get"
    )
    kb.adjust(1)
    return kb.as_markup()

#обрабатывает старт
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        text="Привет! Выбери действие:",
        reply_markup=start_menu()
    )

#обработка кнопки
@router.callback_query(lambda c: c.data == "stats:get")
async def get_stats(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "Статистики нет."
    )


async def main():
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "BOT_TOKEN is not exist"
        )
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())