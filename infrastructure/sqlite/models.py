from sqlalchemy import String, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker

from infrastructure.database.models.base import TableNameMixin

engine = create_async_engine(url="sqlite+aiosqlite:///infrastructure/sqlite/db.sqlite3")

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Reminders(Base, TableNameMixin):

    id: Mapped[int] = mapped_column(primary_key=True)
    time = mapped_column(DateTime)
    text: Mapped[str] = mapped_column(String(500))


async def make_base():
    async with engine.begin() as connect:
        await connect.run_sync(Base.metadata.create_all)
