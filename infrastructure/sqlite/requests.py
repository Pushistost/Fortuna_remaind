from sqlalchemy import select

from infrastructure.sqlite.models import async_session, User, Category, Items


async def set_user(tg_id: int) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()


async def get_categories():
    async with async_session() as session:
        result = await session.scalars(select(Category))
        return result


async def get_category_item(category_id):
    async with async_session() as session:
        result = await session.scalars(select(Items).where(Items.category == category_id))
        return result


async def get_item(item_id):
    async with async_session() as session:
        result = await session.scalar(select(Items).where(Items.id == item_id))
        return result
