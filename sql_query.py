from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import numpy as np
from sql_declarative import Base, Tank, Alliance
from sqlalchemy import and_
import matplotlib.pyplot as plt
import seaborn as sns

engine = create_engine('sqlite:///alliances_and_tanks.db')
Base.metadata.bind = engine
DBSession = sessionmaker()
DBSession.bind = engine
session = DBSession()

# country = 'Poland'

# for res in session.query(Tank.seller_name).filter(Tank.owner_name == country).all():
#     print(res[0])
#
# for res in session.query(Alliance.name_2).filter(Alliance.name_1 == country).all():
#     print(res[0])


# TODO query, które pobiera dla danego kraju jego sojuszników i dla każdego z nich daje liczbę czołgów w sumie
def get_sum_of_tanks_from_allies(country, session):

    c_alliances = []
    for res in session.query(Alliance.name_2).filter(Alliance.name_1 == country).all():
        c_alliances.append(res[0])

    c_alliances_unique = list(set(c_alliances))  # list with unique elements
    print(c_alliances_unique)      # problem - kilka razy pojawia się takie samo państwo

    alliances_tanks = []
    for allian in c_alliances_unique:
        tanks = session.query(Tank.tank, Tank.amount).filter(Tank.owner_name == allian).all()
        if len(tanks) > 0:
            alliances_tanks.append([allian, list(set(tanks))])

    alliances_tanks_amount = []
    for tup in alliances_tanks:
        amount = 0
        for t in tup[1]:
            amount += t[1]
        alliances_tanks_amount.append([tup[0], amount])

    for tup in alliances_tanks:
        print(tup)

    for tup in alliances_tanks_amount:
        print(tup)

    labels, ys = zip(*alliances_tanks_amount)
    xs = np.arange(len(labels))
    width = 0.8
    # plt.yscale('log') # log scale
    fig = plt.figure()
    sns.barplot(x=xs, y=ys, palette=sns.cubehelix_palette(len(xs), start=.5, rot=-.75))
    plt.grid(axis='y')
    plt.title('Number of all tanks for allies of {}'.format(country))
    plt.xticks(xs, labels, rotation='vertical')
    fig.set_facecolor("#e8fffe")
    plt.show()
    plt.close()


# # TODO query, które wybiera sojuszników z wybranym krajem dla danego przedziału od danego roku
# country = 'Germany'
# start_year = 1967
# c_alliances = []
# for res in session.query(Alliance.name_2).filter(and_(Alliance.name_1 == country,
#                                                       Alliance.start_year >= start_year)).all():
#     c_alliances.append(res[0])
# c_alliances_unique = list(set(c_alliances))  # list with unique elements
# # print(c_alliances_unique)


# TODO query, które wybiera czołgi i ich ilość dla danego kraju
def get_tanks(country, session):
    tanks = session.query(Tank.tank, Tank.amount).filter(Tank.owner_name == country).all()
    tanks = list(set(tanks))

    labels, ys = zip(*tanks)
    xs = np.arange(len(labels))
    width = 0.8
    # plt.yscale('log') # log scale
    fig = plt.figure()
    sns.barplot(x=xs, y=ys, palette=sns.cubehelix_palette(len(xs), start=.5, rot=-.75))
    plt.grid(axis='y')
    plt.title('Number of tanks for {}'.format(country))
    plt.xticks(xs, labels, rotation='vertical')
    fig.set_facecolor("#e8fffe")
    plt.show()
    plt.close()


# TODO query, które pobiera dla danego kraju te, które sprzedały mu czołgi i dla tych krajów liczbę wszystich czołgów
def get_tank_sellers_tank_sum(country, session):
    c_sellers = []
    for res in session.query(Tank.seller_name).filter(Tank.owner_name == country).all():
        c_sellers.append(res[0])

    seller_tanks = []
    for sell in c_sellers:
        tanks = session.query(Tank.tank, Tank.amount).filter(Tank.owner_name == sell).all()
        if len(tanks) > 0:
            seller_tanks.append([sell, list(set(tanks))])
    # seller_tanks = list(set(seller_tanks))

    sellers_tanks_amount = []
    for tup in seller_tanks:
        amount = 0
        for t in tup[1]:
            amount += t[1]
        sellers_tanks_amount.append((tup[0], amount))

        sellers_tanks_amount = list(set(sellers_tanks_amount))

    labels, ys = zip(*sellers_tanks_amount)
    xs = np.arange(len(labels))
    width = 0.8
    # plt.yscale('log') # log scale
    fig = plt.figure()
    sns.barplot(x=xs, y=ys, palette=sns.cubehelix_palette(len(xs), start=.5, rot=-.75))
    plt.grid(axis='y')
    plt.title('Number of all tanks for tank sellers of {}'.format(country))
    plt.xticks(xs, labels, rotation='vertical')
    fig.set_facecolor("#e8fffe")
    plt.show()
    plt.close()


