from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db.repository import Repository
from bot.utils.scoring import calculate_score

# Создаем маршрутизатор для хендлеров подбора кандидатов
router = Router()

# Локальная переменная для хранения сессий подбора кандидатов
# Ключ: user_id, значение: словарь с vacancy_id, index, candidates list
match_sessions = {}


# -------- Вспомогательная функция: создание клавиатуры для отображения кандидата --------
def get_candidate_navigation_keyboard(has_next: bool = True):
    """
    Создает inline клавиатуру для навигации по кандидатам.
    """
    kb = InlineKeyboardBuilder()
    
    if has_next:
        kb.button(text="➡️ Далее", callback_data="match_next")
    
    kb.button(text="📱 Получить контакт", callback_data="match_contact")
    kb.adjust(1)
    
    return kb.as_markup()


# -------- Вспомогательная функция: создание клавиатуры для подтверждения оферты --------
def get_offer_confirmation_keyboard():
    """
    Создает inline клавиатуру для подтверждения согласия с офертой.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Показать контакт", callback_data="match_contact_show")
    kb.button(text="❌ Отмена", callback_data="match_cancel")
    kb.adjust(1)
    
    return kb.as_markup()


# -------- Callback: нажата кнопка "Подобрать кандидатов" --------
@router.callback_query(F.data.startswith("match_"))
async def start_matching(callback: CallbackQuery):
    """
    Начинает процесс подбора кандидатов для вакансии.
    Получает vacancy_id, считает скоры, показывает первого кандидата.
    """
    # -------- Распарсиваем vacancy_id из callback_data --------
    try:
        vacancy_id = int(callback.data.split("_")[1])
    except (IndexError, ValueError):
        await callback.answer("❌ Ошибка при обработке.", show_alert=True)
        return
    
    user_id = callback.from_user.id
    
    # -------- Получаем вакансию --------
    vacancy = await Repository.get_vacancy_by_id(vacancy_id)
    if not vacancy:
        await callback.answer("❌ Вакансия не найдена.", show_alert=True)
        return
    
    # -------- Получаем всех кандидатов --------
    candidates = await Repository.get_all_candidates()
    
    if not candidates:
        await callback.message.edit_text("❌ Нет зарегистрированных кандидатов.")
        return
    
    # -------- Рассчитываем скоры для каждого кандидата --------
    candidates_with_scores = []
    for candidate in candidates:
        score = await calculate_score(candidate, vacancy)
        if score > 0:  # Добавляем только кандидатов с положительным скором
            candidates_with_scores.append({
                'candidate': candidate,
                'score': score
            })
    
    # -------- Сортируем по скору (выше — лучше) --------
    candidates_with_scores.sort(key=lambda x: x['score'], reverse=True)
    
    if not candidates_with_scores:
        await callback.message.edit_text(
            "❌ Нет подходящих кандидатов для этой вакансии."
        )
        return
    
    # -------- Сохраняем сессию --------
    match_sessions[user_id] = {
        'vacancy_id': vacancy_id,
        'index': 0,
        'candidates': candidates_with_scores
    }
    
    # -------- Показываем первого кандидата --------
    await _show_candidate(callback.message, user_id)
    await callback.answer()


# -------- Вспомогательная функция: показать кандидата --------
async def _show_candidate(message, user_id):
    """
    Показывает текущего кандидата из сессии.
    """
    if user_id not in match_sessions:
        await message.edit_text("❌ Сессия истекла.")
        return
    
    session = match_sessions[user_id]
    candidates = session['candidates']
    index = session['index']
    
    # -------- Проверяем, не вышли ли за границы списка --------
    if index >= len(candidates):
        await message.edit_text(
            "✅ Кандидаты закончились.\n\n"
            "Вы просмотрели всех подходящих кандидатов."
        )
        del match_sessions[user_id]
        return
    
    # -------- Получаем текущего кандидата и его скор --------
    current_item = candidates[index]
    candidate = current_item['candidate']
    score = current_item['score']
    
    # -------- Формируем карточку кандидата --------
    candidate_card = (
        f"👤 <b>Имя:</b> {candidate.name}\n"
        f"🎂 <b>Возраст:</b> {candidate.age} лет\n"
        f"📍 <b>Город:</b> {candidate.city}\n"
        f"💰 <b>Желаемая зарплата:</b> {candidate.expected_salary} руб.\n"
        f"💼 <b>Опыт:</b> {candidate.experience}\n"
        f"🎯 <b>Совпадение:</b> {score}%\n\n"
        f"<i>Кандидат {index + 1} из {len(candidates)}</i>"
    )
    
    # -------- Проверяем, есть ли еще кандидаты после текущего --------
    has_next = (index + 1) < len(candidates)
    
    await message.edit_text(
        candidate_card,
        reply_markup=get_candidate_navigation_keyboard(has_next),
        parse_mode="HTML"
    )


# -------- Callback: кнопка "Далее" — следующий кандидат --------
@router.callback_query(F.data == "match_next")
async def next_candidate(callback: CallbackQuery):
    """
    Переходит к следующему кандидату в списке.
    """
    user_id = callback.from_user.id
    
    if user_id not in match_sessions:
        await callback.answer("❌ Сессия истекла.", show_alert=True)
        return
    
    # -------- Увеличиваем индекс --------
    match_sessions[user_id]['index'] += 1
    
    # -------- Показываем следующего кандидата --------
    await _show_candidate(callback.message, user_id)
    await callback.answer()


# -------- Callback: кнопка "Получить контакт" --------
@router.callback_query(F.data == "match_contact")
async def request_contact(callback: CallbackQuery):
    """
    Показывает оферту и просит подтвердить согласие перед отправкой контакта.
    """
    await callback.message.edit_text(
        "📋 <b>Условия оферты:</b>\n\n"
        "Нажимая кнопку ниже, вы подтверждаете согласие с условиями оферты.\n\n"
        "Контакт кандидата будет отправлен в соответствии с политикой конфиденциальности.",
        reply_markup=get_offer_confirmation_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


# -------- Callback: кнопка "Показать контакт" --------
@router.callback_query(F.data == "match_contact_show")
async def show_contact(callback: CallbackQuery):
    """
    Показывает номер телефона кандидата и сохраняет событие в БД.
    """
    user_id = callback.from_user.id
    
    if user_id not in match_sessions:
        await callback.answer("❌ Сессия истекла.", show_alert=True)
        return
    
    session = match_sessions[user_id]
    index = session['index']
    candidates = session['candidates']
    vacancy_id = session['vacancy_id']
    
    # -------- Проверяем границы --------
    if index >= len(candidates):
        await callback.answer("❌ Кандидат не найден.", show_alert=True)
        return
    
    # -------- Получаем кандидата --------
    current_item = candidates[index]
    candidate = current_item['candidate']
    score = current_item['score']
    
    try:
        # -------- Сохраняем событие в БД --------
        await Repository.add_match(
            vacancy_id=vacancy_id,
            candidate_id=candidate.id,
            matching_score=score
        )
        
        # -------- Показываем контакт --------
        contact_message = (
            f"✅ <b>Контакт кандидата:</b>\n\n"
            f"📱 <b>Телефон:</b> <code>{candidate.phone}</code>\n"
            f"👤 <b>Имя:</b> {candidate.name}\n\n"
            f"<i>Контакт был сохранен в истории.</i>"
        )
        
        await callback.message.edit_text(
            contact_message,
            parse_mode="HTML"
        )
        
    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка при сохранении: {str(e)}"
        )
    
    await callback.answer()


# -------- Callback: кнопка "Отмена" --------
@router.callback_query(F.data == "match_cancel")
async def cancel_contact(callback: CallbackQuery):
    """
    Отменяет запрос контакта и возвращается к карточке кандидата.
    """
    user_id = callback.from_user.id
    
    if user_id in match_sessions:
        await _show_candidate(callback.message, user_id)
    else:
        await callback.answer("❌ Сессия истекла.", show_alert=True)
    
    await callback.answer()
