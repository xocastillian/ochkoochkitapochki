from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User, Candidate, Employer, Vacancy, MatchedCandidate, EmployerRating
from db.database import SessionLocal


class Repository:
    """
    Единая точка доступа к базе данных.
    Все CRUD операции проходят через этот класс.
    """

    # -------- USERS: создание пользователя --------
    @staticmethod
    async def create_user(telegram_id: int, role: str, username: str = None):
        """
        Создает нового пользователя в БД.
        role: 'candidate' или 'employer'
        """
        async with SessionLocal() as session:
            user = User(
                telegram_id=telegram_id,
                role=role,
                username=username
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    # -------- USERS: получение пользователя по telegram_id --------
    @staticmethod
    async def get_user_by_telegram_id(telegram_id: int):
        """
        Ищет пользователя по его telegram_id.
        Возвращает объект User или None.
        """
        async with SessionLocal() as session:
            stmt = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(stmt)
            user = result.scalars().first()
            return user

    # -------- CANDIDATES: создание профиля кандидата --------
    @staticmethod
    async def create_candidate(user_id: int, name: str, age: int, city: str, 
                              experience: str, phone: str, desired_position: str, 
                              expected_salary: float, ready_date: str):
        """
        Создает новый профиль кандидата и связывает с пользователем.
        """
        async with SessionLocal() as session:
            candidate = Candidate(
                user_id=user_id,
                name=name,
                age=age,
                city=city,
                experience=experience,
                phone=phone,
                desired_position=desired_position,
                expected_salary=expected_salary,
                ready_date=ready_date
            )
            session.add(candidate)
            await session.commit()
            await session.refresh(candidate)
            return candidate

    # -------- CANDIDATES: получение профиля по ID --------
    @staticmethod
    async def get_candidate_by_id(candidate_id: int):
        """
        Ищет кандидата по его ID.
        Возвращает объект Candidate или None.
        """
        async with SessionLocal() as session:
            stmt = select(Candidate).where(Candidate.id == candidate_id)
            result = await session.execute(stmt)
            candidate = result.scalars().first()
            return candidate

    # -------- CANDIDATES: получение всех кандидатов --------
    @staticmethod
    async def get_all_candidates():
        """
        Возвращает список всех кандидатов из БД.
        """
        async with SessionLocal() as session:
            stmt = select(Candidate)
            result = await session.execute(stmt)
            candidates = result.scalars().all()
            return candidates

    # -------- CANDIDATES: обновление профиля кандидата --------
    @staticmethod
    async def update_candidate(candidate_id: int, **kwargs):
        """
        Обновляет данные кандидата.
        kwargs: поля для обновления (name, age, city и т.д.)
        """
        async with SessionLocal() as session:
            stmt = update(Candidate).where(Candidate.id == candidate_id).values(**kwargs)
            await session.execute(stmt)
            await session.commit()

    # -------- EMPLOYERS: создание профиля работодателя --------
    @staticmethod
    async def create_employer(user_id: int, company_name: str, city: str, 
                             company_info: str, requirements: str):
        """
        Создает новый профиль работодателя и связывает с пользователем.
        """
        async with SessionLocal() as session:
            employer = Employer(
                user_id=user_id,
                company_name=company_name,
                city=city,
                company_info=company_info,
                requirements=requirements
            )
            session.add(employer)
            await session.commit()
            await session.refresh(employer)
            return employer

    # -------- EMPLOYERS: получение профиля по ID --------
    @staticmethod
    async def get_employer_by_id(employer_id: int):
        """
        Ищет работодателя по его ID.
        Возвращает объект Employer или None.
        """
        async with SessionLocal() as session:
            stmt = select(Employer).where(Employer.id == employer_id)
            result = await session.execute(stmt)
            employer = result.scalars().first()
            return employer

    # -------- EMPLOYERS: получение работодателя по user_id --------
    @staticmethod
    async def get_employer_by_user_id(user_id: int):
        """
        Ищет работодателя по ID пользователя.
        Каждый пользователь-работодатель имеет один профиль.
        """
        async with SessionLocal() as session:
            stmt = select(Employer).where(Employer.user_id == user_id)
            result = await session.execute(stmt)
            employer = result.scalars().first()
            return employer

    # -------- VACANCIES: создание новой вакансии --------
    @staticmethod
    async def create_vacancy(employer_id: int, position: str, city: str, 
                            salary: float, requirements: str, count_needed: int = 1):
        """
        Создает новую вакансию для работодателя.
        """
        async with SessionLocal() as session:
            vacancy = Vacancy(
                employer_id=employer_id,
                position=position,
                city=city,
                salary=salary,
                requirements=requirements,
                count_needed=count_needed,
                is_active=True
            )
            session.add(vacancy)
            await session.commit()
            await session.refresh(vacancy)
            return vacancy

    # -------- VACANCIES: получение вакансии по ID --------
    @staticmethod
    async def get_vacancy_by_id(vacancy_id: int):
        """
        Ищет вакансию по ее ID.
        Возвращает объект Vacancy или None.
        """
        async with SessionLocal() as session:
            stmt = select(Vacancy).where(Vacancy.id == vacancy_id)
            result = await session.execute(stmt)
            vacancy = result.scalars().first()
            return vacancy

    # -------- VACANCIES: получение всех вакансий работодателя --------
    @staticmethod
    async def get_vacancies_by_employer(employer_id: int):
        """
        Возвращает все вакансии конкретного работодателя.
        """
        async with SessionLocal() as session:
            stmt = select(Vacancy).where(Vacancy.employer_id == employer_id)
            result = await session.execute(stmt)
            vacancies = result.scalars().all()
            return vacancies

    # -------- VACANCIES: получение всех активных вакансий --------
    @staticmethod
    async def get_all_vacancies(active_only: bool = True):
        """
        Возвращает все вакансии из БД.
        active_only: если True, только активные вакансии.
        """
        async with SessionLocal() as session:
            if active_only:
                stmt = select(Vacancy).where(Vacancy.is_active == True)
            else:
                stmt = select(Vacancy)
            result = await session.execute(stmt)
            vacancies = result.scalars().all()
            return vacancies

    # -------- MATCHED_CANDIDATES: добавление совпадения --------
    @staticmethod
    async def add_match(vacancy_id: int, candidate_id: int, matching_score: float):
        """
        Создает запись о совпадении кандидата с вакансией.
        matching_score: процент совпадения (0-100).
        """
        async with SessionLocal() as session:
            match = MatchedCandidate(
                vacancy_id=vacancy_id,
                candidate_id=candidate_id,
                matching_score=matching_score
            )
            session.add(match)
            await session.commit()
            await session.refresh(match)
            return match

    # -------- MATCHED_CANDIDATES: получение совпадений по вакансии --------
    @staticmethod
    async def get_matches_for_vacancy(vacancy_id: int):
        """
        Возвращает все совпадения для конкретной вакансии.
        Отсортировано по скору совпадения (выше - лучше).
        """
        async with SessionLocal() as session:
            stmt = select(MatchedCandidate).where(
                MatchedCandidate.vacancy_id == vacancy_id
            ).order_by(MatchedCandidate.matching_score.desc())
            result = await session.execute(stmt)
            matches = result.scalars().all()
            return matches

    # -------- MATCHED_CANDIDATES: получение совпадения по ID --------
    @staticmethod
    async def get_match_by_id(match_id: int):
        """
        Ищет запись о совпадении по ID.
        """
        async with SessionLocal() as session:
            stmt = select(MatchedCandidate).where(MatchedCandidate.id == match_id)
            result = await session.execute(stmt)
            match = result.scalars().first()
            return match

    # -------- MATCHED_CANDIDATES: обновление статуса совпадения --------
    @staticmethod
    async def update_match_status(match_id: int, **kwargs):
        """
        Обновляет статус совпадения.
        kwargs: contact_requested, contact_shared, candidate_confirmed_hire и т.д.
        """
        async with SessionLocal() as session:
            stmt = update(MatchedCandidate).where(
                MatchedCandidate.id == match_id
            ).values(**kwargs)
            await session.execute(stmt)
            await session.commit()

    # -------- EMPLOYER_RATINGS: добавление рейтинга --------
    @staticmethod
    async def add_rating(employer_id: int, candidate_id: int, rating: int, comment: str = None):
        """
        Добавляет оценку работодателя от кандидата.
        rating: оценка 1-5 звёзд.
        comment: опциональный комментарий.
        """
        async with SessionLocal() as session:
            new_rating = EmployerRating(
                employer_id=employer_id,
                candidate_id=candidate_id,
                rating=rating,
                comment=comment
            )
            session.add(new_rating)
            
            # Обновляем средний рейтинг работодателя
            stmt = select(EmployerRating).where(
                EmployerRating.employer_id == employer_id
            )
            result = await session.execute(stmt)
            all_ratings = result.scalars().all()
            
            if all_ratings:
                avg_rating = sum(r.rating for r in all_ratings) / len(all_ratings)
            else:
                avg_rating = rating
            
            # Обновляем поле rating в таблице Employer
            update_stmt = update(Employer).where(
                Employer.id == employer_id
            ).values(
                rating=avg_rating,
                rating_count=len(all_ratings) + 1
            )
            await session.execute(update_stmt)
            await session.commit()
            await session.refresh(new_rating)
            return new_rating

    # -------- EMPLOYER_RATINGS: получение рейтинга работодателя --------
    @staticmethod
    async def get_employer_rating(employer_id: int):
        """
        Возвращает средний рейтинг работодателя.
        """
        async with SessionLocal() as session:
            stmt = select(Employer).where(Employer.id == employer_id)
            result = await session.execute(stmt)
            employer = result.scalars().first()
            if employer:
                return {
                    'rating': employer.rating,
                    'count': employer.rating_count
                }
            return None

    # -------- EMPLOYER_RATINGS: получение всех оценок работодателя --------
    @staticmethod
    async def get_all_ratings(employer_id: int):
        """
        Возвращает все оценки, оставленные кандидатами для работодателя.
        """
        async with SessionLocal() as session:
            stmt = select(EmployerRating).where(
                EmployerRating.employer_id == employer_id
            ).order_by(EmployerRating.created_at.desc())
            result = await session.execute(stmt)
            ratings = result.scalars().all()
            return ratings
