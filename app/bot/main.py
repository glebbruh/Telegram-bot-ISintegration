import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from auth import router as auth_router
from checks_filters import router as checks_filters_router
from bot_calendar import router as calendar_router

load_dotenv()

async def main():
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "BOT_TOKEN is not exist"
        )
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(auth_router)
    dp.include_router(checks_filters_router)
    dp.include_router(calendar_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())