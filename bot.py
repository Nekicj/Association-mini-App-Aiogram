import os
import asyncpg
import json
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv
from aiogram.types import ReplyKeyboardMarkup,WebAppInfo,Message,ContentType,KeyboardButton
load_dotenv()

# Database connection
async def get_db():
    return await asyncpg.connect(
        user="postgres",
        password="csgolox13",
        database="AssociationMiniApp",
        host="127.0.0.1",  # безопаснее, чем имя
        port=5432
    )

# Create table
async def create_table():
    conn = await get_db()
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            name VARCHAR(100),
            phone VARCHAR(20),
            class VARCHAR(50),
            description TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        )
    ''')
    await conn.close()

bot = Bot(token=os.getenv('BOT_TOKEN'))

# Start command with Web App button
@dp.message(Command('start'))
async def start(message: types.Message):
    await create_table()  # Ensure table exists
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="Open Questionnaire",
                    web_app=WebAppInfo(url=os.getenv("WEBAPP_URL"))
                )
            ]
        ],
        resize_keyboard=True
    )
    
    await message.answer("Click the button below:", reply_markup=keyboard)

# Handle Web App data
@dp.message(F.content_type == ContentType.WEB_APP_DATA)
async def handle_webapp_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        
        conn = await get_db()
        await conn.execute('''
            INSERT INTO users (user_id, name, phone, class, description)
            VALUES ($1, $2, $3, $4, $5)
        ''', message.from_user.id, 
           data['name'], data['phone'], data['class'], data['description'])
        
        await message.answer("✅ Thank you! Your data has been saved.")
    except Exception as e:
        await message.answer("❌ Error saving data. Please try again.")
    finally:
        await conn.close()

async def main():
    await create_table()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())