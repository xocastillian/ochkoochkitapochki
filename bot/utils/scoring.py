"""
Модуль для расчета совпадения между кандидатом и вакансией.
Используется для ранжирования кандидатов по релевантности.
"""


async def calculate_score(candidate, vacancy) -> int:
    """
    Рассчитывает процент совпадения между кандидатом и вакансией.
    
    Критерии оценки:
    +40 если города совпадают
    +25 если ожидаемая зарплата кандидата <= предложенной зарплате
    +25 если требования вакансии содержат ключевые слова из опыта кандидата
    +10 если кандидат готов в ближайшее время
    
    Максимальный результат: 100 (100% совпадение)
    
    Args:
        candidate: объект Candidate из БД
        vacancy: объект Vacancy из БД
    
    Returns:
        int: число от 0 до 100 (процент совпадения)
    """
    score = 0
    
    # -------- Критерий 1: города совпадают --------
    if candidate.city.lower() == vacancy.city.lower():
        score += 40
    
    # -------- Критерий 2: зарплата подходит --------
    if candidate.expected_salary <= vacancy.salary:
        score += 25
    
    # -------- Критерий 3: требования соответствуют опыту --------
    score += _check_experience_match(candidate.experience, vacancy.requirements)
    
    # -------- Критерий 4: кандидат готов скоро --------
    if _is_ready_soon(candidate.ready_date):
        score += 10
    
    # Возвращаем минимум 100%, чтобы не превысить максимум
    return min(score, 100)


def _check_experience_match(experience: str, requirements: str) -> int:
    """
    Проверяет, содержит ли опыт кандидата ключевые слова из требований.
    
    Args:
        experience: описание опыта кандидата
        requirements: требования вакансии
    
    Returns:
        int: 0 если нет совпадений, 25 если есть совпадение
    """
    # Преобразуем оба текста в нижний регистр для сравнения
    experience_lower = experience.lower()
    requirements_lower = requirements.lower()
    
    # Разбиваем требования на слова
    requirement_words = requirements_lower.split()
    
    # Проверяем, есть ли хотя бы одно слово из требований в опыте
    # Слово должно быть минимум 3 символа, чтобы избежать шума
    for word in requirement_words:
        if len(word) >= 3 and word in experience_lower:
            return 25
    
    return 0


def _is_ready_soon(ready_date: str) -> bool:
    """
    Проверяет, готов ли кандидат выйти на работу в ближайшее время.
    
    Распознает:
    - "завтра", "скоро", "неделю", "день", "дней", "дня"
    - или пустую строку (если готов немедленно)
    
    Args:
        ready_date: дата доступности в виде строки
    
    Returns:
        bool: True если готов скоро, False иначе
    """
    ready_lower = ready_date.lower()
    
    # Ключевые слова, которые означают скорую готовность
    ready_keywords = [
        "завтра",
        "скоро",
        "неделю",
        "день",
        "дней",
        "дня",
        "немедленно",
        "сразу"
    ]
    
    # Проверяем наличие ключевых слов
    for keyword in ready_keywords:
        if keyword in ready_lower:
            return True
    
    # Если что-то указано, то кандидат готов
    if ready_date and ready_date.strip():
        return True
    
    return False
