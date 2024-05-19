from sqlalchemy import select

from models import async_session
from models import User, Category, Items


async def set_user(tg_id: int) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()

# Поискать проблему тут
async def get_categories():
    async with async_session() as session:
        return session.scalars(select(Category))


async def get_category_item(category_id):
    async with async_session() as session:
        return await session.scalars(select(Items).where(Items.category == category_id))
