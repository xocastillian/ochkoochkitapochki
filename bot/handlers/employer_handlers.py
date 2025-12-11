from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.states.employer_states import EmployerStates
from db.repository import Repository

router = Router()


# ---------- Кнопки ----------
def get_start_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="Начать", callback_data="employer_start")
    return kb.as_markup()


def get_confirm_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="Да", callback_data="employer_confirm_yes")
    kb.button(text="Нет", callback_data="employer_confirm_no")
    kb.adjust(2)
    return kb.as_markup()


# ---------- /employer_start ----------
@router.message(Command("employer_start"))
async def cmd_employer_start(message: Message, state: FSMContext):
    await state.clear()

    # Проверяем, есть ли юзер в таблице users
    user = await Repository.get_user_by_telegram_id(message.from_user.id)
    if not user:
        user = await Repository.create_user(
            telegram_id=message.from_user.id,
            role="employer",
            username=message.from_user.username
        )

    await message.answer(
        "👋 Здравствуйте! Давайте создадим вашу анкету работодателя.\n\nГотовы начать?",
        reply_markup=get_start_keyboard()
    )


# ---------- Начать анкету ----------
@router.callback_query(F.data == "employer_start")
async def start_employer_form(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EmployerStates.company_name)
    await callback.message.edit_text("❓ Как называется ваша компания?")
    await callback.answer()


# ---------- Шаг 1: название компании ----------
@router.message(EmployerStates.company_name)
async def process_company_name(message: Message, state: FSMContext):
    company_name = message.text.strip()
    if len(company_name) < 2:
        await message.answer("❌ Название компании должно содержать минимум 2 символа.")
        return

    await state.update_data(company_name=company_name)
    await state.set_state(EmployerStates.contact_phone)
    await message.answer("❓ Ваш контактный номер телефона?")


# ---------- Шаг 2: телефон ----------
@router.message(EmployerStates.contact_phone)
async def process_contact_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    if not any(c.isdigit() for c in phone) or len(phone) < 7:
        await message.answer("❌ Введите корректный номер телефона.")
        return

    await state.update_data(contact_phone=phone)
    await state.set_state(EmployerStates.city)
    await message.answer("❓ В каком городе находится ваша компания?")


# ---------- Шаг 3: город ----------
@router.message(EmployerStates.city)
async def process_company_city(message: Message, state: FSMContext):
    city = message.text.strip()
    if len(city) < 2:
        await message.answer("❌ Введите корректный город.")
        return

    await state.update_data(city=city)
    await state.set_state(EmployerStates.vacancy_title)
    await message.answer("❓ Какую должность вы предлагаете?")


# ---------- Шаг 4: должность ----------
@router.message(EmployerStates.vacancy_title)
async def process_vacancy_title(message: Message, state: FSMContext):
    title = message.text.strip()
    if len(title) < 2:
        await message.answer("❌ Введите корректное название должности.")
        return

    await state.update_data(vacancy_title=title)
    await state.set_state(EmployerStates.vacancy_salary)
    await message.answer("❓ Какая зарплата предлагается? (число)")


# ---------- Шаг 5: зарплата ----------
@router.message(EmployerStates.vacancy_salary)
async def process_salary(message: Message, state: FSMContext):
    try:
        salary = float(message.text.strip())
        if salary <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Зарплата должна быть числом > 0.")
        return

    await state.update_data(vacancy_salary=salary)
    await state.set_state(EmployerStates.vacancy_requirements)
    await message.answer("❓ Какие требования к кандидату?")


# ---------- Шаг 6: требования ----------
@router.message(EmployerStates.vacancy_requirements)
async def process_requirements(message: Message, state: FSMContext):
    requirements = message.text.strip()
    if len(requirements) < 5:
        await message.answer("❌ Опишите требования подробнее.")
        return

    await state.update_data(vacancy_requirements=requirements)
    await state.set_state(EmployerStates.vacancy_needed)
    await message.answer("❓ Сколько сотрудников вам требуется? (число)")


# ---------- Шаг 7: количество ----------
@router.message(EmployerStates.vacancy_needed)
async def process_needed(message: Message, state: FSMContext):
    try:
        count = int(message.text.strip())
        if count <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Введите положительное целое число.")
        return

    await state.update_data(vacancy_needed=count)
    await state.set_state(EmployerStates.confirm)

    data = await state.get_data()

    text = (
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

    await message.answer(text, reply_markup=get_confirm_keyboard(), parse_mode="HTML")


# ---------- Подтверждение: Да ----------
@router.callback_query(F.data == "employer_confirm_yes")
async def employer_confirm_yes(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    try:
        # 1. Находим юзера (user.id — нужен для employer.user_id)
        user = await Repository.get_user_by_telegram_id(callback.from_user.id)
        if not user:
            user = await Repository.create_user(
                telegram_id=callback.from_user.id,
                role="employer",
                username=callback.from_user.username
            )

        # 2. Находим профиль работодателя
        employer = await Repository.get_employer_by_user_id(user.id)

        if not employer:
            employer = await Repository.create_employer(
                user_id=user.id,
                company_name=data["company_name"],
                city=data["city"],
                company_info=f"Контакт: {data['contact_phone']}",
                requirements=data["vacancy_requirements"]
            )

        # 3. Создаем вакансию
        await Repository.create_vacancy(
            employer_id=employer.id,
            position=data["vacancy_title"],
            city=data["city"],
            salary=data["vacancy_salary"],
            requirements=data["vacancy_requirements"],
            count_needed=data["vacancy_needed"]
        )

        await callback.message.edit_text(
            "🎉 Вакансия успешно сохранена!\nОжидайте подбор кандидатов."
        )

    except Exception as e:
        await callback.message.edit_text(f"❌ Ошибка при сохранении: {e}")

    finally:
        await state.clear()
        await callback.answer()


# ---------- Подтверждение: Нет ----------
@router.callback_query(F.data == "employer_confirm_no")
async def employer_confirm_no(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "❌ Создание вакансии отменено.\nВведите /employer_start, чтобы попробовать снова."
    )
    await callback.answer()
