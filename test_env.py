import os
from db.database import engine

print("DATABASE_URL from env:", os.getenv("DATABASE_URL"))
print("Engine URL parsed:    ", engine.url)
