import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    url = os.getenv("DATABASE_URL")
    conn = await asyncpg.connect(
        user="postgres",
        password="Aassww2222",
        database="hrbot",
        host="localhost",
        port=5433,
    )

    row = await conn.fetchrow("SELECT inet_server_addr(), inet_server_port();")
    print("Connected to host:", row["inet_server_addr"])
    print("Port inside server:", row["inet_server_port"])

asyncio.run(main())
