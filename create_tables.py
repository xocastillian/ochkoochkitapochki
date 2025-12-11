import asyncio
import sys

# ФИКС ДЛЯ WINDOWS
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from db.database import engine
from db.models import Base

async def create_tables():
    print(">>> Создаем таблицы...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print(">>> Таблицы успешно созданы!")

asyncio.run(create_tables())
