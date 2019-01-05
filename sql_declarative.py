# based on https://www.pythoncentral.io/introductory-tutorial-python-sqlalchemy/

import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Tank(Base):
    __tablename__ = 'tanks'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    owner_name = Column(String(250), nullable=False)
    tank = Column(String(250), nullable=False)
    amount = Column(Integer, nullable=False)
    seller_name = Column(String(250), nullable=False)


class Alliance(Base):
    __tablename__ = 'alliances'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    name_1 = Column(String(250), nullable=False)
    name_2 = Column(String(250), nullable=False)
    start_year = Column(Integer, nullable=True)
    end_year = Column(Integer, nullable=True)




# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///alliances_and_tanks.db')

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)