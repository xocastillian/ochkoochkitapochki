from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Загружаем .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Создаем engine для psycopg2
engine = create_engine(
    DATABASE_URL,
    echo=True,           # логирование SQL
    pool_pre_ping=True,  # проверка соединения перед использованием
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)
