from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.states.candidate_states import CandidateStates
from db.repository import Repository

router = Router()


# -------- Кнопка "Начать анкету" --------
def get_start_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="Начать анкету", callback_data="candidate_start")
    return kb.as_markup()


# -------- Кнопки подтверждения --------
def get_confirm_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="Да", callback_data="candidate_confirm_yes")
    kb.button(text="Нет", callback_data="candidate_confirm_no")
    kb.adjust(2)
    return kb.as_markup()


# -------- Команда /start --------
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    # Проверяем, есть ли пользователь в БД
    user = await Repository.get_user_by_telegram_id(message.from_user.id)
    if not user:
        user = await Repository.create_user(
            telegram_id=message.from_user.id,
            role="candidate",
            username=message.from_user.username
        )

    await message.answer(
        "👋 Привет! Давай создадим твою анкету кандидата.\n\nНачать?",
        reply_markup=get_start_keyboard()
    )


# -------- Нажата кнопка "Начать анкету" --------
@router.callback_query(F.data == "candidate_start")
async def start_candidate_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CandidateStates.name)
    await callback.message.edit_text("❓ Как вас зовут? (Введите полное имя)")
    await callback.answer()


# -------- Имя --------
@router.message(CandidateStates.name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()

    if len(name) < 2:
        await message.answer("❌ Имя должно содержать минимум 2 символа.")
        return

    await state.update_data(name=name)
    await state.set_state(CandidateStates.age)
    await message.answer("❓ Сколько вам лет?")


# -------- Возраст --------
@router.message(CandidateStates.age)
async def process_age(message: Message, state: FSMContext):
    try:
        age = int(message.text.strip())
        if not (16 <= age <= 80):
            await message.answer("❌ Возраст должен быть от 16 до 80.")
            return
    except ValueError:
        await message.answer("❌ Введите число.")
        return

    await state.update_data(age=age)
    await state.set_state(CandidateStates.city)
    await message.answer("❓ В каком городе вы проживаете?")


# -------- Город --------
@router.message(CandidateStates.city)
async def process_city(message: Message, state: FSMContext):
    city = message.text.strip()

    if len(city) < 2:
        await message.answer("❌ Введите корректный город.")
        return

    await state.update_data(city=city)
    await state.set_state(CandidateStates.experience)
    await message.answer("❓ Опишите ваш опыт работы.")


# -------- Опыт --------
@router.message(CandidateStates.experience)
async def process_experience(message: Message, state: FSMContext):
    experience = message.text.strip()

    if len(experience) < 5:
        await message.answer("❌ Опишите опыт подробнее.")
        return

    await state.update_data(experience=experience)
    await state.set_state(CandidateStates.phone)
    await message.answer("❓ Ваш номер телефона?")


# -------- Телефон --------
@router.message(CandidateStates.phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text.strip()

    if not any(ch.isdigit() for ch in phone) or len(phone) < 7:
        await message.answer("❌ Неверный номер телефона.")
        return

    await state.update_data(phone=phone)
    await state.set_state(CandidateStates.position)
    await message.answer("❓ Какую должность вы ищете?")


# -------- Желаемая должность --------
@router.message(CandidateStates.position)
async def process_position(message: Message, state: FSMContext):
    position = message.text.strip()

    if len(position) < 2:
        await message.answer("❌ Введите корректную должность.")
        return

    await state.update_data(position=position)
    await state.set_state(CandidateStates.expected_salary)
    await message.answer("❓ Желаемая зарплата? (число)")


# -------- Зарплата --------
@router.message(CandidateStates.expected_salary)
async def process_salary(message: Message, state: FSMContext):
    try:
        salary = float(message.text.strip())
        if salary <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Введите корректное число.")
        return

    await state.update_data(expected_salary=salary)
    await state.set_state(CandidateStates.available_from)
    await message.answer("❓ Когда вы можете выйти на работу?")


# -------- Доступность --------
@router.message(CandidateStates.available_from)
async def process_available_date(message: Message, state: FSMContext):
    available_from = message.text.strip()

    if len(available_from) < 2:
        await message.answer("❌ Введите дату / период.")
        return

    await state.update_data(available_from=available_from)
    await state.set_state(CandidateStates.confirm)

    data = await state.get_data()

    text = (
        "✅ Проверьте вашу анкету:\n\n"
        f"<b>Имя:</b> {data['name']}\n"
        f"<b>Возраст:</b> {data['age']}\n"
        f"<b>Город:</b> {data['city']}\n"
        f"<b>Опыт:</b> {data['experience']}\n"
        f"<b>Телефон:</b> {data['phone']}\n"
        f"<b>Должность:</b> {data['position']}\n"
        f"<b>Зарплата:</b> {data['expected_salary']}\n"
        f"<b>Готов работать с:</b> {data['available_from']}\n\n"
        "Сохранить анкету?"
    )

    await message.answer(text, reply_markup=get_confirm_keyboard(), parse_mode="HTML")


# -------- Сохранение "Да" --------
@router.callback_query(F.data == "candidate_confirm_yes")
async def confirm_candidate_yes(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    try:
        # 1. Получаем юзера из таблицы users
        user = await Repository.get_user_by_telegram_id(callback.from_user.id)

        if not user:
            # если не нашли — создаём
            user = await Repository.create_user(
                telegram_id=callback.from_user.id,
                role="candidate",
                username=callback.from_user.username
            )

        # 2. Создаем профиль кандидата с user_id = PK users.id
        await Repository.create_candidate(
            user_id=user.id,
            name=data["name"],
            age=data["age"],
            city=data["city"],
            experience=data["experience"],
            phone=data["phone"],
            desired_position=data["position"],
            expected_salary=data["expected_salary"],
            ready_date=data["available_from"]
        )

        await callback.message.edit_text(
            "🎉 Анкета успешно сохранена!\nМы уведомим вас о подходящих вакансиях."
        )

    except Exception as e:
        await callback.message.edit_text(f"❌ Ошибка при сохранении: {e}")

    finally:
        await state.clear()
        await callback.answer()


# -------- Сохранение "Нет" --------
@router.callback_query(F.data == "candidate_confirm_no")
async def confirm_candidate_no(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Анкета отменена.\nВведите /start для начала.")
    await callback.answer()
