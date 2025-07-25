from aiogram import Bot, Dispatcher
from aiogram.types import Update
from fastapi import FastAPI, Request
import logging
import os
from dotenv import load_dotenv
from hendler import router

load_dotenv()
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # наприклад, https://yourdomain.com/webhook

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)

app = FastAPI()


@app.post("/webhook")
async def handle_webhook(request: Request):
    update = Update.model_validate(await request.json())
    await dp.feed_update(bot, update)
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
