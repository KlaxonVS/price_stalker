from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    price = Column(Integer, nullable=False)
    title = Column(String(150),)
