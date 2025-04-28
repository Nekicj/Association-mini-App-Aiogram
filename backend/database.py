import asyncpg

async def test_connection():
    try:
        conn = await asyncpg.connect(
            user='postgres',
            password='csgolox13',
            database='association',
            host='localhost',
            port=5432
        )
        print("✅ Подключение успешно!")
        await conn.close()
    except Exception as e:
        print(f"❌ Ошибка: {e}")

# Запустите проверку
import asyncio
asyncio.run(test_connection())