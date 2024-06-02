from sqlalchemy import DateTime, BigInteger, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker

from sqlite.base import TableNameMixin

engine = create_async_engine(url="sqlite+aiosqlite:///sqlite/db.sqlite3")

async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Remind(Base, TableNameMixin):

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.tg_id"))
    time = mapped_column(DateTime)
    hours: Mapped[int] = mapped_column()
    text: Mapped[str] = mapped_column()


class User(Base, TableNameMixin):

    tg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    group_id: Mapped[int] = mapped_column(BigInteger)


async def make_base():
    async with engine.begin() as connect:
        await connect.run_sync(Base.metadata.create_all)
