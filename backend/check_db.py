import asyncio

from app.core.database import engine
from sqlalchemy import text


async def main() -> None:
    async with engine.connect() as connection:
        database = await connection.scalar(
            text("SELECT current_database()")
        )

        schema = await connection.scalar(
            text("SELECT current_schema()")
        )

        print("DATABASE:", database)
        print("SCHEMA:", schema)


asyncio.run(main())