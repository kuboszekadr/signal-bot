import os
import logging

from sqlalchemy import create_engine, Column, Integer, String, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from pydantic_settings import BaseSettings


Base = declarative_base()

class DBConfig(BaseSettings):
    path: str

    class Config:
        env_prefix = 'SQLLITE_'
    

class Chat(Base):
    __tablename__ = 'chats'
    message_id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String(50))
    message = Column(Text)
    envelope = Column(JSON, nullable=False)

db_config = DBConfig()
engine = create_engine(
    f'sqlite:///{db_config.path}', 
    echo=True
    )

local_session = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
    )

if not os.path.exists(db_config.path):
    logging.info(f"Initalizing sqllite database under: {db_config.path}")    
    Base.metadata.create_all(bind=engine)