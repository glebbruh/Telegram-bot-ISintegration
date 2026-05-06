import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from bot.handlers.auth import router as auth_router
from bot.handlers.checks import router as checks_router
from bot.handlers.tasks import router as tasks_router
from bot.handlers.patterns import router as patterns_router
from bot.handlers.bot_calendar import router as calendar_router
from bot.handlers.session import router as session_router
from bot.webhook_server import start_internal_webhook_server

load_dotenv()

async def run_forever():
    while True:
        try:
            await main()
        except KeyboardInterrupt:
            raise
        except Exception:
            await asyncio.sleep(5)

async def main():
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "BOT_TOKEN does not exist"
        )
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(auth_router)
    dp.include_router(checks_router)
    dp.include_router(tasks_router)
    dp.include_router(patterns_router)
    dp.include_router(calendar_router)
    dp.include_router(session_router)
    runner = await start_internal_webhook_server(bot)
    try:
        await dp.start_polling(bot)
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(run_forever())