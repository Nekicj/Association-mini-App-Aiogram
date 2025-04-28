import logging
import asyncio
from aiogram import Bot,Dispatcher

from handlers.client import router,db

logging.basicConfig(level=logging.INFO)

async def main():
    dp = Dispatcher()
    bot = Bot("7654853075:AAHTCa_xax0k7UEc-kIKx1V8Lc8DeWRSxXc")
    dp.include_router(router)
    await db.connect()
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")