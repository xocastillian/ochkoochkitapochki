from db.database import engine
from db.models import Base

def create_tables():
    print(">>> Создаем таблицы...")
    Base.metadata.create_all(bind=engine)
    print(">>> Таблицы успешно созданы!")

if __name__ == "__main__":
    create_tables()
