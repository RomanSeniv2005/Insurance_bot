from aiogram import Bot, Dispatcher
from aiogram.types import Update
from fastapi import FastAPI, Request
import logging
import os
from dotenv import load_dotenv
from hendler import router
import asyncio

load_dotenv()
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  

USE_WEBHOOK = os.getenv("USE_WEBHOOK", "True") == "True"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)

app = FastAPI()


@app.post("/webhook")
async def handle_webhook(request: Request):
    try:
        update = Update.model_validate(await request.json())
        await dp.feed_update(bot, update)
    except Exception as e:
        logging.exception("❌ Виняток у webhook")
    return {"ok": True}



@app.on_event("startup")
async def on_startup():
    # Реєстрація вебхуку
    webhook_info = await bot.set_webhook(WEBHOOK_URL)
    print("Webhook set:", webhook_info)


@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()


async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()
    dp.include_router(router)
    if USE_WEBHOOK:
        # Webhook mode
        await dp.start_webhook(
            bot=bot,
            webhook_path="/webhook",
            on_startup=None,
            on_shutdown=None,
            skip_updates=True,
            host="0.0.0.0",
            port=int(os.getenv("PORT", 8080)),
        )
    else:
        # Polling mode
        await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
