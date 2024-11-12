import datetime
import os
import random
import psycopg2

from dotenv import load_dotenv
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql.sqltypes import TIMESTAMP, DateTime
from sqlalchemy.sql.expression import func, select
from sqlalchemy import *
from sqlalchemy.sql import func

load_dotenv()

# copy-pasted from waifuquest
def get_engine():
  url = f"{os.getenv('DB')}://{os.getenv('DB_USER')}:{os.getenv('DB_PW')}@{os.getenv('DB_IP')}:5432"
  print(url)
  engine = create_engine(url, pool_size=50, echo=False)
  return engine


Base = declarative_base()

class streams(Base):
    __tablename__ = "streams"
    row_id = Column('row_id', Integer, primary_key=True,autoincrement=True)
    id = Column("id", String)
    user_id = Column("user_id", String)
    user_login = Column("user_login", String)
    user_name = Column("user_name", String)
    game_id = Column("game_id", String)
    game_name = Column("game_name", String)
    type = Column("type", String)
    title = Column("title", String)
    tags = Column("tags", ARRAY(String))
    viewer_count = Column("viewer_count", Integer)
    started_at = Column("started_at", String)
    is_mature = Column("is_mature", Boolean)
    time_created = Column(DateTime(timezone=True), server_default=func.now())

    def __init__(self, row_id, id, user_id, user_login, user_name, game_id, game_name, type, title, tags, viewer_count, started_at, is_mature):
        self.id = id
        self.user_id = user_id
        self.user_login = user_login
        self.user_name = user_name
        self.game_id = game_id
        self.game_name = game_name
        self.type = type
        self.title = title
        self.tags = tags
        self.viewer_count = viewer_count
        self.started_at = started_at
        self.is_mature = is_mature

    def __repr__(self, row_id, id, user_id, user_login, user_name, game_id, game_name, type, title, tags, viewer_count, started_at, is_mature):
        return f"({self.id} {self.user_id} {self.user_login} {self.user_name})"


engine = get_engine()
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()
stream1 = streams('','123', '345', '76', '2345', '67', '2345', '854', '643', {'123', '1231'}, 531, '8w5', True)
session.add(stream1)
session.commit()
