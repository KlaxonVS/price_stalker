import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.sql.expression import select, update

from models import Base, Item
from settings import DATABASE_NAME


async def create_database():
    engine = create_async_engine(
        f'sqlite+aiosqlite:///{DATABASE_NAME}.db', echo=True
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def run_session(function):
    async def _wrapper(item):
        engine = create_async_engine(
            f'sqlite+aiosqlite:///{DATABASE_NAME}.db', echo=True
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
            check = session.execute(
                select(Item.id).where(id == item_id).exists().scalar_one()
            )
            await session.commit()
            return await check


@run_session
async def add_item(async_session: async_sessionmaker[AsyncSession], item):
    async with async_session() as session:
        item_id = item[0]
        price = item[1]
        async with session.begin():
            session.add(Item(id=item_id, price=price))
            await session.commit()


@run_session
async def add_items(async_session: async_sessionmaker[AsyncSession], items):
    async with async_session() as session:
        async with session.begin():
            session.add_all([
                Item(id=item[0], price=item[1])
                for item in items
                ])
            await session.commit()


@run_session
async def update_item(async_session: async_sessionmaker[AsyncSession], item):
    async with async_session() as session:
        async with session.begin():
            print(item[0])
            await session.execute(
                update(Item).where(Item.id == item[0]).values(price=item[1])
            )
            await session.commit()


@run_session
async def delete_item(async_session: async_sessionmaker[AsyncSession], item_id):
    async with async_session() as session:
        async with session.begin():
            session.delete(session.get(Item, item_id))
            await session.commit()


@run_session
async def get_all(async_session: async_sessionmaker[AsyncSession], item):
    item = Item if 'item' else item
    async with async_session() as session:
        async with session.begin():
            result = await session.scalars(select(item))
            session.expunge_all()
            return result


'''if __name__ == '__main__':
    async def main():
        items = await get_all(Item)
        for item in items:
            print(item.id, item.price)

asyncio.run(main())'''
