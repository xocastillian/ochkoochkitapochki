from aiogram.fsm.state import StatesGroup, State


# Состояния для регистрации кандидатов
# Используется для сбора анкеты с 9 полями
class CandidateStates(StatesGroup):
    name = State()  # ФИО кандидата
    age = State()  # Возраст
    city = State()  # Город проживания
    experience = State()  # Опыт работы
    phone = State()  # Номер телефона
    position = State()  # Желаемая должность
    expected_salary = State()  # Ожидаемая зарплата
    available_from = State()  # Дата доступности
    confirm = State()  # Подтверждение данных перед сохранением
