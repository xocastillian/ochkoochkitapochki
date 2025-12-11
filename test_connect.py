import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    url = os.getenv("DATABASE_URL")
    print("Connecting to:", url)
    conn = await asyncpg.connect(url)
    print("Connected!")
    await conn.close()

asyncio.run(main())
