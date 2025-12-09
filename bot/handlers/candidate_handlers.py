from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.states.candidate_states import CandidateStates
from db.repository import Repository

# Создаем маршрутизатор для хендлеров кандидатов
router = Router()


# -------- Вспомогательная функция: создание кнопки "Начать анкету" --------
def get_start_keyboard():
    """
    Создает inline клавиатуру с кнопкой для начала анкеты.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text="Начать анкету", callback_data="candidate_start")
    return kb.as_markup()


# -------- Вспомогательная функция: создание кнопок подтверждения --------
def get_confirm_keyboard():
    """
    Создает inline клавиатуру с кнопками Да/Нет для подтверждения.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text="Да", callback_data="candidate_confirm_yes")
    kb.button(text="Нет", callback_data="candidate_confirm_no")
    kb.adjust(2)
    return kb.as_markup()


# -------- Команда /start: главное меню --------
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """
    Обработчик команды /start.
    Показывает приветственное сообщение с предложением начать анкету.
    """
    await state.clear()
    await message.answer(
        "👋 Привет! Давай создадим твою анкету кандидата.\n\n"
        "Начать?",
        reply_markup=get_start_keyboard()
    )


# -------- Нажата кнопка "Начать анкету" --------
@router.callback_query(F.data == "candidate_start")
async def start_candidate_form(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик нажатия кнопки "Начать анкету".
    Переходит в первое состояние (вопрос о имени).
    """
    await state.set_state(CandidateStates.name)
    await callback.message.edit_text(
        "❓ Как вас зовут? (Введите ваше полное имя)"
    )
    await callback.answer()


# -------- Шаг 1: спрашиваем имя --------
@router.message(CandidateStates.name)
async def process_name(message: Message, state: FSMContext):
    """
    Получает имя кандидата.
    Валидирует: не пустое и не слишком короткое.
    """
    name = message.text.strip()
    
    if not name or len(name) < 2:
        await message.answer("❌ Имя должно содержать минимум 2 символа. Попробуйте снова.")
        return
    
    await state.update_data(name=name)
    await state.set_state(CandidateStates.age)
    await message.answer("❓ Сколько вам лет?")


# -------- Шаг 2: спрашиваем возраст --------
@router.message(CandidateStates.age)
async def process_age(message: Message, state: FSMContext):
    """
    Получает возраст кандидата.
    Валидирует: целое число в диапазоне 16-80.
    """
    try:
        age = int(message.text.strip())
        if age < 16 or age > 80:
            await message.answer("❌ Возраст должен быть между 16 и 80 годами.")
            return
    except ValueError:
        await message.answer("❌ Пожалуйста, введите число.")
        return
    
    await state.update_data(age=age)
    await state.set_state(CandidateStates.city)
    await message.answer("❓ В каком городе вы проживаете?")


# -------- Шаг 3: спрашиваем город --------
@router.message(CandidateStates.city)
async def process_city(message: Message, state: FSMContext):
    """
    Получает город проживания.
    Валидирует: не пустое.
    """
    city = message.text.strip()
    
    if not city or len(city) < 2:
        await message.answer("❌ Введите название города (минимум 2 символа).")
        return
    
    await state.update_data(city=city)
    await state.set_state(CandidateStates.experience)
    await message.answer("❓ Опишите ваш опыт работы (должности, компании, годы).")


# -------- Шаг 4: спрашиваем опыт работы --------
@router.message(CandidateStates.experience)
async def process_experience(message: Message, state: FSMContext):
    """
    Получает описание опыта работы.
    Валидирует: не пустое.
    """
    experience = message.text.strip()
    
    if not experience or len(experience) < 5:
        await message.answer("❌ Опишите опыт подробнее (минимум 5 символов).")
        return
    
    await state.update_data(experience=experience)
    await state.set_state(CandidateStates.phone)
    await message.answer("❓ Ваш номер телефона? (например: +7 900 123 45 67)")


# -------- Шаг 5: спрашиваем телефон --------
@router.message(CandidateStates.phone)
async def process_phone(message: Message, state: FSMContext):
    """
    Получает номер телефона.
    Валидирует: содержит только цифры, +, пробелы, дефисы и скобки.
    """
    phone = message.text.strip()
    
    # Простая валидация: должны быть цифры и возможно +, -, (), пробелы
    if not any(c.isdigit() for c in phone):
        await message.answer("❌ Номер телефона должен содержать цифры.")
        return
    
    if len(phone) < 7:
        await message.answer("❌ Номер телефона должен быть полным.")
        return
    
    await state.update_data(phone=phone)
    await state.set_state(CandidateStates.position)
    await message.answer("❓ Какую должность вы ищете?")


# -------- Шаг 6: спрашиваем желаемую должность --------
@router.message(CandidateStates.position)
async def process_position(message: Message, state: FSMContext):
    """
    Получает желаемую должность.
    Валидирует: не пустое.
    """
    position = message.text.strip()
    
    if not position or len(position) < 2:
        await message.answer("❌ Введите должность (минимум 2 символа).")
        return
    
    await state.update_data(position=position)
    await state.set_state(CandidateStates.expected_salary)
    await message.answer("❓ Желаемая зарплата? (введите сумму в рублях, например: 100000)")


# -------- Шаг 7: спрашиваем ожидаемую зарплату --------
@router.message(CandidateStates.expected_salary)
async def process_salary(message: Message, state: FSMContext):
    """
    Получает ожидаемую зарплату.
    Валидирует: положительное число.
    """
    try:
        salary = float(message.text.strip())
        if salary <= 0:
            await message.answer("❌ Зарплата должна быть положительной суммой.")
            return
    except ValueError:
        await message.answer("❌ Пожалуйста, введите число.")
        return
    
    await state.update_data(expected_salary=salary)
    await state.set_state(CandidateStates.available_from)
    await message.answer("❓ Когда вы можете выйти на работу? (например: завтра, 1 января, через неделю)")


# -------- Шаг 8: спрашиваем дату доступности --------
@router.message(CandidateStates.available_from)
async def process_available_date(message: Message, state: FSMContext):
    """
    Получает информацию о дате доступности.
    Валидирует: не пустое.
    """
    available_from = message.text.strip()
    
    if not available_from or len(available_from) < 2:
        await message.answer("❌ Введите дату или описание доступности.")
        return
    
    await state.update_data(available_from=available_from)
    await state.set_state(CandidateStates.confirm)
    
    # -------- Шаг 9: показываем карточку для подтверждения --------
    data = await state.get_data()
    
    confirmation_text = (
        "✅ Проверьте вашу анкету:\n\n"
        f"<b>Имя:</b> {data['name']}\n"
        f"<b>Возраст:</b> {data['age']} лет\n"
        f"<b>Город:</b> {data['city']}\n"
        f"<b>Опыт:</b> {data['experience']}\n"
        f"<b>Телефон:</b> {data['phone']}\n"
        f"<b>Должность:</b> {data['position']}\n"
        f"<b>Зарплата:</b> {data['expected_salary']} руб.\n"
        f"<b>Доступен с:</b> {data['available_from']}\n\n"
        "Сохранить анкету?"
    )
    
    await message.answer(confirmation_text, reply_markup=get_confirm_keyboard(), parse_mode="HTML")


# -------- Подтверждение: нажата кнопка "Да" --------
@router.callback_query(F.data == "candidate_confirm_yes")
async def confirm_candidate_yes(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик нажатия "Да" при подтверждении.
    Сохраняет анкету в БД и очищает состояние.
    """
    data = await state.get_data()
    
    try:
        # Сохраняем кандидата в БД
        user_id = callback.from_user.id
        
        await Repository.create_candidate(
            user_id=user_id,
            name=data['name'],
            age=data['age'],
            city=data['city'],
            experience=data['experience'],
            phone=data['phone'],
            desired_position=data['position'],
            expected_salary=data['expected_salary'],
            ready_date=data['available_from']
        )
        
        await callback.message.edit_text(
            "🎉 Анкета успешно сохранена!\n\n"
            "Мы уведомим вас, когда появятся подходящие вакансии."
        )
        
    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка при сохранении: {str(e)}"
        )
    
    finally:
        await state.clear()
        await callback.answer()


# -------- Подтверждение: нажата кнопка "Нет" --------
@router.callback_query(F.data == "candidate_confirm_no")
async def confirm_candidate_no(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик нажатия "Нет" при подтверждении.
    Отменяет анкету и предлагает начать заново.
    """
    await state.clear()
    await callback.message.edit_text(
        "❌ Анкета отменена.\n\n"
        "Если хотите заполнить снова — введите /start."
    )
    await callback.answer()
