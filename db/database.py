from dotenv import load_dotenv
load_dotenv()

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Импорт моделей
from db.models import Base

# URL берём из .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Асинхронный движок
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    # ВАЖНО! Исправляет ошибки Windows и обрывы соединения
    pool_pre_ping=True,          # Проверяет соединение перед выдачей
    pool_recycle=1800,           # Закрывает старые соединения (Windows fix)
    pool_size=3,                 # Уменьшаем размер пула для стабильности
    max_overflow=5,              # Ограничиваем переполнение
    pool_timeout=30,             # Таймаут получения соединения
    connect_args={
        "timeout": 10,           # Таймаут подключения к БД
        "command_timeout": 60,   # Таймаут выполнения команд
        "server_settings": {     # Параметры сервера PostgreSQL
            "jit": "off",        # Отключаем JIT для стабильности
        }
    }
)

# Фабрика сессий
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Инициализация БД
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Закрытие соединений
async def close_db():
    await engine.dispose()

# Получение сессии
async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
