import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QComboBox, QCheckBox, QMessageBox, QPushButton
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QImage, QPalette, QBrush

import networkx as nx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import numpy as np
from sql_declarative import Base, Tank, Alliance
from sqlalchemy import and_
import matplotlib.pyplot as plt
import graph_draw as gd
import sql_query as sql


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(950, 610))
        self.setWindowTitle("Tanks and Alliances Tool")

        oImage = QImage("tank2.jpg")
        sImage = oImage.scaled(QSize(950, 610))  # resize Image to widgets size
        palette = QPalette()
        palette.setBrush(10, QBrush(sImage))  # 10 = Windowrole
        self.setPalette(palette)

        self.combo_label = QLabel(self)
        self.combo_label.setText('Graph type:')
        self.combo_label.move(20, 40)

        self.combo = QComboBox(self)
        self.combo.addItem("All Tanks")
        self.combo.addItem("All Alliances")
        self.combo.resize(150, 32)
        self.combo.move(130, 40)
        self.combo.activated[str].connect(self.onActivated)

        self.core_label = QLabel(self)
        self.core_label.setText('Cores:')
        self.core_label.move(20, 80)

        self.core_val = QLineEdit(self)
        self.core_val.move(130, 80)
        self.core_val.resize(150, 32)

        self.year_label = QLabel(self)
        self.year_label.setText('Alliances from:')
        self.year_label.move(20, 120)

        self.year_val = QLineEdit(self)
        self.year_val.move(130, 120)
        self.year_val.resize(150, 32)

        self.country_label = QLabel(self)
        self.country_label.setText('Country name:')
        self.country_label.move(370, 120)

        self.country_name = QLineEdit(self)
        self.country_name.move(480, 120)
        self.country_name.resize(150, 32)

        self.but_allie= QPushButton('Generate graph', self)
        self.but_allie.clicked.connect(self.clickMethodAllie)
        self.but_allie.resize(150, 32)
        self.but_allie.move(130, 160)

        self.but_tanks_for_country = QPushButton('Draw for country', self)
        self.but_tanks_for_country.clicked.connect(self.clickMethodCountry)
        self.but_tanks_for_country.resize(150, 32)
        self.but_tanks_for_country.move(480, 160)
        # --------------------------------------------------------------------------
        self.cb = QCheckBox('Generate more', self)
        self.cb.resize(150, 32)
        self.cb.move(20, 10)
        self.cb.toggle()
        self.cb.stateChanged.connect(self.changeTitle)
        # --------------------------------------------------------------------------
        self.check_1 = QCheckBox('Tanks distribution', self)
        self.check_1.resize(350, 32)
        self.check_1.toggle()
        self.check_1.move(370, 20)

        self.check_2 = QCheckBox('Number of all tanks of allies', self)
        self.check_2.resize(350, 32)
        self.check_2.toggle()
        self.check_2.move(370, 40)

        self.check_3 = QCheckBox('Number of all tanks of tank sellers', self)
        self.check_3.resize(380, 32)
        self.check_3.toggle()
        self.check_3.move(370, 60)

        self.combo_tanks = QComboBox(self)
        _, tank_names = zip(*sql.get_popular_tanks_by_number_of_owners(min_pop=3))
        for t in tank_names:
            self.combo_tanks.addItem(t)
        self.combo_tanks.resize(150, 32)
        self.combo_tanks.move(780, 120)

        self.tank_label = QLabel(self)
        self.tank_label.setText('Tank type:')
        self.tank_label.resize(150, 32)
        self.tank_label.move(700, 120)

        self.but_countries_for_tanks = QPushButton('Draw for tank', self)
        self.but_countries_for_tanks.clicked.connect(self.clickMethodTank)
        self.but_countries_for_tanks.resize(150, 32)
        self.but_countries_for_tanks.move(780, 160)

        self.btn = QPushButton('Click me!', self)
        self.btn.clicked.connect(self.onClick)
        self.btn.resize(150, 32)
        self.btn.move(500, 500)

    def onClick(self):
        self.SW = SecondWindow()
        self.SW.show()

    def changeTitle(self, state):

        if state == Qt.Checked:
            self.setWindowTitle('QCheckBox')
        else:
            self.setWindowTitle(' ')

    def clickMethodAllie(self):

        print('test: ' + self.country_name.text())
        print('test: ' + self.year_val.text())
        print('test: ' + self.combo.currentText())
        print('test: ' + self.core_val.text())

        if self.combo.currentText() == 'All Alliances':
            start_year = 0
            alliances = []
            if self.year_val.text():
                try:
                    start_year = int(self.year_val.text())
                except:
                    QMessageBox.about(self, 'Wrong input!', 'Year number has to be an integer.')
                    return
            for res in session.query(Alliance.name_1, Alliance.name_2).filter(Alliance.start_year >= start_year).all():
                alliances.append(res)
            G_allies = nx.Graph()
            G_allies.add_edges_from(alliances)
            G_allies = G_allies.to_undirected()

            if self.core_val.text():
                try:
                    G_allies = nx.k_core(G_allies, k=int(self.core_val.text()))
                except:
                    QMessageBox.about(self, 'Wrong input!', 'Core size has to be an integer.')
            gd.draw_alliance(G_allies)

        elif self.combo.currentText() == 'All Tanks':
            seller_buyers = []

            for res in session.query(Tank.owner_name, Tank.seller_name).all():
                seller_buyers.append(res)
            G_sell_buy = nx.Graph()
            G_sell_buy.add_edges_from(seller_buyers)
            G_sell_buy = G_sell_buy.to_undirected()

            if self.core_val.text():
                G_sell_buy.remove_edges_from(nx.selfloop_edges(G_sell_buy))

                try:
                    G_sell_buy = nx.k_core(G_sell_buy, k=int(self.core_val.text()))
                except:
                    QMessageBox.about(self, 'Wrong input!', 'Core size has to be an integer.')
            gd.draw_tanks(G_sell_buy)

    def clickMethodCountry(self):

        print('test: ' + self.country_name.text())
        print('test: ' + self.year_val.text())
        print('test: ' + self.combo.currentText())

        if self.country_name.text():
            try:
                if self.check_1.isChecked():
                    sql.get_tanks(self.country_name.text(), session)
                if self.check_2.isChecked():
                    sql.get_sum_of_tanks_from_allies(self.country_name.text(), session)
                if self.check_3.isChecked():
                    sql.get_tank_sellers_tank_sum(self.country_name.text(), session)
            except:
                QMessageBox.about(self, 'Wrong input!', 'Try to change the country name.')

    def clickMethodTank(self):

        tank_name = self.combo_tanks.currentText()
        sql.get_countries_with_tank(tank_name)



    def onActivated(self, text):
        print(text)
        if text == 'All Tanks':
            self.year_val.setEnabled(False)
        else:
            self.year_val.setEnabled(True)
        # self.year_label.setText(text)


class SecondWindow(QMainWindow):
    def __init__(self):
        super(SecondWindow, self).__init__()
        self.setMinimumSize(QSize(750, 340))
        self.country_label = QLabel(self)
        self.country_label.setText('Country name:')
        self.country_label.move(370, 120)


if __name__ == "__main__":
    engine = create_engine('sqlite:///alliances_and_tanks.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker()
    DBSession.bind = engine
    session = DBSession()

    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
