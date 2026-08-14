import asyncio

from sqlalchemy import text

from app.core.database import engine


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