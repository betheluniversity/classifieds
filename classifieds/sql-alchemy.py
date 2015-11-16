__author__ = 'phg49389'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import *

Base = declarative_base()
engine = create_engine('sqlite:///classifieds2.db')
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()

class Classifieds(Base):
    __tablename__ = "classifieds"
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    price = Column(String(50), nullable=False)
    duration = Column(String(15), nullable=False)
    categories = Column(String(200), nullable=False)
    username = Column(String(8), ForeignKey('contacts.username'))
    dateAdded = Column(DateTime, nullable=False)
    completed = Column(Boolean, nullable=False)

class Contacts(Base):
    __tablename__ = "contacts"
    username = Column(String(8), primary_key=True)
    first_name = Column(String(20), nullable=False)
    last_name = Column(String(30), nullable=False)
    email = Column(String(50), nullable=False)
    phone_number = Column(String(15), nullable=False)

def create_tables():
    # TODO
    pass

def table_exists(table_name):
    # TODO
    pass

def reset_tables():
    # TODO
    pass

def add_classified(title, description, price, duration, categories, username):
    # TODO
    pass

def add_contact(username, first_name, last_name, email, phone_number):
    # TODO
    pass

def mark_entry_as_complete(entry_id):
    # TODO
    pass