# TODO query, które wybiera wszystkich właścicieli dowolnego czołgu i robi wykres ich ilości w zależności od państwa
def get_countries_with_tank(tank_name):
    countries = []
    for res in session.query(Tank.owner_name, Tank.amount).filter(Tank.tank == tank_name).all():
        countries.append(res)
    countries = list(set(countries))
    labels, ys = zip(*countries)
    xs = np.arange(len(labels))
    width = 0.8
    # plt.yscale('log') # log scale
    fig = plt.figure()
    sns.barplot(x=xs, y=ys, palette=sns.cubehelix_palette(len(xs), start=.5, rot=-.75))
    plt.grid(axis='y')
    plt.title('Number of all countries owning the {} tank'.format(tank_name))
    plt.xticks(xs, labels, rotation='vertical')
    fig.set_facecolor("#e8fffe")
    plt.show()
    plt.close()
    print(sum(ys))


# TODO query, które znajduje wszystkie czołgi i zwraca krotki (nazwa czołgu, ilość egzemplarzy na całym świecie)
def get_tanks_by_popularity():
    tank_names = []
    for res in session.query(Tank.tank).all():
        tank_names.append(res)

    tank_names = list(set(tank_names))

    tank_numbers = []
    for t in tank_names:
        owners = []
        for res in session.query(Tank.owner_name, Tank.amount).filter(Tank.tank == t[0]).all():
            owners.append(res)
        labels, ys = zip(*owners)
        tank_numbers.append((sum(ys), t[0]))
        print(sum(ys), t[0], labels)
    return tank_numbers


# TODO rysowanie bar chartu z czołgami i ich liczbą występowania na świecie w zależności od min liczby występowań
def draw_all_tanks_by_popularity(min_pop=200):
    all_tanks = get_tanks_by_popularity()

    tanks_chosen = []

    for t in all_tanks:
        if t[0] >= min_pop:
            tanks_chosen.append(t)

    ys, labels = zip(*tanks_chosen)
    xs = np.arange(len(labels))
    width = 0.8
    # plt.yscale('log') # log scale
    fig = plt.figure()
    sns.barplot(x=xs, y=ys, palette=sns.cubehelix_palette(len(xs), start=.5, rot=-.75))
    plt.grid(axis='y')
    plt.title('Number of all tanks in the world more popular than {}'.format(min_pop))
    plt.xticks(xs, labels, rotation='vertical')
    fig.set_facecolor("#e8fffe")
    plt.show()
    plt.close()


# TODO query, które znajduje wszystkie czołgi i zwraca krotki (nazwa czołgu, ilość państw, które taki czołg posiadają)
def get_tanks_by_number_of_owners():
    tank_names = []
    for res in session.query(Tank.tank).all():
        tank_names.append(res)

    tank_names = list(set(tank_names))

    tank_numbers = []
    for t in tank_names:
        owners = []
        for res in session.query(Tank.owner_name, Tank.amount).filter(Tank.tank == t[0]).all():
            owners.append(res)
        labels, ys = zip(*owners)
        tank_numbers.append((len(labels), t[0]))
    return tank_numbers


# TODO funkcja sortująca po popularnych czołgach ze względu na liczbę krajów je posiadających
def get_popular_tanks_by_number_of_owners(min_pop=2):
    all_tanks = get_tanks_by_number_of_owners()
    all_tanks = list(set(all_tanks))
    tanks_chosen = []

    for t in all_tanks:
        if t[0] >= min_pop:
            tanks_chosen.append(t)

    return list(set(tanks_chosen))


# TODO rysowanie bar chartu z czołgami i liczbą krajów je posiadających w zależności od min liczby występowań
def draw_all_tanks_by_number_of_owners(min_pop=2):

    tanks_chosen = get_popular_tanks_by_number_of_owners(min_pop=min_pop)

    ys, labels = zip(*tanks_chosen)
    xs = np.arange(len(labels))
    width = 0.8
    # plt.yscale('log') # log scale
    fig = plt.figure()
    sns.barplot(x=xs, y=ys, palette=sns.cubehelix_palette(len(xs), start=.5, rot=-.75))
    plt.grid(axis='y')
    plt.title('Number of countries owning most popular tanks with more than {} countries'.format(min_pop))
    plt.xticks(xs, labels, rotation='vertical')
    fig.set_facecolor("#e8fffe")
    plt.show()
    plt.close()


if __name__ == '__main__':


    # get_sum_of_tanks_from_allies('Russia', session)
    # get_tanks('Russia', session)
    # get_tank_sellers_tank_sum('Japan', session)
    # get_countries_with_tank('T-55')
    draw_all_tanks_by_popularity(500)
    # get_tanks_by_popularity()
    # get_tanks_by_number_of_owners()
    # draw_all_tanks_by_number_of_owners()
    # _, tank_names = zip(*get_popular_tanks_by_number_of_owners(min_pop=3))
    # print(tank_names)
    # for t in tank_names:
    #     get_countries_with_tank(t)