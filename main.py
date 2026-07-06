import os
import sys
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Python loyiha yo'lini ko'rmay qolmasligi uchun majburiy qo'shilgan qism
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# MANA SHU YERDA HANDLERS ICHIDAGI ROUTER IMPORT QILINMOQDA
from app.handlers import router
from config import TOKEN
import app.db_setup as db

# Botni standart HTML formatida ishlaydigan qilib yaratamiz
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


async def on_startup():
    await db.db_start()
    print("Database connection established")


async def main():
    try:
        print("Bot is running...")
        await on_startup()

        # MANA SHU SATR ROUTERNI ISHLAYDIGAN QILIB ULAYDI (DP GA QO'SHADI)
        dp.include_router(router)

        await dp.start_polling(bot)
    finally:
        print("Bot is stopped...")
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())