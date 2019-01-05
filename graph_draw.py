import networkx as nx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import numpy as np
from sql_declarative import Base, Tank, Alliance
from sqlalchemy import and_
import matplotlib.pyplot as plt


def draw_alliance(graph):
    fig = plt.figure()
    plt.title('Alliances graph', fontsize=16)
    nx.draw(graph, node_size=160, font_size=10, with_labels=True, node_color="skyblue", node_shape="s", alpha=0.5,
            edge_color='b')
    fig.set_facecolor("#e8fffe")
    plt.show()
    plt.close()


def draw_tanks(graph):
    fig = plt.figure()
    plt.title('Tanks - buyers and sellers graph', fontsize=16)
    nx.draw(graph, node_size=160, font_size=10, with_labels=True, node_color="skyblue", node_shape="s", alpha=0.5,
            edge_color='b')
    fig.set_facecolor("#e8fffe")
    plt.show()
    plt.close()


if __name__ == '__main__':
    engine = create_engine('sqlite:///alliances_and_tanks.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker()
    DBSession.bind = engine
    session = DBSession()

    alliances = []
    start_year = 1990
    for res in session.query(Alliance.name_1, Alliance.name_2).filter(Alliance.start_year >= start_year).all():
        alliances.append(res)
    G_allies = nx.Graph()
    G_allies.add_edges_from(alliances)
    G_allies = G_allies.to_undirected()
    print(alliances)

    draw_alliance(G_allies)


    seller_buyers = []

    for res in session.query(Tank.owner_name, Tank.seller_name).all():
        seller_buyers.append(res)
    G_sell_buy = nx.Graph()
    G_sell_buy.add_edges_from(seller_buyers)
    G_sell_buy = G_sell_buy.to_undirected()

    draw_tanks(G_sell_buy)
