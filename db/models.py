from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Базовый класс для всех моделей
Base = declarative_base()


# Таблица пользователей
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    role = Column(String(50), nullable=False)  # 'candidate' или 'employer'
    username = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи с другими таблицами
    candidate = relationship('Candidate', uselist=False, back_populates='user', cascade='all, delete-orphan')
    employer = relationship('Employer', uselist=False, back_populates='user', cascade='all, delete-orphan')


# Таблица профилей кандидатов
class Candidate(Base):
    __tablename__ = 'candidates'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    city = Column(String(255), nullable=False)
    experience = Column(Text, nullable=False)  # Описание опыта работы
    phone = Column(String(20), nullable=False)
    desired_position = Column(String(255), nullable=False)
    expected_salary = Column(Float, nullable=False)
    ready_date = Column(String(100), nullable=False)  # Дата или описание готовности
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    user = relationship('User', back_populates='candidate')
    matched_candidates = relationship('MatchedCandidate', back_populates='candidate', cascade='all, delete-orphan')


# Таблица профилей работодателей
class Employer(Base):
    __tablename__ = 'employers'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    company_name = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    company_info = Column(Text, nullable=False)  # Описание компании
    requirements = Column(Text, nullable=False)  # Требования к работникам
    rating = Column(Float, default=0.0)  # Средняя оценка
    rating_count = Column(Integer, default=0)  # Количество оценок
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    user = relationship('User', back_populates='employer')
    vacancies = relationship('Vacancy', back_populates='employer', cascade='all, delete-orphan')
    ratings = relationship('EmployerRating', back_populates='employer', cascade='all, delete-orphan')


# Таблица вакансий
class Vacancy(Base):
    __tablename__ = 'vacancies'
    
    id = Column(Integer, primary_key=True)
    employer_id = Column(Integer, ForeignKey('employers.id'), nullable=False)
    position = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    salary = Column(Float, nullable=False)
    requirements = Column(Text, nullable=False)  # Требования к кандидату
    count_needed = Column(Integer, default=1)  # Сколько людей нужно
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    employer = relationship('Employer', back_populates='vacancies')
    matched_candidates = relationship('MatchedCandidate', back_populates='vacancy', cascade='all, delete-orphan')


# Таблица совпадений (кандидат - вакансия)
class MatchedCandidate(Base):
    __tablename__ = 'matched_candidates'
    
    id = Column(Integer, primary_key=True)
    vacancy_id = Column(Integer, ForeignKey('vacancies.id'), nullable=False)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    matching_score = Column(Float, default=0.0)  # Оценка совпадения (0-100)
    contact_requested = Column(Boolean, default=False)  # Кандидат запросил контакт
    contact_shared = Column(Boolean, default=False)  # Контакт был поделен
    candidate_confirmed_hire = Column(Boolean, default=False)  # Кандидат согласился на найм
    employer_confirmed_hire = Column(Boolean, default=False)  # Работодатель подтвердил найм
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    vacancy = relationship('Vacancy', back_populates='matched_candidates')
    candidate = relationship('Candidate', back_populates='matched_candidates')


# Таблица рейтингов работодателей
class EmployerRating(Base):
    __tablename__ = 'employer_ratings'
    
    id = Column(Integer, primary_key=True)
    employer_id = Column(Integer, ForeignKey('employers.id'), nullable=False)
    candidate_id = Column(Integer, ForeignKey('candidates.id'), nullable=False)
    rating = Column(Integer, nullable=False)  # Оценка 1-5
    comment = Column(Text, nullable=True)  # Комментарий кандидата
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    employer = relationship('Employer', back_populates='ratings')
