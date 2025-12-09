from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.states.employer_states import EmployerStates
from db.repository import Repository

# Создаем маршрутизатор для хендлеров работодателей
router = Router()


# -------- Вспомогательная функция: создание кнопки "Начать" --------
def get_start_keyboard():
    """
    Создает inline клавиатуру с кнопкой для начала анкеты работодателя.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text="Начать", callback_data="employer_start")
    return kb.as_markup()


# -------- Вспомогательная функция: создание кнопок подтверждения --------
def get_confirm_keyboard():
    """
    Создает inline клавиатуру с кнопками Да/Нет для подтверждения.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text="Да", callback_data="employer_confirm_yes")
    kb.button(text="Нет", callback_data="employer_confirm_no")
    kb.adjust(2)
    return kb.as_markup()


# -------- Команда /employer_start: главное меню --------
@router.message(Command("employer_start"))
async def cmd_employer_start(message: Message, state: FSMContext):
    """
    Обработчик команды /employer_start.
    Показывает приветственное сообщение для работодателя.
    """
    await state.clear()
    await message.answer(
        "👋 Здравствуйте! Давайте создадим вашу анкету работодателя.\n\n"
        "Готовы начать?",
        reply_markup=get_start_keyboard()
    )


# -------- Нажата кнопка "Начать" --------
@router.callback_query(F.data == "employer_start")
async def start_employer_form(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик нажатия кнопки "Начать".
    Переходит в первое состояние (вопрос о названии компании).
    """
    await state.set_state(EmployerStates.company_name)
    await callback.message.edit_text(
        "❓ Как называется ваша компания?"
    )
    await callback.answer()


# -------- Шаг 1: спрашиваем название компании --------
@router.message(EmployerStates.company_name)
async def process_company_name(message: Message, state: FSMContext):
    """
    Получает название компании.
    Валидирует: не пустое и не слишком короткое.
    """
    company_name = message.text.strip()
    
    if not company_name or len(company_name) < 2:
        await message.answer("❌ Название компании должно содержать минимум 2 символа. Попробуйте снова.")
        return
    
    await state.update_data(company_name=company_name)
    await state.set_state(EmployerStates.contact_phone)
    await message.answer("❓ Ваш контактный номер телефона? (например: +7 900 123 45 67)")


# -------- Шаг 2: спрашиваем контактный телефон --------
@router.message(EmployerStates.contact_phone)
async def process_contact_phone(message: Message, state: FSMContext):
    """
    Получает контактный телефон работодателя.
    Валидирует: содержит цифры и минимальную длину.
    """
    contact_phone = message.text.strip()
    
    # Простая валидация: должны быть цифры
    if not any(c.isdigit() for c in contact_phone):
        await message.answer("❌ Номер телефона должен содержать цифры.")
        return
    
    if len(contact_phone) < 7:
        await message.answer("❌ Номер телефона должен быть полным.")
        return
    
    await state.update_data(contact_phone=contact_phone)
    await state.set_state(EmployerStates.city)
    await message.answer("❓ В каком городе находится ваша компания?")


# -------- Шаг 3: спрашиваем город компании --------
@router.message(EmployerStates.city)
async def process_city(message: Message, state: FSMContext):
    """
    Получает город, где находится компания.
    Валидирует: не пустое и минимальная длина.
    """
    city = message.text.strip()
    
    if not city or len(city) < 2:
        await message.answer("❌ Введите название города (минимум 2 символа).")
        return
    
    await state.update_data(city=city)
    await state.set_state(EmployerStates.vacancy_title)
    await message.answer("❓ Какую должность вы предлагаете?")


# -------- Шаг 4: спрашиваем название вакансии --------
@router.message(EmployerStates.vacancy_title)
async def process_vacancy_title(message: Message, state: FSMContext):
    """
    Получает название вакансии/должности.
    Валидирует: не пустое и минимальная длина.
    """
    vacancy_title = message.text.strip()
    
    if not vacancy_title or len(vacancy_title) < 2:
        await message.answer("❌ Введите название должности (минимум 2 символа).")
        return
    
    await state.update_data(vacancy_title=vacancy_title)
    await state.set_state(EmployerStates.vacancy_salary)
    await message.answer("❓ Какая зарплата для этой должности? (введите сумму в рублях)")


# -------- Шаг 5: спрашиваем зарплату --------
@router.message(EmployerStates.vacancy_salary)
async def process_vacancy_salary(message: Message, state: FSMContext):
    """
    Получает зарплату для вакансии.
    Валидирует: положительное число.
    """
    try:
        vacancy_salary = float(message.text.strip())
        if vacancy_salary <= 0:
            await message.answer("❌ Зарплата должна быть положительной суммой.")
            return
    except ValueError:
        await message.answer("❌ Пожалуйста, введите число.")
        return
    
    await state.update_data(vacancy_salary=vacancy_salary)
    await state.set_state(EmployerStates.vacancy_requirements)
    await message.answer("❓ Какие требования к кандидату? (опыт, навыки, образование и т.д.)")


# -------- Шаг 6: спрашиваем требования к кандидату --------
@router.message(EmployerStates.vacancy_requirements)
async def process_vacancy_requirements(message: Message, state: FSMContext):
    """
    Получает требования к кандидату.
    Валидирует: не пустое и минимальная длина.
    """
    vacancy_requirements = message.text.strip()
    
    if not vacancy_requirements or len(vacancy_requirements) < 5:
        await message.answer("❌ Опишите требования подробнее (минимум 5 символов).")
        return
    
    await state.update_data(vacancy_requirements=vacancy_requirements)
    await state.set_state(EmployerStates.vacancy_needed)
    await message.answer("❓ Сколько человек вам нужно на эту должность? (введите число)")


# -------- Шаг 7: спрашиваем количество вакансий --------
@router.message(EmployerStates.vacancy_needed)
async def process_vacancy_needed(message: Message, state: FSMContext):
    """
    Получает количество нужных сотрудников.
    Валидирует: положительное целое число.
    """
    try:
        vacancy_needed = int(message.text.strip())
        if vacancy_needed <= 0:
            await message.answer("❌ Количество должно быть положительным числом.")
            return
    except ValueError:
        await message.answer("❌ Пожалуйста, введите целое число.")
        return
    
    await state.update_data(vacancy_needed=vacancy_needed)
    await state.set_state(EmployerStates.confirm)
    
    # -------- Шаг 8: показываем карточку для подтверждения --------
    data = await state.get_data()
    
    confirmation_text = (
        "✅ Проверьте данные вакансии:\n\n"
        f"<b>Компания:</b> {data['company_name']}\n"
        f"<b>Телефон:</b> {data['contact_phone']}\n"
        f"<b>Город:</b> {data['city']}\n"
        f"<b>Вакансия:</b> {data['vacancy_title']}\n"
        f"<b>Зарплата:</b> {data['vacancy_salary']} руб.\n"
        f"<b>Требования:</b> {data['vacancy_requirements']}\n"
        f"<b>Количество:</b> {data['vacancy_needed']} чел.\n\n"
        "Сохранить вакансию?"
    )
    
    await message.answer(confirmation_text, reply_markup=get_confirm_keyboard(), parse_mode="HTML")


# -------- Подтверждение: нажата кнопка "Да" --------
@router.callback_query(F.data == "employer_confirm_yes")
async def confirm_employer_yes(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик нажатия "Да" при подтверждении.
    Сохраняет анкету работодателя и создает вакансию в БД.
    """
    data = await state.get_data()
    
    try:
        user_id = callback.from_user.id
        
        # -------- Проверяем, есть ли уже профиль работодателя --------
        existing_employer = await Repository.get_employer_by_user_id(user_id)
        
        if existing_employer:
            employer_id = existing_employer.id
        else:
            # -------- Создаем новый профиль работодателя --------
            employer = await Repository.create_employer(
                user_id=user_id,
                company_name=data['company_name'],
                city=data['city'],
                company_info="",  # Пока пусто
                requirements=data['vacancy_requirements']
            )
            employer_id = employer.id
        
        # -------- Создаем вакансию --------
        await Repository.create_vacancy(
            employer_id=employer_id,
            position=data['vacancy_title'],
            city=data['city'],
            salary=data['vacancy_salary'],
            requirements=data['vacancy_requirements'],
            count_needed=data['vacancy_needed']
        )
        
        await callback.message.edit_text(
            "🎉 Вакансия успешно сохранена!\n\n"
            "Теперь вы можете искать подходящих кандидатов."
        )
        
    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка при сохранении: {str(e)}"
        )
    
    finally:
        await state.clear()
        await callback.answer()


# -------- Подтверждение: нажата кнопка "Нет" --------
@router.callback_query(F.data == "employer_confirm_no")
async def confirm_employer_no(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик нажатия "Нет" при подтверждении.
    Отменяет создание вакансии и предлагает начать заново.
    """
    await state.clear()
    await callback.message.edit_text(
        "❌ Создание вакансии отменено.\n\n"
        "Чтобы начать заново — используйте команду /employer_start"
    )
    await callback.answer()
