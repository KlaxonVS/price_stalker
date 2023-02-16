import os

from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.sql.expression import delete, select, update

from models import Base, Item
from settings import DATABASE_NAME, BASE_DIR


async def create_database():
    engine = create_async_engine(
        f'sqlite+aiosqlite:///{os.path.join(BASE_DIR, DATABASE_NAME)}.db',
        echo=True
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def run_session(function):
    async def _wrapper(item):
        engine = create_async_engine(
            f'sqlite+aiosqlite:///{os.path.join(BASE_DIR, DATABASE_NAME)}.db',
            echo=True
        )
        async_session = async_sessionmaker(engine)
        result = await function(async_session, item)
        await engine.dispose()
        return result
    return _wrapper


@run_session
async def check_item(async_session: async_sessionmaker[AsyncSession], item_id):
    async with async_session() as session:
        async with session.begin():
            check = await session.get(Item, item_id)
            await session.commit()
            return check is None


@run_session
async def add_item(async_session: async_sessionmaker[AsyncSession], item):
    async with async_session() as session:
        async with session.begin():
            session.add(Item(id=item[0], price=item[1], title=item[2]))
            await session.commit()


@run_session
async def add_items(async_session: async_sessionmaker[AsyncSession], items):
    async with async_session() as session:
        async with session.begin():
            items = [
                Item(id=item, price=price_title[0], title=price_title[1])
                for item, price_title in items.items()
                ]
            session.add_all(items)
            await session.commit()


@run_session
async def update_item(async_session: async_sessionmaker[AsyncSession], item):
    async with async_session() as session:
        async with session.begin():
            await session.execute(
                update(Item).where(Item.id == item[0]).values(price=item[1])
            )
            await session.commit()


@run_session
async def delete_item(async_session: async_sessionmaker[AsyncSession],
                      item_id):
    async with async_session() as session:
        async with session.begin():
            await session.execute(delete(Item).where(Item.id == item_id))
            await session.commit()


@run_session
async def delete_all(async_session: async_sessionmaker[AsyncSession], item):
    item = Item if 'item' else item
    async with async_session() as session:
        async with session.begin():
            await session.execute(delete(Item).where(Item.id))
            await session.commit()


@run_session
async def get_all(async_session: async_sessionmaker[AsyncSession], item):
    item = Item if 'item' else item
    async with async_session() as session:
        async with session.begin():
            result = await session.scalars(select(item))
            session.expunge_all()
            return result

if __name__ == '__name__':
    create_database()
