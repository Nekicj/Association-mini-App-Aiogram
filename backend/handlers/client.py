import os
import asyncpg
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command, Filter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

BOT_TOKEN = "7654853075:AAHTCa_xax0k7UEc-kIKx1V8Lc8DeWRSxXc"
DB_URL = "postgresql://postgres:csgolox13@localhost:5432/association"

router = Router()

class AdminFilter(Filter):
    async def __call__(self, message: types.Message) -> bool:
        ADMINS = [12345678]  
        return message.from_user.id in ADMINS

class Form(StatesGroup):
    full_name = State()
    contact = State()
    education = State()
    sphere = State()
    skills = State()

class Database:
    def __init__(self):
        self.conn = None

    async def connect(self):
        self.conn = await asyncpg.connect(DB_URL)
    
    async def create_user(self, data):
        query = """
            INSERT INTO users (tg_id, username, full_name, contact, education, sphere, skills)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id
        """
        return await self.conn.fetchval(query, *data)
    
    async def update_status(self, user_id, status):
        await self.conn.execute("UPDATE users SET status = $1 WHERE tg_id = $2", status, user_id)
    
    async def get_users_by_status(self, status):
        return await self.conn.fetch("SELECT * FROM users WHERE status = $1", status)

db = Database()

@router.message(Command('start'))
async def start_cmd(message: types.Message, state: FSMContext):
    await state.set_state(Form.full_name)
    await message.answer("📝 Давайте заполним анкету!\nВаше полное имя:")

@router.message(Form.full_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await state.set_state(Form.contact)
    await message.answer("📱 Ваш контактный номер телефона:")

@router.message(Form.contact)
async def process_contact(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    await state.set_state(Form.education)
    await message.answer("🎓 Ваше учебное заведение:")

@router.message(Form.education)
async def process_education(message: types.Message, state: FSMContext):
    await state.update_data(education=message.text)
    await state.set_state(Form.sphere)
    await message.answer("🌐 Сфера развития (IT, химия и т.д.):")

@router.message(Form.sphere)
async def process_sphere(message: types.Message, state: FSMContext):
    await state.update_data(sphere=message.text)
    await state.set_state(Form.skills)
    await message.answer("💻 Опишите ваши навыки:")

@router.message(Form.skills)
async def process_skills(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = message.from_user.id
    username = message.from_user.username
    
    await db.create_user((
        user_id,
        username,
        user_data['full_name'],
        user_data['contact'],
        user_data['education'],
        user_data['sphere'],
        message.text
    ))
    
    await state.clear()
    await message.answer("✅ Анкета заполнена! Ожидайте решения администратора.")

@router.message(Command('approve'), AdminFilter())
async def approve_user(message: types.Message):
    try:
        user_id = int(message.text.split()[1])
        await db.update_status(user_id, 'approved')
        await message.bot.send_message(user_id, "🎉 Вы одобрены! Ссылка на сообщество: ...")
        await message.answer("✅ Пользователь одобрен")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")

@router.message(Command('broadcast'), AdminFilter())
async def broadcast_message(message: types.Message):
    try:
        text = message.text.split(' ', 1)[1]
        users = await db.get_users_by_status('approved')
        for user in users:
            try:
                await message.bot.send_message(user['tg_id'], text)
            except:
                continue
        await message.answer(f"📢 Рассылка завершена. Получили: {len(users)} пользователей")
    except IndexError:
        await message.answer("❌ Укажите текст рассылки")