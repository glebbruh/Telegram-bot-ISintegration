import os
from aiohttp import web
from aiogram import Bot

from bot.schemas.webhook_events import BotWebhookPayload
from bot.services.notification_formatter import build_notification_text

async def handle_internal_webhook(request: web.Request) -> web.Response:
    bot: Bot = request.app["bot"]
    try:
        raw_data = await request.json()
        payload = BotWebhookPayload.model_validate(raw_data)
    except Exception as e:
        return web.json_response({"ok": False, "error": f"bad payload: {e}"}, status=400)
    text = build_notification_text(payload)
    await bot.send_message(
        chat_id=payload.chat_id,
        text=text,
    )
    return web.json_response({"ok": True})

async def start_internal_webhook_server(bot: Bot):
    app = web.Application()
    app["bot"] = bot
    app.router.add_post("/webhook/events", handle_internal_webhook)
    host = os.getenv("BOT_INTERNAL_WEBHOOK_HOST", "127.0.0.1")
    port = int(os.getenv("BOT_INTERNAL_WEBHOOK_PORT", "8081"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=host, port=port)
    await site.start()
    return runner