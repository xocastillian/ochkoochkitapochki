# db/repository.py
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User, Candidate, Employer, Vacancy, MatchedCandidate, EmployerRating
from db.database import AsyncSessionLocal  # <- убедитесь, что так называется

class Repository:
    """
    Асинхронная точка доступа к БД.
    Все CRUD операции через AsyncSessionLocal.
    """

    # -------- USERS: создание пользователя --------
    @staticmethod
    async def create_user(telegram_id: int, role: str, username: str = None) -> User:
        async with AsyncSessionLocal() as session:
            user = User(telegram_id=telegram_id, role=role, username=username)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    # -------- USERS: получение пользователя по telegram_id --------
    @staticmethod
    async def get_user_by_telegram_id(telegram_id: int) -> User | None:
        async with AsyncSessionLocal() as session:
            stmt = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(stmt)
            return result.scalars().first()

    # -------- CANDIDATES: создание профиля кандидата --------
    @staticmethod
    async def create_candidate(user_id: int, name: str, age: int, city: str,
                              experience: str, phone: str, desired_position: str,
                              expected_salary: float, ready_date: str) -> Candidate:
        async with AsyncSessionLocal() as session:
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
    async def get_candidate_by_id(candidate_id: int) -> Candidate | None:
        async with AsyncSessionLocal() as session:
            stmt = select(Candidate).where(Candidate.id == candidate_id)
            result = await session.execute(stmt)
            return result.scalars().first()

    # -------- CANDIDATES: получение всех кандидатов --------
    @staticmethod
    async def get_all_candidates() -> list[Candidate]:
        async with AsyncSessionLocal() as session:
            stmt = select(Candidate)
            result = await session.execute(stmt)
            return result.scalars().all()

    # -------- CANDIDATES: обновление профиля кандидата --------
    @staticmethod
    async def update_candidate(candidate_id: int, **kwargs) -> None:
        async with AsyncSessionLocal() as session:
            stmt = update(Candidate).where(Candidate.id == candidate_id).values(**kwargs)
            await session.execute(stmt)
            await session.commit()

    # -------- EMPLOYERS: создание профиля работодателя --------
    @staticmethod
    async def create_employer(user_id: int, company_name: str, city: str,
                             company_info: str, requirements: str) -> Employer:
        async with AsyncSessionLocal() as session:
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
    async def get_employer_by_id(employer_id: int) -> Employer | None:
        async with AsyncSessionLocal() as session:
            stmt = select(Employer).where(Employer.id == employer_id)
            result = await session.execute(stmt)
            return result.scalars().first()

    # -------- EMPLOYERS: получение работодателя по user_id --------
    @staticmethod
    async def get_employer_by_user_id(user_id: int) -> Employer | None:
        async with AsyncSessionLocal() as session:
            stmt = select(Employer).where(Employer.user_id == user_id)
            result = await session.execute(stmt)
            return result.scalars().first()

    # -------- VACANCIES: создание новой вакансии --------
    @staticmethod
    async def create_vacancy(employer_id: int, position: str, city: str,
                             salary: float, requirements: str, count_needed: int = 1) -> Vacancy:
        async with AsyncSessionLocal() as session:
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
    async def get_vacancy_by_id(vacancy_id: int) -> Vacancy | None:
        async with AsyncSessionLocal() as session:
            stmt = select(Vacancy).where(Vacancy.id == vacancy_id)
            result = await session.execute(stmt)
            return result.scalars().first()

    # -------- VACANCIES: получение всех вакансий работодателя --------
    @staticmethod
    async def get_vacancies_by_employer(employer_id: int) -> list[Vacancy]:
        async with AsyncSessionLocal() as session:
            stmt = select(Vacancy).where(Vacancy.employer_id == employer_id)
            result = await session.execute(stmt)
            return result.scalars().all()

    # -------- VACANCIES: получение всех активных вакансий --------
    @staticmethod
    async def get_all_vacancies(active_only: bool = True) -> list[Vacancy]:
        async with AsyncSessionLocal() as session:
            if active_only:
                stmt = select(Vacancy).where(Vacancy.is_active == True)
            else:
                stmt = select(Vacancy)
            result = await session.execute(stmt)
            return result.scalars().all()

    # -------- MATCHED_CANDIDATES: добавление совпадения --------
    @staticmethod
    async def add_match(vacancy_id: int, candidate_id: int, matching_score: float) -> MatchedCandidate:
        async with AsyncSessionLocal() as session:
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
    async def get_matches_for_vacancy(vacancy_id: int) -> list[MatchedCandidate]:
        async with AsyncSessionLocal() as session:
            stmt = select(MatchedCandidate).where(
                MatchedCandidate.vacancy_id == vacancy_id
            ).order_by(MatchedCandidate.matching_score.desc())
            result = await session.execute(stmt)
            return result.scalars().all()

    # -------- MATCHED_CANDIDATES: получение совпадения по ID --------
    @staticmethod
    async def get_match_by_id(match_id: int) -> MatchedCandidate | None:
        async with AsyncSessionLocal() as session:
            stmt = select(MatchedCandidate).where(MatchedCandidate.id == match_id)
            result = await session.execute(stmt)
            return result.scalars().first()

    # -------- MATCHED_CANDIDATES: обновление статуса совпадения --------
    @staticmethod
    async def update_match_status(match_id: int, **kwargs) -> None:
        async with AsyncSessionLocal() as session:
            stmt = update(MatchedCandidate).where(
                MatchedCandidate.id == match_id
            ).values(**kwargs)
            await session.execute(stmt)
            await session.commit()

    # -------- EMPLOYER_RATINGS: добавление рейтинга --------
    @staticmethod
    async def add_rating(employer_id: int, candidate_id: int, rating: int, comment: str = None) -> EmployerRating:
        """
        Добавляет оценку работодателя от кандидата.
        Затем пересчитывает average rating и count в таблице Employer.
        """
        async with AsyncSessionLocal() as session:
            new_rating = EmployerRating(
                employer_id=employer_id,
                candidate_id=candidate_id,
                rating=rating,
                comment=comment
            )
            session.add(new_rating)
            await session.commit()
            await session.refresh(new_rating)

            # Посчитать средний рейтинг и количество через SQL aggregate
            stmt = select(func.avg(EmployerRating.rating), func.count(EmployerRating.id)).where(
                EmployerRating.employer_id == employer_id
            )
            avg_count_res = await session.execute(stmt)
            avg_val, cnt = avg_count_res.one()
            avg_rating = float(avg_val) if avg_val is not None else float(rating)
            cnt = int(cnt)

            # Обновить работодателя
            update_stmt = update(Employer).where(Employer.id == employer_id).values(
                rating=avg_rating,
                rating_count=cnt
            )
            await session.execute(update_stmt)
            await session.commit()

            return new_rating

    # -------- EMPLOYER_RATINGS: получение рейтинга работодателя --------
    @staticmethod
    async def get_employer_rating(employer_id: int):
        async with AsyncSessionLocal() as session:
            stmt = select(Employer).where(Employer.id == employer_id)
            result = await session.execute(stmt)
            employer = result.scalars().first()
            if employer:
                return {'rating': employer.rating, 'count': employer.rating_count}
            return None

    # -------- EMPLOYER_RATINGS: получение всех оценок работодателя --------
    @staticmethod
    async def get_all_ratings(employer_id: int) -> list[EmployerRating]:
        async with AsyncSessionLocal() as session:
            stmt = select(EmployerRating).where(
                EmployerRating.employer_id == employer_id
            ).order_by(EmployerRating.created_at.desc())
            result = await session.execute(stmt)
            return result.scalars().all()
