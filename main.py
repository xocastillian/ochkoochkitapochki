import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from bot.handlers.candidate_handlers import router as candidate_router
from bot.handlers.employer_handlers import router as employer_router
from bot.handlers.vacancy_handlers import router as vacancy_router
from bot.handlers.match_handlers import router as match_router

# -------- Загружаем переменные окружения --------
load_dotenv()

# -------- Получаем токен бота из .env файла --------
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден в .env файле!")


# -------- Главная асинхронная функция --------
async def main():
    """
    Инициализирует бота, подключает роутеры и запускает polling.
    """
    
    # -------- Создаем бота с поддержкой HTML-разметки --------
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    
    # -------- Создаем диспетчер --------
    dp = Dispatcher()
    
    # -------- Подключаем все роутеры --------
    dp.include_router(candidate_router)
    dp.include_router(employer_router)
    dp.include_router(vacancy_router)
    dp.include_router(match_router)
    
    # -------- Запускаем polling (прослушиваем сообщения) --------
    print("🤖 Бот запущен и слушает сообщения...")
    await dp.start_polling(bot)


# -------- Точка входа в программу --------
if __name__ == "__main__":
    asyncio.run(main())
