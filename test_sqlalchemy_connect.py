import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os
from dotenv import load_dotenv

# Windows fix
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()
url = os.getenv("DATABASE_URL")
print("SQLAlchemy URL:", url)

async def main():
    engine = create_async_engine(url, echo=True)

    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("Result:", result.scalar())
        print(">>> SUCCESS — psycopg работает!")
    except Exception as e:
        print("ERROR:", e)

asyncio.run(main())
