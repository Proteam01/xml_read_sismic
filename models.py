from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.session import sessionmaker
from helpers import OPTIONS

Base = declarative_base()

engine = create_engine(OPTIONS['database'])
Session = sessionmaker(engine)

class Sismo(Base):
    __tablename__ = 'sismos'
    id = Column('id',Integer,primary_key=True)
    title = Column('title',String(1000),unique=True)
    description = Column('description',String(4000))
    link = Column('link',String(2000))
    latitud = Column('latitud',Float)
    longigud = Column('longitud',Float)
