from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

import settings

def db_connect():
    return create_engine(URL(**settings.DATABASE))

DeclarativeBase = declarative_base()

def create_posts_table(engine):
    DeclarativeBase.metadata.create_all(engine)

class Posts(DeclarativeBase):
    """SQLAlchemy posts model"""
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    subforum = Column('subforum', String)
    username = Column('username', String)
    time = Column('time', DateTime)
    text = Column('text', Text)
