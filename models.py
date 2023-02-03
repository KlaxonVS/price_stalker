from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    price = Column(Integer, nullable=False)
