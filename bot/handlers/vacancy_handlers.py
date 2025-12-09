from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db.repository import Repository

# Создаем маршрутизатор для хендлеров вакансий
router = Router()


# -------- Вспомогательная функция: создание клавиатуры со списком вакансий --------
def get_vacancies_keyboard(vacancies):
    """
    Создает inline клавиатуру со списком вакансий.
    Каждая кнопка содержит название и зарплату.
    """
    kb = InlineKeyboardBuilder()
    
    for vacancy in vacancies:
        button_text = f"{vacancy.position} | {vacancy.salary} руб."
        callback_data = f"vacancy_{vacancy.id}"
        kb.button(text=button_text, callback_data=callback_data)
    
    kb.adjust(1)  # По одной кнопке в ряд
    return kb.as_markup()


# -------- Команда /vacancies: показать список вакансий работодателя --------
@router.message(Command("vacancies"))
async def cmd_vacancies(message: Message):
    """
    Показывает список всех вакансий текущего работодателя.
    Если вакансий нет - предлагает создать новую.
    """
    telegram_id = message.from_user.id
    
    # -------- Проверяем, существует ли пользователь --------
    user = await Repository.get_user_by_telegram_id(telegram_id)
    
    if not user:
        await message.answer(
            "❌ Вы не зарегистрированы в системе.\n\n"
            "Используйте /start для регистрации."
        )
        return
    
    # -------- Проверяем, является ли пользователь работодателем --------
    if user.role != 'employer':
        await message.answer(
            "❌ Эта команда доступна только для работодателей.\n\n"
            "Если вы работодатель, используйте /employer_start."
        )
        return
    
    # -------- Получаем профиль работодателя --------
    employer = await Repository.get_employer_by_user_id(user.id)
    
    if not employer:
        await message.answer(
            "❌ У вас пока нет созданных вакансий.\n\n"
            "Создайте одну с помощью команды /employer_start"
        )
        return
    
    # -------- Получаем список вакансий работодателя --------
    vacancies = await Repository.get_vacancies_by_employer(employer.id)
    
    if not vacancies:
        await message.answer(
            "❌ У вас нет активных вакансий.\n\n"
            "Создайте вакансию командой /employer_start"
        )
        return
    
    # -------- Показываем список вакансий --------
    await message.answer(
        "📋 Ваши вакансии:\n\n"
        "Выберите одну, чтобы посмотреть подробности:",
        reply_markup=get_vacancies_keyboard(vacancies)
    )


# -------- Callback: показать карточку вакансии --------
@router.callback_query(F.data.startswith("vacancy_"))
async def show_vacancy_details(callback: CallbackQuery):
    """
    Показывает подробную информацию о выбранной вакансии.
    Парсит vacancy_id из callback_data и получает данные из БД.
    """
    # -------- Распарсиваем vacancy_id из callback_data --------
    try:
        vacancy_id = int(callback.data.split("_")[1])
    except (IndexError, ValueError):
        await callback.answer("❌ Ошибка при обработке вакансии.", show_alert=True)
        return
    
    # -------- Получаем данные вакансии из БД --------
    vacancy = await Repository.get_vacancy_by_id(vacancy_id)
    
    if not vacancy:
        await callback.answer(
            "❌ Вакансия не найдена.",
            show_alert=True
        )
        return
    
    # -------- Формируем карточку вакансии --------
    vacancy_card = (
        f"📌 <b>Вакансия:</b> {vacancy.position}\n"
        f"💰 <b>Зарплата:</b> {vacancy.salary} руб.\n"
        f"📍 <b>Город:</b> {vacancy.city}\n"
        f"📄 <b>Требования:</b>\n{vacancy.requirements}\n"
        f"👥 <b>Нужно сотрудников:</b> {vacancy.count_needed}\n"
    )
    
    # -------- Показываем карточку --------
    await callback.message.edit_text(
        vacancy_card,
        parse_mode="HTML"
    )
    await callback.answer()
