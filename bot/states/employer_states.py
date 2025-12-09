from aiogram.fsm.state import StatesGroup, State


# Состояния для регистрации работодателей и создания вакансий
# Используется для сбора данных компании и информации о вакансии
class EmployerStates(StatesGroup):
    company_name = State()  # Название компании
    contact_phone = State()  # Контактный телефон
    city = State()  # Город, где находится компания
    vacancy_title = State()  # Название вакансии/должности
    vacancy_salary = State()  # Зарплата для вакансии
    vacancy_requirements = State()  # Требования к кандидату
    vacancy_needed = State()  # Количество вакансий
    confirm = State()  # Подтверждение данных перед сохранением
