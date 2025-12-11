import asyncio
import sys

# На Windows asyncpg ломается под ProactorEventLoop → фикс:
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import create_tables  # теперь можно запускать

