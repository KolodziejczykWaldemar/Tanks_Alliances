# based on https://www.pythoncentral.io/introductory-tutorial-python-sqlalchemy/

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
from sql_declarative import Base, Tank, Alliance
import math
engine = create_engine('sqlite:///alliances_and_tanks.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Insert a Tank in the person table
df_tanks = pd.read_csv('tanks.csv')
for row in df_tanks.iterrows():
    new_tank = Tank(owner_name=row[1][1],
                    tank=row[1][2],
                    amount=int(row[1][3]),
                    seller_name=row[1][4])
    session.add(new_tank)
    session.commit()

df_alliances = pd.read_csv('alliance.csv')
df_alliances = df_alliances[['state_name1', 'state_name2', 'dyad_st_year', 'dyad_end_year']]
for row in df_alliances.iterrows():
    end_year = row[1][3]
    if not math.isnan(end_year):
        end_year = int(end_year)
    new_alliance = Alliance(name_1=row[1][0],
                            name_2=row[1][1],
                            start_year=int(row[1][2]),
                            end_year=end_year)
    session.add(new_alliance)
    session.commit()

